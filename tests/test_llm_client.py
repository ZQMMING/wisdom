"""Unit tests for the OpenAI-compatible LLM renderer client (T501).

Simulates the provider endpoint with httpx.MockTransport so no real API
calls are made. Covers: happy path, JSON-parse retry + guardrail, fabricated
claim-id filtering, missing-coverage retry→raise, top_k degradation block,
length clamp, below-min rejection, missing API key, transport error, and the
env-gated factory.
"""

from __future__ import annotations
import json
import os
import unittest
from contextlib import contextmanager
from unittest.mock import patch

import httpx

# NOTE: on this Windows/uv-Python, the OpenSSL 3 provider locates its config
# via env vars, so emptying os.environ (patch.dict clear=True) breaks
# ssl.SSLContext() itself ("[SSL] unknown error"). Also os.environ rejects
# None values, so patch.dict's None-delete is unusable here. Pop/restore
# individual keys instead.


@contextmanager
def _env_without(*names: str):
    saved = {n: os.environ.pop(n, None) for n in names}
    try:
        yield
    finally:
        for n, v in saved.items():
            if v is not None:
                os.environ[n] = v

from tongshu.render.clients import get_llm_client
from tongshu.render.clients.openai_compat import OpenAICompatLLMClient, RenderClientError

# ---------------------------------------------------------------------- #
# helpers
# ---------------------------------------------------------------------- #


def _completion(content: str) -> dict:
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 1700000000,
        "model": "deepseek-chat",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content, "refusal": None},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10},
    }


def _sir(claims: list[dict]) -> dict:
    return {"theme": "WORK", "atomic_claims": claims, "exclusions": []}


def _client(handler) -> OpenAICompatLLMClient:
    transport = httpx.MockTransport(handler)
    http = httpx.Client(transport=transport)
    return OpenAICompatLLMClient(
        api_key="test-key",
        base_url="http://test.local/v1",
        http_client=http,
    )


def _rm(mode: str = "full", dropped: list[str] | None = None, min_len: int = 80, max_len: int = 150) -> dict:
    return {
        "mode": mode,
        "capacity": 5,
        "dropped_claim_ids": dropped or [],
        "length": {"min": min_len, "max": max_len},
    }


def _ok_payload(covered: list[str], text_len: int = 90) -> dict:
    return {
        "text": "今日【WORK】主题方向： " + "z" * text_len,
        "covered_claim_ids": covered,
        "honored_exclusion_ids": [],
        "self_check": {
            "forbidden_content_absent": True,
            "all_claims_covered": True,
            "length_within_bounds": True,
        },
    }


# ---------------------------------------------------------------------- #
# tests
# ---------------------------------------------------------------------- #


class TestOpenAICompatLLMClient(unittest.TestCase):
    def test_happy_path_full_mode(self):
        claims = [{"claim_id": "AC-A", "claim": "x" * 30}, {"claim_id": "AC-B", "claim": "y" * 30}]
        sir = _sir(claims)

        def handler(request):
            return httpx.Response(200, json=_completion(json.dumps(_ok_payload(["AC-A", "AC-B"]), ensure_ascii=False)))

        out = _client(handler).call("sys", json.dumps(sir), render_mode=_rm())
        self.assertEqual(out["covered_claim_ids"], ["AC-A", "AC-B"])
        self.assertTrue(out["self_check"]["all_claims_covered"])
        self.assertNotIn("degradation", out)

    def test_retry_appends_guardrail_on_json_failure(self):
        calls = {"n": 0, "system_content": None}
        claims = [{"claim_id": "AC-A", "claim": "x" * 40}]
        sir = _sir(claims)

        def handler(request):
            body = json.loads(request.content)
            calls["n"] += 1
            calls["system_content"] = body["messages"][0]["content"]
            if calls["n"] == 1:
                return httpx.Response(200, json=_completion("not json at all"))
            return httpx.Response(200, json=_completion(json.dumps(_ok_payload(["AC-A"]), ensure_ascii=False)))

        out = _client(handler).call("SYSTEM PROMPT", json.dumps(sir), render_mode=_rm())
        self.assertEqual(calls["n"], 2)
        self.assertIn("rejected because", calls["system_content"])

    def test_raises_after_all_retries_exhausted(self):
        def handler(request):
            return httpx.Response(200, json=_completion("garbage"))

        with self.assertRaises(RenderClientError):
            _client(handler).call("sys", json.dumps(_sir([{"claim_id": "AC-A", "claim": "x"}])), render_mode=_rm())

    def test_fabricated_claim_ids_filtered_without_retry(self):
        claims = [{"claim_id": "AC-A", "claim": "x" * 40}]
        sir = _sir(claims)

        def handler(request):
            return httpx.Response(200, json=_completion(json.dumps(_ok_payload(["AC-A", "AC-FAKE"]), ensure_ascii=False)))

        out = _client(handler).call("sys", json.dumps(sir), render_mode=_rm())
        self.assertEqual(out["covered_claim_ids"], ["AC-A"])

    def test_missing_covered_claim_triggers_retry_then_raise(self):
        calls = {"n": 0}
        claims = [{"claim_id": "AC-A", "claim": "x" * 40}]
        sir = _sir(claims)

        def handler(request):
            calls["n"] += 1
            return httpx.Response(200, json=_completion(json.dumps(_ok_payload([]), ensure_ascii=False)))

        with self.assertRaises(RenderClientError):
            _client(handler).call("sys", json.dumps(sir), render_mode=_rm())
        self.assertEqual(calls["n"], 3)  # 1 initial + 2 retries

    def test_top_k_degradation_block(self):
        claims = [{"claim_id": f"AC-{i}", "claim": "x" * 30} for i in range(6)]
        sir = _sir(claims)
        rm = _rm(mode="top_k", dropped=["AC-5"])

        def handler(request):
            return httpx.Response(200, json=_completion(json.dumps(_ok_payload(["AC-0", "AC-1", "AC-2", "AC-3", "AC-4"]), ensure_ascii=False)))

        out = _client(handler).call("sys", json.dumps(sir), render_mode=rm)
        self.assertEqual(out["degradation"]["mode"], "top_k")
        self.assertEqual(out["degradation"]["capacity"], 5)
        self.assertEqual(out["degradation"]["total_claims"], 6)
        self.assertEqual(out["degradation"]["dropped_claim_ids"], ["AC-5"])
        self.assertNotIn("AC-5", out["covered_claim_ids"])

    def test_length_clamped_at_max(self):
        claims = [{"claim_id": "AC-A", "claim": "x" * 40}]
        sir = _sir(claims)

        def handler(request):
            return httpx.Response(200, json=_completion(json.dumps(_ok_payload(["AC-A"], text_len=300), ensure_ascii=False)))

        out = _client(handler).call("sys", json.dumps(sir), render_mode=_rm())
        self.assertLessEqual(len(out["text"]), 150)
        self.assertTrue(out["text"].endswith("..."))

    def test_below_min_length_rejected(self):
        claims = [{"claim_id": "AC-A", "claim": "x"}]
        sir = _sir(claims)

        def handler(request):
            return httpx.Response(200, json=_completion(json.dumps(_ok_payload(["AC-A"], text_len=2), ensure_ascii=False)))

        with self.assertRaises(RenderClientError):
            _client(handler).call("sys", json.dumps(sir), render_mode=_rm())

    def test_no_api_key_raises_at_construction(self):
        with _env_without("DEEPSEEK_API_KEY", "TONGSHU_LLM_API_KEY"):
            with self.assertRaises(RenderClientError):
                OpenAICompatLLMClient(api_key=None, base_url="http://test.local/v1")

    def test_transport_error_raises(self):
        # 500 is transient, but with max_transport_retries=0 it must fail
        # immediately (the "not silently swallowed" guarantee).
        def handler(request):
            return httpx.Response(500, text="boom")

        c = _client(handler)
        c._max_transport_retries = 0
        with self.assertRaises(RenderClientError):
            c.call("sys", json.dumps(_sir([{"claim_id": "AC-A", "claim": "x"}])), render_mode=_rm())

    def test_transport_429_retries_with_backoff_then_succeeds(self):
        calls = {"n": 0}

        def handler(request):
            calls["n"] += 1
            if calls["n"] == 1:
                return httpx.Response(429, json={"error": {"message": "inference tpm exhausted"}})
            return httpx.Response(200, json=_completion(json.dumps(_ok_payload(["AC-A"]), ensure_ascii=False)))

        with patch("tongshu.render.clients.openai_compat.time.sleep") as mock_sleep:
            out = _client(handler).call(
                "sys", json.dumps(_sir([{"claim_id": "AC-A", "claim": "x" * 40}])), render_mode=_rm()
            )
        self.assertEqual(calls["n"], 2)
        self.assertEqual(out["covered_claim_ids"], ["AC-A"])
        mock_sleep.assert_called_once()

    def test_transport_500_exhausts_retries_then_raises(self):
        calls = {"n": 0}

        def handler(request):
            calls["n"] += 1
            return httpx.Response(503, text="unavailable")

        with patch("tongshu.render.clients.openai_compat.time.sleep"):
            with self.assertRaises(RenderClientError):
                _client(handler).call(
                    "sys", json.dumps(_sir([{"claim_id": "AC-A", "claim": "x"}])), render_mode=_rm()
                )
        # Each §7 validation attempt (3) does its own transport retry loop (3)
        # against a persistently-transient endpoint → 3 × 3 = 9 calls.
        self.assertEqual(calls["n"], 9)

    def test_bad_self_check_triggers_guardrail_retry(self):
        """Contract output_validation.md §4.7: self_check flags must all be
        true. The client must reject a wrong schema so the §7 guardrail retry
        fires (previously this was only caught in Layer 1, too late)."""
        calls = {"n": 0, "system_content": None}
        claims = [{"claim_id": "AC-A", "claim": "x" * 40}]
        sir = _sir(claims)

        def handler(request):
            body = json.loads(request.content)
            calls["n"] += 1
            calls["system_content"] = body["messages"][0]["content"]
            if calls["n"] == 1:
                # Model invented its own self_check schema.
                bad = dict(_ok_payload(["AC-A"]))
                bad["self_check"] = {
                    "no_added_content": True,
                    "no_modified_claims": True,
                    "length_ok": True,
                    "tone_ok": True,
                }
                return httpx.Response(200, json=_completion(json.dumps(bad, ensure_ascii=False)))
            return httpx.Response(200, json=_completion(json.dumps(_ok_payload(["AC-A"]), ensure_ascii=False)))

        out = _client(handler).call("sys", json.dumps(sir), render_mode=_rm())
        self.assertEqual(calls["n"], 2)
        self.assertIn("self_check", calls["system_content"])

    def test_bad_self_check_always_fails_then_raises(self):
        calls = {"n": 0}
        claims = [{"claim_id": "AC-A", "claim": "x" * 40}]
        sir = _sir(claims)

        def handler(request):
            calls["n"] += 1
            bad = dict(_ok_payload(["AC-A"]))
            bad["self_check"] = {"forbidden_content_absent": True}  # missing 2 flags
            return httpx.Response(200, json=_completion(json.dumps(bad, ensure_ascii=False)))

        with self.assertRaises(RenderClientError):
            _client(handler).call("sys", json.dumps(sir), render_mode=_rm())
        self.assertEqual(calls["n"], 3)


class TestGetLLMClientGating(unittest.TestCase):
    def test_env_gate(self):
        with _env_without("DEEPSEEK_API_KEY", "TONGSHU_LLM_API_KEY"):
            self.assertIsNone(get_llm_client())
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "k"}):
            client = get_llm_client()
            self.assertIsInstance(client, OpenAICompatLLMClient)


if __name__ == "__main__":
    unittest.main()
