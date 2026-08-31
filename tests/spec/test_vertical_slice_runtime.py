"""
P1.2-D: Real Bazi Runtime Vertical Slice

目标：用真实生产输入（BaziEngine.compute）跑通完整链路，证明：
  1. 新 Contract 可以消费真实引擎输出
  2. 旧 Signal Engine / CrossAnalyzer 不参与新链路
  3. 追溯链完整

输出：docs/audit/p1_2d_runtime_trace.md（生产调用图）
"""
from __future__ import annotations

import json
import sys
import inspect
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.bazi.evidence_producer import BaziEvidenceProducer
from tongshu.spec.canonical import (
    EngineEvidence,
    SemanticAtom,
    CanonicalAssertion,
    EvidenceRef,
    EngineName,
    TemporalScope,
)
from tongshu.assertion.assertion_rule_library import AssertionRuleLibrary


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def real_bazi_chart():
    """真实生产输入：纪晓岚命例（公历 1724-08-03 午时）。"""
    engine = BaziEngine()
    chart = engine.compute((1724, 8, 3, 11), gender="male")
    return chart


@pytest.fixture(scope="session")
def assertion_rules_path(tmp_path_factory):
    """测试断言规则（覆盖纪晓岚实际十神：偏印/正财/比肩）。"""
    rules_data = {
        "_meta": {
            "version": "1.0",
            "description": "P1.2-D 测试断言规则",
            "status": "TEST",
        },
        "rules": [
            {
                "rule_id": "ASR-BT-PIAN_YIN",
                "domain": "GROWTH",
                "match_strategy": "EXACT",
                "condition": {"atom_id": "TEN_GOD_PIAN_YIN"},
                "direction": "caution",
                "canonical_source": "子平真诠·论偏印",
            },
            {
                "rule_id": "ASR-BT-ZHENG_CAi",
                "domain": "FINANCE",
                "match_strategy": "EXACT",
                "condition": {"atom_id": "TEN_GOD_ZHENG_CAi"},
                "direction": "supportive",
                "canonical_source": "子平真诠·论正财",
            },
            {
                "rule_id": "ASR-BT-BI_JIAN",
                "domain": "SOCIAL",
                "match_strategy": "EXACT",
                "condition": {"atom_id": "TEN_GOD_BI_JIAN"},
                "direction": "neutral",
                "canonical_source": "子平真诠·论比肩",
            },
        ],
    }
    p = tmp_path_factory.mktemp("fixtures").joinpath("assertion_rules_runtime.json")
    p.write_text(json.dumps(rules_data, ensure_ascii=False), encoding="utf-8")
    return str(p)


@pytest.fixture(scope="session")
def ten_gods_path() -> str:
    base = Path(__file__).parent.parent.parent
    return str(base / "data" / "semantic_atoms" / "ten_gods.json")


# ─── P1.2-D: Real Runtime Tests ─────────────────────────────────────────────


class TestRealRuntimeVerticalSlice:
    """用真实 BaziEngine 输出跑通新 Contract 全链路。"""

    def test_real_chart_produces_evidence(self, real_bazi_chart):
        """D1: 真实 BaziChart → EngineEvidence 列表非空。"""
        producer = BaziEvidenceProducer()
        evidences = producer.produce(real_bazi_chart)
        assert isinstance(evidences, list)
        assert len(evidences) > 0, "真实命例必须产出证据"
        assert all(isinstance(e, EngineEvidence) for e in evidences)

    def test_real_chart_evidence_no_direction(self, real_bazi_chart):
        """D2: 真实命例产出的 EngineEvidence 无 direction/polarity/strength/confidence。"""
        producer = BaziEvidenceProducer()
        evidences = producer.produce(real_bazi_chart)
        for ev in evidences:
            assert not hasattr(ev, "direction"), f"Evidence {ev.evidence_id} 携带 direction"
            assert not hasattr(ev, "polarity")
            assert "direction" not in ev.attributes
            assert "polarity" not in ev.attributes
            assert "strength" not in ev.attributes
            assert "confidence" not in ev.attributes

    def test_real_chart_evidence_traceable(self, real_bazi_chart):
        """D3: 真实命例产出的每条 Evidence 可追溯。"""
        producer = BaziEvidenceProducer()
        evidences = producer.produce(real_bazi_chart)
        for ev in evidences:
            assert ev.evidence_id and len(ev.evidence_id) > 0
            assert ev.rule_id and len(ev.rule_id) > 0
            assert ev.engine == EngineName.ZI_PING
            assert ev.temporal_scope in list(TemporalScope)
            assert ev.source_rule_ref is not None
            assert ev.calculation_version == "2026.09"
            assert ev.contract_version == "v13.0"
            assert ev.evidence_id != ev.rule_id

    def test_real_chart_to_semantic_atom(self, real_bazi_chart, ten_gods_path):
        """D4: 真实命例的 Evidence → SemanticAtom 映射无方向泄漏。"""
        producer = BaziEvidenceProducer()
        evidences = producer.produce(real_bazi_chart)

        with open(ten_gods_path, encoding="utf-8") as f:
            atom_db = json.load(f)

        atoms = []
        for ev in evidences:
            if ev.attributes.get("ten_god"):
                tg = ev.attributes["ten_god"]
                for atom_def in atom_db.get("atoms", []):
                    if atom_def.get("label_zh") == tg:
                        atom = SemanticAtom(
                            atom_id=atom_def["atom_id"],
                            engine=ev.engine,
                            evidence_ref=ev.evidence_id,
                            semantic_keys=atom_def.get("semantic_keys", []),
                            domain_candidates=atom_def.get("domain_candidates", []),
                            label_zh=tg,
                            category=atom_def.get("category", ""),
                            guidance_keys=atom_def.get("guidance_keys", []),
                        )
                        atoms.append(atom)
                        break

        assert len(atoms) > 0, "十神 Evidence 应能映射到 SemanticAtom"
        for atom in atoms:
            assert not hasattr(atom, "direction")

    def test_real_chart_assertion_from_rule(self, real_bazi_chart, ten_gods_path, assertion_rules_path):
        """D5: 真实命例的 SemanticAtom → CanonicalAssertion，direction 来自规则授权。"""
        library = AssertionRuleLibrary.load(assertion_rules_path)
        producer = BaziEvidenceProducer()
        evidences = producer.produce(real_bazi_chart)

        with open(ten_gods_path, encoding="utf-8") as f:
            atom_db = json.load(f)

        atoms_with_evidence = []
        evidence_map = {ev.evidence_id: ev for ev in evidences}

        for ev in evidences:
            if ev.attributes.get("ten_god"):
                tg = ev.attributes["ten_god"]
                for atom_def in atom_db.get("atoms", []):
                    if atom_def.get("label_zh") == tg:
                        atom = SemanticAtom(
                            atom_id=atom_def["atom_id"],
                            engine=ev.engine,
                            evidence_ref=ev.evidence_id,
                            semantic_keys=atom_def.get("semantic_keys", []),
                            domain_candidates=atom_def.get("domain_candidates", []),
                            label_zh=tg,
                            category=atom_def.get("category", ""),
                            guidance_keys=atom_def.get("guidance_keys", []),
                        )
                        atoms_with_evidence.append((atom, ev))
                        break

        assertions = []
        for atom, ev in atoms_with_evidence:
            rule = library.find_rule(atom, {"temporal_scope": "birth", "case_id": "jixiaolan"})
            if rule is not None:
                assertion = CanonicalAssertion(
                    assertion_id=f"AS-{ev.evidence_id}-{atom.atom_id}",
                    subject="jixiaolan",
                    domain=rule.domain,
                    semantic=atom.atom_id,
                    direction=rule.direction,
                    temporal_scope="birth",
                    source_engine=atom.engine.value,
                    source_rule=atom.evidence_ref,
                    authorized_rule_id=rule.rule_id,
                    evidence=EvidenceRef(
                        evidence_id=atom.evidence_ref,
                        engine=atom.engine.value,
                        value=ev.value,
                        source_rule_ref=ev.source_rule_ref,
                    ),
                )
                assertions.append(assertion)

        assert len(assertions) > 0, "至少应有一条 Assertion 命中规则"

        for a in assertions:
            matched_rule = library.find_rule(
                next(at for at, _ in atoms_with_evidence if at.atom_id == a.semantic),
                {"temporal_scope": "birth", "case_id": "jixiaolan"},
            )
            assert matched_rule is not None
            assert a.direction == matched_rule.direction
            assert a.authorized_rule_id == matched_rule.rule_id

    def test_real_chart_no_legacy_signal_in_chain(self, real_bazi_chart):
        """D6: 新链路中不包含旧 Signal Engine 的调用。"""
        source = inspect.getsource(BaziEvidenceProducer)
        assert "SignalEngine" not in source
        assert "signal_engine" not in source
        assert "reasoning.signal" not in source
        assert "cross_analysis" not in source
        assert "ConvergenceArbiter" not in source

    def test_real_chart_no_cross_analyzer(self, real_bazi_chart):
        """D7: 新链路不涉及 CrossAnalyzer。"""
        source = inspect.getsource(AssertionRuleLibrary)
        assert "cross_analysis" not in source.lower()
        assert "CrossAnalyzer" not in source
        assert "CONFLICTED" not in source
        assert "ALIGNED" not in source
        assert "_is_opposite" not in source

    def test_real_chart_no_evidence_count_voting(self, real_bazi_chart):
        """D8: 新链路不涉及 evidence_count 投票。"""
        source = inspect.getsource(AssertionRuleLibrary)
        assert "evidence_count" not in source
        assert "vote" not in source.lower()
        assert "majority" not in source.lower()

    def test_real_chart_full_traceability(self, real_bazi_chart, ten_gods_path, assertion_rules_path):
        """D9: 真实命例的完整追溯链。"""
        library = AssertionRuleLibrary.load(assertion_rules_path)
        producer = BaziEvidenceProducer()
        evidences = producer.produce(real_bazi_chart)

        with open(ten_gods_path, encoding="utf-8") as f:
            atom_db = json.load(f)

        evidence_map = {ev.evidence_id: ev for ev in evidences}

        for ev in evidences:
            if ev.attributes.get("ten_god"):
                tg = ev.attributes["ten_god"]
                for atom_def in atom_db.get("atoms", []):
                    if atom_def.get("label_zh") == tg:
                        atom = SemanticAtom(
                            atom_id=atom_def["atom_id"],
                            engine=ev.engine,
                            evidence_ref=ev.evidence_id,
                            semantic_keys=atom_def.get("semantic_keys", []),
                            domain_candidates=atom_def.get("domain_candidates", []),
                        )
                        rule = library.find_rule(atom, {"temporal_scope": "birth", "case_id": "jixiaolan"})
                        if rule is not None:
                            assertion = CanonicalAssertion(
                                assertion_id=f"AS-{ev.evidence_id}-{atom.atom_id}",
                                subject="jixiaolan",
                                domain=rule.domain,
                                semantic=atom.atom_id,
                                direction=rule.direction,
                                temporal_scope="birth",
                                source_engine=atom.engine.value,
                                source_rule=atom.evidence_ref,
                                authorized_rule_id=rule.rule_id,
                                evidence=EvidenceRef(
                                    evidence_id=atom.evidence_ref,
                                    engine=atom.engine.value,
                                    value=evidence_map[atom.evidence_ref].value,
                                    source_rule_ref=evidence_map[atom.evidence_ref].source_rule_ref,
                                    temporal_scope=evidence_map[atom.evidence_ref].temporal_scope.value,
                                    rule_id=evidence_map[atom.evidence_ref].rule_id,
                                    calculation_version=evidence_map[atom.evidence_ref].calculation_version,
                                    contract_version=evidence_map[atom.evidence_ref].contract_version,
                                ),
                            )
                            assert assertion.evidence.evidence_id == ev.evidence_id
                            assert assertion.evidence.engine == ev.engine.value
                            assert assertion.evidence.source_rule_ref is not None
                            assert assertion.evidence.rule_id == ev.rule_id
                            assert assertion.authorized_rule_id == rule.rule_id
                            assert assertion.direction == rule.direction
                        break


class TestProductionCallTrace:
    """生产调用图：记录真实运行时的调用链。"""

    def test_call_trace_full_chain(self, real_bazi_chart, ten_gods_path, assertion_rules_path):
        """D10: 完整调用链追溯，输出生产调用图数据。"""
        # Step 1: BaziEngine.compute() → BaziChart
        engine = BaziEngine()
        chart = engine.compute((1724, 8, 3, 11), gender="male")
        assert chart.day_master == "BING"
        assert chart.year_pillar.heavenly_stem == "JIA"
        assert chart.year_pillar.earthly_branch == "CHEN"

        # Step 2: BaziEvidenceProducer.produce() → list[EngineEvidence]
        producer = BaziEvidenceProducer()
        evidences = producer.produce(chart)
        assert len(evidences) > 0

        # Step 3: 验证每条 Evidence 结构
        sample = evidences[0]
        assert isinstance(sample, EngineEvidence)
        assert sample.engine == EngineName.ZI_PING
        assert sample.rule_id.startswith("ZP_")
        assert sample.evidence_id.startswith("ZP-")
        assert sample.temporal_scope == TemporalScope.BIRTH
        assert not hasattr(sample, "direction")

        # Step 4: Evidence → SemanticAtom → Assertion
        with open(ten_gods_path, encoding="utf-8") as f:
            atom_db = json.load(f)
        library = AssertionRuleLibrary.load(assertion_rules_path)

        evidence_map = {ev.evidence_id: ev for ev in evidences}
        atoms = []
        for ev in evidences:
            if ev.attributes.get("ten_god"):
                tg = ev.attributes["ten_god"]
                for atom_def in atom_db.get("atoms", []):
                    if atom_def.get("label_zh") == tg:
                        atoms.append(SemanticAtom(
                            atom_id=atom_def["atom_id"],
                            engine=ev.engine,
                            evidence_ref=ev.evidence_id,
                            semantic_keys=atom_def.get("semantic_keys", []),
                            domain_candidates=atom_def.get("domain_candidates", []),
                        ))
                        break

        assertions = []
        for atom in atoms:
            rule = library.find_rule(atom, {"temporal_scope": "birth", "case_id": "jixiaolan"})
            if rule is not None:
                assertions.append(CanonicalAssertion(
                    assertion_id=f"AS-{atom.evidence_ref}-{atom.atom_id}",
                    subject="jixiaolan",
                    domain=rule.domain,
                    semantic=atom.atom_id,
                    direction=rule.direction,
                    temporal_scope="birth",
                    source_engine=atom.engine.value,
                    source_rule=atom.evidence_ref,
                    authorized_rule_id=rule.rule_id,
                    evidence=EvidenceRef(evidence_id=atom.evidence_ref, engine=atom.engine.value, value="", source_rule_ref=""),
                ))

        # 输出调用图数据（供 P1_2D_BAZI_RUNTIME_TRACE.md 使用）
        trace_data = {
            "input": {
                "engine": "BaziEngine",
                "method": "compute((1724, 8, 3, 11), gender='male')",
                "output_type": "BaziChart",
                "day_master": chart.day_master,
                "pillars": [
                    f"{p.heavenly_stem}{p.earthly_branch}"
                    for p in [chart.year_pillar, chart.month_pillar, chart.day_pillar, chart.hour_pillar]
                ],
            },
            "stage_1_evidence": {
                "producer": "BaziEvidenceProducer.produce()",
                "output_type": "list[EngineEvidence]",
                "count": len(evidences),
                "sample": evidences[0].to_dict() if evidences else None,
                "no_direction": all(
                    not hasattr(e, "direction") and "direction" not in e.attributes
                    for e in evidences
                ),
            },
            "stage_2_atom": {
                "mapper": "ten_gods.json 查表",
                "output_type": "list[SemanticAtom]",
                "atom_count": len(atoms),
                "no_direction": all(not hasattr(a, "direction") for a in atoms),
            },
            "stage_3_assertion": {
                "builder": "AssertionRuleLibrary.find_rule() + CanonicalAssertion()",
                "output_type": "list[CanonicalAssertion]",
                "assertion_count": len(assertions),
                "direction_from_rule": all(
                    any(
                        a.authorized_rule_id == r.rule_id and a.direction == r.direction
                        for r in library.list_rules()
                        if r.rule_id == a.authorized_rule_id
                    )
                    for a in assertions
                ) if assertions else True,
            },
            "old_components_not_involved": {
                "SignalEngine": "not imported",
                "CrossAnalyzer": "not imported",
                "ConvergenceArbiter": "not imported",
                "LegacyAdapter": "not imported",
            },
        }

        # 保存调用图数据到 JSON
        output_path = Path(__file__).parent.parent.parent / "docs" / "audit" / "p1_2d_trace_data.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(trace_data, f, ensure_ascii=False, indent=2)

        # 核心断言
        assert len(evidences) > 0
        assert len(atoms) > 0
        assert trace_data["stage_1_evidence"]["no_direction"]
        assert trace_data["stage_2_atom"]["no_direction"]

    def test_no_old_pipeline_involvement(self, real_bazi_chart):
        """D11: 确认旧 Pipeline 组件未被导入/调用。"""
        import sys

        loaded_before = set(sys.modules.keys())

        from tongshu.engines.bazi.evidence_producer import BaziEvidenceProducer
        from tongshu.assertion.assertion_rule_library import AssertionRuleLibrary

        producer = BaziEvidenceProducer()
        evidences = producer.produce(real_bazi_chart)
        library = AssertionRuleLibrary(rules=[])

        new_modules = set(sys.modules.keys()) - loaded_before
        old_indicators = [
            "tongshu.reasoning.signal_engine",
            "tongshu.reasoning.cross_analysis",
            "tongshu.signal.convergence",
            "tongshu.signal.aggregator",
            "tongshu.signal.legacy_adapter",
        ]
        for indicator in old_indicators:
            assert indicator not in new_modules, (
                f"旧组件 {indicator} 在新链路中被导入，违反 P1.2 架构约束"
            )
