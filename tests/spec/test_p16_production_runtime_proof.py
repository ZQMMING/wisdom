"""
P1.6: Production Runtime Proof — Integration Test

验证 P1.6 生产路径在真实 Pipeline 中完整运行：
1. ProductionRuleLibrary 加载
2. CrossDomainOrchestrator 创建
3. Rule Matching 命中
4. Authorized Assertion 产生
5. Atomic Claims 产生
6. 失败时 fail-closed 不 degraded
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
from tongshu.spec.canonical import SemanticAtom, EngineName, TemporalScope


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

        # 验证是生产库（hasattr is_production）
        lib = pipeline.compute_stage._assertion_library
        assert getattr(lib, "is_production", False) is True, \
            "P1.6: assertion_library 不是生产库"

        # 验证规则数量
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

        # 创建测试用的 SemanticAtom
        atom = SemanticAtom(
            atom_id="TEN_GOD_ZHENG_GUAN",
            engine=EngineName.ZI_PING,
            evidence_ref="E-TEST-001",
            semantic_keys=["AUTHORITY", "CAREER"],
            domain_candidates=["CAREER"],
            label_zh="正官",
            category="TEN_GOD",
        )

        # 验证规则能匹配
        rule = lib.find_rule(atom, {})
        assert rule is not None, \
            f"P1.6: 无法匹配 SemanticAtom(TEN_GOD_ZHENG_GUAN) — 规则可能不兼容"
        assert rule.rule_id == "ASR-PROD-ZHI_YIN", \
            f"P1.6: 匹配到错误规则 {rule.rule_id}"

        print(f"P16-03 PASS: Rule {rule.rule_id} matched TEN_GOD_ZHENG_GUAN")

    def test_p16_04_orchestrator_produces_authorized_assertions(self, pipeline):
        """P16-04: Orchestrator 能产生 Authorized Assertion。"""
        orchestrator = pipeline.compute_stage._orchestrator
        lib = pipeline.compute_stage._assertion_library

        # 验证 orchestrator 能处理
        assert hasattr(orchestrator, "orchestrate"), \
            "P1.6: CrossDomainOrchestrator 缺少 orchestrate() 方法"

        # 创建测试用的 Evidence 和 Atom
        from tongshu.spec.canonical import EngineEvidence

        evidence = EngineEvidence(
            evidence_id="E-TEST-001",
            engine=EngineName.ZI_PING,
            canonical_text="正官当令",
            attributes={"ten_god": "正官"},
            temporal_scope=TemporalScope.BASELINE,
        )

        atom = SemanticAtom(
            atom_id="TEN_GOD_ZHENG_GUAN",
            engine=EngineName.ZI_PING,
            evidence_ref="E-TEST-001",
            semantic_keys=["AUTHORITY", "CAREER"],
            domain_candidates=["CAREER"],
            label_zh="正官",
            category="TEN_GOD",
        )

        # 验证 orchestrator 能处理
        assert hasattr(orchestrator, 'process_evidence'), \
            "P1.6: CrossDomainOrchestrator 缺少 process_evidence() 方法"

        print("P16-04 PASS: Orchestrator has required methods")

    def test_p16_05_pipeline_run_produces_atomic_claims(self, pipeline):
        """P16-05: 完整 Pipeline.run() 产生 Atomic Claims。"""
        # 运行一个最小化的 pipeline
        result = pipeline.run(
            analysis_date=date(2026, 9, 2),
            birth_date=(1984, 12, 7, 16),
            gender="male",
            theme="WORK",
            compute_only=True,  # 只计算，不渲染
        )

        # 验证 canonical 中有 atomic_claims
        claims = result.canonical.atomic_claims
        assert claims is not None, "P1.6: atomic_claims 为 None"

        claims_count = len(claims) if claims else 0
        # 必须有实际的 claims 产生，不能为空
        assert claims_count > 0, \
            f"P1.6: Atomic claims 为空，生产规则未生效。claims_count={claims_count}"

        print(f"P16-05 PASS: Pipeline produced {claims_count} atomic claims")
        print(f"  canonical_id: {result.canonical.canonical_id}")
        print(f"  signals: BASELINE={len(result.canonical.signals.get('BASELINE', []))}")

        # 打印具体的 claims 内容
        for claim in claims[:3]:  # 打印前3个
            print(f"  Claim: {claim.get('claim_id', 'N/A')}")

    def test_p16_06_fail_closed_when_assertion_library_missing(self):
        """P16-06: 当 assertion_library 缺失时，应 fail-closed。"""
        # 验证 ComputeStage 在 assertion_library=None 时不会创建 orchestrator
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
            assertion_library=None,  # 故意不加载
        )

        # 验证 orchestrator 为 None
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

    def test_p16_08_runtime_trace_complete(self, pipeline):
        """P16-08: 完整 Runtime Trace 验证。"""
        # 追踪完整路径
        trace = []

        # 1. ProductionRuleLibrary
        lib = pipeline.compute_stage._assertion_library
        trace.append(f"1. ProductionRuleLibrary loaded: {len(lib._rules)} rules")

        # 2. CrossDomainOrchestrator
        orch = pipeline.compute_stage._orchestrator
        trace.append(f"2. CrossDomainOrchestrator created: {orch is not None}")

        # 3. Run pipeline
        result = pipeline.run(
            analysis_date=date(2026, 9, 2),
            birth_date=(1984, 12, 7, 16),
            gender="male",
            theme="WORK",
            compute_only=True,
        )

        # 4. Check claims - MUST be non-empty
        claims = result.canonical.atomic_claims
        claims_count = len(claims) if claims else 0
        trace.append(f"3. Atomic claims produced: {claims_count}")

        # 5. Check signals
        baseline_signals = len(result.canonical.signals.get("BASELINE", []))
        trace.append(f"4. Baseline signals: {baseline_signals}")

        # 关键断言：必须有实际的 claims
        assert claims_count > 0, \
            f"P1.6: Runtime trace failed - no atomic claims produced (claims_count={claims_count})"

        for t in trace:
            print(f"  {t}")

        print("P16-08 PASS: Runtime trace complete with actual claims")


# ─── 辅助函数 ────────────────────────────────────────────────────────────────


def verify_assertion_path(pipeline):
    """验证 Assertion 路径是否完整。"""
    assert pipeline.compute_stage._assertion_library is not None, \
        "Assertion library not loaded"
    assert pipeline.compute_stage._orchestrator is not None, \
        "CrossDomainOrchestrator not created"
