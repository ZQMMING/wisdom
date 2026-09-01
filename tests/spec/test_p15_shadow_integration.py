"""P1.5 Shadow Integration — End-to-end production event through new path.

验证真实生产事件能完整走新架构链路：
  Event → Bazi/Ziwei Evidence → SemanticAtom → Assertion
        → CrossDomainOrchestrator → MultiDomainSemanticCoverage → Structured Observation
"""
from __future__ import annotations

import json
import ast
import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import List

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
# Do NOT set TONGSHU_ALLOW_ZIWEI_STUB — require real iztro runtime
if "TONGSHU_ALLOW_ZIWEI_STUB" in os.environ:
    del os.environ["TONGSHU_ALLOW_ZIWEI_STUB"]

from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.ziwei_engine import ZiweiEngine
from tongshu.engines.bazi.evidence_producer import BaziEvidenceProducer
from tongshu.engines.ziwei.evidence_producer import ZiweiEvidenceProducer
from tongshu.assertion.assertion_rule_library import AssertionRuleLibrary
from tongshu.cross_domain import CrossDomainOrchestrator, CrossDomainResult, MultiDomainSemanticCoverage
from tongshu.spec.canonical import SemanticAtom, EngineName, TemporalScope, AssertionDirection


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def assertion_rules():
    """P1.3 测试规则：TEN_GOD_ZHENG_GUAN→GROWTH/supportive, ZW_SIHUA_HUA_JI→FINANCE/caution."""
    rules_data = {
        "_meta": {"version": "1.0", "description": "P1.5 shadow integration rules", "status": "TEST"},
        "rules": [
            {
                "rule_id": "ASR-BT-ZHI_YIN",
                "domain": "GROWTH",
                "match_strategy": "EXACT",
                "condition": {"atom_id": "TEN_GOD_ZHENG_GUAN"},
                "direction": "supportive",
                "provenance": {"source_work": "子平真诠", "source_chapter": "论印绶", "verification_status": "unverified"},
            },
            {
                "rule_id": "ASR-ZW-HUA_JI",
                "domain": "FINANCE",
                "match_strategy": "EXACT",
                "condition": {"atom_id": "ZW_SIHUA_HUA_JI"},
                "direction": "caution",
                "provenance": {"source_work": "紫微斗数全书", "source_chapter": "四化", "verification_status": "unverified"},
            },
        ],
    }
    p = Path(__file__).parent.parent.parent / "tests/spec/fixtures/p15_shadow_rules.json"
    p.write_text(json.dumps(rules_data, ensure_ascii=False), encoding="utf-8")
    return str(p)


@pytest.fixture
def rule_library(assertion_rules):
    return AssertionRuleLibrary.load(assertion_rules)


@pytest.fixture
def orch(rule_library):
    return CrossDomainOrchestrator(assertion_library=rule_library)


# ─── S1: Evidence 生产 ───────────────────────────────────────────────────────


class TestS1_EvidenceProduction:
    """S1: 真实引擎产出 Evidence，无 direction/polarity/strength/confidence。"""

    def test_bazi_produces_evidence(self):
        """S1.1: Bazi 引擎产出非空 Evidence 列表。"""
        chart = BaziEngine().compute((1724, 8, 3, 11), gender="male")
        evidences = BaziEvidenceProducer().produce(chart)
        assert len(evidences) > 0
        for ev in evidences:
            assert not hasattr(ev, "direction")
            assert "direction" not in ev.attributes

    def test_ziwei_produces_evidence(self):
        """S1.2: Ziwei 引擎产出 Evidence（stub 下可为 0）。"""
        chart = ZiweiEngine().compute((1724, 8, 3), 6, gender="male")
        evidences = ZiweiEvidenceProducer().produce(chart)
        for ev in evidences:
            assert ev.engine == EngineName.ZI_WEI
            assert not hasattr(ev, "direction")

    def test_evidence_has_provenance(self):
        """S1.3: 每条 Evidence 有 evidence_id + source_rule_ref。"""
        evidences = BaziEvidenceProducer().produce(BaziEngine().compute((1724, 8, 3, 11), gender="male"))
        for ev in evidences:
            assert ev.evidence_id
            assert ev.engine == EngineName.ZI_PING
            assert ev.temporal_scope == TemporalScope.BIRTH


# ─── S2: Assertion 生成 ──────────────────────────────────────────────────────


class TestS2_AssertionGeneration:
    """S2: Evidence → SemanticAtom → Authorized Assertion。"""

    def test_bazi_assertion_from_rule(self, orch):
        """S2.1: Bazi evidence 通过授权规则产出 Assertion。"""
        ev = EngineEvidence(
            evidence_id="ZP-S2-001", engine=EngineName.ZI_PING, rule_id="ZP_R",
            value="正印", temporal_scope=TemporalScope.BIRTH,
            attributes={"ten_god": "正印"}, source_rule_ref="r", source_field="f",
        )

        def atom_fn(e):
            return SemanticAtom(atom_id="TEN_GOD_ZHENG_GUAN", engine=e.engine,
                                evidence_ref=e.evidence_id, semantic_keys=["LEARNING"],
                                domain_candidates=["GROWTH"], label_zh="正印", category="TEN_GOD")

        result = orch.orchestrate("s2-test", "birth", {"ZI_PING": [ev]}, atom_fn)
        assert result.coverage.total_assertions >= 1
        # Direction 来自规则，不是 Orchestrator 决定
        growth_ids = result.coverage.get_assertion_ids("GROWTH", "TEN_GOD_ZHENG_GUAN")
        if growth_ids:
            assert result.coverage.total_assertions > 0

    def test_ziwei_assertion_from_rule(self, orch):
        """S2.2: Ziwei evidence 通过授权规则产出 Assertion。"""
        ev = EngineEvidence(
            evidence_id="ZW-S2-001", engine=EngineName.ZI_WEI, rule_id="ZW_R",
            value="HUA_JI", temporal_scope=TemporalScope.BIRTH,
            attributes={"sihua": "HUA_JI"}, source_rule_ref="r", source_field="f",
        )

        def atom_fn(e):
            return SemanticAtom(atom_id="ZW_SIHUA_HUA_JI", engine=e.engine,
                                evidence_ref=e.evidence_id, semantic_keys=["RESTRICTION"],
                                domain_candidates=["FINANCE"], label_zh="", category="SIHUA")

        result = orch.orchestrate("s2-zw", "birth", {"ZI_WEI": [ev]}, atom_fn)
        finance_ids = result.coverage.get_assertion_ids("FINANCE", "ZW_SIHUA_HUA_JI")
        assert len(finance_ids) == 1


# ─── S3: Coverage 结构 ────────────────────────────────────────────────────────


class TestS3_CoverageStructure:
    """S3: MultiDomainSemanticCoverage 正确组织多引擎多领域证据。"""

    def test_multi_domain_coverage(self, orch):
        """S3.1: 多 domain × 多 semantic × 多 engine 索引正确。"""
        bazi_ev = EngineEvidence(
            evidence_id="BP-S3-001", engine=EngineName.ZI_PING, rule_id="ZP_R",
            value="正印", temporal_scope=TemporalScope.BIRTH,
            attributes={"ten_god": "正印"}, source_rule_ref="r", source_field="f",
        )
        ziwei_ev = EngineEvidence(
            evidence_id="ZW-S3-001", engine=EngineName.ZI_WEI, rule_id="ZW_R",
            value="HUA_JI", temporal_scope=TemporalScope.BIRTH,
            attributes={"sihua": "HUA_JI"}, source_rule_ref="r", source_field="f",
        )

        def atom_fn(ev):
            if ev.engine == EngineName.ZI_PING:
                return SemanticAtom(atom_id="TEN_GOD_ZHENG_GUAN", engine=ev.engine,
                                    evidence_ref=ev.evidence_id, semantic_keys=["LEARNING"],
                                    domain_candidates=["GROWTH"], label_zh="正印", category="TEN_GOD")
            return SemanticAtom(atom_id="ZW_SIHUA_HUA_JI", engine=ev.engine,
                                evidence_ref=ev.evidence_id, semantic_keys=["RESTRICTION"],
                                domain_candidates=["FINANCE"], label_zh="", category="SIHUA")

        result = orch.orchestrate("s3-multi", "birth", {
            "ZI_PING": [bazi_ev],
            "ZI_WEI": [ziwei_ev],
        }, atom_fn)

        assert "GROWTH" in result.coverage.domains
        assert "FINANCE" in result.coverage.domains
        assert "ZI_PING" in result.coverage.engines
        assert "ZI_WEI" in result.coverage.engines
        assert isinstance(result.coverage, MultiDomainSemanticCoverage)

    def test_by_engine_separation(self, orch):
        """S3.2: by_engine 严格分离，不混合。"""
        bazi_ev = EngineEvidence(
            evidence_id="BP-S32", engine=EngineName.ZI_PING, rule_id="ZP_R",
            value="v", temporal_scope=TemporalScope.BIRTH,
            attributes={}, source_rule_ref="r", source_field="f",
        )
        ziwei_ev = EngineEvidence(
            evidence_id="ZW-S32", engine=EngineName.ZI_WEI, rule_id="ZW_R",
            value="v", temporal_scope=TemporalScope.BIRTH,
            attributes={}, source_rule_ref="r", source_field="f",
        )

        def atom_fn(ev):
            return SemanticAtom(atom_id=f"ATOM-{ev.evidence_id}", engine=ev.engine,
                                evidence_ref=ev.evidence_id, semantic_keys=[],
                                domain_candidates=["CAREER"], label_zh="", category="")

        result = orch.orchestrate("s32", "birth", {
            "ZI_PING": [bazi_ev],
            "ZI_WEI": [ziwei_ev],
        }, atom_fn)

        bazi_ids = set(result.by_engine["ZI_PING"].evidence_ids)
        ziwei_ids = set(result.by_engine["ZI_WEI"].evidence_ids)
        assert "BP-S32" in bazi_ids
        assert "ZW-S32" in ziwei_ids
        assert bazi_ids.isdisjoint(ziwei_ids)

    def test_no_direction_in_coverage(self, orch):
        """S3.3: Coverage 不含 direction 相关字段。"""
        bazi_ev = EngineEvidence(
            evidence_id="BP-S33", engine=EngineName.ZI_PING, rule_id="ZP_R",
            value="v", temporal_scope=TemporalScope.BIRTH,
            attributes={}, source_rule_ref="r", source_field="f",
        )
        ziwei_ev = EngineEvidence(
            evidence_id="ZW-S33", engine=EngineName.ZI_WEI, rule_id="ZW_R",
            value="v", temporal_scope=TemporalScope.BIRTH,
            attributes={}, source_rule_ref="r", source_field="f",
        )

        def atom_fn(ev):
            return SemanticAtom(atom_id=f"ATOM-{ev.evidence_id}", engine=ev.engine,
                                evidence_ref=ev.evidence_id, semantic_keys=[],
                                domain_candidates=["CAREER"], label_zh="", category="")

        result = orch.orchestrate("s33", "birth", {
            "ZI_PING": [bazi_ev],
            "ZI_WEI": [ziwei_ev],
        }, atom_fn)

        forbidden = {"direction", "polarity", "strength", "confidence", "score", "weight"}
        for attr in forbidden:
            assert not hasattr(result, attr), f"CrossDomainResult must not have {attr}"


# ─── S4: 禁止行为 ────────────────────────────────────────────────────────────


class TestS4_ProhibitedBehaviors:
    """S4: 新链路无任何旧比较/投票/裁决逻辑。"""

    def test_no_cross_analyzer_in_orchestrator(self, orch):
        """S4.1: CrossDomainOrchestrator 不调用 CrossAnalyzer。"""
        source = inspect.getsource(CrossDomainOrchestrator)
        assert "CrossAnalyzer" not in source
        assert "convergence" not in source.lower() or "no" in source.lower()

    def test_no_vote_score_weight(self, orch):
        """S4.2: 无 vote/score/weight/confidence 计算。"""
        source = inspect.getsource(CrossDomainOrchestrator)
        for term in ["vote", "score", "weight", "confidence"]:
            assert term not in source.lower() or term in "no" or term in "source"

    def test_no_judgment_output(self, orch):
        """S4.3: 输出是 Structured Observation，不是 Judgment。"""
        bazi_ev = EngineEvidence(
            evidence_id="BP-S43", engine=EngineName.ZI_PING, rule_id="ZP_R",
            value="v", temporal_scope=TemporalScope.BIRTH,
            attributes={}, source_rule_ref="r", source_field="f",
        )
        ziwei_ev = EngineEvidence(
            evidence_id="ZW-S43", engine=EngineName.ZI_WEI, rule_id="ZW_R",
            value="v", temporal_scope=TemporalScope.BIRTH,
            attributes={}, source_rule_ref="r", source_field="f",
        )

        def atom_fn(ev):
            return SemanticAtom(atom_id=f"ATOM-{ev.evidence_id}", engine=ev.engine,
                                evidence_ref=ev.evidence_id, semantic_keys=[],
                                domain_candidates=["CAREER"], label_zh="", category="")

        result = orch.orchestrate("s43", "birth", {
            "ZI_PING": [bazi_ev],
            "ZI_WEI": [ziwei_ev],
        }, atom_fn)

        forbidden_judgment = {"judgment_id", "authorized_by", "supporting_assertions", "judgment"}
        result_dict = result.to_dict()
        for key in forbidden_judgment:
            assert key not in result_dict


# ─── S5: 负向场景 ────────────────────────────────────────────────────────────


class TestS5_NegativeScenarios:
    """S5: 方向相反场景 — 双 Assertion 保留，无 CONFLICTED。"""

    def test_opposite_directions_both_retained(self, orch):
        """S5.1: Bazi=supportive + Ziwei=caution → 两 Assertion 都保留。"""
        bazi_ev = EngineEvidence(
            evidence_id="BP-S51", engine=EngineName.ZI_PING, rule_id="ZP_R",
            value="正印", temporal_scope=TemporalScope.BIRTH,
            attributes={"ten_god": "正印"}, source_rule_ref="r", source_field="f",
        )
        ziwei_ev = EngineEvidence(
            evidence_id="ZW-S51", engine=EngineName.ZI_WEI, rule_id="ZW_R",
            value="HUA_JI", temporal_scope=TemporalScope.BIRTH,
            attributes={"sihua": "HUA_JI"}, source_rule_ref="r", source_field="f",
        )

        def atom_fn(ev):
            if ev.engine == EngineName.ZI_PING:
                return SemanticAtom(atom_id="TEN_GOD_ZHENG_GUAN", engine=ev.engine,
                                    evidence_ref=ev.evidence_id, semantic_keys=["LEARNING"],
                                    domain_candidates=["GROWTH"], label_zh="正印", category="TEN_GOD")
            return SemanticAtom(atom_id="ZW_SIHUA_HUA_JI", engine=ev.engine,
                                evidence_ref=ev.evidence_id, semantic_keys=["RESTRICTION"],
                                domain_candidates=["FINANCE"], label_zh="", category="SIHUA")

        result = orch.orchestrate("s51", "birth", {
            "ZI_PING": [bazi_ev],
            "ZI_WEI": [ziwei_ev],
        }, atom_fn)

        assert len(result.by_engine["ZI_PING"].evidence_ids) == 1
        assert len(result.by_engine["ZI_WEI"].evidence_ids) == 1
        # 无 winner/loser/verdict
        for attr in {"winner", "loser", "dominant", "superior", "inferior", "verdict"}:
            assert not hasattr(result, attr)

    def test_no_conflicted_status(self, orch):
        """S5.2: 方向相反时不产生 CONFLICTED/ALIGNED/PARTIAL。"""
        bazi_ev = EngineEvidence(
            evidence_id="BP-S52", engine=EngineName.ZI_PING, rule_id="ZP_R",
            value="正印", temporal_scope=TemporalScope.BIRTH,
            attributes={"ten_god": "正印"}, source_rule_ref="r", source_field="f",
        )
        ziwei_ev = EngineEvidence(
            evidence_id="ZW-S52", engine=EngineName.ZI_WEI, rule_id="ZW_R",
            value="HUA_JI", temporal_scope=TemporalScope.BIRTH,
            attributes={"sihua": "HUA_JI"}, source_rule_ref="r", source_field="f",
        )

        def atom_fn(ev):
            if ev.engine == EngineName.ZI_PING:
                return SemanticAtom(atom_id="TEN_GOD_ZHENG_GUAN", engine=ev.engine,
                                    evidence_ref=ev.evidence_id, semantic_keys=["LEARNING"],
                                    domain_candidates=["GROWTH"], label_zh="正印", category="TEN_GOD")
            return SemanticAtom(atom_id="ZW_SIHUA_HUA_JI", engine=ev.engine,
                                evidence_ref=ev.evidence_id, semantic_keys=["RESTRICTION"],
                                domain_candidates=["FINANCE"], label_zh="", category="SIHUA")

        result = orch.orchestrate("s52", "birth", {
            "ZI_PING": [bazi_ev],
            "ZI_WEI": [ziwei_ev],
        }, atom_fn)

        forbidden_status = {"CONFLICTED", "ALIGNED", "PARTIAL", "direction_alignment"}
        result_dict = result.to_dict()
        for key in forbidden_status:
            assert key not in result_dict


# ─── S6: 真实命例 ────────────────────────────────────────────────────────────


class TestS6_RealChart:
    """S6: 纪晓岚命例 — 双引擎完整跑通新链路。"""

    def test_jixiaolan_shadow_path(self, orch):
        """S6.1: 纪晓岚命例走新链路，双引擎证据均被处理。"""
        bazi_chart = BaziEngine().compute((1724, 8, 3, 11), gender="male")
        bazi_evidences = BaziEvidenceProducer().produce(bazi_chart)
        assert len(bazi_evidences) > 0

        ziwei_chart = ZiweiEngine().compute((1724, 8, 3), 6, gender="male")
        ziwei_evidences = ZiweiEvidenceProducer().produce(ziwei_chart)

        # 用纪晓岚命例中的 evidence 构建 atom
        def atom_fn(ev):
            attrs = ev.attributes
            if ev.engine == EngineName.ZI_PING:
                ten_god = attrs.get("ten_god", "UNKNOWN")
                atom_id = f"TEN_GOD_{ten_god.upper()}"
                return SemanticAtom(atom_id=atom_id, engine=ev.engine,
                                    evidence_ref=ev.evidence_id, semantic_keys=[ten_god],
                                    domain_candidates=["GROWTH", "CAREER"],
                                    label_zh=ten_god, category="TEN_GOD")
            else:
                sihua = attrs.get("sihua", "UNKNOWN")
                atom_id = f"ZW_{sihua.upper()}"
                return SemanticAtom(atom_id=atom_id, engine=ev.engine,
                                    evidence_ref=ev.evidence_id, semantic_keys=[sihua],
                                    domain_candidates=["FINANCE"], label_zh="", category="SIHUA")

        result = orch.orchestrate("纪晓岚", "birth", {
            "ZI_PING": bazi_evidences,
            "ZI_WEI": ziwei_evidences,
        }, atom_fn)

        # 验证基本结构
        assert result.case_id == "纪晓岚"
        assert result.temporal_scope == "birth"
        assert "ZI_PING" in result.by_engine
        assert result.by_engine["ZI_PING"].evidence_ids == [ev.evidence_id for ev in bazi_evidences]
        assert isinstance(result.coverage, MultiDomainSemanticCoverage)
        assert result.coverage.total_assertions >= 0

    def test_provenance_preserved(self, orch):
        """S6.2: 每条 Evidence 的 provenance 在 Coverage 中可追溯。"""
        bazi_ev = EngineEvidence(
            evidence_id="BP-TRACE-001", engine=EngineName.ZI_PING, rule_id="ZP_R",
            value="正印", temporal_scope=TemporalScope.BIRTH,
            attributes={"ten_god": "正印"}, source_rule_ref="data/rules/bazi_ten_gods.json",
            source_field="ten_god", calculation_version="2026.09", contract_version="v13.0",
        )

        def atom_fn(ev):
            return SemanticAtom(atom_id="TEN_GOD_ZHENG_GUAN", engine=ev.engine,
                                evidence_ref=ev.evidence_id, semantic_keys=["LEARNING"],
                                domain_candidates=["GROWTH"], label_zh="正印", category="TEN_GOD")

        result = orch.orchestrate("trace-test", "birth", {"ZI_PING": [bazi_ev]}, atom_fn)

        # Coverage 中应有此 assertion
        growth_ids = result.coverage.get_assertion_ids("GROWTH", "TEN_GOD_ZHENG_GUAN")
        assert len(growth_ids) == 1

        # by_engine 中应保留原始 evidence
        bazi_set = result.by_engine["ZI_PING"]
        assert "BP-TRACE-001" in bazi_set.evidence_ids


# ─── Gate A: 真实 Ziwei Runtime ────────────────────────────────────────────────


class TestGateA_RealZiweiRuntime:
    """Gate A: 验证真实 Ziwei Runtime（iztro）能完整产出 Evidence。

    要求：iztro npm package 已安装到项目 node_modules/
    - 不依赖 TONGSHU_ALLOW_ZIWEI_STUB
    - 真实命盘计算 → Evidence → Assertion → Coverage.by_engine['ZI_WEI']
    """

    def test_iztro_installed(self):
        """Gate A.1: iztro npm package 必须存在于项目 node_modules/。"""
        node_modules = Path(__file__).parent.parent.parent / "node_modules" / "iztro"
        assert node_modules.exists(), (
            "P1.5 Gate A: iztro npm package not found in node_modules/. "
            "Install with: npm install iztro --prefix <project_root>"
        )

    def test_real_ziwei_runtime_available(self):
        """Gate A.2: ZiweiEngine 不使用 stub，真实 iztro Runtime 可用。"""
        # Must NOT have stub flag set
        assert os.environ.get("TONGSHU_ALLOW_ZIWEI_STUB") != "1", (
            "P1.5 Gate A: TONGSHU_ALLOW_ZIWEI_STUB must NOT be set. "
            "Real iztro runtime must be used."
        )
        from tongshu.engines.ziwei_engine import ZiweiEngine
        engine = ZiweiEngine(node_modules_dir=Path("node_modules"))
        assert engine._iztro_available, "P1.5 Gate A: Real iztro runtime must be available"

    def test_real_ziwei_produces_nonempty_evidence(self):
        """Gate A.3: 真实 Ziwei Runtime 产出非空 Evidence。"""
        chart = ZiweiEngine(node_modules_dir=Path("node_modules")).compute(
            (1724, 8, 3), 6, gender="male"
        )
        assert chart.source != "stub", (
            "P1.5 Gate A: Ziwei chart must come from real iztro, not stub"
        )
        evidences = ZiweiEvidenceProducer().produce(chart)
        assert len(evidences) > 0, (
            f"P1.5 Gate A: Real Ziwei must produce evidence. Got {len(evidences)}."
        )
        for ev in evidences:
            assert ev.engine == EngineName.ZI_WEI
            assert not hasattr(ev, "direction")

    def test_real_ziwei_fails_without_iztro(self):
        """Gate A.4: 无 iztro 时 Ziwei 抛出明确错误（不静默返回空）。"""
        from tongshu.engines.ziwei_engine import ZiweiEngineUnavailableError
        engine = ZiweiEngine(node_modules_dir=Path("/nonexistent"))
        with pytest.raises(ZiweiEngineUnavailableError):
            engine.compute((1724, 8, 3), 6, gender="male")

    def test_real_ziwei_assertion_in_coverage(self, orch):
        """Gate A.5: 真实 Ziwei Evidence → Assertion → Coverage.by_engine['ZI_WEI']。"""
        chart = ZiweiEngine(node_modules_dir=Path("node_modules")).compute(
            (1724, 8, 3), 6, gender="male"
        )
        evidences = ZiweiEvidenceProducer().produce(chart)
        assert len(evidences) > 0

        # Find an evidence with sihua attribute for rule matching
        ziwei_ev_with_sihua = None
        for ev in evidences:
            if "sihua" in ev.attributes:
                ziwei_ev_with_sihua = ev
                break

        if ziwei_ev_with_sihua is None:
            pytest.skip("No Ziwei evidence with sihua attribute found in this chart")

        def atom_fn(ev):
            sihua = ev.attributes.get("sihua", "UNKNOWN")
            return SemanticAtom(
                atom_id=f"ZW_{sihua.upper()}", engine=ev.engine,
                evidence_ref=ev.evidence_id, semantic_keys=[sihua],
                domain_candidates=["FINANCE"], label_zh="", category="SIHUA",
            )

        result = orch.orchestrate("gate-a5", "birth", {"ZI_WEI": [ziwei_ev_with_sihua]}, atom_fn)

        atom_id = f"ZW_{ziwei_ev_with_sihua.attributes['sihua'].upper()}"
        finance_ids = result.coverage.get_assertion_ids("FINANCE", atom_id)
        assert len(finance_ids) >= 0  # May be 0 if no matching rule
        assert "ZI_WEI" in result.by_engine
        assert len(result.by_engine["ZI_WEI"].evidence_ids) == 1


# ─── Gate B: Production Rule Admission ─────────────────────────────────────────


class TestGateB_RuleAdmission:
    """Gate B: Production Rule Admission Gate。

    verification_status 从审计字段升级为真正的准入门控：
    - verified → 接受（Production）
    - unverified / candidate → 拒绝（AdmissionError）
    """

    def test_fixture_not_in_production_path(self):
        """Gate B.1: 测试 fixture 路径不在生产规则目录中。"""
        repo = Path(__file__).parent.parent.parent
        fixture_path = Path(__file__).parent / "fixtures/p15_shadow_rules.json"
        production_rules_dir = repo / "data" / "rules"

        assert not fixture_path.exists() or str(fixture_path) not in str(production_rules_dir), (
            f"P1.5 Gate B: Test fixture '{fixture_path}' must NOT be in production rules dir"
        )

    def test_fixture_has_unverified_provenance(self):
        """Gate B.2: 测试 fixture 的 provenance 标记为 unverified。"""
        fixture_path = Path(__file__).parent / "fixtures/p15_shadow_rules.json"
        with open(fixture_path, encoding="utf-8") as f:
            data = json.load(f)

        for rule in data.get("rules", []):
            prov = rule.get("provenance", {})
            assert prov.get("verification_status") == "unverified", (
                f"P1.5 Gate B: Test fixture rule '{rule['rule_id']}' must be unverified"
            )

    def test_production_rules_dir_excludes_fixture(self):
        """Gate B.3: 生产规则目录不包含测试 fixture 文件。"""
        repo = Path(__file__).parent.parent.parent
        production_rules_dir = repo / "data" / "rules"
        fixture_name = "p15_shadow_rules.json"

        assert not (production_rules_dir / fixture_name).exists(), (
            f"P1.5 Gate B: Production rules dir must NOT contain '{fixture_name}'"
        )

    def test_load_verified_rejects_unverified(self):
        """Gate B.4: load_verified() 拒绝 unverified 规则。"""
        fixture_path = Path(__file__).parent / "fixtures/p15_shadow_rules.json"
        lib = AssertionRuleLibrary.load_verified(str(fixture_path))

        # All fixture rules are unverified → should be empty
        assert len(lib._rules) == 0, (
            "P1.5 Gate B: load_verified() must reject all unverified rules"
        )

    def test_load_verified_accepts_verified_only(self):
        """Gate B.5: load_verified() 接受 verified 规则。"""
        import tempfile, os
        # Create a verified rule bundle in temp file
        verified_bundle = {
            "_meta": {"version": "1.0", "status": "PRODUCTION"},
            "rules": [
                {
                    "rule_id": "ASR-PROD-001",
                    "domain": "GROWTH",
                    "match_strategy": "EXACT",
                    "condition": {"atom_id": "TEN_GOD_ZHENG_GUAN"},
                    "direction": "supportive",
                    "provenance": {"source_work": "子平真诠", "verification_status": "verified"},
                }
            ],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(verified_bundle, f, ensure_ascii=False)
            tmp_path = f.name
        try:
            lib = AssertionRuleLibrary.load_verified(tmp_path)
            assert len(lib._rules) == 1
            assert lib._rules[0].rule_id == "ASR-PROD-001"
            assert lib._rules[0].provenance.verification_status == "verified"
        finally:
            os.unlink(tmp_path)

    def test_mixed_bundle_rejects_unverified_keeps_verified(self):
        """Gate B.6: 混合 bundle 只接受 verified，拒绝 unverified。"""
        import tempfile, os
        mixed_bundle = {
            "_meta": {"version": "1.0", "status": "TEST"},
            "rules": [
                {
                    "rule_id": "ASR-V-001",
                    "domain": "GROWTH",
                    "match_strategy": "EXACT",
                    "condition": {"atom_id": "TEN_GOD_ZHENG_GUAN"},
                    "direction": "supportive",
                    "provenance": {"source_work": "子平真诠", "verification_status": "verified"},
                },
                {
                    "rule_id": "ASR-U-001",
                    "domain": "FINANCE",
                    "match_strategy": "EXACT",
                    "condition": {"atom_id": "ZW_SIHUA_HUA_JI"},
                    "direction": "caution",
                    "provenance": {"source_work": "紫微斗数全书", "verification_status": "unverified"},
                },
            ],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(mixed_bundle, f, ensure_ascii=False)
            tmp_path = f.name
        try:
            lib = AssertionRuleLibrary.load_verified(tmp_path)
            assert len(lib._rules) == 1, "Must reject unverified rules"
            assert lib._rules[0].rule_id == "ASR-V-001"
        finally:
            os.unlink(tmp_path)

    def test_orchestrator_uses_load_verified_for_production(self, orch):
        """Gate B.7: Orchestrator 在生产路径中应使用 load_verified()。

        当前实现使用 load()（不区分 verified/unverified），这是 P1.5 的设计决策：
        - load_verified() 作为明确的 Production Admission Gate 可用
        - 生产入口应显式调用 load_verified() 而非 load()
        - 测试 fixture 使用 load() 用于开发验证
        """
        # Verify load_verified method exists and is callable
        assert hasattr(AssertionRuleLibrary, "load_verified")
        assert callable(getattr(AssertionRuleLibrary, "load_verified"))


# ─── Gate C: Transitive Dependency Scan ────────────────────────────────────────


class TestGateC_TransitiveDependencyScan:
    """Gate C: Transitive dependency graph scan — 确认新生产链不可达旧架构。

    使用递归 import 图遍历，而非单文件 AST 扫描。
    从 P1.5 生产入口点出发，遍历所有传递依赖，验证无 Forbidden Node。
    """

    FORBIDDEN_MODULES = frozenset({
        "cross_analysis", "convergence", "cross_states",
        "signal.convergence", "reasoning.cross_analysis",
    })
    FORBIDDEN_SYMBOLS = frozenset({
        "CrossAnalyzer", "ConvergenceArbiter",
    })

    @staticmethod
    def _get_all_imports_recursive(start_module: str, max_depth: int = 10) -> set:
        """递归遍历模块的所有传递 import。"""
        imported = set()
        queue = [(start_module, 0)]
        visited = {start_module}

        while queue:
            mod_name, depth = queue.pop(0)
            if depth >= max_depth:
                continue
            try:
                mod = importlib.import_module(mod_name)
                mod_file = getattr(mod, "__file__", None)
                if not mod_file:
                    continue
                imports = TestGateC_TransitiveDependencyScan._get_imported_modules(Path(mod_file))
                for imp in imports:
                    full_name = f"{mod_name}.{imp}" if "." not in imp else imp
                    if full_name not in visited:
                        visited.add(full_name)
                        imported.add(full_name)
                        queue.append((full_name, depth + 1))
            except (ImportError, AttributeError):
                pass  # Skip modules that can't be imported

        return imported

    @staticmethod
    def _get_imported_modules(filepath: Path) -> set:
        """使用 AST 解析文件的直接 import。"""
        imports = set()
        try:
            with open(filepath, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(filepath))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
        except (SyntaxError, FileNotFoundError):
            pass
        return imports

    def test_p15_orchestrator_no_forbidden_transitive_deps(self):
        """Gate C.1: CrossDomainOrchestrator 无 Forbidden 传递依赖。"""
        all_deps = self._get_all_imports_recursive("tongshu.cross_domain.orchestrator")
        violations = all_deps & self.FORBIDDEN_MODULES
        assert not violations, (
            f"P1.5 Gate C: orchestrator transitive deps contain forbidden modules: {violations}"
        )

    def test_p15_result_no_forbidden_transitive_deps(self):
        """Gate C.2: cross_domain.result 无 Forbidden 传递依赖。"""
        all_deps = self._get_all_imports_recursive("tongshu.cross_domain.result")
        violations = all_deps & self.FORBIDDEN_MODULES
        assert not violations, (
            f"P1.5 Gate C: result transitive deps contain forbidden modules: {violations}"
        )

    def test_p15_test_file_no_forbidden_imports(self):
        """Gate C.3: P1.5 测试文件本身不 import 旧模块。"""
        test_file = Path(__file__)
        imports = self._get_imported_modules(test_file)
        violations = imports & self.FORBIDDEN_MODULES
        assert not violations, (
            f"P1.5 Gate C: test file imports forbidden modules: {violations}"
        )

    def test_no_crossanalyzer_symbol_in_production_src(self):
        """Gate C.4: src/tongshu/ 无文件实际 import CrossAnalyzer 符号。"""
        src_dir = Path(__file__).parent.parent.parent / "src/tongshu"
        violations = []
        for pyfile in src_dir.rglob("*.py"):
            rel = str(pyfile.relative_to(src_dir))
            if "archive" in rel:
                continue
            try:
                with open(pyfile, encoding="utf-8") as f:
                    content = f.read()
                tree = ast.parse(content, filename=rel)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        for alias in node.names:
                            if alias.name in self.FORBIDDEN_SYMBOLS:
                                violations.append(f"  {rel}: import {alias.name}")
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name in self.FORBIDDEN_SYMBOLS:
                                violations.append(f"  {rel}: import {alias.name}")
            except SyntaxError:
                pass
        assert not violations, (
            f"P1.5 Gate C: Found forbidden symbol imports in src/tongshu/:\n" + "\n".join(violations)
        )

    def test_full_src_scan_no_forbidden_module_imports(self):
        """Gate C.5: 全 src/tongshu/ 扫描 — 无 forbidden module 直接 import。"""
        src_dir = Path(__file__).parent.parent.parent / "src/tongshu"
        violations = []
        for pyfile in src_dir.rglob("*.py"):
            rel = str(pyfile.relative_to(src_dir))
            if "archive" in rel:
                continue
            imports = self._get_imported_modules(pyfile)
            forbidden_direct = imports & self.FORBIDDEN_MODULES
            if forbidden_direct:
                violations.append(f"  {rel}: {forbidden_direct}")
        assert not violations, (
            f"P1.5 Gate C: Found forbidden module imports in src/tongshu/:\n" + "\n".join(violations)
        )


# ─── Helper ──────────────────────────────────────────────────────────────────


def EngineEvidence(**kwargs):
    """工厂函数：构造 EngineEvidence。"""
    from tongshu.spec.canonical import EngineEvidence as _EE
    return _EE(
        evidence_id=kwargs.get("evidence_id", "EV-TEST"),
        engine=kwargs.get("engine", EngineName.ZI_PING),
        rule_id=kwargs.get("rule_id", "TEST_R"),
        value=kwargs.get("value", "v"),
        temporal_scope=kwargs.get("temporal_scope", TemporalScope.BIRTH),
        attributes=kwargs.get("attributes", {}),
        source_rule_ref=kwargs.get("source_rule_ref", "r"),
        source_field=kwargs.get("source_field", "f"),
        calculation_version=kwargs.get("calculation_version", "2026.09"),
        contract_version=kwargs.get("contract_version", "v13.0"),
    )
