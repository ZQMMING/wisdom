"""
P0-① CanonicalState 单元测试

验证 CanonicalState 数据结构的完整性、一致性和治理约束。
"""

import pytest
from tongshu.canonical.state import (
    CanonicalState,
    Fact,
    Relation,
    ClassicalState,
    Qualifier,
    UnresolvedReason,
    Provenance,
    FactType,
    RelationType,
    StateAuthorizationLevel,
    StateStatus,
    OverallState,
    QualifierType,
)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def sample_facts():
    """示例 L1 事实"""
    return [
        Fact(
            fact_id="F-001",
            fact_type=FactType.HEAVENLY_STEM,
            subject="甲",
            value="甲木",
            position="day",
        ),
        Fact(
            fact_id="F-002",
            fact_type=FactType.EARTHLY_BRANCH,
            subject="亥",
            value="亥水",
            position="month",
        ),
        Fact(
            fact_id="F-003",
            fact_type=FactType.HIDDEN_STEM,
            subject="亥",
            value="甲",
            position="month",
            metadata={"layer": "本气"},
        ),
    ]


@pytest.fixture
def sample_relations():
    """示例 L1 关系"""
    return [
        Relation(
            relation_id="R-001",
            relation_type=RelationType.GEN,
            subject="亥中甲",
            object="甲",
            relation="通根",
            position="month",
            source_facts=["F-001", "F-003"],
        ),
    ]


@pytest.fixture
def sample_provenance():
    """示例溯源"""
    return Provenance(
        state_id="DTS-WS-005",
        classic="滴天髓阐微",
        chapter="十七、衰旺",
        source_text="是故日干不论月令休囚，只要四柱有根，便能受财官食神而当伤官七杀。",
        source_span="任氏曰",
        text_type="COMMENTARY",
        author="任铁樵",
        primitive_id="DTS-WS-005",
        fact_ids=["F-001", "F-003"],
        relation_ids=["R-001"],
        authorization_level=StateAuthorizationLevel.CLASSICAL_EXPLICIT,
        verification_status="verified",
    )


@pytest.fixture
def sample_classical_state(sample_provenance):
    """示例经典状态"""
    return ClassicalState(
        state_id="DTS-WS-005",
        name="有根",
        domain="wangshuai",
        classic="滴天髓阐微",
        value="ROOT_PRESENT",
        subject="甲木",
        status=StateStatus.CONFIRMED,
        authorization_level=StateAuthorizationLevel.CLASSICAL_EXPLICIT,
        provenance=sample_provenance,
        position="month",
    )


@pytest.fixture
def sample_qualifier():
    """示例限定条件"""
    return Qualifier(
        qualifier_id="Q-001",
        qualifier_type=QualifierType.BLOCKING,
        target_state="DTS-WS-005",
        condition="得时不旺",
        description="春木虽强，金太重而木亦危",
        source="滴天髓阐微·十七、衰旺",
        authorization_level=StateAuthorizationLevel.CLASSICAL_EXPLICIT,
    )


@pytest.fixture
def sample_unresolved_reason():
    """示例未解决原因"""
    return UnresolvedReason(
        reason_id="UR-001",
        target="overall",
        reason="五部经典综合辨证规则尚未获得原典授权",
        category="原典未授权",
        blocking_items=["DTS-STRENGTH-001 组合逻辑未证明", "五部经典跨体系综合规则未定义"],
        next_steps=["P0-2.9-F DTS旺衰Primitive关系层审计", "五部经典各自辨证规则原典审计"],
    )


@pytest.fixture
def sample_canonical_state(sample_facts, sample_relations, sample_classical_state, sample_qualifier, sample_unresolved_reason):
    """示例完整 CanonicalState"""
    return CanonicalState(
        state_id="CS-001",
        chart_id="CHART-001",
        facts=sample_facts,
        relations=sample_relations,
        classical_states=[sample_classical_state],
        qualifiers=[sample_qualifier],
        unresolved_reasons=[sample_unresolved_reason],
        overall_state=OverallState.UNRESOLVED,
    )


# ============================================================
# 测试：基本结构
# ============================================================

class TestCanonicalStateStructure:
    """测试 CanonicalState 基本结构"""

    def test_create_empty_state(self):
        """创建空状态"""
        state = CanonicalState(state_id="CS-001", chart_id="CHART-001")
        assert state.state_id == "CS-001"
        assert state.chart_id == "CHART-001"
        assert state.facts == []
        assert state.relations == []
        assert state.classical_states == []
        assert state.qualifiers == []
        assert state.unresolved_reasons == []
        assert state.overall_state == OverallState.UNRESOLVED

    def test_default_overall_state_is_unresolved(self):
        """整体状态默认 UNRESOLVED"""
        state = CanonicalState(state_id="CS-001", chart_id="CHART-001")
        assert state.overall_state == OverallState.UNRESOLVED
        assert state.overall_state_reason is None

    def test_facts_are_frozen(self):
        """Fact 是不可变的"""
        fact = Fact(fact_id="F-001", fact_type=FactType.HEAVENLY_STEM, subject="甲", value="甲木")
        with pytest.raises(Exception):
            fact.value = "乙木"  # type: ignore

    def test_relations_are_frozen(self):
        """Relation 是不可变的"""
        rel = Relation(
            relation_id="R-001", relation_type=RelationType.GEN,
            subject="壬", object="甲", relation="水生木",
        )
        with pytest.raises(Exception):
            rel.relation = "木克土"  # type: ignore


# ============================================================
# 测试：查询方法
# ============================================================

class TestCanonicalStateQueries:
    """测试 CanonicalState 查询方法"""

    def test_get_facts_by_type(self, sample_canonical_state):
        """按类型获取事实"""
        hidden_stems = sample_canonical_state.get_facts_by_type(FactType.HIDDEN_STEM)
        assert len(hidden_stems) == 1
        assert hidden_stems[0].fact_id == "F-003"

    def test_get_relations_by_type(self, sample_canonical_state):
        """按类型获取关系"""
        gen_relations = sample_canonical_state.get_relations_by_type(RelationType.GEN)
        assert len(gen_relations) == 1
        assert gen_relations[0].relation_id == "R-001"

    def test_get_states_by_domain(self, sample_canonical_state):
        """按辨证域获取状态"""
        wangshuai_states = sample_canonical_state.get_states_by_domain("wangshuai")
        assert len(wangshuai_states) == 1
        assert wangshuai_states[0].state_id == "DTS-WS-005"

    def test_get_states_by_classic(self, sample_canonical_state):
        """按经典获取状态"""
        dts_states = sample_canonical_state.get_states_by_classic("滴天髓阐微")
        assert len(dts_states) == 1

    def test_get_state_by_id(self, sample_canonical_state):
        """按ID获取状态"""
        state = sample_canonical_state.get_state_by_id("DTS-WS-005")
        assert state is not None
        assert state.name == "有根"

    def test_get_state_by_id_not_found(self, sample_canonical_state):
        """按ID获取不存在的状态"""
        state = sample_canonical_state.get_state_by_id("NOT-EXIST")
        assert state is None

    def test_get_qualifiers_for_state(self, sample_canonical_state):
        """获取某个状态的限定条件"""
        qualifiers = sample_canonical_state.get_qualifiers_for_state("DTS-WS-005")
        assert len(qualifiers) == 1
        assert qualifiers[0].qualifier_id == "Q-001"

    def test_get_unresolved_for_target(self, sample_canonical_state):
        """获取某个目标的未解决原因"""
        reasons = sample_canonical_state.get_unresolved_for_target("overall")
        assert len(reasons) == 1
        assert reasons[0].reason_id == "UR-001"


# ============================================================
# 测试：验证方法（治理约束）
# ============================================================

class TestCanonicalStateValidation:
    """测试 CanonicalState 验证方法（治理约束）"""

    def test_valid_state_passes_validation(self, sample_canonical_state):
        """合法状态通过验证"""
        errors = sample_canonical_state.validate()
        assert errors == []

    def test_state_without_provenance_fails(self):
        """缺少 Provenance 的状态验证失败"""
        bad_state = ClassicalState(
            state_id="BAD-001",
            name="测试",
            domain="test",
            classic="测试经典",
            value="TEST",
            subject="测试",
            status=StateStatus.CANDIDATE,
            authorization_level=StateAuthorizationLevel.SOURCE_UNVERIFIED,
            provenance=Provenance(state_id="BAD-001"),  # 空provenance
        )
        cs = CanonicalState(
            state_id="CS-BAD",
            chart_id="CHART-BAD",
            classical_states=[bad_state],
        )
        errors = cs.validate()
        assert any("缺少来源事实/关系" in e for e in errors)

    def test_overall_state_not_unresolved_without_reason_fails(self):
        """整体状态不是 UNRESOLVED 但缺少原因，验证失败"""
        cs = CanonicalState(
            state_id="CS-BAD",
            chart_id="CHART-BAD",
            overall_state=OverallState.CANDIDATE_STRONG,
            overall_state_reason=None,
        )
        errors = cs.validate()
        assert any("整体状态不是 UNRESOLVED" in e for e in errors)

    def test_overall_state_not_unresolved_with_reason_passes(self):
        """整体状态不是 UNRESOLVED 但有原因，验证通过"""
        cs = CanonicalState(
            state_id="CS-OK",
            chart_id="CHART-OK",
            overall_state=OverallState.CANDIDATE_STRONG,
            overall_state_reason="测试原因",
        )
        errors = cs.validate()
        # 可能有其他错误（如缺少states），但不应该有整体状态相关错误
        assert not any("整体状态不是 UNRESOLVED" in e for e in errors)

    def test_qualifier_target_not_exist_fails(self):
        """Qualifier 的 target_state 不存在，验证失败"""
        bad_qualifier = Qualifier(
            qualifier_id="Q-BAD",
            qualifier_type=QualifierType.BLOCKING,
            target_state="NOT-EXIST",
            condition="测试",
        )
        cs = CanonicalState(
            state_id="CS-BAD",
            chart_id="CHART-BAD",
            qualifiers=[bad_qualifier],
        )
        errors = cs.validate()
        assert any("target_state" in e and "NOT-EXIST" in e for e in errors)

    def test_forbidden_strength_score_in_metadata_fails(self):
        """metadata 中包含 strength_score，验证失败"""
        cs = CanonicalState(
            state_id="CS-BAD",
            chart_id="CHART-BAD",
            metadata={"strength_score": 85},
        )
        errors = cs.validate()
        assert any("strength_score" in e for e in errors)

    def test_forbidden_root_score_in_state_metadata_fails(self):
        """State metadata 中包含 root_score，验证失败"""
        bad_state = ClassicalState(
            state_id="BAD-001",
            name="测试",
            domain="test",
            classic="测试",
            value="TEST",
            subject="测试",
            status=StateStatus.CANDIDATE,
            authorization_level=StateAuthorizationLevel.SOURCE_UNVERIFIED,
            provenance=Provenance(state_id="BAD-001", fact_ids=["F-001"]),
            metadata={"root_score": 70},
        )
        cs = CanonicalState(
            state_id="CS-BAD",
            chart_id="CHART-BAD",
            classical_states=[bad_state],
        )
        errors = cs.validate()
        assert any("root_score" in e for e in errors)


# ============================================================
# 测试：序列化
# ============================================================

class TestCanonicalStateSerialization:
    """测试 CanonicalState 序列化"""

    def test_to_dict_contains_all_fields(self, sample_canonical_state):
        """to_dict 包含所有字段"""
        d = sample_canonical_state.to_dict()
        assert "state_id" in d
        assert "chart_id" in d
        assert "facts" in d
        assert "relations" in d
        assert "classical_states" in d
        assert "qualifiers" in d
        assert "unresolved_reasons" in d
        assert "overall_state" in d
        assert "validation_errors" in d

    def test_fact_to_dict(self, sample_facts):
        """Fact 序列化"""
        d = sample_facts[0].to_dict()
        assert d["fact_id"] == "F-001"
        assert d["fact_type"] == "heavenly_stem"
        assert d["subject"] == "甲"

    def test_relation_to_dict(self, sample_relations):
        """Relation 序列化"""
        d = sample_relations[0].to_dict()
        assert d["relation_id"] == "R-001"
        assert d["relation_type"] == "gen"
        assert d["relation"] == "通根"

    def test_classical_state_to_dict(self, sample_classical_state):
        """ClassicalState 序列化"""
        d = sample_classical_state.to_dict()
        assert d["state_id"] == "DTS-WS-005"
        assert d["name"] == "有根"
        assert d["domain"] == "wangshuai"
        assert d["status"] == "confirmed"
        assert d["authorization_level"] == "classical_explicit"
        assert "provenance" in d

    def test_provenance_to_dict(self, sample_provenance):
        """Provenance 序列化"""
        d = sample_provenance.to_dict()
        assert d["state_id"] == "DTS-WS-005"
        assert d["classic"] == "滴天髓阐微"
        assert d["authorization_level"] == "classical_explicit"
        assert "fact_ids" in d
        assert "relation_ids" in d

    def test_summary(self, sample_canonical_state):
        """摘要"""
        s = sample_canonical_state.summary()
        assert s["facts_count"] == 3
        assert s["relations_count"] == 1
        assert s["classical_states_count"] == 1
        assert s["qualifiers_count"] == 1
        assert s["unresolved_reasons_count"] == 1
        assert s["overall_state"] == "unresolved"
        assert "wangshuai" in s["domains"]
        assert "滴天髓阐微" in s["classics"]


# ============================================================
# 测试：枚举值
# ============================================================

class TestEnums:
    """测试枚举值"""

    def test_fact_type_values(self):
        """FactType 枚举值"""
        assert FactType.HEAVENLY_STEM.value == "heavenly_stem"
        assert FactType.HIDDEN_STEM.value == "hidden_stem"
        assert FactType.TEN_GOD.value == "ten_god"

    def test_relation_type_values(self):
        """RelationType 枚举值"""
        assert RelationType.SHENG.value == "sheng"
        assert RelationType.KE.value == "ke"
        assert RelationType.GEN.value == "gen"

    def test_state_authorization_level_values(self):
        """StateAuthorizationLevel 枚举值（严格分级）"""
        levels = [
            StateAuthorizationLevel.CLASSICAL_EXPLICIT,
            StateAuthorizationLevel.CLASSICAL_IMPLICIT,
            StateAuthorizationLevel.REASONABLE_HYPOTHESIS,
            StateAuthorizationLevel.ENGINEERING_DERIVED,
            StateAuthorizationLevel.SOURCE_UNVERIFIED,
            StateAuthorizationLevel.NOT_AUTHORIZED,
        ]
        # 确保所有级别都有唯一值
        values = [l.value for l in levels]
        assert len(values) == len(set(values))

    def test_overall_state_default_unresolved(self):
        """OverallState 默认 UNRESOLVED"""
        assert OverallState.UNRESOLVED.value == "unresolved"

    def test_qualifier_type_values(self):
        """QualifierType 枚举值"""
        assert QualifierType.NECESSARY.value == "necessary"
        assert QualifierType.SUFFICIENT.value == "sufficient"
        assert QualifierType.BLOCKING.value == "blocking"
        assert QualifierType.EXCEPTION.value == "exception"


# ============================================================
# 测试：治理原则
# ============================================================

class TestGovernancePrinciples:
    """测试治理原则是否在代码中体现"""

    def test_no_strength_score_in_state(self, sample_classical_state):
        """ClassicalState 不包含 strength_score 字段"""
        d = sample_classical_state.to_dict()
        assert "strength_score" not in d
        assert "root_score" not in d

    def test_no_automatic_overall_derivation(self):
        """不允许自动推导整体状态"""
        # 即使有很多 classical_states，整体状态仍然默认 UNRESOLVED
        states = [
            ClassicalState(
                state_id=f"S-{i}",
                name=f"状态{i}",
                domain="wangshuai",
                classic="测试",
                value=f"V{i}",
                subject="甲木",
                status=StateStatus.CONFIRMED,
                authorization_level=StateAuthorizationLevel.CLASSICAL_EXPLICIT,
                provenance=Provenance(state_id=f"S-{i}", fact_ids=[f"F-{i}"]),
            )
            for i in range(10)
        ]
        cs = CanonicalState(
            state_id="CS-MANY",
            chart_id="CHART-MANY",
            classical_states=states,
        )
        # 即使有10个状态，整体状态仍然是 UNRESOLVED
        assert cs.overall_state == OverallState.UNRESOLVED

    def test_every_state_has_provenance_chain(self, sample_classical_state):
        """每个状态都有溯源链"""
        p = sample_classical_state.provenance
        assert p.fact_ids  # 有来源事实
        assert p.classic  # 有经典来源
        assert p.authorization_level  # 有授权等级

    def test_unresolved_reasons_explicitly_recorded(self, sample_unresolved_reason):
        """未解决原因显式记录"""
        assert sample_unresolved_reason.reason  # 有原因描述
        assert sample_unresolved_reason.category  # 有类别
        assert sample_unresolved_reason.blocking_items  # 有阻断项
        assert sample_unresolved_reason.next_steps  # 有下一步
