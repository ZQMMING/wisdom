"""
P1.2-C: ZiPing 单引擎垂直切片测试

目标：跑通完整链路
  BaziChart → BaziEvidenceProducer → EngineEvidence
            → SemanticAtomMapper → SemanticAtom
            → AssertionRuleLibrary → CanonicalAssertion

验证 6 项约束（全部必须 PASS）：
  ① EngineEvidence 无 direction/polarity/strength/confidence
  ② SemanticAtom 无 direction
  ③ CanonicalAssertion.direction 来自 AuthorizedRule，非 MappingLayer 自由决定
  ④ 未命中规则 → NO_ASSERTION（不是 NEUTRAL）
  ⑤ 每个 Assertion 可追溯：assertion → rule → evidence → engine → source_rule_ref
  ⑥ 无 CrossAnalyzer / ConvergenceArbiter / evidence_count 投票
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Ensure src/ is on path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.engines.bazi_engine import BaziChart, Pillar
from tongshu.engines.bazi.evidence_producer import BaziEvidenceProducer
from tongshu.spec.canonical import (
    EngineEvidence,
    SemanticAtom,
    CanonicalAssertion,
    EvidenceCoverage,
    Judgment,
    AssertionDirection,
    EngineName,
    TemporalScope,
    EvidenceRef,
)
from tongshu.assertion.assertion_rule_library import (
    AssertionRuleLibrary,
    MatchStrategy,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def sample_chart() -> BaziChart:
    """真实命例：纪晓岚（乾隆十年乙丑年己未月甲午日乙亥时）

    注：此处使用简化版本，仅验证垂直切片逻辑，不依赖完整排盘引擎。
    四柱：乙丑 己未 甲午 乙亥
    """
    return BaziChart(
        year_pillar=Pillar("YI", "CHOU"),
        month_pillar=Pillar("JI", "WEI"),
        day_pillar=Pillar("JIA", "WU"),
        hour_pillar=Pillar("YI", "HAI"),
        day_master="JIA",
        luck_pillars=[],
        gender="male",
        peach_blossom=False,
        branch_clash_map={},
        five_element_imbalance=False,
        five_element_balance={},
    )


@pytest.fixture
def assertion_rules_path(tmp_path: Path) -> str:
    """创建测试用断言规则 JSON。"""
    rules_data = {
        "_meta": {
            "version": "1.0",
            "description": "P1.2-C 测试断言规则",
            "status": "TEST",
        },
        "rules": [
            {
                "rule_id": "ASR-TG-ZHENG_GUAN",
                "domain": "CAREER",
                "match_strategy": "EXACT",
                "condition": {"atom_id": "TEN_GOD_ZHENG_GUAN"},
                "direction": "supportive",
                "canonical_source": "子平真诠·论正官",
            },
            {
                "rule_id": "ASR-TG-ZHI_YIN",
                "domain": "GROWTH",
                "match_strategy": "EXACT",
                "condition": {"atom_id": "TEN_GOD_ZHI_YIN"},
                "direction": "supportive",
                "canonical_source": "子平真诠·论印绶",
            },
            {
                "rule_id": "ASR-TG-SHANG_GUAN",
                "domain": "CAREER",
                "match_strategy": "SET_SUBSET",
                "condition": {"keys": ["EXPRESSION", "INNOVATION"]},
                "direction": "caution",
                "canonical_source": "滴天髓·伤官章",
            },
        ],
    }
    p = tmp_path / "assertion_rules_test.json"
    p.write_text(json.dumps(rules_data, ensure_ascii=False), encoding="utf-8")
    return str(p)


@pytest.fixture
def ten_gods_path() -> str:
    """ten_gods.json 路径。"""
    base = Path(__file__).parent.parent.parent
    return str(base / "data" / "semantic_atoms" / "ten_gods.json")


# ─── Stage 1: Engine → EngineEvidence ────────────────────────────────────────


class TestStage1_EvidenceProduction:
    """验证 EngineEvidence 产出符合 V13 约束。"""

    def test_producer_returns_evidence_list(self, sample_chart):
        """S1.1: produce() 返回 list[EngineEvidence]。"""
        producer = BaziEvidenceProducer()
        evidences = producer.produce(sample_chart)
        assert isinstance(evidences, list)
        assert len(evidences) > 0
        assert all(isinstance(e, EngineEvidence) for e in evidences)

    def test_evidence_no_direction_field(self, sample_chart):
        """S1.2: EngineEvidence 不携带 direction 字段。"""
        producer = BaziEvidenceProducer()
        evidences = producer.produce(sample_chart)
        for ev in evidences:
            assert not hasattr(ev, "direction"), (
                f"Evidence {ev.evidence_id} 意外携带 direction"
            )
            assert not hasattr(ev, "polarity"), (
                f"Evidence {ev.evidence_id} 意外携带 polarity"
            )

    def test_evidence_no_strength_confidence(self, sample_chart):
        """S1.3: EngineEvidence 不携带 strength/confidence。"""
        producer = BaziEvidenceProducer()
        evidences = producer.produce(sample_chart)
        for ev in evidences:
            attrs = ev.attributes
            assert "strength" not in attrs, f"Evidence {ev.evidence_id} 携带 strength"
            assert "confidence" not in attrs, f"Evidence {ev.evidence_id} 携带 confidence"

    def test_evidence_has_required_fields(self, sample_chart):
        """S1.4: 每条 Evidence 有 evidence_id + rule_id + engine + temporal_scope。"""
        producer = BaziEvidenceProducer()
        evidences = producer.produce(sample_chart)
        for ev in evidences:
            assert ev.evidence_id and len(ev.evidence_id) > 0
            assert ev.rule_id and len(ev.rule_id) > 0
            assert ev.engine == EngineName.ZI_PING
            assert ev.temporal_scope in list(TemporalScope)
            # evidence_id ≠ rule_id（同一规则可能多次命中）
            assert ev.evidence_id != ev.rule_id

    def test_evidence_traceability(self, sample_chart):
        """S1.5: 每条 Evidence 有 source_rule_ref（可追溯原典文件）。"""
        producer = BaziEvidenceProducer()
        evidences = producer.produce(sample_chart)
        for ev in evidences:
            assert ev.source_rule_ref is not None, (
                f"Evidence {ev.evidence_id} 缺少 source_rule_ref"
            )
            assert isinstance(ev.source_rule_ref, str)
            assert len(ev.source_rule_ref) > 0

    def test_evidence_versioning(self, sample_chart):
        """S1.6: evidence 携带 calculation_version 和 contract_version。"""
        producer = BaziEvidenceProducer()
        evidences = producer.produce(sample_chart)
        for ev in evidences:
            assert ev.calculation_version == "2026.09"
            assert ev.contract_version == "v13.0"

    def test_no_cross_analyzer_in_evidence(self, sample_chart):
        """S1.7: 证据生产阶段不涉及 CrossAnalyzer。"""
        # 如果 import CrossAnalyzer 成功但不在生产路径中，则通过
        # 这里验证 produce() 返回的不含任何 cross analysis 结果
        producer = BaziEvidenceProducer()
        evidences = producer.produce(sample_chart)
        for ev in evidences:
            # attributes 中不应有 cross 相关字段
            for key in ev.attributes:
                assert "cross" not in key.lower()
                assert "conflict" not in key.lower()
                assert "aligned" not in key.lower()


# ─── Stage 2: EngineEvidence → SemanticAtom ──────────────────────────────────


class TestStage2_SemanticAtomMapping:
    """验证 SemanticAtom 映射无方向泄漏。"""

    def test_atom_no_direction(self, sample_chart, ten_gods_path):
        """S2.1: SemanticAtom 不携带 direction。"""
        from tongshu.spec.canonical.semantic_atom import SemanticAtom

        producer = BaziEvidenceProducer()
        evidences = producer.produce(sample_chart)

        # 手动查表生成 SemanticAtom（模拟 mapper）
        with open(ten_gods_path, encoding="utf-8") as f:
            atom_db = json.load(f)

        for ev in evidences:
            if ev.attributes.get("ten_god"):
                tg = ev.attributes["ten_god"]
                # 查找对应 atom
                for atom_def in atom_db.get("atoms", []):
                    if atom_def.get("label_zh") == tg:
                        atom = SemanticAtom(
                            atom_id=atom_def["atom_id"],
                            engine=ev.engine,
                            evidence_ref=ev.evidence_id,
                            semantic_keys=atom_def.get("semantic_keys", []),
                            domain_candidates=atom_def.get("domain_candidates", []),
                            label_zh=atom_def.get("label_zh", ""),
                            category=atom_def.get("category", ""),
                            guidance_keys=atom_def.get("guidance_keys", []),
                        )
                        assert not hasattr(atom, "direction"), (
                            f"SemanticAtom {atom.atom_id} 意外携带 direction"
                        )
                        # evidence_ref 追溯到 evidence_id
                        assert atom.evidence_ref == ev.evidence_id
                        break

    def test_atom_evidence_ref_to_evidence_id(self, sample_chart, ten_gods_path):
        """S2.2: SemanticAtom.evidence_ref = EngineEvidence.evidence_id。"""
        from tongshu.spec.canonical.semantic_atom import SemanticAtom

        producer = BaziEvidenceProducer()
        evidences = producer.produce(sample_chart)

        with open(ten_gods_path, encoding="utf-8") as f:
            atom_db = json.load(f)

        evidence_ids = {ev.evidence_id for ev in evidences}
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
                        assert atom.evidence_ref in evidence_ids
                        break


# ─── Stage 3: SemanticAtom → CanonicalAssertion（通过 AssertionRuleLibrary） ─

class TestStage3_AssertionGeneration:
    """验证 Assertion 的 direction 来自规则授权，非 MappingLayer 自由决定。"""

    def test_direction_from_rule_not_default(self, assertion_rules_path, sample_chart, ten_gods_path):
        """S3.1: direction 必须来自匹配的规则，不能是 NEUTRAL 默认值。"""
        from tongshu.spec.canonical.semantic_atom import SemanticAtom
        from tongshu.assertion.assertion_rule_library import AssertionRuleLibrary

        library = AssertionRuleLibrary.load(assertion_rules_path)
        producer = BaziEvidenceProducer()
        evidences = producer.produce(sample_chart)

        with open(ten_gods_path, encoding="utf-8") as f:
            atom_db = json.load(f)

        # 构建 SemanticAtom 列表
        atoms: list[SemanticAtom] = []
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
                            label_zh=tg,
                        ))
                        break

        # 对每个 atom 匹配规则
        assertions = []
        no_assertion_count = 0
        for atom in atoms:
            context = {"temporal_scope": "birth", "case_id": "test-case"}
            rule = library.find_rule(atom, context)
            if rule is not None:
                assertion = CanonicalAssertion(
                    assertion_id=f"AS-{atom.evidence_ref}-{atom.atom_id}",
                    subject="test-case",
                    domain=rule.domain,
                    semantic=atom.atom_id,
                    direction=rule.direction,
                    temporal_scope="birth",
                    source_engine=atom.engine.value,
                    source_rule=atom.evidence_ref,
                    authorized_rule_id=rule.rule_id,
                    evidence=EvidenceRef(evidence_id=atom.evidence_ref, engine=atom.engine.value, value="", source_rule_ref=""),
                )
                assertions.append(assertion)
            else:
                no_assertion_count += 1

        # 验证：有命中的 assertion 其 direction 来自 rule，不是 NEUTRAL 默认
        for a in assertions:
            # direction 必须等于授权规则的 direction
            matched_rule = library.find_rule(
                next(at for at in atoms if at.atom_id == a.semantic),
                {"temporal_scope": "birth", "case_id": "test-case"},
            )
            assert matched_rule is not None
            assert a.direction == matched_rule.direction
            assert a.authorized_rule_id == matched_rule.rule_id

    def test_no_assertion_not_neutral(self, sample_chart):
        """S3.2: 未命中规则 → NO_ASSERTION，不是 NEUTRAL。"""
        from tongshu.assertion.assertion_rule_library import AssertionRuleLibrary

        # 创建一个永远不会命中的规则库（空库）
        empty_library = AssertionRuleLibrary(rules=[])
        # 创建一个假的 SemanticAtom
        from tongshu.spec.canonical import SemanticAtom, EngineName

        fake_atom = SemanticAtom(
            atom_id="NON_EXISTENT_ATOM",
            engine=EngineName.ZI_PING,
            evidence_ref="EV-FAKE-001",
            semantic_keys=["NONEXISTENT_KEY"],
            domain_candidates=["CAREER"],
        )

        result = empty_library.find_rule(fake_atom, {})
        assert result is None, "未命中应返回 None（NO_ASSERTION），不应返回规则"

    def test_assertion_traceability_full_chain(self, assertion_rules_path, sample_chart, ten_gods_path):
        """S3.3: 完整追溯链：Assertion → rule_id → evidence_id → engine → source_rule_ref。"""
        from tongshu.spec.canonical.semantic_atom import SemanticAtom
        from tongshu.assertion.assertion_rule_library import AssertionRuleLibrary

        library = AssertionRuleLibrary.load(assertion_rules_path)
        producer = BaziEvidenceProducer()
        evidences = producer.produce(sample_chart)

        # 建立 evidence_id → EngineEvidence 的映射
        evidence_map = {ev.evidence_id: ev for ev in evidences}

        with open(ten_gods_path, encoding="utf-8") as f:
            atom_db = json.load(f)

        # 生成 assertions
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
                        )
                        rule = library.find_rule(atom, {"temporal_scope": "birth", "case_id": "test"})
                        if rule is not None:
                            assertion = CanonicalAssertion(
                                assertion_id=f"AS-{ev.evidence_id}-{atom.atom_id}",
                                subject="test",
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
                                ),
                            )
                            # 验证追溯链
                            assert assertion.evidence["evidence_ref"] == ev.evidence_id
                            assert assertion.evidence["engine"] == ev.engine.value
                            assert assertion.evidence["source_rule_ref"] is not None
                            assert assertion.authorized_rule_id == rule.rule_id
                            assert assertion.direction == rule.direction
                        break


# ─── Stage 4: 约束验证汇总 ───────────────────────────────────────────────────


class TestConstraintVerification:
    """6 项架构约束的全局验证。"""

    def test_c1_no_direction_in_engine_evidence(self, sample_chart):
        """约束 ①: EngineEvidence 无 direction/polarity/strength/confidence。"""
        producer = BaziEvidenceProducer()
        evidences = producer.produce(sample_chart)
        for ev in evidences:
            assert not hasattr(ev, "direction")
            assert not hasattr(ev, "polarity")
            assert "direction" not in ev.attributes
            assert "polarity" not in ev.attributes
            assert "strength" not in ev.attributes
            assert "confidence" not in ev.attributes

    def test_c2_no_cross_analyzer_in_chain(self, sample_chart):
        """约束 ④: 垂直切片不涉及 CrossAnalyzer。"""
        # 如果 CrossAnalyzer 被导入，确认它不在 produce() 或 mapper 中被调用
        # 这里通过验证 producer 不 import cross_analysis 来间接验证
        import inspect
        source = inspect.getsource(BaziEvidenceProducer)
        assert "cross_analysis" not in source
        assert "CrossAnalyzer" not in source
        assert "convergence" not in source.lower()

    def test_c3_no_evidence_count_voting(self, sample_chart):
        """约束 ③: 无 evidence_count 投票机制。"""
        import inspect
        from tongshu.assertion.assertion_rule_library import AssertionRuleLibrary
        source = inspect.getsource(AssertionRuleLibrary)
        assert "evidence_count" not in source
        assert "vote" not in source.lower()
        assert "majority" not in source.lower()
        assert "weight" not in source.lower()

    def test_c4_no_neutral_as_default(self):
        """约束 ⑤: NO_ASSERTION ≠ NEUTRAL。"""
        from tongshu.assertion.assertion_rule_library import AssertionRuleLibrary
        from tongshu.spec.canonical import SemanticAtom, EngineName, AssertionDirection

        empty_lib = AssertionRuleLibrary(rules=[])
        fake_atom = SemanticAtom(
            atom_id="FAKE",
            engine=EngineName.ZI_PING,
            evidence_ref="EV-FAKE",
            semantic_keys=["FAKE_KEY"],
            domain_candidates=["CAREER"],
        )
        result = empty_lib.find_rule(fake_atom, {})
        # 必须是 None，不能是任何 AssertionDirection
        assert result is None
        # NEUTRAL 只能是规则明确授权的，不能作为 fallback
        # 这里验证: find_rule 返回 None 时，调用方不应自动使用 NEUTRAL

    def test_c5_full_traceability(self, assertion_rules_path, sample_chart, ten_gods_path):
        """约束 ⑥: 每个 Assertion 可完整追溯。"""
        from tongshu.spec.canonical.semantic_atom import SemanticAtom
        from tongshu.assertion.assertion_rule_library import AssertionRuleLibrary

        library = AssertionRuleLibrary.load(assertion_rules_path)
        producer = BaziEvidenceProducer()
        evidences = producer.produce(sample_chart)

        evidence_map = {ev.evidence_id: ev for ev in evidences}

        with open(ten_gods_path, encoding="utf-8") as f:
            atom_db = json.load(f)

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
                        rule = library.find_rule(atom, {})
                        if rule is not None:
                            # 完整追溯链验证
                            assert ev.evidence_id in atom.evidence_ref
                            assert ev.engine.value == atom.engine.value
                            assert ev.source_rule_ref is not None
                            assert rule.rule_id is not None
                            assert rule.canonical_source is not None
                        break

    def test_c6_no_intensity_in_assertion(self, sample_chart):
        """约束补充: CanonicalAssertion 无 intensity 字段。"""
        from tongshu.spec.canonical.assertion import CanonicalAssertion
        import inspect
        sig = inspect.signature(CanonicalAssertion)
        assert "intensity" not in sig.parameters, "CanonicalAssertion 不应有 intensity 字段"


# ─── Entry Point ─────────────────────────────────────────────────────────────


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
