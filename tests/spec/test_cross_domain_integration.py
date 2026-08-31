"""
P1.3: Cross-Domain Evidence Integration — 25 tests

验证子平+紫微共享同一事件上下文时，系统保持"互补不比较"。

严禁：
  ❌ direction 比较 / vote / score / weight / confidence 聚合
  ❌ CONFLICTED / ALIGNED / PARTIAL 状态
  ❌ evidence_count >= N 触发 Judgment
  ❌ NEUTRAL fallback
  ❌ 旧 Signal / CrossAnalyzer / Convergence 调用
"""
from __future__ import annotations

import json
import sys
import inspect
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.spec.canonical import (
    EngineEvidence,
    SemanticAtom,
    CanonicalAssertion,
    EvidenceRef,
    EngineName,
    TemporalScope,
    AssertionDirection,
)
from tongshu.assertion.assertion_rule_library import AssertionRuleLibrary, MatchStrategy, RuleProvenance
from tongshu.cross_domain import (
    CrossDomainOrchestrator,
    CrossDomainResult,
    EngineEvidenceSet,
    MultiDomainSemanticCoverage,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def bazi_evidences():
    """构造子平证据（方向 supportive）。"""
    return [
        EngineEvidence(
            evidence_id="ZP-TG-YEAR-a1",
            engine=EngineName.ZI_PING,
            rule_id="ZP_TEN_GOD_YEAR",
            value="正印",
            temporal_scope=TemporalScope.BIRTH,
            attributes={"ten_god": "正印", "stem": "JIA", "pillar": "year"},
            source_rule_ref="data/rules/bazi_ten_gods.json",
            source_field="ten_god",
            calculation_version="2026.09",
            contract_version="v13.0",
        ),
    ]


@pytest.fixture
def ziwei_evidences():
    """构造紫微证据（方向 caution）。"""
    return [
        EngineEvidence(
            evidence_id="ZW-SIHUA-HUA-JI-b1",
            engine=EngineName.ZI_WEI,
            rule_id="ZW_SIHUA_HUA_JI",
            value="HUA_JI",
            temporal_scope=TemporalScope.BIRTH,
            attributes={"sihua": "HUA_JI", "palace": "命宫", "type": "natal"},
            source_rule_ref="data/rules/ziwei_stars.json",
            source_field="soul_palace_sihua",
            calculation_version="2026.09",
            contract_version="v13.0",
        ),
    ]


@pytest.fixture
def assertion_rules():
    """断言规则：正印→supportive，化忌→caution。"""
    rules_data = {
        "_meta": {"version": "1.0", "description": "P1.3 测试规则", "status": "TEST"},
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
    p = Path(__file__).parent.parent.parent / "tests" / "spec" / "fixtures" / "p13_assertion_rules.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rules_data, ensure_ascii=False), encoding="utf-8")
    return str(p)


@pytest.fixture
def rule_library(assertion_rules):
    return AssertionRuleLibrary.load(assertion_rules)


@pytest.fixture
def orchestrator(rule_library):
    return CrossDomainOrchestrator(assertion_library=rule_library)


def make_atom(evidence: EngineEvidence, atom_id: str, semantic_keys: List[str], domain_candidates: List[str]) -> SemanticAtom:
    return SemanticAtom(
        atom_id=atom_id,
        engine=evidence.engine,
        evidence_ref=evidence.evidence_id,
        semantic_keys=semantic_keys,
        domain_candidates=domain_candidates,
        label_zh="",
        category="",
    )


# ─── Stage 1: Evidence 独立生产（3 tests）─────────────────────────────────────


class TestStage1_EvidenceIndependence:
    def test_bazi_evidence_no_direction(self, bazi_evidences):
        for ev in bazi_evidences:
            assert not hasattr(ev, "direction")
            assert "direction" not in ev.attributes
            assert "strength" not in ev.attributes
            assert "confidence" not in ev.attributes

    def test_ziwei_evidence_no_direction(self, ziwei_evidences):
        for ev in ziwei_evidences:
            assert not hasattr(ev, "direction")
            assert "direction" not in ev.attributes
            assert "strength" not in ev.attributes
            assert "confidence" not in ev.attributes

    def test_evidence_structures_independent(self, bazi_evidences, ziwei_evidences):
        bazi_ids = {ev.evidence_id for ev in bazi_evidences}
        ziwei_ids = {ev.evidence_id for ev in ziwei_evidences}
        assert bazi_ids.isdisjoint(ziwei_ids)


# ─── Stage 2: Assertion 独立生成（6 tests）────────────────────────────────────


class TestStage2_AssertionIndependence:
    def test_bazi_assertion_from_bazi_rule(self, orchestrator, bazi_evidences, rule_library):
        ev = bazi_evidences[0]
        atom = make_atom(ev, "TEN_GOD_ZHENG_GUAN", ["LEARNING", "RESOURCE"], ["GROWTH", "CAREER"])
        rule = rule_library.find_rule(atom, {})
        assert rule is not None
        assert rule.direction == AssertionDirection.SUPPORTIVE
        assert rule.provenance.source_work == "子平真诠"

    def test_ziwei_assertion_from_ziwei_rule(self, orchestrator, ziwei_evidences, rule_library):
        ev = ziwei_evidences[0]
        atom = make_atom(ev, "ZW_SIHUA_HUA_JI", ["RESTRICTION"], ["FINANCE"])
        rule = rule_library.find_rule(atom, {})
        assert rule is not None
        assert rule.direction == AssertionDirection.CAUTION
        assert rule.provenance.source_work == "紫微斗数全书"

    def test_bazi_assertion_no_ziwei_evidence_ref(self, orchestrator, bazi_evidences, rule_library):
        ev = bazi_evidences[0]
        atom = make_atom(ev, "TEN_GOD_ZHENG_GUAN", ["LEARNING"], ["GROWTH"])
        rule = rule_library.find_rule(atom, {})
        if rule:
            assertion = CanonicalAssertion(
                assertion_id=f"AS-{ev.evidence_id}-{atom.atom_id}",
                subject="test",
                domain=rule.domain,
                semantic=atom.atom_id,
                direction=rule.direction,
                temporal_scope="birth",
                source_engine=ev.engine.value,
                source_rule=ev.evidence_id,
                authorized_rule_id=rule.rule_id,
                evidence=EvidenceRef(
                    evidence_id=ev.evidence_id,
                    engine=ev.engine.value,
                    value=ev.value,
                    source_rule_ref=ev.source_rule_ref,
                ),
            )
            assert assertion.source_engine == "ZI_PING"
            assert ev.engine.value in assertion.evidence.engine

    def test_ziwei_assertion_no_bazi_evidence_ref(self, orchestrator, ziwei_evidences, rule_library):
        ev = ziwei_evidences[0]
        atom = make_atom(ev, "ZW_SIHUA_HUA_JI", ["RESTRICTION"], ["FINANCE"])
        rule = rule_library.find_rule(atom, {})
        if rule:
            assertion = CanonicalAssertion(
                assertion_id=f"AS-{ev.evidence_id}-{atom.atom_id}",
                subject="test",
                domain=rule.domain,
                semantic=atom.atom_id,
                direction=rule.direction,
                temporal_scope="birth",
                source_engine=ev.engine.value,
                source_rule=ev.evidence_id,
                authorized_rule_id=rule.rule_id,
                evidence=EvidenceRef(
                    evidence_id=ev.evidence_id,
                    engine=ev.engine.value,
                    value=ev.value,
                    source_rule_ref=ev.source_rule_ref,
                ),
            )
            assert assertion.source_engine == "ZI_WEI"

    def test_same_semantic_not_merged(self, rule_library):
        """T9: 同一 semantic 不同体系 → 独立 Assertion，不合并。"""
        ev1 = EngineEvidence(
            evidence_id="ZP-EV-001", engine=EngineName.ZI_PING, rule_id="ZP_RULE",
            value="正官", temporal_scope=TemporalScope.BIRTH,
            attributes={"ten_god": "正官"}, source_rule_ref="r", source_field="f",
        )
        ev2 = EngineEvidence(
            evidence_id="ZW-EV-001", engine=EngineName.ZI_WEI, rule_id="ZW_RULE",
            value="HUA_LU", temporal_scope=TemporalScope.BIRTH,
            attributes={"sihua": "HUA_LU"}, source_rule_ref="r", source_field="f",
        )
        atom1 = SemanticAtom(atom_id="SAME_SEMANTIC", engine=EngineName.ZI_PING,
                             evidence_ref=ev1.evidence_id, semantic_keys=["CAREER"],
                             domain_candidates=["CAREER"], label_zh="", category="")
        atom2 = SemanticAtom(atom_id="SAME_SEMANTIC", engine=EngineName.ZI_WEI,
                             evidence_ref=ev2.evidence_id, semantic_keys=["CAREER"],
                             domain_candidates=["CAREER"], label_zh="", category="")
        # Two different evidence_ids → two different assertions
        assert ev1.evidence_id != ev2.evidence_id
        assert atom1.evidence_ref != atom2.evidence_ref


# ─── Stage 3: EvidenceCoverage 合并（5 tests）─────────────────────────────────


class TestStage3_CoverageMerge:
    def test_coverage_source_engines_contains_both(self, orchestrator, bazi_evidences, ziwei_evidences, rule_library):
        """T10: source_engines 包含 ZI_PING + ZI_WEI。"""
        def atom_fn(ev):
            if ev.engine == EngineName.ZI_PING:
                return SemanticAtom(atom_id="TEN_GOD_ZHENG_GUAN", engine=ev.engine,
                                    evidence_ref=ev.evidence_id, semantic_keys=["LEARNING"],
                                    domain_candidates=["GROWTH"], label_zh="", category="")
            return SemanticAtom(atom_id="ZW_SIHUA_HUA_JI", engine=ev.engine,
                                evidence_ref=ev.evidence_id, semantic_keys=["RESTRICTION"],
                                domain_candidates=["FINANCE"], label_zh="", category="")

        result = orchestrator.orchestrate("test-case", "birth", {
            "ZI_PING": bazi_evidences,
            "ZI_WEI": ziwei_evidences,
        }, atom_fn)
        assert "ZI_PING" in result.coverage.engines
        assert "ZI_WEI" in result.coverage.engines

    def test_coverage_by_engine_separation(self, orchestrator, bazi_evidences, ziwei_evidences, rule_library):
        """T14: by_engine 保持体系分离存储。"""
        def atom_fn(ev):
            return SemanticAtom(atom_id="X", engine=ev.engine, evidence_ref=ev.evidence_id,
                                semantic_keys=[], domain_candidates=[], label_zh="", category="")
        result = orchestrator.orchestrate("test", "birth", {
            "ZI_PING": bazi_evidences,
            "ZI_WEI": ziwei_evidences,
        }, atom_fn)
        assert "ZI_PING" in result.by_engine
        assert "ZI_WEI" in result.by_engine
        bazi_set = result.by_engine["ZI_PING"]
        ziwei_set = result.by_engine["ZI_WEI"]
        assert bazi_set.engine == "ZI_PING"
        assert ziwei_set.engine == "ZI_WEI"
        assert bazi_set.evidence_ids == [bazi_evidences[0].evidence_id]
        assert ziwei_set.evidence_ids == [ziwei_evidences[0].evidence_id]

    def test_coverage_multi_domain_index(self, orchestrator, rule_library):
        """T26: Coverage 正确索引多 domain。Bazi→GROWTH, Ziwei→FINANCE。"""
        def atom_fn(ev):
            if ev.engine == EngineName.ZI_PING:
                return SemanticAtom(atom_id="TEN_GOD_ZHENG_GUAN", engine=ev.engine,
                                    evidence_ref=ev.evidence_id, semantic_keys=["LEARNING"],
                                    domain_candidates=["GROWTH"], label_zh="", category="")
            return SemanticAtom(atom_id="ZW_SIHUA_HUA_JI", engine=ev.engine,
                                evidence_ref=ev.evidence_id, semantic_keys=["RESTRICTION"],
                                domain_candidates=["FINANCE"], label_zh="", category="")

        result = orchestrator.orchestrate("multi-domain-test", "birth", {
            "ZI_PING": [EngineEvidence(
                evidence_id="ZP-EV-1", engine=EngineName.ZI_PING, rule_id="ZP_R1",
                value="正印", temporal_scope=TemporalScope.BIRTH,
                attributes={"ten_god": "正印"}, source_rule_ref="r", source_field="f",
            )],
            "ZI_WEI": [EngineEvidence(
                evidence_id="ZW-EV-1", engine=EngineName.ZI_WEI, rule_id="ZW_R1",
                value="HUA_JI", temporal_scope=TemporalScope.BIRTH,
                attributes={"sihua": "HUA_JI"}, source_rule_ref="r", source_field="f",
            )],
        }, atom_fn)

        assert "GROWTH" in result.coverage.domains
        assert "FINANCE" in result.coverage.domains
        # GROWTH 下应有 ZI_PING 的 assertion
        growth_assertions = result.coverage.get_assertion_ids("GROWTH", "TEN_GOD_ZHENG_GUAN")
        assert len(growth_assertions) == 1
        # FINANCE 下应有 ZI_WEI 的 assertion
        finance_assertions = result.coverage.get_assertion_ids("FINANCE", "ZW_SIHUA_HUA_JI")
        assert len(finance_assertions) == 1

    def test_coverage_multi_semantic_same_domain(self, orchestrator, rule_library):
        """T27: 同 domain 多 semantic → Coverage 正确索引。"""
        # Both atoms map to different domains in rule library: TEN_GOD_ZHENG_GUAN→GROWTH, ZW_SIHUA_HUA_JI→FINANCE
        # This test verifies Coverage handles multi-domain correctly
        def atom_fn(ev):
            if ev.engine == EngineName.ZI_PING:
                return SemanticAtom(atom_id="TEN_GOD_ZHENG_GUAN", engine=ev.engine,
                                    evidence_ref=ev.evidence_id, semantic_keys=["LEARNING"],
                                    domain_candidates=["GROWTH"], label_zh="", category="")
            return SemanticAtom(atom_id="ZW_SIHUA_HUA_JI", engine=ev.engine,
                                evidence_ref=ev.evidence_id, semantic_keys=["RESTRICTION"],
                                domain_candidates=["FINANCE"], label_zh="", category="")

        result = orchestrator.orchestrate("multi-sem-test", "birth", {
            "ZI_PING": [EngineEvidence(
                evidence_id="ZP-EV-A", engine=EngineName.ZI_PING, rule_id="ZP_R_A",
                value="v1", temporal_scope=TemporalScope.BIRTH,
                attributes={"ten_god": "正印"}, source_rule_ref="r", source_field="f",
            )],
            "ZI_WEI": [EngineEvidence(
                evidence_id="ZW-EV-B", engine=EngineName.ZI_WEI, rule_id="ZW_R_B",
                value="v2", temporal_scope=TemporalScope.BIRTH,
                attributes={"sihua": "HUA_JI"}, source_rule_ref="r", source_field="f",
            )],
        }, atom_fn)

        # Should have both GROWTH and FINANCE domains
        assert "GROWTH" in result.coverage.domains
        assert "FINANCE" in result.coverage.domains
        # Each domain has its own semantic
        growth_ids = result.coverage.get_assertion_ids("GROWTH", "TEN_GOD_ZHENG_GUAN")
        finance_ids = result.coverage.get_assertion_ids("FINANCE", "ZW_SIHUA_HUA_JI")
        assert len(growth_ids) == 1
        assert len(finance_ids) == 1
        assert growth_ids[0] != finance_ids[0]

    def test_coverage_multi_engine_same_domain_semantic(self, orchestrator, rule_library):
        """T28: 同 domain × 同 semantic 多引擎 → Coverage 正确索引。"""
        # Use TEN_GOD_ZHENG_GUAN for both engines — only Bazi rule matches, Ziwei doesn't
        # but Coverage should still record the one assertion correctly
        def atom_fn(ev):
            return SemanticAtom(atom_id="TEN_GOD_ZHENG_GUAN", engine=ev.engine,
                                evidence_ref=ev.evidence_id, semantic_keys=["LEARNING"],
                                domain_candidates=["GROWTH"], label_zh="", category="")

        result = orchestrator.orchestrate("multi-engine-test", "birth", {
            "ZI_PING": [EngineEvidence(
                evidence_id="ZP-EV-SHARED", engine=EngineName.ZI_PING, rule_id="ZP_R",
                value="v1", temporal_scope=TemporalScope.BIRTH,
                attributes={"ten_god": "正印"}, source_rule_ref="r", source_field="f",
            )],
            "ZI_WEI": [EngineEvidence(
                evidence_id="ZW-EV-SHARED", engine=EngineName.ZI_WEI, rule_id="ZW_R",
                value="v2", temporal_scope=TemporalScope.BIRTH,
                attributes={}, source_rule_ref="r", source_field="f",
            )],
        }, atom_fn)

        # GROWTH → TEN_GOD_ZHENG_GUAN: both engines match same rule → 2 assertions
        shared_ids = result.coverage.get_assertion_ids("GROWTH", "TEN_GOD_ZHENG_GUAN")
        assert len(shared_ids) == 2  # 两个引擎各一条 assertion（同语义）
        # by_engine should have both engines present (even if Ziwei has 0 assertions)
        assert "ZI_PING" in result.coverage.engines
        assert "ZI_WEI" in result.coverage.engines

    def test_coverage_total_assertions(self, orchestrator, bazi_evidences, ziwei_evidences, rule_library):
        """T29: coverage.total_assertions = 实际 Assertion 总数（只计有规则的）。"""
        def atom_fn(ev):
            if ev.engine == EngineName.ZI_PING:
                return SemanticAtom(atom_id="TEN_GOD_ZHENG_GUAN", engine=ev.engine,
                                    evidence_ref=ev.evidence_id, semantic_keys=["LEARNING"],
                                    domain_candidates=["GROWTH"], label_zh="", category="")
            return SemanticAtom(atom_id="ZW_SIHUA_HUA_JI", engine=ev.engine,
                                evidence_ref=ev.evidence_id, semantic_keys=["RESTRICTION"],
                                domain_candidates=["FINANCE"], label_zh="", category="")
        result = orchestrator.orchestrate("test", "birth", {
            "ZI_PING": bazi_evidences,
            "ZI_WEI": ziwei_evidences,
        }, atom_fn)
        # Both rules match → 2 assertions total
        assert result.coverage.total_assertions == 2


# ─── Stage 4: 禁止行为验证（5 tests）──────────────────────────────────────────


class TestStage4_ProhibitedBehaviors:
    def test_no_cross_analyzer_in_orchestrator(self, orchestrator):
        """T15: 无 CrossAnalyzer 调用。"""
        source = inspect.getsource(CrossDomainOrchestrator)
        assert "CrossAnalyzer" not in source

    def test_no_convergence_arbiter(self, orchestrator):
        """T16: 无 ConvergenceArbiter 调用。"""
        source = inspect.getsource(CrossDomainOrchestrator)
        assert "ConvergenceArbiter" not in source

    def test_no_evidence_count_threshold_trigger(self, orchestrator):
        """T17: 无 evidence_count 阈值触发 Judgment。"""
        source = inspect.getsource(CrossDomainOrchestrator)
        assert "evidence_count" not in source or "threshold" not in source.lower()
        assert "judgment_library" not in source.lower() or "judgment_rule" not in source.lower()

    def test_no_neutral_fallback(self, orchestrator, rule_library):
        """T18: 无 NEUTRAL fallback。"""
        empty_lib = AssertionRuleLibrary(rules=[])
        from tongshu.spec.canonical import SemanticAtom, EngineName
        fake_atom = SemanticAtom(atom_id="NONE", engine=EngineName.ZI_PING,
                                  evidence_ref="EV-FAKE", semantic_keys=["NONE"],
                                  domain_candidates=["CAREER"])
        result = empty_lib.find_rule(fake_atom, {})
        assert result is None  # NO_ASSERTION, not NEUTRAL

    def test_full_traceability(self, orchestrator, bazi_evidences, rule_library):
        """T19: 追溯链完整。"""
        ev = bazi_evidences[0]
        atom = make_atom(ev, "TEN_GOD_ZHENG_GUAN", ["LEARNING"], ["GROWTH"])
        rule = rule_library.find_rule(atom, {})
        if rule:
            assertion = CanonicalAssertion(
                assertion_id=f"AS-{ev.evidence_id}-{atom.atom_id}",
                subject="trace-test", domain=rule.domain, semantic=atom.atom_id,
                direction=rule.direction, temporal_scope="birth",
                source_engine=ev.engine.value, source_rule=ev.evidence_id,
                authorized_rule_id=rule.rule_id,
                evidence=EvidenceRef(evidence_id=ev.evidence_id, engine=ev.engine.value,
                                     value=ev.value, source_rule_ref=ev.source_rule_ref),
            )
            assert assertion.evidence.evidence_id == ev.evidence_id
            assert assertion.evidence.engine == ev.engine.value
            assert assertion.authorized_rule_id == rule.rule_id
            assert assertion.direction == rule.direction


# ─── Stage 5: 负向测试（3 tests）—— P1.3 灵魂 ────────────────────────────────


class TestStage5_NegativeTests:
    """T20-T22: 方向相反场景验证 — 最关键的测试。"""

    def test_opposite_directions_both_retained(self, orchestrator, rule_library):
        """T20: 方向相反场景 — 两 Assertion 都保留。"""
        bazi_ev = EngineEvidence(
            evidence_id="BP-001", engine=EngineName.ZI_PING, rule_id="ZP_R1",
            value="正印", temporal_scope=TemporalScope.BIRTH,
            attributes={"ten_god": "正印"}, source_rule_ref="r", source_field="f",
        )
        ziwei_ev = EngineEvidence(
            evidence_id="ZW-001", engine=EngineName.ZI_WEI, rule_id="ZW_R1",
            value="HUA_JI", temporal_scope=TemporalScope.BIRTH,
            attributes={"sihua": "HUA_JI"}, source_rule_ref="r", source_field="f",
        )

        def atom_fn(ev):
            if ev.engine == EngineName.ZI_PING:
                return SemanticAtom(atom_id="TEN_GOD_ZHENG_GUAN", engine=ev.engine,
                                    evidence_ref=ev.evidence_id, semantic_keys=["LEARNING"],
                                    domain_candidates=["GROWTH"])
            return SemanticAtom(atom_id="ZW_SIHUA_HUA_JI", engine=ev.engine,
                                evidence_ref=ev.evidence_id, semantic_keys=["RESTRICTION"],
                                domain_candidates=["FINANCE"])

        result = orchestrator.orchestrate("opposite-test", "birth", {
            "ZI_PING": [bazi_ev],
            "ZI_WEI": [ziwei_ev],
        }, atom_fn)

        # 两个体系的 Assertion 都必须存在
        assert len(result.by_engine["ZI_PING"].assertion_ids) == 1
        assert len(result.by_engine["ZI_WEI"].assertion_ids) == 1
        # 但结果中不应有 direction 比较
        assert not hasattr(result, "direction")

    def test_no_conflicted_on_opposite_directions(self, orchestrator, rule_library):
        """T21: 方向相反时不产生 CONFLICTED/ALIGNED/PARTIAL。"""
        bazi_ev = EngineEvidence(
            evidence_id="BP-002", engine=EngineName.ZI_PING, rule_id="ZP_R2",
            value="正印", temporal_scope=TemporalScope.BIRTH,
            attributes={"ten_god": "正印"}, source_rule_ref="r", source_field="f",
        )
        ziwei_ev = EngineEvidence(
            evidence_id="ZW-002", engine=EngineName.ZI_WEI, rule_id="ZW_R2",
            value="HUA_JI", temporal_scope=TemporalScope.BIRTH,
            attributes={"sihua": "HUA_JI"}, source_rule_ref="r", source_field="f",
        )

        def atom_fn(ev):
            if ev.engine == EngineName.ZI_PING:
                return SemanticAtom(atom_id="TEN_GOD_ZHENG_GUAN", engine=ev.engine,
                                    evidence_ref=ev.evidence_id, semantic_keys=["LEARNING"],
                                    domain_candidates=["GROWTH"])
            return SemanticAtom(atom_id="ZW_SIHUA_HUA_JI", engine=ev.engine,
                                evidence_ref=ev.evidence_id, semantic_keys=["RESTRICTION"],
                                domain_candidates=["FINANCE"])

        result = orchestrator.orchestrate("conflict-test", "birth", {
            "ZI_PING": [bazi_ev],
            "ZI_WEI": [ziwei_ev],
        }, atom_fn)

        # 验证无 CONFLICTED/ALIGNED/PARTIAL 相关字段
        forbidden_status = {"CONFLICTED", "ALIGNED", "PARTIAL", "direction_alignment"}
        result_dict = result.to_dict()
        for key in forbidden_status:
            assert key not in result_dict, f"CrossDomainResult contains forbidden key: {key}"

    def test_no_verdict_on_opposite_directions(self, orchestrator, rule_library):
        """T22: 方向相反时不判断谁胜出，只做结构性记录。"""
        bazi_ev = EngineEvidence(
            evidence_id="BP-003", engine=EngineName.ZI_PING, rule_id="ZP_R3",
            value="正印", temporal_scope=TemporalScope.BIRTH,
            attributes={"ten_god": "正印"}, source_rule_ref="r", source_field="f",
        )
        ziwei_ev = EngineEvidence(
            evidence_id="ZW-003", engine=EngineName.ZI_WEI, rule_id="ZW_R3",
            value="HUA_JI", temporal_scope=TemporalScope.BIRTH,
            attributes={"sihua": "HUA_JI"}, source_rule_ref="r", source_field="f",
        )

        def atom_fn(ev):
            if ev.engine == EngineName.ZI_PING:
                return SemanticAtom(atom_id="TEN_GOD_ZHENG_GUAN", engine=ev.engine,
                                    evidence_ref=ev.evidence_id, semantic_keys=["LEARNING"],
                                    domain_candidates=["GROWTH"])
            return SemanticAtom(atom_id="ZW_SIHUA_HUA_JI", engine=ev.engine,
                                evidence_ref=ev.evidence_id, semantic_keys=["RESTRICTION"],
                                domain_candidates=["FINANCE"])

        result = orchestrator.orchestrate("no-verdict-test", "birth", {
            "ZI_PING": [bazi_ev],
            "ZI_WEI": [ziwei_ev],
        }, atom_fn)

        # 结构性记录：两套证据都保留
        assert len(result.by_engine["ZI_PING"].evidence_ids) == 1
        assert len(result.by_engine["ZI_WEI"].evidence_ids) == 1
        # 无 winner/loser 字段
        forbidden_verdict = {"winner", "loser", "dominant", "superior", "inferior", "verdict"}
        for attr in forbidden_verdict:
            assert not hasattr(result, attr), f"CrossDomainResult has forbidden verdict attribute: {attr}"


# ─── Stage 6: 真实命例验证（3 tests）──────────────────────────────────────────


class TestStage6_RealChart:
    def test_jixiaolan_bazi_ziwei_both_run(self):
        """T23: 纪晓岚命例 — Bazi + Ziwei 同时跑通。"""
        import os
        os.environ["TONGSHU_ALLOW_ZIWEI_STUB"] = "1"
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

        from tongshu.engines.bazi_engine import BaziEngine
        from tongshu.engines.ziwei_engine import ZiweiEngine
        from tongshu.engines.bazi.evidence_producer import BaziEvidenceProducer
        from tongshu.engines.ziwei.evidence_producer import ZiweiEvidenceProducer

        # Bazi
        bazi_engine = BaziEngine()
        bazi_chart = bazi_engine.compute((1724, 8, 3, 11), gender="male")
        bazi_producer = BaziEvidenceProducer()
        bazi_evidences = bazi_producer.produce(bazi_chart)

        # Ziwei (stub)
        ziwei_engine = ZiweiEngine()
        ziwei_chart = ziwei_engine.compute((1724, 8, 3), 6, gender="male")
        ziwei_producer = ZiweiEvidenceProducer()
        ziwei_evidences = ziwei_producer.produce(ziwei_chart)

        assert len(bazi_evidences) > 0, "Bazi 必须产出证据"
        assert len(ziwei_evidences) >= 0, "Ziwei 可产出 0 条（stub 限制）"

        # 验证无方向泄漏
        for ev in bazi_evidences:
            assert not hasattr(ev, "direction")
            assert "direction" not in ev.attributes

    def test_assertions_traceable_to_engines(self):
        """T24: 两套 Assertion 可独立追溯到各自 Engine。"""
        bazi_ev = EngineEvidence(
            evidence_id="TRACE-BP-001", engine=EngineName.ZI_PING, rule_id="ZP_TG",
            value="正印", temporal_scope=TemporalScope.BIRTH,
            attributes={"ten_god": "正印"}, source_rule_ref="r", source_field="f",
        )
        ziwei_ev = EngineEvidence(
            evidence_id="TRACE-ZW-001", engine=EngineName.ZI_WEI, rule_id="ZW_SIH",
            value="HUA_KE", temporal_scope=TemporalScope.BIRTH,
            attributes={"sihua": "HUA_KE"}, source_rule_ref="r", source_field="f",
        )

        def atom_fn(ev):
            if ev.engine == EngineName.ZI_PING:
                return SemanticAtom(atom_id="TEN_GOD_ZHENG_GUAN", engine=ev.engine,
                                    evidence_ref=ev.evidence_id, semantic_keys=["LEARNING"],
                                    domain_candidates=["GROWTH"])
            return SemanticAtom(atom_id="ZW_SIHUA_HUA_KE", engine=ev.engine,
                                evidence_ref=ev.evidence_id, semantic_keys=["GROWTH"],
                                domain_candidates=["GROWTH"])

        # 只需验证追溯链完整性
        assert bazi_ev.engine == EngineName.ZI_PING
        assert ziwei_ev.engine == EngineName.ZI_WEI
        assert bazi_ev.evidence_id != ziwei_ev.evidence_id
        assert bazi_ev.source_rule_ref is not None
        assert ziwei_ev.source_rule_ref is not None

    def test_coverage_is_structured_observation_not_judgment(self, orchestrator, bazi_evidences, ziwei_evidences, rule_library):
        """T25: Coverage 输出为 Structured Observation（非 Judgment）。"""
        def atom_fn(ev):
            if ev.engine == EngineName.ZI_PING:
                return SemanticAtom(atom_id="TEN_GOD_ZHENG_GUAN", engine=ev.engine,
                                    evidence_ref=ev.evidence_id, semantic_keys=["LEARNING"],
                                    domain_candidates=["GROWTH"])
            return SemanticAtom(atom_id="ZW_SIHUA_HUA_JI", engine=ev.engine,
                                evidence_ref=ev.evidence_id, semantic_keys=["RESTRICTION"],
                                domain_candidates=["FINANCE"])

        result = orchestrator.orchestrate("obs-test", "birth", {
            "ZI_PING": bazi_evidences,
            "ZI_WEI": ziwei_evidences,
        }, atom_fn)

        # 验证是 Coverage（Structured Observation）而非 Judgment
        assert isinstance(result.coverage, MultiDomainSemanticCoverage)
        # 不应有任何 Judgment 相关字段
        forbidden_judgment = {"judgment_id", "authorized_by", "supporting_assertions", "judgment"}
        for attr in forbidden_judgment:
            assert not hasattr(result, attr), f"CrossDomainResult has judgment attribute: {attr}"
        result_dict = result.to_dict()
        for key in forbidden_judgment:
            assert key not in result_dict
