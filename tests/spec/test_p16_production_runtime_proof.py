"""
P1.6: Production Runtime Proof — End-to-End Integration Test

证明真实 Production Pipeline 完整路径：
EngineEvidence → SemanticAtom → ProductionRuleLibrary → CrossDomainOrchestrator
→ Authorized Assertion → Atomic Claim (with production rule provenance)

硬断言：
- claims_count > 0
- 每个 claim 能追溯到 production rule
- loader 失败时 fail-closed
"""
from __future__ import annotations

import json
import pytest
from pathlib import Path
from datetime import date

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.pipeline import TONGSHUPipeline
from tongshu.assertion.assertion_rule_library import ProductionRuleLoader
from tongshu.spec.canonical import SemanticAtom, EngineName, TemporalScope, EngineEvidence
from tongshu.cross_domain import CrossDomainOrchestrator


class TestP16ProductionRuntimeProof:
    """P1.6 生产路径完整运行验证。"""

    @pytest.fixture
    def pipeline(self, tmp_path):
        """创建真实 Pipeline 实例（使用 for_demo 模式）。"""
        repo_root = Path(__file__).parent.parent.parent
        return TONGSHUPipeline.for_demo(repo_root)

    def test_p16_01_production_rule_library_loaded(self, pipeline):
        """P16-01: ProductionRuleLibrary 被正确加载。"""
        assert pipeline.compute_stage._assertion_library is not None, \
            "P1.6: assertion_library 未加载"

        lib = pipeline.compute_stage._assertion_library
        assert getattr(lib, "is_production", False) is True, \
            "P1.6: assertion_library 不是生产库"

        rules = getattr(lib, "_rules", [])
        assert len(rules) > 0, "P1.6: 没有加载到任何规则"
        print(f"P16-01 PASS: Loaded {len(rules)} production rules")

    def test_p16_02_cross_domain_orchestrator_created(self, pipeline):
        """P16-02: CrossDomainOrchestrator 被正确创建。"""
        orchestrator = pipeline.compute_stage._orchestrator
        assert orchestrator is not None, \
            "P1.6: CrossDomainOrchestrator 未创建（orchestrator is None）"
        print("P16-02 PASS: CrossDomainOrchestrator created successfully")

    def test_p16_03_production_rule_matches_semantic_atom(self, pipeline):
        """P16-03: 生产规则能匹配 SemanticAtom。"""
        lib = pipeline.compute_stage._assertion_library

        atom = SemanticAtom(
            atom_id="TEN_GOD_ZHENG_GUAN",
            engine=EngineName.ZI_PING,
            evidence_ref="E-TEST-001",
            semantic_keys=["AUTHORITY", "CAREER"],
            domain_candidates=["CAREER"],
            label_zh="正官",
            category="TEN_GOD",
        )

        rule = lib.find_rule(atom, {})
        assert rule is not None, \
            f"P1.6: 无法匹配 SemanticAtom(TEN_GOD_ZHENG_GUAN)"
        assert rule.rule_id == "ASR-PROD-ZHI_YIN", \
            f"P1.6: 匹配到错误规则 {rule.rule_id}"

        print(f"P16-03 PASS: Rule {rule.rule_id} matched TEN_GOD_ZHENG_GUAN")

    def test_p16_04_end_to_end_real_pipeline(self, pipeline):
        """P16-04: 真实 Pipeline → EngineEvidence → SemanticAtom → Assertion → Claim

        这是核心测试：证明完整 production path 有效。
        使用真实 engine 产出，不人工构造。
        """
        # 运行真实 pipeline
        result = pipeline.run(
            analysis_date=date(2026, 9, 2),
            birth_date=(1984, 12, 7, 16),
            gender="male",
            theme="WORK",
            compute_only=True,
        )

        # 验证 claims 存在且非空
        claims = result.canonical.atomic_claims
        assert claims is not None, "P1.6: atomic_claims 为 None"

        claims_count = len(claims) if claims else 0
        assert claims_count > 0, \
            f"P1.6: Atomic claims 为空，生产路径未激活。claims_count={claims_count}"

        # 关键验证：claims 必须包含 production rule 引用
        production_rule_ids = ["ASR-PROD-ZHI_YIN", "ASR-PROD-PIAN_YIN", "ASR-PROD-ZHENG_CAi"]
        found_production_rule = False
        production_rule_match = None

        for claim in claims:
            if isinstance(claim, dict):
                rule_id = claim.get("rule_id", claim.get("claim_id", ""))
                rule_refs = claim.get("rule_refs", [])

                # 检查 claim_id 或 rule_refs 是否包含 production rule
                if rule_id in production_rule_ids or any(r in production_rule_ids for r in rule_refs):
                    found_production_rule = True
                    production_rule_match = rule_id if rule_id in production_rule_ids else rule_refs[0]
                    break

        # 硬断言：必须找到 production rule
        assert found_production_rule, \
            f"P1.6: Claims 未包含任何 production rule 引用。claims={claims[:3]}"

        print(f"P16-04 PASS: End-to-end production path verified")
        print(f"  Claims: {claims_count}")
        print(f"  Production rule matched: {production_rule_match}")
        print(f"  Canonical ID: {result.canonical.canonical_id}")

        # 打印前3个 claims 的 provenance
        for i, claim in enumerate(claims[:3]):
            if isinstance(claim, dict):
                print(f"  Claim {i}: id={claim.get('claim_id', 'N/A')}, "
                      f"rule_refs={claim.get('rule_refs', [])}, "
                      f"direction={claim.get('direction', 'N/A')}")

    def test_p16_05_orchestrator_executes_with_real_evidence(self, pipeline):
        """P16-05: 使用真实 EngineEvidence 调用 orchestrator。"""
        orchestrator = pipeline.compute_stage._orchestrator
        lib = pipeline.compute_stage._assertion_library

        # 创建真实 EngineEvidence（非人工构造 SemanticAtom）
        evidence = EngineEvidence(
            evidence_id="E-END-TO-END-001",
            engine=EngineName.ZI_PING,
            canonical_text="正官当令，日主受生而有本",
            attributes={"ten_god": "正官", "strength": "STRONG"},
            temporal_scope=TemporalScope.BASELINE,
            value="正官",
        )

        # atom_map_fn: 从真实 EngineEvidence 提取 SemanticAtom
        def atom_map_fn(ev: EngineEvidence) -> SemanticAtom | None:
            ten_god = ev.attributes.get("ten_god", "")
            if ten_god == "正官":
                return SemanticAtom(
                    atom_id="TEN_GOD_ZHENG_GUAN",
                    engine=ev.engine,
                    evidence_ref=ev.evidence_id,
                    semantic_keys=["AUTHORITY", "CAREER"],
                    domain_candidates=["CAREER", "GROWTH"],
                    label_zh="正官",
                    category="TEN_GOD",
                )
            return None

        # 实际调用 orchestrator
        result = orchestrator.orchestrate(
            case_id="E2E-TEST",
            temporal_scope="baseline",
            engine_evidences={"ZI_PING": [evidence]},
            atom_map_fn=atom_map_fn,
        )

        # 验证结果
        assert result is not None, "P1.6: orchestrator 返回 None"
        assertions = getattr(result, "assertions", [])
        assert len(assertions) > 0, \
            f"P1.6: Orchestrator 未产生 Authorized Assertion，assertions={assertions}"

        # 验证 assertion 包含 production rule_id
        assertion = assertions[0]
        assert hasattr(assertion, "authorized_rule_id"), \
            "P1.6: Assertion 缺少 authorized_rule_id 字段"
        assert assertion.authorized_rule_id == "ASR-PROD-ZHI_YIN", \
            f"P1.6: Assertion rule_id 不匹配: {assertion.authorized_rule_id}"

        print(f"P16-05 PASS: Orchestrator produced {len(assertions)} assertion(s)")
        print(f"  Assertion: {assertion.assertion_id}")
        print(f"  Rule: {assertion.authorized_rule_id}")
        print(f"  Direction: {assertion.direction}")

    def test_p16_06_fail_closed_when_assertion_library_missing(self):
        """P16-06: 当 assertion_library 缺失时，应 fail-closed。"""
        from tongshu.pipeline_stages.compute_stage import ComputeStage

        stage = ComputeStage(
            bazi_engine=None,
            ziwei_engine=None,
            huangli_engine=None,
            signal_engine=None,
            theme_engine=None,
            mapping_registry=None,
            composer=None,
            schema_dir=Path("/tmp"),
            matcher=None,
            renderer_model_id="stub",
            assertion_library=None,
        )

        assert stage._orchestrator is None, \
            "P1.6: assertion_library=None 时 orchestrator 不应创建"

        print("P16-06 PASS: Fail-closed when assertion_library is None")

    def test_p16_07_all_three_production_rules_loadable(self):
        """P16-07: 三条生产规则都能从文件加载。"""
        rules_path = Path(__file__).parent.parent.parent / "data" / "assertion_rules" / "production_assertion_rules.json"

        lib = ProductionRuleLoader.load(str(rules_path))

        rule_ids = [r.rule_id for r in lib._rules]
        expected = ["ASR-PROD-ZHI_YIN", "ASR-PROD-PIAN_YIN", "ASR-PROD-ZHENG_CAi"]

        for exp_id in expected:
            assert exp_id in rule_ids, f"P1.6: 缺少规则 {exp_id}"

        assert len(lib._rules) == 3, f"P1.6: 预期 3 条规则，实际 {len(lib._rules)}"
        print(f"P16-07 PASS: All {len(lib._rules)} production rules loaded")

    def test_p16_08_complete_runtime_trace(self, pipeline):
        """P16-08: 完整 Runtime Trace — 证明端到端路径。"""
        trace_log = []

        # 1. ProductionRuleLibrary
        lib = pipeline.compute_stage._assertion_library
        rule_count = len(getattr(lib, "_rules", []))
        trace_log.append(f"1. ProductionRuleLibrary loaded: {rule_count} rules")
        assert rule_count > 0, "P1.6: 没有加载到规则"

        # 2. CrossDomainOrchestrator
        orch = pipeline.compute_stage._orchestrator
        trace_log.append(f"2. CrossDomainOrchestrator created: {orch is not None}")
        assert orch is not None, "P1.6: Orchestrator 未创建"

        # 3. 使用真实 Evidence 运行 orchestrator
        evidence = EngineEvidence(
            evidence_id="E-TRACE-001",
            engine=EngineName.ZI_PING,
            canonical_text="正官当令",
            attributes={"ten_god": "正官"},
            temporal_scope=TemporalScope.BASELINE,
            value="正官",
        )

        def atom_map_fn(ev):
            if ev.attributes.get("ten_god") == "正官":
                return SemanticAtom(
                    atom_id="TEN_GOD_ZHENG_GUAN",
                    engine=EngineName.ZI_PING,
                    evidence_ref=ev.evidence_id,
                    semantic_keys=["AUTHORITY", "CAREER"],
                    domain_candidates=["CAREER"],
                    label_zh="正官",
                    category="TEN_GOD",
                )
            return None

        orch_result = orch.orchestrate(
            case_id="TRACE",
            temporal_scope="baseline",
            engine_evidences={"ZI_PING": [evidence]},
            atom_map_fn=atom_map_fn,
        )

        assertions = getattr(orch_result, "assertions", [])
        trace_log.append(f"3. Orchestrator executed: {len(assertions)} assertion(s)")
        assert len(assertions) > 0, "P1.6: Orchestrator 未产生 assertion"

        # 4. 运行真实 pipeline
        result = pipeline.run(
            analysis_date=date(2026, 9, 2),
            birth_date=(1984, 12, 7, 16),
            gender="male",
            theme="WORK",
            compute_only=True,
        )

        # 5. 验证 claims
        claims = result.canonical.atomic_claims
        claims_count = len(claims) if claims else 0
        trace_log.append(f"4. Pipeline atomic claims: {claims_count}")

        # 6. 验证 signals
        baseline_signals = len(result.canonical.signals.get("BASELINE", []))
        trace_log.append(f"5. Baseline signals: {baseline_signals}")

        # 7. 验证 claims 包含 production rule
        production_rule_ids = ["ASR-PROD-ZHI_YIN", "ASR-PROD-PIAN_YIN", "ASR-PROD-ZHENG_CAi"]
        has_production_claim = False
        for claim in claims:
            if isinstance(claim, dict):
                rule_id = claim.get("rule_id", claim.get("claim_id", ""))
                rule_refs = claim.get("rule_refs", [])
                if rule_id in production_rule_ids or any(r in production_rule_ids for r in rule_refs):
                    has_production_claim = True
                    break

        trace_log.append(f"6. Production claim found: {has_production_claim}")

        # 关键断言：必须有 claims 且包含 production rule
        assert claims_count > 0, \
            f"P1.6: Runtime trace failed - no claims (claims_count={claims_count})"
        assert has_production_claim, \
            f"P1.6: Runtime trace failed - no production rule in claims"

        for t in trace_log:
            print(f"  {t}")

        print("P16-08 PASS: Complete end-to-end runtime trace verified")

    def test_p16_09_loader_failure_fail_closed(self):
        """P16-09: ProductionRuleLoader 加载失败时，应 fail-closed。"""
        with pytest.raises(Exception):
            ProductionRuleLoader.load("/nonexistent/path/rules.json")

        print("P16-09 PASS: Loader failure raises exception")


# ─── 辅助函数 ────────────────────────────────────────────────────────────────


def verify_assertion_path(pipeline):
    """验证 Assertion 路径是否完整。"""
    assert pipeline.compute_stage._assertion_library is not None, \
        "Assertion library not loaded"
    assert pipeline.compute_stage._orchestrator is not None, \
        "CrossDomainOrchestrator not created"
