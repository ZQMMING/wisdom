"""ZiweiMethodProfile 方法论契约测试"""

import pytest
from src.tongshu.engines.ziwei_method_profile import (
    MethodId,
    RuleType,
    ConfidenceLevel,
    EvidenceRef,
    RuleSpec,
    SiHuaTable,
    ZiweiMethodContract,
    SanheContract,
    ZhongzhouContract,
    FeixingContract,
    QintianContract,
    METHOD_CONTRACTS,
    get_contract,
    list_contracts,
)


class TestMethodId:
    def test_values(self):
        assert MethodId.SANHE.value == "sanhe"
        assert MethodId.ZHONGZHOU.value == "zhongzhou"
        assert MethodId.FEIXING.value == "feixing"
        assert MethodId.QINTIAN.value == "qintian"


class TestEvidenceRef:
    def test_create(self):
        ref = EvidenceRef(
            source_type="classic",
            source_name="紫微斗数全书",
            section="论四化",
            quote="甲廉破武阳",
            verified=True,
        )
        assert ref.source_name == "紫微斗数全书"
        assert ref.verified is True
    
    def test_empty_source_raises(self):
        with pytest.raises(ValueError):
            EvidenceRef(source_type="classic", source_name="", section="", quote="")


class TestRuleSpec:
    def test_create(self):
        rule = RuleSpec(
            rule_id="ZW-PAT-001",
            rule_type=RuleType.PATTERN,
            method_ids=(MethodId.SANHE, MethodId.ZHONGZHOU),
            condition=lambda f: True,
            effect=lambda f: {},
            description="紫微独坐",
            evidence=[
                EvidenceRef(source_type="classic", source_name="紫微斗数全书", section="", quote="", verified=True)
            ],
            confidence=ConfidenceLevel.HIGH,
        )
        assert rule.rule_id == "ZW-PAT-001"
        assert rule.applies_to(MethodId.SANHE)
        assert not rule.applies_to(MethodId.FEIXING)


class TestSiHuaTable:
    def test_classic_get(self):
        table = SiHuaTable(name="classic", description="", data={"甲": ("廉贞", "破军", "武曲", "太阳")})
        assert table.get("甲") == ("廉贞", "破军", "武曲", "太阳")
        assert table.get("丙") is None
    
    def test_zhongzhou_wu_stem(self):
        table = SiHuaTable(name="zhongzhou", description="", data={"戊": ("贪狼", "太阴", "太阳", "天机")})
        assert table.get("戊") == ("贪狼", "太阴", "太阳", "天机")
        assert table.get("戊")[2] == "太阳"  # 科 = 太阳


class TestSanheContract:
    def test_init(self):
        c = SanheContract()
        assert c.method_id == MethodId.SANHE
        assert c.name == "三合派"
    
    def test_sihua_table(self):
        c = SanheContract()
        assert c.sihua_table.name == "classic"
        assert c.sihua_table.get("甲") == ("廉贞", "破军", "武曲", "太阳")
    
    def test_features(self):
        c = SanheContract()
        assert not c.has_self_hua
        assert not c.has_liji_gong
        assert not c.has_liuchangliuqu
        assert c.use_xiaoxian is True
        assert c.empty_palace_policy == "partial"


class TestZhongzhouContract:
    def test_init(self):
        c = ZhongzhouContract()
        assert c.method_id == MethodId.ZHONGZHOU
    
    def test_wu_gan_taiyang_ke(self):
        c = ZhongzhouContract()
        wu = c.sihua_table.get("戊")
        assert wu == ("贪狼", "太阴", "太阳", "天机")
        assert wu[2] == "太阳"  # 科 = 太阳
    
    def test_features(self):
        c = ZhongzhouContract()
        assert c.has_liuchangliuqu is True
        assert c.empty_palace_policy == "full"


class TestFeixingContract:
    def test_init(self):
        c = FeixingContract()
        assert c.method_id == MethodId.FEIXING
    
    def test_no_xiaoxian(self):
        c = FeixingContract()
        assert c.use_xiaoxian is False
    
    def test_self_hua(self):
        c = FeixingContract()
        assert c.has_self_hua is True


class TestQintianContract:
    def test_init(self):
        c = QintianContract()
        assert c.method_id == MethodId.QINTIAN
    
    def test_features(self):
        c = QintianContract()
        assert c.has_self_hua is True
        assert c.has_liji_gong is True
        assert c.use_xiaoxian == "partial"


class TestMethodMapping:
    def test_all_registered(self):
        assert len(METHOD_CONTRACTS) == 4
    
    def test_get_contract(self):
        assert get_contract(MethodId.SANHE) == SanheContract
        assert get_contract(MethodId.FEIXING) == FeixingContract
    
    def test_get_unknown_raises(self):
        with pytest.raises(ValueError):
            get_contract(MethodId("unknown"))
    
    def test_list_contracts(self):
        contracts = list_contracts()
        assert len(contracts) == 4
        methods = [c["method_id"] for c in contracts]
        assert set(methods) == {"sanhe", "zhongzhou", "feixing", "qintian"}


class TestRuleManagement:
    def test_add_and_get_rule(self):
        c = SanheContract()
        rule = RuleSpec(
            rule_id="TEST-001",
            rule_type=RuleType.PATTERN,
            method_ids=(MethodId.SANHE,),
            condition=lambda f: True,
            effect=lambda f: {"test": True},
        )
        c.add_rule(rule)
        assert c.get_rule("TEST-001") == rule
    
    def test_query_rules(self):
        c = SanheContract()
        r1 = RuleSpec(rule_id="R1", rule_type=RuleType.PATTERN, method_ids=(MethodId.SANHE,), condition=lambda f: True, effect=lambda f: {})
        r2 = RuleSpec(rule_id="R2", rule_type=RuleType.SIHUA, method_ids=(MethodId.SANHE,), condition=lambda f: True, effect=lambda f: {})
        c.add_rule(r1)
        c.add_rule(r2)
        
        patterns = c.query_rules(RuleType.PATTERN)
        assert len(patterns) == 1
        assert patterns[0].rule_id == "R1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
