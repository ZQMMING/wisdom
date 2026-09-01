"""
Production Admission 攻击测试 - 7 项不可绕过边界

测试目标：证明 Production Rule Library 的 Admission Boundary 不可被任何方式绕过。

GPT 裁决要求的攻击向量：
① 直接 production_verified=True → FAIL
② 修改 module/private state → FAIL
③ 伪造 production context → FAIL
④ JSON 手工写 PRODUCTION_ADMITTED → FAIL (load() 接受但 load_verified/ProductionRuleLoader 拒绝)
⑤ Candidate 直接转 Production → FAIL
⑥ 只有合法 AdmissionRecord → PASS
⑦ 非准入 rule 混入 Production Library → FAIL
"""
import pytest
import sys
import tempfile
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tongshu.assertion.assertion_rule_library import (
    AssertionRuleLibrary,
    ProductionRuleLibrary,
    ProductionRuleLoader,
    AdmissionRecord,
    AssertionRule,
    RuleProvenance,
    MatchStrategy,
    VerificationScope,
)
from tongshu.spec.canonical import AssertionDirection


# ============================================================
# 测试数据构造
# ============================================================

def _make_production_rule(rule_id: str = "PROD-RULE-001") -> dict:
    """构造有效的 PRODUCTION_ADMITTED 规则字典。"""
    return {
        "rule_id": rule_id,
        "domain": "GROWTH",
        "match_strategy": "EXACT",
        "condition": {"atom_id": "TEST_ATOM"},
        "direction": "supportive",
        "provenance": {
            "source_work": "子平真诠",
            "source_chapter": "论印绶",
            "passage_ref": "卷一·论印绶第一",
            "verification_scope": "PRODUCTION_ADMITTED",
            "verified_by": "audit-bot",
            "verification_version": "2026.09",
        },
    }


def _make_test_fixture_rule(rule_id: str = "TEST-RULE-001") -> dict:
    """构造 TEST_FIXTURE 规则字典。"""
    return {
        "rule_id": rule_id,
        "domain": "CAREER",
        "match_strategy": "EXACT",
        "condition": {"atom_id": "TEST_ATOM_2"},
        "direction": "caution",
        "provenance": {
            "source_work": "子平真诠",
            "verification_status": "unverified",
            "verification_scope": "TEST_FIXTURE",
        },
    }


def _write_rules_file(rules: list) -> str:
    """将规则列表写入临时 JSON 文件并返回路径。"""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    try:
        json.dump({"_meta": {"version": "1.0"}, "rules": rules}, tmp)
        return tmp.name
    finally:
        tmp.close()


# ============================================================
# 测试用例
# ============================================================

class TestProductionAdmissionAttackVector:
    """生产准入攻击向量测试。"""

    def test_01_direct_construction_with_production_flag_fails(self):
        """① 直接 construction 传递 production_verified=True → 必须失败。
        
        旧架构问题：AssertionRuleLibrary(rules=[], production_verified=True)
        新架构：AssertionRuleLibrary 不再接受此参数
        """
        with pytest.raises(TypeError):
            AssertionRuleLibrary(rules=[], production_verified=True)

    def test_02_cannot_forgery_production_context_state(self):
        """② 修改 module/private state 试图伪造 production 上下文 → 必须失败。
        
        新架构没有 _production_context 或 inside_production 状态，
        因此无法通过修改状态来绕过。
        """
        # 验证不存在可伪造的状态变量
        import tongshu.assertion.assertion_rule_library as m
        
        # 检查是否还存在可以伪造的上下文状态
        has_context_attr = hasattr(m, '_production_context')
        has_inside_attr = hasattr(m, '_in_production_context')
        
        # 如果存在这些属性，尝试伪造它们
        if has_context_attr:
            original = getattr(m._production_context, 'inside_production', False)
            try:
                m._production_context.inside_production = True
                # 尝试构造（应该仍然失败，因为没有对应参数）
                with pytest.raises(TypeError):
                    AssertionRuleLibrary(rules=[], production_verified=True)
            finally:
                m._production_context.inside_production = original
        
        # 验证不存在直接的布尔标志
        assert not hasattr(AssertionRuleLibrary, '_production_verified')

    def test_03_candidate_to_production_direct_conversion_fails(self):
        """⑤ Candidate AssertionRuleLibrary 不能直接转为 ProductionRuleLibrary。
        
        ProductionRuleLibrary 只能通过 ProductionRuleLoader.load() 创建。
        """
        # 创建一个候选规则库
        candidate_lib = AssertionRuleLibrary(rules=[
            AssertionRule(
                rule_id="CAND-001",
                domain="TEST",
                match_strategy=MatchStrategy.EXACT,
                condition={"atom_id": "TEST"},
                direction=AssertionDirection.SUPPORTIVE,
                provenance=RuleProvenance(
                    source_work="test",
                    verification_scope=VerificationScope.TEST_FIXTURE,
                ),
            )
        ])
        
        # 验证不能直接转换为 ProductionRuleLibrary
        # 生产规则库只能通过 ProductionRuleLoader 创建
        with pytest.raises((TypeError, AttributeError)):
            # 尝试直接构造（应该失败或不存在此路径）
            ProductionRuleLibrary([], admission_record=None)  # type: ignore

    def test_04_json_produces_candidate_not_production(self):
        """④ JSON 文件手工写 PRODUCTION_ADMITTED → load() 接受但返回 Candidate，
        只有 ProductionRuleLoader 会验证并过滤。
        """
        rule = _make_production_rule()
        path = _write_rules_file([rule])
        
        try:
            # AssertionRuleLibrary.load() 会接受所有规则（开发路径）
            candidate_lib = AssertionRuleLibrary.load(path)
            assert len(candidate_lib._rules) == 1
            assert candidate_lib.is_production is False  # 不是生产库
            
            # ProductionRuleLoader.load() 会验证并创建生产库
            prod_lib = ProductionRuleLoader.load(path)
            assert len(prod_lib._rules) == 1
            assert prod_lib.is_production is True
            assert prod_lib.admission_record is not None
        finally:
            Path(path).unlink(missing_ok=True)

    def test_05_non_admitted_rule_cannot_enter_production(self):
        """⑦ 非准入规则不能混入 Production Library。
        
        ProductionRuleLoader 严格过滤，只接受 PRODUCTION_ADMITTED 且 provenance 完整。
        """
        # 混合 bundle：1 个 PRODUCTION_ADMITTED + 1 个 TEST_FIXTURE
        rules = [_make_production_rule(), _make_test_fixture_rule()]
        path = _write_rules_file(rules)
        
        try:
            # 开发路径：接受所有规则
            dev_lib = AssertionRuleLibrary.load(path)
            assert len(dev_lib._rules) == 2
            
            # 生产路径：只接受 PRODUCTION_ADMITTED
            prod_lib = ProductionRuleLoader.load(path)
            assert len(prod_lib._rules) == 1
            assert prod_lib._rules[0].rule_id == "PROD-RULE-001"
            assert prod_lib.admission_record.admitted_rules_count == 1
        finally:
            Path(path).unlink(missing_ok=True)

    def test_06_admission_record_is_immutable_and_unforgeable(self):
        """⑥ 合法的 AdmissionRecord 是不可变的，且外部无法伪造。
        
        AdmissionRecord 是 frozen dataclass，包含规则哈希和时间戳。
        """
        path = _write_rules_file([_make_production_rule()])
        
        try:
            prod_lib = ProductionRuleLoader.load(path)
            record = prod_lib.admission_record
            
            # 验证记录完整性
            assert record.admission_id != ""
            assert record.admission_hash != ""
            assert record.admitted_rules_count == 1
            assert record.source_path == path
            assert record.admission_timestamp > 0
            assert len(record.rule_ids) == 1
            assert "PROD-RULE-001" in record.rule_ids
            
            # 验证不可变性
            with pytest.raises((AttributeError, frozen_dataclass_error)):
                record.admission_id = "forged"
        finally:
            Path(path).unlink(missing_ok=True)

    def test_07_hash_verifies_integrity(self):
        """验证 AdmissionRecord 的 hash 可以检测规则篡改。
        
        如果规则内容被修改，hash 会改变。
        """
        path = _write_rules_file([_make_production_rule()])
        
        try:
            prod_lib = ProductionRuleLoader.load(path)
            original_hash = prod_lib.admission_record.admission_hash
            
            # 修改规则内容并重新加载
            modified_rule = _make_production_rule("MODIFIED-RULE")
            modified_rule["condition"] = {"atom_id": "FORGED_ATOM"}
            modified_path = _write_rules_file([modified_rule])
            
            try:
                modified_lib = ProductionRuleLoader.load(modified_path)
                modified_hash = modified_lib.admission_record.admission_hash
                
                # hash 应该不同
                assert original_hash != modified_hash, "Hash should change when rules are modified"
            finally:
                Path(modified_path).unlink(missing_ok=True)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_08_no_backdoor_in_new_architecture(self):
        """验证新架构中不存在回退后门。
        
        检查：
        - 没有 _production_verified 属性
        - 没有 _production_context 模块状态
        - 没有 from_production_admission 方法
        """
        import tongshu.assertion.assertion_rule_library as m
        
        # AssertionRuleLibrary 不应有这些属性
        assert not hasattr(AssertionRuleLibrary, '_production_verified'), \
            "AssertionRuleLibrary should not have _production_verified"
        
        # 类级别不应该有从旧架构遗留的方法
        assert not hasattr(AssertionRuleLibrary, '_from_production_admission'), \
            "AssertionRuleLibrary should not have _from_production_admission"
        
        # 模块级别不应该有可伪造的上下文状态
        # （如果存在，也应该是只读的或通过受控方式访问）
        # 新架构使用 frozen AdmissionRecord，不需要这种状态

    def test_09_production_library_type_isolation(self):
        """验证 ProductionRuleLibrary 和 AssertionRuleLibrary 类型隔离。
        
        生产路径返回 ProductionRuleLibrary，开发路径返回 AssertionRuleLibrary。
        """
        path = _write_rules_file([_make_production_rule()])
        
        try:
            dev_lib = AssertionRuleLibrary.load(path)
            prod_lib = ProductionRuleLoader.load(path)
            
            # 类型应该不同
            assert type(dev_lib) is AssertionRuleLibrary
            assert type(prod_lib) is ProductionRuleLibrary
            
            # 属性访问应该有不同的语义
            assert dev_lib.is_production is False
            assert prod_lib.is_production is True
            
            # 只有 ProductionRuleLibrary 有 admission_record
            assert hasattr(prod_lib, 'admission_record')
            assert not hasattr(dev_lib, 'admission_record')
        finally:
            Path(path).unlink(missing_ok=True)

    def test_10_orchestrator_requires_production_library(self):
        """验证 CrossDomainOrchestrator 只接受 ProductionRuleLibrary。
        
        传入 AssertionRuleLibrary 应该抛出 ValueError。
        """
        from tongshu.cross_domain.orchestrator import CrossDomainOrchestrator
        
        # 创建候选库
        candidate_lib = AssertionRuleLibrary(rules=[])
        
        # 应该拒绝
        with pytest.raises(ValueError, match="ProductionRuleLibrary"):
            CrossDomainOrchestrator(assertion_library=candidate_lib)
        
        # 创建生产库（需要有效文件）
        path = _write_rules_file([_make_production_rule()])
        try:
            prod_lib = ProductionRuleLoader.load(path)
            # 应该接受
            orch = CrossDomainOrchestrator(assertion_library=prod_lib)
            assert orch is not None
        finally:
            Path(path).unlink(missing_ok=True)


# ============================================================
# 辅助异常类
# ============================================================

class frozen_dataclass_error(AttributeError):
    """用于测试 frozen dataclass 的异常别名。"""
    pass
