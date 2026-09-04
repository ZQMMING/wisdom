"""Block F — V3.6 §22-23 审计四道 Gate(G1-G4 命名对齐包装)。

Covers:
  - G1 Evidence Gate:rule/evidence linkage、证据存在性解析、AC-* traceability
  - G2 Translation Gate:mapping_refs 解析、modern_theme 成对性与 registry 一致
  - G3 Safety Gate:复合词 + 模式逐类命中,良性文本不误伤
  - G4 Output Gate:schema + meta 版本族 + 子门聚合(fail-closed)
  - §63 遥测:block 计数随门 BLOCK 累加、reset、/health 暴露
  - pipeline 接线:审计 entry 的 validation_results["gates"] 四项齐全,
    fail-closed 时 validation_passed=False 走模板回退
"""

from __future__ import annotations
import json
import os
import unittest
from contextlib import contextmanager
from datetime import date
from pathlib import Path

from tongshu.audit.gates import (
    GateResult,
    evidence_gate,
    translation_gate,
    safety_gate,
    output_gate,
    run_gates,
    gates_passed,
    gate_block_counts,
    reset_gate_block_counts,
)
from tongshu.reasoning.mapping_registry import MappingRegistry
from tongshu.pipeline import TONGSHUPipeline

_LLM_ENV_VARS = ("TONGSHU_LLM_API_KEY", "TONGSHU_LLM_BASE_URL", "TONGSHU_LLM_MODEL", "DEEPSEEK_API_KEY")

_ROOT = Path(__file__).resolve().parents[1]  # .../wisdom (project root)


@contextmanager
def _env_without(*names: str):
    saved = {n: os.environ.pop(n, None) for n in names}
    try:
        yield
    finally:
        for n, v in saved.items():
            if v is not None:
                os.environ[n] = v


def _registry() -> MappingRegistry:
    return MappingRegistry(_ROOT / "backend" / "data", _ROOT / "docs")


def _valid_claim(overrides: dict | None = None) -> dict:
    claim = {
        "claim_id": "AC-SIG-BA-YI000",
        "signal_type": "SUPPORT",
        "claim": "主体在 WORK 主题上 SUPPORT 类信号。",
        "direction": "STABLE",
        "strength": "MODERATE",
        "source_layers": ["BASELINE"],
        "rule_refs": ["ZPZ-101"],
        "evidence_refs": ["E-ZPZ-101-001"],
    }
    if overrides:
        claim.update(overrides)
    return claim


def _full_meta() -> dict:
    return {
        "request_id": "RR-ABCD1234",
        "trace_id": "TRACE-ABCD1234",
        "document_id": "CC-GOLDEN-001-0001",
        "schema_version": "3.6.0",
        "calculation_version": "1.0.0",
        "knowledge_version": "1.0.0",
        "mapping_version": "0.1.0",
        "translation_version": "0.1.0",
        "audit_version": "1.0.0",
        "model_version": "stub",
        "created_at": "2026-08-18T00:00:00+00:00",
    }


class TestEvidenceGate(unittest.TestCase):
    def test_pass_when_all_linkages_resolve(self):
        sir = {"atomic_claims": [_valid_claim()]}
        g = evidence_gate(sir, {"E-ZPZ-101-001"})
        self.assertTrue(g.passed)
        self.assertEqual(g.gate, "G1")
        self.assertEqual(g.reasons, [])

    def test_empty_evidence_refs_blocks(self):
        sir = {"atomic_claims": [_valid_claim({"evidence_refs": []})]}
        g = evidence_gate(sir, {"E-ZPZ-101-001"})
        self.assertFalse(g.passed)
        self.assertTrue(any("empty evidence_refs" in r for r in g.reasons))

    def test_unresolved_evidence_ref_blocks(self):
        sir = {"atomic_claims": [_valid_claim({"evidence_refs": ["E-NOPE-001"]})]}
        g = evidence_gate(sir, {"E-ZPZ-101-001"})
        self.assertFalse(g.passed)
        self.assertTrue(any("unresolved" in r and "E-NOPE-001" in r for r in g.reasons))

    def test_empty_rule_refs_blocks(self):
        sir = {"atomic_claims": [_valid_claim({"rule_refs": []})]}
        self.assertFalse(evidence_gate(sir, {"E-ZPZ-101-001"}).passed)

    def test_no_source_layers_blocks(self):
        sir = {"atomic_claims": [_valid_claim({"source_layers": []})]}
        self.assertFalse(evidence_gate(sir, {"E-ZPZ-101-001"}).passed)

    def test_non_ac_claim_id_blocks(self):
        sir = {"atomic_claims": [_valid_claim({"claim_id": "X-1"})]}
        self.assertFalse(evidence_gate(sir, {"E-ZPZ-101-001"}).passed)

    def test_no_claims_blocks(self):
        self.assertFalse(evidence_gate({"atomic_claims": []}, {"E-ZPZ-101-001"}).passed)

    def test_existence_checked_even_without_evidence_ids(self):
        """evidence_ids=None:G1 仍检查 evidence_refs 非空,只是跳过解析。"""
        sir = {"atomic_claims": [_valid_claim({"evidence_refs": ["E-ANY-1"]})]}
        self.assertTrue(evidence_gate(sir, None).passed)
        sir_bad = {"atomic_claims": [_valid_claim({"evidence_refs": []})]}
        self.assertFalse(evidence_gate(sir_bad, None).passed)


class TestTranslationGate(unittest.TestCase):
    def setUp(self):
        self.reg = _registry()

    def test_pass_when_no_mappings(self):
        """无标签层 claim 不挡道(词库是可选的现代语层)。"""
        sir = {"atomic_claims": [_valid_claim()]}
        self.assertTrue(translation_gate(sir, self.reg).passed)

    def test_pass_when_mappings_resolve_and_consistent(self):
        claim = _valid_claim({"mapping_refs": ["MAP-1001"], "modern_theme": "滋养与根基支撑"})
        self.assertTrue(translation_gate({"atomic_claims": [claim]}, self.reg).passed)

    def test_unknown_mapping_id_blocks(self):
        claim = _valid_claim({"mapping_refs": ["MAP-9999"], "modern_theme": "X"})
        g = translation_gate({"atomic_claims": [claim]}, self.reg)
        self.assertFalse(g.passed)
        self.assertTrue(any("MAP-9999" in r for r in g.reasons))

    def test_theme_mismatch_against_registry_blocks(self):
        claim = _valid_claim({"mapping_refs": ["MAP-1001"], "modern_theme": "错误主题"})
        g = translation_gate({"atomic_claims": [claim]}, self.reg)
        self.assertFalse(g.passed)
        self.assertTrue(any("modern_theme" in r for r in g.reasons))

    def test_refs_without_theme_blocks(self):
        claim = _valid_claim({"mapping_refs": ["MAP-1001"]})
        self.assertFalse(translation_gate({"atomic_claims": [claim]}, self.reg).passed)

    def test_theme_without_refs_blocks(self):
        claim = _valid_claim({"modern_theme": "滋养与根基支撑"})
        self.assertFalse(translation_gate({"atomic_claims": [claim]}, self.reg).passed)

    def test_multi_mapping_claim_theme_matches_first(self):
        """多映射 claim:modern_theme 只与首条(确定性胜者)比对 —— apply_to_claims 契约。"""
        claim = _valid_claim({"mapping_refs": ["MAP-1001", "MAP-1002"], "modern_theme": "滋养与根基支撑"})
        self.assertTrue(translation_gate({"atomic_claims": [claim]}, self.reg).passed)

    def test_multi_mapping_claim_theme_mismatch_blocks(self):
        """多映射 claim 的 theme 若取次条映射的主题,与首条不一致 → block。"""
        claim = _valid_claim({"mapping_refs": ["MAP-1001", "MAP-1002"], "modern_theme": "洞察与偏门资源"})
        self.assertFalse(translation_gate({"atomic_claims": [claim]}, self.reg).passed)

    def test_registry_none_skips_resolution_but_keeps_pairing(self):
        """registry=None(词库未配置):解析类检查跳过,成对性仍查。"""
        claim = _valid_claim({"mapping_refs": ["MAP-1001"]})
        # 无 registry 时 refs-without-theme 仍 block;解析不 block。
        self.assertFalse(translation_gate({"atomic_claims": [claim]}, None).passed)
        full = _valid_claim({"mapping_refs": ["MAP-1001"], "modern_theme": "任意"})
        self.assertTrue(translation_gate({"atomic_claims": [full]}, None).passed)


class TestSafetyGate(unittest.TestCase):
    def test_benign_text_passes(self):
        text = "今日宜稳中求进,注意休息。明天天气转凉,建议关注变化,不宜冒进。"
        self.assertTrue(safety_gate(text).passed)

    def test_financial_guarantee_blocks(self):
        self.assertFalse(safety_gate("此局稳赚不赔。").passed)
        self.assertFalse(safety_gate("保证收益可观。").passed)

    def test_medical_claim_blocks(self):
        self.assertFalse(safety_gate("此法包治此病。").passed)
        self.assertFalse(safety_gate("保证痊愈,无副作用。").passed)

    def test_deterministic_prediction_blocks(self):
        self.assertFalse(safety_gate("此行必定成功。").passed)
        self.assertFalse(safety_gate("你一定会遇到贵人。").passed)

    def test_fear_induction_blocks(self):
        self.assertFalse(safety_gate("此局血光之灾。").passed)
        self.assertFalse(safety_gate("命中必有灾祸。").passed)

    def test_coercive_guidance_blocks(self):
        self.assertFalse(safety_gate("你必须今日行动。").passed)
        self.assertFalse(safety_gate("你万万不能北上。").passed)

    def test_probability_claim_blocks(self):
        self.assertFalse(safety_gate("有 80% 可能获利。").passed)
        self.assertFalse(safety_gate("成功率 95% 会达成。").passed)

    def test_forbidden_word_blocks(self):
        self.assertFalse(safety_gate("建议买入 绩优股。").passed)

    def test_empty_text_passes(self):
        self.assertTrue(safety_gate("").passed)


class TestOutputGate(unittest.TestCase):
    @staticmethod
    def _ok(gate: str) -> GateResult:
        return GateResult(gate, True, [])

    def test_pass_aggregates_all_ok(self):
        sir = {"atomic_claims": [_valid_claim()], "meta": _full_meta()}
        g = output_gate(sir, g1=self._ok("G1"), g2=self._ok("G2"), g3=self._ok("G3"), schema_valid=True)
        self.assertTrue(g.passed)

    def test_schema_invalid_blocks(self):
        sir = {"atomic_claims": [], "meta": _full_meta()}
        g = output_gate(sir, g1=self._ok("G1"), g2=self._ok("G2"), g3=self._ok("G3"),
                        schema_valid=False, schema_errors=["meta/trace_id: None"])
        self.assertFalse(g.passed)
        self.assertTrue(any("Schema" in r for r in g.reasons))

    def test_missing_meta_blocks(self):
        sir = {"atomic_claims": []}
        g = output_gate(sir, g1=self._ok("G1"), g2=self._ok("G2"), g3=self._ok("G3"), schema_valid=True)
        self.assertFalse(g.passed)
        self.assertTrue(any("meta missing" in r for r in g.reasons))

    def test_missing_trace_id_blocks(self):
        meta = _full_meta()
        del meta["trace_id"]
        sir = {"atomic_claims": [], "meta": meta}
        g = output_gate(sir, g1=self._ok("G1"), g2=self._ok("G2"), g3=self._ok("G3"), schema_valid=True)
        self.assertFalse(g.passed)
        self.assertTrue(any("trace_id" in r for r in g.reasons))

    def test_missing_version_field_blocks(self):
        meta = _full_meta()
        del meta["schema_version"]
        sir = {"atomic_claims": [], "meta": meta}
        g = output_gate(sir, g1=self._ok("G1"), g2=self._ok("G2"), g3=self._ok("G3"), schema_valid=True)
        self.assertFalse(g.passed)
        self.assertTrue(any("schema_version" in r for r in g.reasons))

    def test_subgate_block_propagates_to_g4(self):
        sir = {"atomic_claims": [], "meta": _full_meta()}
        blocked = GateResult("G3", False, ["forbidden word"])
        g = output_gate(sir, g1=self._ok("G1"), g2=self._ok("G2"), g3=blocked, schema_valid=True)
        self.assertFalse(g.passed)
        self.assertTrue(any("G3 blocked" in r for r in g.reasons))


class TestRunGatesAndTelemetry(unittest.TestCase):
    def setUp(self):
        reset_gate_block_counts()

    def tearDown(self):
        reset_gate_block_counts()

    def test_full_pass_pipeline_scenario(self):
        sir = {
            "atomic_claims": [_valid_claim(
                {"mapping_refs": ["MAP-1001"], "modern_theme": "滋养与根基支撑"}
            )],
            "meta": _full_meta(),
        }
        reg = _registry()
        gates = run_gates(
            sir, "今日宜稳中求进,注意休息。",
            evidence_ids={"E-ZPZ-101-001"},
            registry=reg,
            schema_valid=True,
        )
        self.assertEqual([g.gate for g in gates], ["G1", "G2", "G3", "G4"])
        self.assertTrue(gates_passed(gates))
        self.assertEqual(gate_block_counts(), {"G1": 0, "G2": 0, "G3": 0, "G4": 0})

    def test_fail_closed_blocks_and_counts(self):
        sir = {"atomic_claims": [_valid_claim()], "meta": _full_meta()}
        gates = run_gates(sir, "此局稳赚不赔。", evidence_ids={"E-ZPZ-101-001"})
        self.assertFalse(gates_passed(gates))
        counts = gate_block_counts()
        self.assertEqual(counts["G3"], 1)
        self.assertEqual(counts["G4"], 1)  # 子门 BLOCK 传播到聚合门
        self.assertEqual(counts["G1"], 0)
        self.assertEqual(counts["G2"], 0)

    def test_g1_block_counts(self):
        sir = {"atomic_claims": [_valid_claim({"evidence_refs": []})], "meta": _full_meta()}
        run_gates(sir, "今日平稳。", evidence_ids={"E-ZPZ-101-001"})
        counts = gate_block_counts()
        self.assertEqual(counts["G1"], 1)
        self.assertEqual(counts["G4"], 1)

    def test_multiple_blocks_accumulate(self):
        sir = {"atomic_claims": [_valid_claim()], "meta": _full_meta()}
        for _ in range(3):
            run_gates(sir, "你必须今日行动。", evidence_ids={"E-ZPZ-101-001"})
        counts = gate_block_counts()
        self.assertEqual(counts["G3"], 3)
        self.assertEqual(counts["G4"], 3)

    def test_reset_clears_counts(self):
        sir = {"atomic_claims": [], "meta": _full_meta()}
        run_gates(sir, "你必须今日行动。")
        self.assertEqual(gate_block_counts()["G3"], 1)
        reset_gate_block_counts()
        self.assertEqual(gate_block_counts(), {"G1": 0, "G2": 0, "G3": 0, "G4": 0})


class TestPipelineWiring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with _env_without(*_LLM_ENV_VARS):
            cls.pipeline = TONGSHUPipeline.for_demo(_ROOT)

    def setUp(self):
        reset_gate_block_counts()

    def tearDown(self):
        reset_gate_block_counts()

    def test_audit_records_gates_and_full_pass(self):
        """Stub 渲染 + 真实 SIR:四道门全过,审计带 gates 数组,验证 PASS。"""
        r = self.pipeline.run(
            analysis_date=date(2026, 8, 17),
            birth_date=(1984, 12, 7, 16),
            gender="male",
            theme="WORK",
        )
        self.assertTrue(r.validation_passed)
        entry = self._last_audit_entry(r.audit_entry_id)
        vr = entry["validation_results"]
        self.assertEqual(vr["final_decision"], "PASS")
        gates = vr["gates"]
        self.assertEqual([g["gate"] for g in gates], ["G1", "G2", "G3", "G4"])
        self.assertTrue(all(g["passed"] for g in gates))
        self.assertEqual(gate_block_counts()["G4"], 0)

    def test_g3_block_forces_template_fallback(self):
        """把 safety_gate 命中注入:fail-closed → validation_passed False + 模板回退。

        回退文本由 cross_result.status 决定(确定性模板),只断言非空。
        """
        # 直接把渲染文本替换为含违禁词的文本(模拟 LLM 输出)。RenderResult 的
        # degradation / token_usage 是 raw_output 派生的属性,直接构造文本即可。
        original_render = self.pipeline.renderer.render
        from tongshu.render.renderer import RenderResult  # noqa: F401

        def poisoned(sir, render_request):
            res = original_render(sir, render_request)
            return RenderResult(
                text="此局稳赚不赔,务必今朝行动。",
                covered_claim_ids=res.covered_claim_ids,
                honored_exclusion_ids=res.honored_exclusion_ids,
                self_check=res.self_check,
                raw_output=res.raw_output,
            )

        self.pipeline.renderer.render = poisoned
        try:
            r = self.pipeline.run(
                analysis_date=date(2026, 8, 17),
                birth_date=(1984, 12, 7, 16),
                gender="male",
                theme="WORK",
            )
        finally:
            self.pipeline.renderer.render = original_render
        self.assertFalse(r.validation_passed)
        self.assertEqual(r.source, "template_fallback")
        self.assertTrue(len(r.rendered_text) > 0)
        entry = self._last_audit_entry(r.audit_entry_id)
        gates = {g["gate"]: g for g in entry["validation_results"]["gates"]}
        self.assertFalse(gates["G3"]["passed"])
        self.assertFalse(gates["G4"]["passed"])
        self.assertEqual(gate_block_counts()["G3"], 1)
        self.assertEqual(gate_block_counts()["G4"], 1)

    def _last_audit_entry(self, entry_id: str) -> dict:
        with open(self.pipeline.audit_writer.log_path, "r", encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                if entry["entry_id"] == entry_id:
                    return entry
        self.fail(f"audit entry {entry_id} not found")


if __name__ == "__main__":
    unittest.main()
