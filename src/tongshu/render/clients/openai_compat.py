"""OpenAI-compatible LLM Renderer client (T501).

Provider-agnostic OpenAI-compatible client targeting DeepSeek by default
(api.deepseek.com). Implements the frozen Renderer contract
(docs/llm_renderer_contract.md, prompt.1.0.0):

Output MUST be strict JSON:
    {"text", "covered_claim_ids", "honored_exclusion_ids", "self_check"}

Design decisions:
  - The frozen system prompt is passed through untouched (contract §4).
  - render_mode (composition mode / capacity / dropped ids / length bounds)
    travels in the USER-message envelope, not the SIR and not the system
    prompt — DECISION-007 puts rendering concerns in the Render Request.
  - covered_claim_ids MUST equal the SIR claim set (full/multi) or the kept
    set (top_k; drops are declared via `degradation` so Layer 1 can validate
    coverage degradation-aware). Fabricated claim ids are never passed
    downstream; divergence triggers a guardrail retry (contract §7).
  - Retry policy per contract §7: same SIR + Render Request, MAY append a
    guardrail line to the system prompt, MAX_RETRIES default 2, then raise
    RenderClientError → the pipeline falls back to TemplateFallback.
  - Defensive hard cap at length.max (mirrors Stub) so a drifting tokenizer
    can never trip Layer 1's length bound.
"""

from __future__ import annotations
import json
import logging
import os
import time
from typing import Any

log = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_MAX_RETRIES = 2


class RenderClientError(RuntimeError):
    """Raised when the LLM client cannot produce a contract-compliant response."""


class OpenAICompatLLMClient:
    """LLMClient implementation against any OpenAI-compatible endpoint.

    Uses the `openai` SDK. Inject `http_client` (e.g. httpx.MockTransport)
    for tests; inject `api_key`/`base_url`/`model` to override env config.
    """

    REQUIRED_KEYS = ("text", "covered_claim_ids", "honored_exclusion_ids", "self_check")

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        temperature: float = 0.3,
        max_retries: int = DEFAULT_MAX_RETRIES,
        use_json_mode: bool = True,
        http_client: Any = None,
        max_transport_retries: int = 2,
        transport_backoff: float = 2.0,
        transport_429_backoff: float = 12.0,
    ):
        self._api_key = (
            api_key
            or os.environ.get("TONGSHU_LLM_API_KEY")
            or os.environ.get("DEEPSEEK_API_KEY")
        )
        if not self._api_key:
            raise RenderClientError(
                "No LLM API key configured. Set DEEPSEEK_API_KEY or TONGSHU_LLM_API_KEY."
            )
        # Resolve base_url/model lazily at construction time (not module import)
        # so TONGSHU_LLM_BASE_URL / TONGSHU_LLM_MODEL in backend/.env take effect
        # (the .env loader runs after openai_compat is imported).
        self._base_url = (
            base_url or os.environ.get("TONGSHU_LLM_BASE_URL") or DEFAULT_BASE_URL
        )
        self._model = model or os.environ.get("TONGSHU_LLM_MODEL") or DEFAULT_MODEL
        self._temperature = temperature
        self._max_retries = max_retries
        self._use_json_mode = use_json_mode
        self._http_client = http_client
        self._max_transport_retries = max_transport_retries
        self._transport_backoff = transport_backoff
        self._transport_429_backoff = transport_429_backoff
        self._client = self._build_sdk_client()

    @property
    def model_id(self) -> str:
        """Resolved model identifier (receipt truth, see Renderer.model_id)."""
        return self._model

    # ------------------------------------------------------------------ #
    # SDK setup
    # ------------------------------------------------------------------ #

    def _build_sdk_client(self):
        from openai import OpenAI

        kwargs: dict[str, Any] = {
            "api_key": self._api_key,
            "base_url": self._base_url,
        }
        if self._http_client is not None:
            kwargs["http_client"] = self._http_client
        return OpenAI(**kwargs)

    # ------------------------------------------------------------------ #
    # LLMClient protocol
    # ------------------------------------------------------------------ #

    def call(
        self,
        system_prompt: str,
        user_payload: str,
        render_mode: dict | None = None,
    ) -> dict:
        """Render SIR through the LLM and return a contract-compliant dict."""
        rm = render_mode or {}
        sir = self._parse_user_payload(user_payload)
        claims = sir.get("atomic_claims", [])
        kept_ids = self._kept_claim_ids(claims, rm)

        user_message = {"render_mode": rm, "sir": sir}

        last_reason = None
        for attempt in range(self._max_retries + 1):
            content, usage = self._request(system_prompt, user_message, last_reason)
            parsed, reason = self._validate(content, kept_ids, rm, usage)
            if parsed is not None:
                return parsed
            last_reason = reason
            log.warning(
                "LLM renderer output rejected (attempt %d/%d): %s",
                attempt + 1,
                self._max_retries + 1,
                reason,
            )

        raise RenderClientError(
            f"LLM renderer failed after {self._max_retries + 1} attempts: {last_reason}"
        )

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_user_payload(user_payload: str | dict) -> dict:
        if isinstance(user_payload, dict):
            return user_payload
        try:
            parsed = json.loads(user_payload)
        except (TypeError, ValueError):
            parsed = {}
        return parsed if isinstance(parsed, dict) else {}

    @staticmethod
    def _kept_claim_ids(claims: list, rm: dict) -> list[str]:
        dropped = set(rm.get("dropped_claim_ids") or [])
        return [
            c.get("claim_id", "")
            for c in claims
            if c.get("claim_id") and c.get("claim_id") not in dropped
        ]

    def _request(
        self, system_prompt: str, user_message: dict, guardrail: str | None
    ) -> tuple[str, dict]:
        """POST to the provider. Returns (content, token_usage)."""
        messages = [{"role": "system", "content": system_prompt}]
        if guardrail:
            # Contract §7.2: retry MAY append a guardrail to the system prompt.
            # Augment the generic "do not repeat" line with the exact expected
            # self_check shape when the rejection was schema-related — real
            # models re-guess the empty placeholder "self_check": {{...}} and
            # sometimes repeat the same mistake, so spell it out literally.
            suffix = f"\n\nThe previous output was rejected because: {guardrail}."
            if "self_check" in guardrail:
                suffix += (
                    ' Your output MUST include "self_check" as exactly '
                    '{"forbidden_content_absent": true, "all_claims_covered": true, '
                    '"length_within_bounds": true} — all three boolean true, no '
                    "other keys, no string values."
                )
            else:
                suffix += " Ensure your next output does not repeat this."
            messages[0]["content"] = system_prompt + suffix
        messages.append(
            {
                "role": "user",
                "content": json.dumps(user_message, ensure_ascii=False),
            }
        )

        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": self._temperature,
        }
        if self._use_json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        # Transport errors: 429 (TPM/quota rate-limit) and 5xx are transient
        # and recoverable by waiting — the contract §7 retry only covers
        # validation rejections, so give transport its own bounded backoff.
        last_exc: Exception | None = None
        for attempt in range(self._max_transport_retries + 1):
            try:
                resp = self._client.chat.completions.create(**kwargs)
                break
            except Exception as e:
                last_exc = e
                status = self._status_of(e)
                if status not in (429, 500, 502, 503, 504):
                    raise RenderClientError(f"LLM API request failed: {e}") from e
                delay = self._transport_429_backoff if status == 429 else self._transport_backoff
                log.warning(
                    "LLM API transient HTTP %s (attempt %d/%d); backing off %.1fs",
                    status, attempt + 1, self._max_transport_retries + 1, delay,
                )
                time.sleep(delay)
        else:
            raise RenderClientError(
                f"LLM API request failed after {self._max_transport_retries + 1} attempts: {last_exc}"
            )

        content = getattr(resp.choices[0].message, "content", "") or ""
        usage: dict = {}
        raw_usage = getattr(resp, "usage", None)
        if raw_usage is not None:
            for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
                if hasattr(raw_usage, key):
                    usage[key] = getattr(raw_usage, key)
        return content, usage

    @staticmethod
    def _status_of(exc: Exception) -> int | None:
        """Best-effort HTTP status from openai SDK / httpx exceptions."""
        status = getattr(exc, "status_code", None)
        if status is not None:
            return int(status)
        response = getattr(exc, "response", None)
        if response is not None:
            return int(getattr(response, "status_code", 0) or 0)
        return None

    def _validate(
        self, content: str, kept_ids: list[str], rm: dict, usage: dict | None = None
    ) -> tuple[dict | None, str | None]:
        """Return (contract-compliant dict, None) or (None, rejection reason)."""
        try:
            parsed = json.loads(content)
        except (ValueError, TypeError):
            return None, "output was not valid JSON"
        if not isinstance(parsed, dict):
            return None, "output JSON root was not an object"

        missing = [k for k in self.REQUIRED_KEYS if k not in parsed]
        if missing:
            return None, f"output missing keys: {missing}"

        text = parsed.get("text")
        if not isinstance(text, str) or not text.strip():
            return None, "text is empty"

        covered = parsed.get("covered_claim_ids")
        if not isinstance(covered, list):
            return None, "covered_claim_ids is not a list"

        # Claim integrity: never pass fabricated ids downstream; missing kept
        # ids is a contract violation and triggers a guardrail retry.
        kept = set(kept_ids)
        fabricated = [cid for cid in covered if cid not in kept]
        if fabricated:
            log.warning("LLM emitted fabricated claim_ids (filtered): %s", fabricated)
        covered_clean = [cid for cid in covered if cid in kept]
        missing_covered = kept - set(covered_clean)
        if missing_covered:
            return None, f"covered_claim_ids missing {sorted(missing_covered)}"

        # Length: defensive hard cap at max (mirrors Stub's guarantee).
        length_cfg = rm.get("length") or {}
        max_len = length_cfg.get("max")
        if max_len and len(text) > max_len:
            text = text[: max_len - 3] + "..."
        min_len = length_cfg.get("min")
        if min_len and len(text) < min_len:
            return None, f"text length {len(text)} below min {min_len}"

        # Contract output_validation.md §4.2/4.7: self_check MUST be an object
        # with all three flags true. Without checking it here the model's
        # noncompliant schema would only be caught in Layer 1 — AFTER the
        # client has accepted the output — so the §7 guardrail retry would
        # never fire. Enforce it here so the model gets the retry it's owed.
        sc = parsed.get("self_check")
        if not isinstance(sc, dict):
            return None, "self_check is not an object"
        bad_flags = [
            k for k in ("forbidden_content_absent", "all_claims_covered", "length_within_bounds")
            if sc.get(k) is not True
        ]
        if bad_flags:
            return None, (
                "self_check flags not all true: "
                f"missing/false {bad_flags}; must set forbidden_content_absent, "
                "all_claims_covered, length_within_bounds all to true"
            )

        parsed["text"] = text
        parsed["covered_claim_ids"] = covered_clean
        parsed["self_check"] = sc
        parsed["usage"] = usage or {}

        # T501 top_k: declare the drop exactly like the Stub so Layer 1 can
        # validate coverage degradation-aware.
        dropped = rm.get("dropped_claim_ids") or []
        if rm.get("mode") == "top_k" and dropped:
            parsed["degradation"] = {
                "mode": "top_k",
                "capacity": rm.get("capacity"),
                "total_claims": len(kept_ids) + len(dropped),
                "dropped_claim_ids": sorted(dropped),
            }

        return parsed, None
