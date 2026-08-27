"""Unit + integration tests for renderer multi-signal capacity (T501).

Covers:
  - _select_render_mode tiering (full / multi / top_k + dropped ids)
  - StubLLMClient capacity curve: N=1..6 all pass length + coverage,
    N>capacity degrades to top_k with a declared degradation block
  - Layer 1 degradation-aware coverage + defensive consistency checks
  - Full render + L1/L2/L3 chain at N=5 (multi) and N=6 (top_k)
  - Render Request max_signals override

Run from backend/:
    PYTHONPATH=src python -m unittest tests.test_render_capacity -v
"""

from __future__ import annotations
import unittest

from tongshu.render.renderer import (
    Renderer,
    StubLLMClient,
    _select_render_mode,
    RENDER_MODE_FULL,
    RENDER_MODE_MULTI,
    RENDER_MODE_TOP_K,
    MAX_SIGNALS_DEFAULT,
)
from tongshu.render.render_request import build_render_request
from tongshu.validation.layer1 import validate_layer1
from tongshu.validation.layer2 import validate_layer2
from tongshu.validation.layer3 import validate_layer3

USO = {
    "SUPPORT": "工作上的支持系统（领导、同事、平台）",
    "ACTION": "工作中的推进力与行动方向",
    "REFLECTION": "工作中的反思、复盘",
    "RELATION": "工作关系、同事生态、上下级动态",
    "CONSTRAINT": "工作结构、流程、规范的限制",
    "RESOURCE": "工作中的资源、报酬、机会",
    "OUTPUT": "工作中的产出、表达、成果",
    "CHANGE": "工作中的变动、转型、调整",
}
VERB = {
    "SUPPORT": "依靠", "ACTION": "推进", "REFLECTION": "复盘",
    "RELATION": "协作", "CONSTRAINT": "克制", "RESOURCE": "获得",
    "OUTPUT": "表达", "CHANGE": "调整",
}


def make_sir(n: int, theme: str = "WORK") -> dict:
    """Synthetic SIR with N atomic claims, one per ontology type."""
    claims = []
    types = list(USO.keys())[:n]
    for i, t in enumerate(types):
        claims.append({
            "claim_id": f"AC-S{str(i).zfill(3)}",
            "signal_type": t,
            "claim": f"{USO[t]} 主体在{theme}主题上以「{VERB[t]}」为主要取向,能量平稳、状态活化。",
            "direction": "STABLE",
            "strength": "MODERATE",
            "source_layers": ["BASELINE"],
            "rule_refs": [],
            "evidence_refs": [],
        })
    return {
        "theme": theme,
        "signals": {"BASELINE": [], "CYCLE_CONTEXT": [], "DAILY_ACTIVATION": []},
        "atomic_claims": claims,
        "exclusions": [],
    }


def render_and_validate(n: int, render_request: dict = None):
    """Run renderer + L1 + L2 + L3 for a synthetic N-claim SIR.

    Mirrors pipeline.py: Layer 2 receives the renderer-declared degradation
    so dropped claims are excluded from entailment.
    """
    # Explicit Stub: the env-gated factory would otherwise hand the Renderer a
    # real LLM client whenever backend/.env carries a key, making these
    # deterministic capacity tests slow / live / rate-limited.
    renderer = Renderer(llm_client=StubLLMClient())
    sir = make_sir(n)
    rreq = render_request or build_render_request("T", "1.0", "WORK").to_dict()
    rendered = renderer.render(sir=sir, render_request=rreq)
    l1 = validate_layer1(rendered.raw_output, sir, rreq, [])
    l2 = validate_layer2(rendered.text, sir, rendered.degradation)
    l3 = validate_layer3(rendered.text, sir)
    return rendered, l1, l2, l3


class TestSelectRenderMode(unittest.TestCase):
    def test_full_under_or_equal_2(self):
        self.assertEqual(_select_render_mode(["a", "b"], MAX_SIGNALS_DEFAULT),
                         (RENDER_MODE_FULL, []))
        self.assertEqual(_select_render_mode(["a"], MAX_SIGNALS_DEFAULT),
                         (RENDER_MODE_FULL, []))

    def test_multi_within_capacity(self):
        self.assertEqual(_select_render_mode(["a", "b", "c"], MAX_SIGNALS_DEFAULT),
                         (RENDER_MODE_MULTI, []))
        ids = [f"s{i}" for i in range(5)]
        self.assertEqual(_select_render_mode(ids, MAX_SIGNALS_DEFAULT),
                         (RENDER_MODE_MULTI, []))

    def test_top_k_over_capacity_drops_tail(self):
        ids = [f"s{i}" for i in range(6)]
        mode, dropped = _select_render_mode(ids, MAX_SIGNALS_DEFAULT)
        self.assertEqual(mode, RENDER_MODE_TOP_K)
        self.assertEqual(dropped, ["s5"])

        ids7 = [f"s{i}" for i in range(7)]
        mode, dropped = _select_render_mode(ids7, MAX_SIGNALS_DEFAULT)
        self.assertEqual(mode, RENDER_MODE_TOP_K)
        self.assertEqual(dropped, ["s5", "s6"])

    def test_capacity_override(self):
        ids = [f"s{i}" for i in range(4)]
        mode, dropped = _select_render_mode(ids, 3)
        self.assertEqual(mode, RENDER_MODE_TOP_K)
        self.assertEqual(dropped, ["s3"])


class TestStubCapacityCurve(unittest.TestCase):
    """N=1..6 through the Renderer: length in bounds, coverage correct."""

    def test_capacity_curve(self):
        for n in range(1, 7):
            rendered, l1, l2, l3 = render_and_validate(n)
            expected_covered = {f"AC-S{str(i).zfill(3)}" for i in range(n)}
            if n > MAX_SIGNALS_DEFAULT:
                expected_covered = {f"AC-S{str(i).zfill(3)}" for i in range(MAX_SIGNALS_DEFAULT)}
            self.assertTrue(80 <= len(rendered.text) <= 150,
                            f"N={n} length {len(rendered.text)} out of bounds")
            self.assertEqual(set(rendered.covered_claim_ids), expected_covered,
                             f"N={n} coverage mismatch")
            self.assertTrue(l1.passed, f"N={n} L1 failed: {l1.errors}")
            self.assertTrue(l2.passed, f"N={n} L2 failed: min_sim={l2.min_similarity}")
            self.assertTrue(l3.passed, f"N={n} L3 failed")

    def test_top_k_declares_degradation(self):
        rendered, _, _, _ = render_and_validate(6)
        dg = rendered.degradation
        self.assertIsNotNone(dg)
        self.assertEqual(dg["mode"], RENDER_MODE_TOP_K)
        self.assertEqual(dg["capacity"], MAX_SIGNALS_DEFAULT)
        self.assertEqual(dg["total_claims"], 6)
        self.assertEqual(dg["dropped_claim_ids"], ["AC-S005"])

    def test_multi_and_full_have_no_degradation(self):
        for n in (2, 5):
            rendered, _, _, _ = render_and_validate(n)
            self.assertIsNone(rendered.degradation, f"N={n} should not degrade")

    def test_max_signals_override(self):
        rreq = build_render_request("T", "1.0", "WORK", max_signals=3).to_dict()
        rendered, l1, l2, l3 = render_and_validate(4, render_request=rreq)
        self.assertEqual(rendered.degradation["dropped_claim_ids"], ["AC-S003"])
        self.assertTrue(l1.passed, f"L1 failed: {l1.errors}")
        self.assertTrue(l2.passed and l3.passed)

    def test_full_mode_text_is_verbatim_echo(self):
        # N=2 full mode: both claims appear verbatim in the text (golden path).
        rendered, _, _, _ = render_and_validate(2)
        sir = make_sir(2)
        for c in sir["atomic_claims"]:
            self.assertIn(c["claim"], rendered.text)

    def test_multi_mode_keeps_all_claims_represented(self):
        # N=5 multi: every claim's opening excerpt appears (condensed, not full).
        rendered, _, _, _ = render_and_validate(5)
        sir = make_sir(5)
        for c in sir["atomic_claims"]:
            self.assertIn(c["claim"][:6], rendered.text)
            self.assertIn(c["signal_type"], rendered.text)


class TestLayer1Degradation(unittest.TestCase):
    def _ok_output(self, covered, dropped=None, text="x" * 120):
        out = {
            "text": text,
            "covered_claim_ids": covered,
            "honored_exclusion_ids": [],
            "self_check": {
                "forbidden_content_absent": True,
                "all_claims_covered": True,
                "length_within_bounds": True,
            },
        }
        if dropped:
            out["degradation"] = {"mode": "top_k", "dropped_claim_ids": dropped}
        return out

    def test_degraded_coverage_accepts_declared_drops(self):
        sir = make_sir(3)
        out = self._ok_output(
            covered=["AC-S000", "AC-S001"], dropped=["AC-S002"]
        )
        rreq = build_render_request("T", "1.0", "WORK").to_dict()
        res = validate_layer1(out, sir, rreq, [])
        self.assertTrue(res.passed, f"errors: {res.errors}")
        self.assertTrue(res.details["degraded"])
        self.assertEqual(res.details["dropped_claim_ids"], ["AC-S002"])

    def test_undegraded_coverage_still_strict(self):
        sir = make_sir(2)
        out = self._ok_output(covered=["AC-S000"])  # missing AC-S001, no degradation
        rreq = build_render_request("T", "1.0", "WORK").to_dict()
        res = validate_layer1(out, sir, rreq, [])
        self.assertFalse(res.passed)
        self.assertFalse(res.details["coverage_ok"])

    def test_dropped_but_covered_is_rejected(self):
        sir = make_sir(3)
        out = self._ok_output(
            covered=["AC-S000", "AC-S001", "AC-S002"], dropped=["AC-S002"]
        )
        rreq = build_render_request("T", "1.0", "WORK").to_dict()
        res = validate_layer1(out, sir, rreq, [])
        self.assertFalse(res.passed)
        self.assertTrue(any("dropped but still covered" in e for e in res.errors))

    def test_dropped_unknown_claim_is_rejected(self):
        sir = make_sir(3)
        out = self._ok_output(
            covered=["AC-S000", "AC-S001"], dropped=["AC-S999"]
        )
        rreq = build_render_request("T", "1.0", "WORK").to_dict()
        res = validate_layer1(out, sir, rreq, [])
        self.assertFalse(res.passed)
        self.assertTrue(any("unknown claim_ids" in e for e in res.errors))

    def test_no_degradation_key_means_not_degraded(self):
        sir = make_sir(2)
        out = self._ok_output(covered=["AC-S000", "AC-S001"])
        rreq = build_render_request("T", "1.0", "WORK").to_dict()
        res = validate_layer1(out, sir, rreq, [])
        self.assertFalse(res.details["degraded"])
        self.assertEqual(res.details["dropped_claim_ids"], [])

    def test_cannot_drop_all_claims(self):
        sir = make_sir(2)
        out = self._ok_output(covered=[], dropped=["AC-S000", "AC-S001"])
        rreq = build_render_request("T", "1.0", "WORK").to_dict()
        res = validate_layer1(out, sir, rreq, [])
        self.assertFalse(res.passed)
        self.assertTrue(any("cannot drop all" in e for e in res.errors))


class TestLayer2Degradation(unittest.TestCase):
    def test_dropped_claim_not_checked(self):
        # Rendered text contains only the first claim's content; the dropped
        # claim would pull min_sim below threshold if checked.
        sir = make_sir(6)
        text = sir["atomic_claims"][0]["claim"]  # only SUPPORT content
        dg = {"mode": "top_k", "dropped_claim_ids": ["AC-S005"]}
        res = validate_layer2(text, sir, dg)
        self.assertTrue(res.passed, f"min_sim={res.min_similarity}")
        self.assertEqual(res.details["skipped_claim_ids"], ["AC-S005"])
        self.assertNotIn("AC-S005", [c for c, _ in res.details["claim_similarities"]])

    def test_no_degradation_checks_all(self):
        sir = make_sir(2)
        text = "完全无关的文本内容，不含任何信号语义。"
        res = validate_layer2(text, sir)
        self.assertEqual(res.details["skipped_claim_ids"], [])
        self.assertEqual(len(res.details["claim_similarities"]), 2)


if __name__ == "__main__":
    unittest.main()
