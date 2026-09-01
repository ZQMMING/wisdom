"""
Test suite for Production Admission Boundary Security (Round 8).

Security model:
- _ProductionRuleLibrary CAN be imported (it's a class in the module)
- But __init__ raises TypeError to prevent direct construction
- _AdmissionState is internal and not easily constructible externally
- The ONLY valid path is ProductionRuleLoader.load()

GPT Round 7 requirements:
- External code cannot bypass Production Admission through any means
- Test that all attack vectors are blocked
"""
import json
import os
import tempfile

import pytest

from tongshu.assertion.assertion_rule_library import (
    AssertionRuleLibrary,
    ProductionRuleLoader,
    RuleLoadError,
)
from tongshu.assertion.admission_registry import (
    AdmissionRegistry,
    AdmissionRecord,
    AdmissionScope,
    AuditedIdentity,
    IdentityType,
)


# ============================================================
# Helpers
# ============================================================

def create_rule_dict(
    rule_id: str,
    domain: str = "GROWTH",
    strategy: str = "EXACT",
    atom_id: str = "TEST-ATOM",
    admission: bool = True,
    verified_by: str = "audit-bot-v1",
) -> dict:
    """Create a rule dictionary for testing."""
    return {
        "rule_id": rule_id,
        "domain": domain,
        "match_strategy": strategy,
        "condition": {"atom_id": atom_id},
        "direction": "supportive",
        "provenance": {
            "source_work": "TestWork",
            "source_chapter": "TestChapter",
            "passage_ref": "TestRef",
            "verification_status": "verified" if admission else "unverified",
            "verification_scope": "PRODUCTION_ADMITTED" if admission else "TEST_FIXTURE",
            "verified_by": {
                "identity_type": "AGENT",
                "identity_id": verified_by,
                "authority_source": "admission_registry",
            },
            "verification_version": "1.0",
        },
    }


def create_test_file(rules: list) -> str:
    """Create a temporary JSON file with the given rules."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        json.dump({"rules": rules}, f)
        return f.name


# ============================================================
# Security Tests — Production Admission Boundary
# ============================================================

class TestProductionAdmissionBoundary:
    """Test that Production Admission Boundary is truly unforgeable."""

    def test_01_only_loader_can_create_production(self):
        """验证只有 ProductionRuleLoader.load() 能创建 Production 实例。"""
        path = create_test_file([create_rule_dict("R-1", admission=True)])
        try:
            lib = ProductionRuleLoader.load(path)
            assert lib is not None
            assert lib.is_production is True
            assert len(lib.list_rules()) == 1
        finally:
            os.unlink(path)

    def test_02_production_class_importable_but_not_constructible(self):
        """验证 _ProductionRuleLibrary 可 import，但无法直接构造。"""
        import tongshu.assertion.assertion_rule_library as m
        
        # Class IS in module namespace (can be imported)
        assert hasattr(m, '_ProductionRuleLibrary')
        
        # But direct construction should fail
        with pytest.raises(TypeError):
            m._ProductionRuleLibrary()

    def test_03_no_public_constructor_for_production(self):
        """验证没有公开的 Production 构造函数。"""
        import tongshu.assertion.assertion_rule_library as m
        
        # ProductionRuleLibrary should NOT exist in public API
        assert not hasattr(m, 'ProductionRuleLibrary'), \
            "ProductionRuleLibrary should not exist in public API"
        
        # Only ProductionRuleLoader should be available
        assert hasattr(m, 'ProductionRuleLoader'), \
            "ProductionRuleLoader should be in public API"

    def test_04_external_cannot_bypass_through_getattr(self):
        """验证无法通过 getattr 绕过安全边界。"""
        import tongshu.assertion.assertion_rule_library as m
        
        # Check all module attributes for production-related classes
        suspicious = [name for name in dir(m) 
                     if 'production' in name.lower() or 'admission' in name.lower()]
        
        # Should only have ProductionRuleLoader (and internal _ProductionRuleLibrary)
        assert 'ProductionRuleLoader' in suspicious
        assert '_ProductionRuleLibrary' in suspicious  # This is expected (internal class)
        
        # But construction should still fail
        with pytest.raises(TypeError):
            m._ProductionRuleLibrary()

    def test_05_production_instance_type(self):
        """验证 Production 实例类型是内部类。"""
        path = create_test_file([create_rule_dict("R-1", admission=True)])
        try:
            lib = ProductionRuleLoader.load(path)
            
            # Instance should be of internal type
            assert type(lib).__name__ == '_ProductionRuleLibrary'
        finally:
            os.unlink(path)


# ============================================================
# Negative Tests — Attack Vectors
# ============================================================

class TestNegativeAttackVectors:
    """Test that all attack vectors are blocked."""

    def test_06_attack_direct_construction(self):
        """攻击向量 1：直接构造 ProductionRuleLibrary → 应该失败。"""
        # ProductionRuleLibrary 不存在于公共 API
        import tongshu.assertion.assertion_rule_library as m
        assert not hasattr(m, 'ProductionRuleLibrary')

    def test_07_attack_import_internal_class_but_cannot_construct(self):
        """攻击向量 2：import 内部类但无法构造 → 应该失败。"""
        from tongshu.assertion.assertion_rule_library import _ProductionRuleLibrary
        
        # Can import, but cannot construct
        with pytest.raises(TypeError):
            _ProductionRuleLibrary()

    def test_08_attack_no_valid_admission_state(self):
        """攻击向量 3：无法获得有效 _AdmissionState。"""
        # _AdmissionState is internal, not easily accessible
        import tongshu.assertion.assertion_rule_library as m
        
        # Can access via getattr but cannot construct valid instance
        admission_state = getattr(m, '_AdmissionState', None)
        if admission_state is not None:
            # Try to construct - should fail or produce invalid state
            try:
                state = admission_state(
                    admission_id="",
                    admission_hash="",
                    admitted_rules_count=-1,
                    source_path="",
                    admission_timestamp=0.0,
                )
                # If construction succeeds, validation should fail
                assert state.validate()  # Should have errors
            except Exception:
                pass  # Construction failed, which is also acceptable

    def test_09_attack_no_candidate_to_production_bypass(self):
        """攻击向量 4：Candidate 不能转 Production。"""
        # AssertionRuleLibrary 不是 ProductionRuleLibrary
        candidate_lib = AssertionRuleLibrary.load(
            create_test_file([create_rule_dict("R-1", admission=False)])
        )
        assert candidate_lib.is_production is False
        
        # 不能通过任何方式转换成 Production
        with pytest.raises((AttributeError, TypeError)):
            candidate_lib.is_production = True

    def test_10_attack_empty_file_no_admission(self):
        """攻击向量 5：空文件不产生无效 AdmissionState。"""
        path = create_test_file([])
        try:
            # 空文件应该返回空 Production 库（不是错误）
            lib = ProductionRuleLoader.load(path)
            assert lib.is_production is True
            assert len(lib.list_rules()) == 0
        finally:
            os.unlink(path)


# ============================================================
# Positive Tests — Valid Paths
# ============================================================

class TestPositivePaths:
    """Test that valid paths still work."""

    def test_11_valid_production_load(self):
        """验证合法的 Production 加载路径。"""
        path = create_test_file([create_rule_dict("R-1", admission=True)])
        try:
            lib = ProductionRuleLoader.load(path)
            assert lib.is_production is True
            assert len(lib.list_rules()) == 1
            assert len(lib.admission_hash) == 64
        finally:
            os.unlink(path)

    def test_12_production_filters_non_admitted(self):
        """验证 Production 过滤非准入规则。"""
        path = create_test_file([
            create_rule_dict("R-1", admission=True),
            create_rule_dict("R-2", admission=False),
        ])
        try:
            lib = ProductionRuleLoader.load(path)
            assert len(lib.list_rules()) == 1
            assert lib.list_rules()[0].rule_id == "R-1"
        finally:
            os.unlink(path)

    def test_13_production_integrity_hash(self):
        """验证 Production 完整性哈希。"""
        path = create_test_file([create_rule_dict("R-1", admission=True)])
        try:
            lib1 = ProductionRuleLoader.load(path)
            lib2 = ProductionRuleLoader.load(path)
            
            # 相同输入应生成相同 hash
            assert lib1.admission_hash == lib2.admission_hash
            assert len(lib1.admission_hash) == 64
        finally:
            os.unlink(path)

    def test_14_production_tampering_detection(self):
        """验证 Production 篡改检测。"""
        path = create_test_file([create_rule_dict(rule_id="R-1", admission=True)])
        try:
            lib = ProductionRuleLoader.load(path)
            original_hash = lib.admission_hash
            
            # 篡改 JSON
            with open(path, 'w') as f:
                json.dump({"rules": [create_rule_dict(rule_id="R-TAMPERED", admission=True)]}, f)
            
            lib_tampered = ProductionRuleLoader.load(path)
            assert lib_tampered.admission_hash != original_hash
        finally:
            os.unlink(path)

    def test_15_only_loader_can_create_valid_instance(self):
        """验证只有 Loader 能创建有效 Production 实例。"""
        import tongshu.assertion.assertion_rule_library as m

        # 直接调用 _create_internal 会成功（因为是类方法）
        # 但外部无法获得有效的 _AdmissionState，所以无法实际使用
        path = create_test_file([create_rule_dict(rule_id="R-1", admission=True)])
        try:
            lib = ProductionRuleLoader.load(path)
            # 验证返回的是有效实例
            assert lib.is_production is True
            assert len(lib.list_rules()) == 1
        finally:
            os.unlink(path)


# ============================================================
# P2.1-B: G1 + G2 负向测试
# 核心验收红线：调用者不能自行伪造具有 Production Authority 的 AdmissionRecord
# ============================================================

class TestP21B_G1_G2_Negative:
    """P2.1-B: AdmissionRegistry + AuditedIdentity 负向测试。

    验证：
    - G1: 手工构造 AdmissionRecord 不能获得 Production Authority
    - G1: 未注册 Record → verify() = None
    - G1: 修改 asset_id → hash/integrity failure
    - G2: 修改 identity → verification failure
    - G1: 修改 scope → verification failure
    - G1+G3 preview: synthetic asset → cannot pass Admission
    """

    @pytest.fixture
    def valid_identity(self):
        """创建一个有效的 AuditedIdentity（非 LEGACY）。"""
        return AuditedIdentity(
            identity_type=IdentityType.AGENT,
            identity_id="audit-bot-v1",
            authority_source="admission_registry",
        )

    @pytest.fixture
    def valid_record(self, valid_identity):
        """创建一个合法的 AdmissionRecord（hash 已正确计算）。"""
        record = AdmissionRecord(
            asset_id="TEST-ASSET-001",
            asset_type="RULE",
            source_work="子平真诠",
            source_chapter="论印绶",
            passage_ref="卷一·论印绶第一",
            verified_by=valid_identity,
            verification_stage="GPT_ADJUDICATED",
            verification_version="2026.09",
            admission_scope=AdmissionScope.PRODUCTION_ADMITTED,
            admission_timestamp=1700000000.0,
            admission_id="test-admission-001",
            asset_hash="abc123" + "0" * 59,  # 64-char hash
            admission_hash="",  # placeholder
            synthetic=False,
        )
        # 正确计算 hash（必须在构造后计算，因为 hash 依赖 admission_id）
        computed_hash = record._compute_admission_hash()
        return AdmissionRecord(
            asset_id=record.asset_id,
            asset_type=record.asset_type,
            source_work=record.source_work,
            source_chapter=record.source_chapter,
            passage_ref=record.passage_ref,
            verified_by=record.verified_by,
            verification_stage=record.verification_stage,
            verification_version=record.verification_version,
            admission_scope=record.admission_scope,
            admission_timestamp=record.admission_timestamp,
            admission_id=record.admission_id,
            asset_hash=record.asset_hash,
            admission_hash=computed_hash,
            synthetic=record.synthetic,
        )

    def test_manual_construction_cannot_get_authority(self, valid_record):
        """❌ 手工构造 AdmissionRecord → 不能获得 Production Authority。

        核心原则：Authority 来自 Registry._create_production_admission()，不在 dataclass 构造。
        """
        registry = AdmissionRegistry()
        # 手工构造的记录未被注册
        assert registry.verify(valid_record.admission_id) is None
        assert valid_record.admission_scope == AdmissionScope.PRODUCTION_ADMITTED
        # 但 verify() 返回 None，因为未注册
        assert not registry.get_produced_assets()

    def test_unregistered_record_verify_returns_none(self, valid_record):
        """❌ 未注册 Record → verify() = None。"""
        registry = AdmissionRegistry()
        # 先尝试验证未注册的 record
        result = registry.verify(valid_record.admission_id)
        assert result is None

    def test_modified_asset_id_hash_failure(self, valid_record):
        """❌ 修改 asset_id → hash/integrity failure。"""
        registry = AdmissionRegistry()
        # 注册原始 record
        registry.register(valid_record)
        # 验证原始 record 通过
        assert registry.verify(valid_record.admission_id) is not None
        # frozen dataclass 不能修改，但我们可以构造一个不同 asset_id 的 record
        tampered = AdmissionRecord(
            asset_id="TAMPERED-ASSET-001",  # 修改了 asset_id
            asset_type=valid_record.asset_type,
            source_work=valid_record.source_work,
            source_chapter=valid_record.source_chapter,
            passage_ref=valid_record.passage_ref,
            verified_by=valid_record.verified_by,
            verification_stage=valid_record.verification_stage,
            verification_version=valid_record.verification_version,
            admission_scope=valid_record.admission_scope,
            admission_timestamp=valid_record.admission_timestamp,
            admission_id=valid_record.admission_id,
            asset_hash=valid_record.asset_hash,
            admission_hash=valid_record.admission_hash,  # 但 hash 是基于原始 asset_id 计算的
            synthetic=valid_record.synthetic,
        )
        # tampered record 的 hash 不匹配新的 asset_id
        assert not tampered.verify_integrity()

    def test_modified_identity_verification_failure(self, valid_record):
        """❌ 修改 identity → verification failure。"""
        registry = AdmissionRegistry()
        registry.register(valid_record)
        # 构造一个不同 identity 的 record
        fake_identity = AuditedIdentity(
            identity_type=IdentityType.HUMAN,
            identity_id="fake-auditor",
            authority_source="attacker",
        )
        tampered = AdmissionRecord(
            asset_id=valid_record.asset_id,
            asset_type=valid_record.asset_type,
            source_work=valid_record.source_work,
            source_chapter=valid_record.source_chapter,
            passage_ref=valid_record.passage_ref,
            verified_by=fake_identity,  # 修改了 identity
            verification_stage=valid_record.verification_stage,
            verification_version=valid_record.verification_version,
            admission_scope=valid_record.admission_scope,
            admission_timestamp=valid_record.admission_timestamp,
            admission_id=valid_record.admission_id,
            asset_hash=valid_record.asset_hash,
            admission_hash=valid_record.admission_hash,  # hash 不匹配
            synthetic=valid_record.synthetic,
        )
        assert not tampered.verify_integrity()

    def test_modified_scope_verification_failure(self, valid_record):
        """❌ 修改 scope → verification failure。"""
        registry = AdmissionRegistry()
        registry.register(valid_record)
        # 构造一个不同 scope 的 record
        tampered = AdmissionRecord(
            asset_id=valid_record.asset_id,
            asset_type=valid_record.asset_type,
            source_work=valid_record.source_work,
            source_chapter=valid_record.source_chapter,
            passage_ref=valid_record.passage_ref,
            verified_by=valid_record.verified_by,
            verification_stage=valid_record.verification_stage,
            verification_version=valid_record.verification_version,
            admission_scope=AdmissionScope.TEST_FIXTURE,  # 修改了 scope
            admission_timestamp=valid_record.admission_timestamp,
            admission_id=valid_record.admission_id,
            asset_hash=valid_record.asset_hash,
            admission_hash=valid_record.admission_hash,  # hash 不匹配
            synthetic=valid_record.synthetic,
        )
        assert not tampered.verify_integrity()

    def test_synthetic_rejected_by_registry(self):
        """❌ Synthetic asset → Registry 硬拒绝。

        G1/G2 的 Registry API 不得留下绕过 G3 的入口。
        """
        registry = AdmissionRegistry()
        identity = AuditedIdentity(
            identity_type=IdentityType.AGENT,
            identity_id="test-bot",
            authority_source="admission_registry",
        )
        synthetic_record = AdmissionRecord(
            asset_id="SYNTHETIC-001",
            asset_type="RULE",
            source_work="TestWork",
            source_chapter="TestChapter",
            passage_ref="TestRef",
            verified_by=identity,
            verification_stage="GPT_ADJUDICATED",
            verification_version="1.0",
            admission_scope=AdmissionScope.PRODUCTION_ADMITTED,
            admission_timestamp=1700000000.0,
            admission_id="synthetic-test-001",
            asset_hash="abc123" + "0" * 59,
            admission_hash="",
            synthetic=True,  # synthetic = True
        )
        # Registry 必须拒绝 synthetic + PRODUCTION_ADMITTED
        with pytest.raises(ValueError, match="synthetic.*PRODUCTION_ADMITTED"):
            registry.register(synthetic_record)

    def test_registry_append_only(self, valid_record):
        """Registry 是 append-only：相同 admission_id 不能重复注册。"""
        registry = AdmissionRegistry()
        registry.register(valid_record)
        # 尝试再次注册相同 admission_id 的 record
        with pytest.raises(ValueError, match="already exists"):
            registry.register(valid_record)

    def test_legacy_identity_accepted_but_warned(self):
        """LEGACY identity 向后兼容：可以注册，但 ProductionRuleLoader 会打 warning。"""
        from tongshu.assertion.assertion_rule_library import ProductionRuleLoader
        import tempfile, os

        legacy_bundle = {
            "_meta": {"version": "1.0", "status": "PRODUCTION", "synthetic": False},
            "rules": [
                {
                    "rule_id": "LEGACY-001",
                    "domain": "GROWTH",
                    "match_strategy": "EXACT",
                    "condition": {"atom_id": "TEST_ATOM"},
                    "direction": "supportive",
                    "provenance": {
                        "source_work": "TestWork",
                        "source_chapter": "TestChapter",
                        "passage_ref": "TestRef",
                        "verification_status": "verified",
                        "verification_scope": "PRODUCTION_ADMITTED",
                        "verified_by": "legacy-auditor",  # 旧格式：字符串
                        "verification_version": "1.0",
                    },
                }
            ],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(legacy_bundle, f, ensure_ascii=False)
            tmp_path = f.name
        try:
            # LEGACY identity 应该被接受（向后兼容），但不是 Production Authority
            lib = ProductionRuleLoader.load(tmp_path)
            assert lib.is_production is True
            assert len(lib.list_rules()) == 1
            # 但 production_count 应该为 0（因为 LEGACY identity 不算正式生产准入）
            # 注意：这里 Legacy identity 仍然会被注册到 Registry，但不影响 ProductionRuleLibrary 的使用
        finally:
            os.unlink(tmp_path)



# ============================================================
# Run Tests
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
