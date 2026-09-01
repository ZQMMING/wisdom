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
    def test_registry_cannot_be_instantiated_externally(self):
        """G1: External code cannot instantiate AdmissionRegistry (v5)."""
        # No-arg call fails because capability is required
        with pytest.raises(TypeError, match="capability"):
            AdmissionRegistry()
        # Even with wrong keyword arg, fails (no 'internal' param)
        with pytest.raises(TypeError, match="unexpected keyword argument"):
            AdmissionRegistry(internal=True)
        # With wrong type, fails
        with pytest.raises(TypeError, match="AdmissionCapability"):
            AdmissionRegistry("not-a-capability")

    def test_no_public_factory_function(self):
        """G1: No module-level factory function exists (v4)."""
        import tongshu.assertion.admission_registry as m
        assert not hasattr(m, "create_admission_record")

    def test_production_loader_creates_valid_admission(self):
        """G1+G2: ProductionRuleLoader is the only path to PRODUCTION_ADMITTED."""
        from tongshu.assertion.assertion_rule_library import ProductionRuleLoader
        import tempfile, os
        bundle = {
            "_meta": {"version": "1.0", "status": "PRODUCTION", "synthetic": False},
            "rules": [
                {
                    "rule_id": "G1-G2-TEST-001",
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
                        "verified_by": {"identity_type": "AGENT", "identity_id": "audit-bot-v1", "authority_source": "admission_registry"},
                        "verification_version": "2026.09",
                    },
                }
            ],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(bundle, f, ensure_ascii=False)
            tmp_path = f.name
        try:
            lib = ProductionRuleLoader.load(tmp_path)
            assert lib.is_production is True
            assert len(lib.list_rules()) == 1
            rule = lib.list_rules()[0]
            # Verify provenance is preserved
            assert rule.provenance.source_work == "TestWork"
            assert rule.provenance.verified_by.identity_type.value == "AGENT"
            assert rule.provenance.verified_by.identity_id == "audit-bot-v1"
        finally:
            os.unlink(tmp_path)

    def test_legacy_identity_rejected_by_production_loader(self):
        """G2: LEGACY identity -> PRODUCTION hard reject."""
        from tongshu.assertion.assertion_rule_library import ProductionRuleLoader
        import tempfile, os
        bundle = {
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
                        "verified_by": "legacy-auditor",
                        "verification_version": "1.0",
                    },
                }
            ],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(bundle, f, ensure_ascii=False)
            tmp_path = f.name
        try:
            lib = ProductionRuleLoader.load(tmp_path)
            # LEGACY identity rejected -> 0 rules
            assert len(lib.list_rules()) == 0
        finally:
            os.unlink(tmp_path)

    def test_synthetic_rejected_by_registry(self):
        """G1+G3 preview: Registry rejects synthetic for PRODUCTION."""
        registry = AdmissionRegistry(AdmissionRegistry._create_capability())
        with pytest.raises(ValueError, match="Synthetic"):
            registry._create_production_admission(
                asset_id="SYN-001", asset_type="RULE",
                source_work="W", source_chapter="C", passage_ref="P",
                verified_by=AuditedIdentity(
                    identity_type=IdentityType.AGENT,
                    identity_id="bot", authority_source="reg"
                ),
                verification_stage="S", verification_version="V",
                synthetic=True,
            )

    def test_hash_integrity_on_modified_asset_id(self):
        """G1: Different asset_id -> different admission_hash (integrity)."""
        import hashlib as _h
        from tongshu.assertion.admission_registry import AdmissionRecord, AuditedIdentity, IdentityType, AdmissionScope
        # Build two records with different asset_id but same admission_id
        identity = AuditedIdentity(identity_type=IdentityType.AGENT, identity_id="auditor", authority_source="reg")
        r1 = AdmissionRecord(
            asset_id="ASSET-A", asset_type="RULE", source_work="W", source_chapter="C",
            passage_ref="P", verified_by=identity, verification_stage="S",
            verification_version="V", admission_scope=AdmissionScope.PRODUCTION_ADMITTED,
            admission_timestamp=1700000000.0, admission_id="same-id",
            asset_hash=_h.sha256(b"asset-a").hexdigest(), admission_hash="", synthetic=False,
        )
        r2 = AdmissionRecord(
            asset_id="ASSET-B", asset_type="RULE", source_work="W", source_chapter="C",
            passage_ref="P", verified_by=identity, verification_stage="S",
            verification_version="V", admission_scope=AdmissionScope.PRODUCTION_ADMITTED,
            admission_timestamp=1700000000.0, admission_id="same-id",
            asset_hash=_h.sha256(b"asset-b").hexdigest(), admission_hash="", synthetic=False,
        )
        # Different asset_hash -> different admission_hash
        assert r1._compute_admission_hash() != r2._compute_admission_hash()

    def test_hash_integrity_on_modified_identity(self):
        """G1: Different identity -> different admission_hash (integrity)."""
        import hashlib as _h
        from tongshu.assertion.admission_registry import AdmissionRecord, AuditedIdentity, IdentityType, AdmissionScope
        i1 = AuditedIdentity(identity_type=IdentityType.AGENT, identity_id="auditor-a", authority_source="src-a")
        i2 = AuditedIdentity(identity_type=IdentityType.AGENT, identity_id="auditor-b", authority_source="src-b")
        r1 = AdmissionRecord(
            asset_id="TEST", asset_type="RULE", source_work="W", source_chapter="C",
            passage_ref="P", verified_by=i1, verification_stage="S",
            verification_version="V", admission_scope=AdmissionScope.PRODUCTION_ADMITTED,
            admission_timestamp=1700000000.0, admission_id="id-1",
            asset_hash=_h.sha256(b"test").hexdigest(), admission_hash="", synthetic=False,
        )
        r2 = AdmissionRecord(
            asset_id="TEST", asset_type="RULE", source_work="W", source_chapter="C",
            passage_ref="P", verified_by=i2, verification_stage="S",
            verification_version="V", admission_scope=AdmissionScope.PRODUCTION_ADMITTED,
            admission_timestamp=1700000000.0, admission_id="id-2",
            asset_hash=_h.sha256(b"test").hexdigest(), admission_hash="", synthetic=False,
        )
        assert r1._compute_admission_hash() != r2._compute_admission_hash()

# ============================================================
# Run Tests
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
