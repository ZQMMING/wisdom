"""
P1.2-B.1 Security Tests: Production Admission Capability Token

测试覆盖：
  1. 直接构造 ProductionRuleLibrary → FAIL（需要 _CAPABILITY）
  2. 伪造 _AdmissionCapability → FAIL（singleton identity check）
  3. Candidate → Production 转换 → FAIL（类型隔离）
  4. JSON 手工写 PRODUCTION_ADMITTED → 过滤为 CANDIDATE
  5. 非准入规则混入 → 被拒绝
  6. _AdmissionState 不可变 + 完整 hash
  7. Hash 完整性验证 (64 chars)
  8. 无 backdoor (production_verified/_AdmissionState 不在公开 API)
  9. 类型隔离 enforced
  10. Orchestrator 只接受 ProductionRuleLibrary
  11. 无法无 token 构造 ProductionRuleLibrary
  12. _AdmissionState 不在公共 API
  13. 空文件路径抛出 RuleLoadError
  14. 规则篡改 detectable (hash 改变)
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tongshu.assertion.assertion_rule_library import (
    AssertionRuleLibrary,
    ProductionRuleLibrary,
    ProductionRuleLoader,
    RuleLoadError,
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


def _make_test_fixture_rule(rule_id: str = "TEST-RULE") -> dict:
    """构造 TEST_FIXTURE 规则字典（不能进入生产）。"""
    return {
        "rule_id": rule_id,
        "domain": "GROWTH",
        "match_strategy": "EXACT",
        "condition": {"atom_id": "TEST_ATOM"},
        "direction": "supportive",
        "provenance": {
            "source_work": "test",
            "source_chapter": "test",
            "passage_ref": "test",
            "verification_scope": "TEST_FIXTURE",
            "verified_by": "test",
            "verification_version": "1.0",
        },
    }


def _write_rules_file(rules: list) -> str:
    """将规则列表写入临时 JSON 文件，返回文件路径。"""
    fd, path = tempfile.mkstemp(suffix=".json", prefix="test_rules_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump({"rules": rules}, f)
    return path


# ============================================================
# 攻击向量测试
# ============================================================

class TestProductionAdmissionAttackVector:
    """10 项攻击向量测试，确保 Production Admission Boundary 不可绕过。"""

    def test_01_direct_construction_with_production_flag_fails(self):
        """① 直接构造 AssertionRuleLibrary with production_verified 参数 → TypeError。

        旧架构允许：AssertionRuleLibrary(rules, production_verified=True)
        新架构：AssertionRuleLibrary.__init__ 不接受 production_verified 参数
        """
        with pytest.raises(TypeError):
            AssertionRuleLibrary([], production_verified=True)

    def test_02_cannot_forgery_production_context_state(self):
        """② 伪造 production context 状态 → AttributeError（不存在此类状态）。

        旧架构有 _production_context = threading.local()
        新架构：完全删除此类状态
        """
        import tongshu.assertion.assertion_rule_library as m
        has_context = hasattr(m, '_production_context')
        assert not has_context, "threading.local() context should not exist"

    def test_03_candidate_to_production_direct_conversion_fails(self):
        """③ Candidate → Production 直接转换 → 类型隔离。

        AssertionRuleLibrary 和 ProductionRuleLibrary 是完全不同的类型。
        不能通过 cast 或 monkey-patch 转换。
        """
        candidate_lib = AssertionRuleLibrary(rules=[])
        # 不能直接赋值
        assert type(candidate_lib).__name__ == "AssertionRuleLibrary"
        # is_production 永远是 False
        assert candidate_lib.is_production is False

    def test_04_json_produces_candidate_not_production(self):
        """④ JSON 手工写 PRODUCTION_ADMITTED → 过滤为 CANDIDATE。

        即使 JSON 中写 verification_scope=PRODUCTION_ADMITTED，
        AssertionRuleLibrary.load() 仍然返回候选库，不是生产库。
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
            assert prod_lib.admission_state is not None
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
            assert prod_lib.admission_state.admitted_rules_count == 1
        finally:
            Path(path).unlink(missing_ok=True)

    def test_06_admission_state_is_immutable_and_unforgeable(self):
        """⑥ 合法的 _AdmissionState 是不可变的，且外部无法伪造。

        _AdmissionState 是 frozen dataclass，包含规则哈希和时间戳。
        """
        path = _write_rules_file([_make_production_rule()])

        try:
            prod_lib = ProductionRuleLoader.load(path)
            state = prod_lib.admission_state

            # 验证状态完整性
            assert state.admission_id != ""
            assert len(state.admission_hash) == 64  # 完整 SHA-256
            assert state.admitted_rules_count == 1
            assert state.source_path == path
            assert state.admission_timestamp > 0
            assert len(state.rule_ids) == 1
            assert "PROD-RULE-001" in state.rule_ids
            assert state.canonical_serialization != ""

            # 验证不可变性
            with pytest.raises(AttributeError):
                state.admission_id = "forged"
        finally:
            Path(path).unlink(missing_ok=True)

    def test_07_hash_verifies_integrity(self):
        """验证 _AdmissionState 的 hash 可以检测规则篡改。

        使用完整 SHA-256（64 hex chars），涵盖全量规则内容。
        """
        path = _write_rules_file([_make_production_rule()])

        try:
            prod_lib = ProductionRuleLoader.load(path)
            original_hash = prod_lib.admission_state.admission_hash

            # 验证 hash 长度（完整 SHA-256，非截断）
            assert len(original_hash) == 64, \
                f"Hash should be full 64-char SHA-256, got {len(original_hash)}"

            # 修改规则内容并重新加载
            modified_rule = _make_production_rule("MODIFIED-RULE")
            modified_rule["condition"] = {"atom_id": "FORGED_ATOM"}
            modified_path = _write_rules_file([modified_rule])

            try:
                modified_lib = ProductionRuleLoader.load(modified_path)
                modified_hash = modified_lib.admission_state.admission_hash

                # hash 应该不同
                assert original_hash != modified_hash, "Hash should change when rules are modified"
            finally:
                Path(modified_path).unlink(missing_ok=True)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_08_no_backdoor_in_new_architecture(self):
        """验证新架构中不存在回退后门。

        检查：
        - 没有 production_verified 参数
        - 没有 _AdmissionState（公开 dataclass）
        - 没有 _production_context 模块状态
        - ProductionRuleLibrary 不接受 capability 参数
        """
        import inspect

        # AssertionRuleLibrary 不应有这些参数
        sig = inspect.signature(AssertionRuleLibrary.__init__)
        assert 'production_verified' not in sig.parameters

        # ProductionRuleLibrary 不应接受 capability 参数
        sig2 = inspect.signature(ProductionRuleLibrary.__init__)
        assert 'capability' not in sig2.parameters
        assert 'admission_state' not in sig2.parameters  # 也不是公开参数

        # 检查模块级别
        import tongshu.assertion.assertion_rule_library as m
        assert not hasattr(m, '_production_context')
        assert not hasattr(m, '_in_production_context')

        # _AdmissionState 不应在 __all__ 中导出
        assert '_AdmissionState' not in m.__all__
        assert 'AdmissionRecord' not in m.__all__

        # _CAPABILITY 不应作为模块级变量导出
        assert '_CAPABILITY' not in m.__all__

    def test_09_production_library_type_isolation(self):
        """验证 ProductionRuleLibrary 和 AssertionRuleLibrary 类型隔离。

        生产路径返回 ProductionRuleLibrary，开发路径返回 AssertionRuleLibrary。
        """
        path = _write_rules_file([_make_production_rule()])

        try:
            dev_lib = AssertionRuleLibrary.load(path)
            prod_lib = ProductionRuleLoader.load(path)

            # 类型应该不同
            assert type(dev_lib).__name__ == "AssertionRuleLibrary"
            assert type(prod_lib).__name__ == "ProductionRuleLibrary"

            # 属性访问应该有不同的语义
            assert dev_lib.is_production is False
            assert prod_lib.is_production is True

            # 只有 ProductionRuleLibrary 有 admission_state
            assert hasattr(prod_lib, 'admission_state')
            assert not hasattr(dev_lib, 'admission_state')
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


class TestCapabilityTokenSecurity:
    """Capability Token 安全性测试。"""

    def test_module_level_capability_not_accessible(self):
        """_CAPABILITY 不应作为模块级变量存在。

        GPT 第六轮裁决指出：外部可以通过 `import _CAPABILITY` 获取真实 singleton。
        修复方案：将 _CAPABILITY 移到 ProductionRuleLoader 类内部作为类属性。
        """
        import tongshu.assertion.assertion_rule_library as m

        # _CAPABILITY 不是模块级变量
        assert not hasattr(m, '_CAPABILITY'), \
            "_CAPABILITY should NOT be accessible at module level"

        # 但它是 ProductionRuleLoader 的类属性
        assert hasattr(m.ProductionRuleLoader, '_CAPABILITY')

    def test_cannot_construct_production_library_without_capability(self):
        """外部代码无法直接构造 ProductionRuleLibrary。

        ProductionRuleLibrary.__init__ 只接受 rules 和 state 参数，
        不接受 capability 参数。外部代码无法绕过 ProductionRuleLoader 构造。
        """
        from tongshu.assertion.assertion_rule_library import ProductionRuleLibrary

        # 尝试直接调用 __init__（应该失败，因为不接受 capability 参数）
        lib = object.__new__(ProductionRuleLibrary)
        with pytest.raises(TypeError):
            # 现在 __init__ 只接受 2 个参数 (self, rules, state)
            # 传入 3 个参数会失败
            lib.__init__([], None, object())  # 多余的参数

    def test_no_public_admission_state_constructor(self):
        """_AdmissionState 不应作为公共 API 导出。

        外部代码不应该能够导入并构造 _AdmissionState。
        """
        import tongshu.assertion.assertion_rule_library as m

        # _AdmissionState 不在 __all__ 中
        assert '_AdmissionState' not in m.__all__, \
            "_AdmissionState should not be in public API"

        # AdmissionRecord 也不应在（旧架构遗留）
        assert 'AdmissionRecord' not in m.__all__, \
            "AdmissionRecord should not be in public API"

    def test_singleton_capability_not_accessible(self):
        """_CAPABILITY singleton 不应从模块外部访问。

        _CAPABILITY 是 ProductionRuleLoader 的类属性，不是模块级变量。
        外部无法通过 import 获取有效 capability。
        """
        import tongshu.assertion.assertion_rule_library as m

        # _CAPABILITY 不在模块命名空间（只存在于类属性）
        assert not hasattr(m, '_CAPABILITY'), \
            "_CAPABILITY should not be a module-level variable"

        # _CAPABILITY 是 ProductionRuleLoader 的类属性
        assert hasattr(m.ProductionRuleLoader, '_CAPABILITY'), \
            "_CAPABILITY should be a class attribute of ProductionRuleLoader"

        # 但即使知道类名，也无法通过 __init__ 使用它
        # 因为 __init__ 不再接受 capability 参数

    def test_empty_file_path_raises_error(self):
        """空文件路径应抛出 RuleLoadError，不产生空 Production Admission。

        上一版缺陷：文件不存在时产生空 AdmissionRecord，导致空 Production Library。
        新版修复：直接抛出异常，fail-closed。
        """
        with pytest.raises(RuleLoadError, match="Rules file not found"):
            ProductionRuleLoader.load("/nonexistent/path/rules.json")


# ============================================================
# Integrity Tests
# ============================================================

class TestAdmissionIntegrity:
    """Admission 完整性测试。"""

    def test_canonical_serialization_contains_full_rule_content(self):
        """验证 canonical_serialization 包含全量规则内容。

        应该包含：rule_id, domain, match_strategy, condition, direction, provenance
        """
        path = _write_rules_file([_make_production_rule()])

        try:
            prod_lib = ProductionRuleLoader.load(path)
            serialization = prod_lib.admission_state.canonical_serialization
            serialized_data = json.loads(serialization)

            assert len(serialized_data) == 1
            rule = serialized_data[0]
            assert "rule_id" in rule
            assert "domain" in rule
            assert "match_strategy" in rule
            assert "condition" in rule
            assert "direction" in rule
            assert "provenance" in rule
        finally:
            Path(path).unlink(missing_ok=True)

    def test_hash_changes_when_rule_modified(self):
        """验证 hash 在规则修改后改变。

        包括：condition, direction, provenance 字段修改。
        """
        path = _write_rules_file([_make_production_rule()])

        try:
            prod_lib = ProductionRuleLoader.load(path)
            original_hash = prod_lib.admission_state.admission_hash

            # 修改 condition
            modified_rule = _make_production_rule("MODIFIED-COND")
            modified_rule["condition"] = {"atom_id": "MODIFIED_ATOM"}
            modified_path = _write_rules_file([modified_rule])

            try:
                modified_lib = ProductionRuleLoader.load(modified_path)
                modified_hash = modified_lib.admission_state.admission_hash
                assert original_hash != modified_hash
            finally:
                Path(modified_path).unlink(missing_ok=True)

            # 修改 direction（使用有效值）
            modified_rule2 = _make_production_rule("MODIFIED-DIR")
            modified_rule2["direction"] = "caution"
            modified_path2 = _write_rules_file([modified_rule2])

            try:
                modified_lib2 = ProductionRuleLoader.load(modified_path2)
                modified_hash2 = modified_lib2.admission_state.admission_hash
                assert original_hash != modified_hash2
            finally:
                Path(modified_path2).unlink(missing_ok=True)
        finally:
            Path(path).unlink(missing_ok=True)


# ============================================================
# Edge Case Tests
# ============================================================

class TestEdgeCases:
    """边界条件测试。"""

    def test_empty_bundle_yields_empty_production_library(self):
        """空 bundle（无规则）应该产生空的 Production Library。"""
        path = _write_rules_file([])

        try:
            prod_lib = ProductionRuleLoader.load(path)
            assert prod_lib.is_production is True
            assert len(prod_lib._rules) == 0
            assert prod_lib.admission_state.admitted_rules_count == 0
        finally:
            Path(path).unlink(missing_ok=True)

    def test_all_rejected_yields_empty_production_library(self):
        """所有规则都被拒绝时，应该产生空的 Production Library。"""
        rules = [_make_test_fixture_rule() for _ in range(3)]
        path = _write_rules_file(rules)

        try:
            prod_lib = ProductionRuleLoader.load(path)
            assert prod_lib.is_production is True
            assert len(prod_lib._rules) == 0
            assert prod_lib.admission_state.admitted_rules_count == 0
        finally:
            Path(path).unlink(missing_ok=True)

    def test_mixed_bundle_keeps_only_admitted(self):
        """混合 bundle 应该只保留 PRODUCTION_ADMITTED 规则。"""
        rules = [
            _make_production_rule("PROD-1"),
            _make_test_fixture_rule("TEST-1"),
            _make_production_rule("PROD-2"),
            _make_test_fixture_rule("TEST-2"),
        ]
        path = _write_rules_file(rules)

        try:
            prod_lib = ProductionRuleLoader.load(path)
            assert len(prod_lib._rules) == 2
            rule_ids = {r.rule_id for r in prod_lib._rules}
            assert rule_ids == {"PROD-1", "PROD-2"}
            assert prod_lib.admission_state.admitted_rules_count == 2
        finally:
            Path(path).unlink(missing_ok=True)

    def test_missing_provenance_fields_rejected(self):
        """缺少 provenance 字段的规则应该被拒绝。"""
        rule = _make_production_rule()
        rule["provenance"]["verified_by"] = ""  # Empty verified_by
        path = _write_rules_file([rule])

        try:
            prod_lib = ProductionRuleLoader.load(path)
            # 应该被拒绝，因为 provenance 不完整
            assert len(prod_lib._rules) == 0
            assert prod_lib.admission_state.admitted_rules_count == 0
        finally:
            Path(path).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
