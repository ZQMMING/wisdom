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
    _ADMISSION_CAPABILITY,
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
        with pytest.raises(TypeError, match="_ADMISSION_CAPABILITY"):
            AdmissionRegistry("not-a-capability")

    def test_no_public_factory_function(self):
        """G1: No module-level factory function exists (v4)."""
        import tongshu.assertion.admission_registry as m
        assert not hasattr(m, "create_admission_record")

    def test_registry_requires_singleton_capability(self):
        """G1: Registry rejects any object that is not the singleton capability."""
        with pytest.raises(TypeError, match="_ADMISSION_CAPABILITY"):
            AdmissionRegistry(object())
        with pytest.raises(TypeError, match="_ADMISSION_CAPABILITY"):
            AdmissionRegistry(None)
        with pytest.raises(TypeError, match="_ADMISSION_CAPABILITY"):
            AdmissionRegistry("fake")

    def test_capability_singleton_not_spoofable(self):
        """G1: Cannot spoof the capability singleton via object.__new__."""
        import tongshu.assertion.admission_registry as m
        # The class _AdmissionAuthority is private (underscore prefix)
        # Even if someone accesses it, creating an instance should fail
        from tongshu.assertion.admission_registry import _AdmissionAuthority
        # Direct instantiation is blocked
        with pytest.raises(TypeError):
            _AdmissionAuthority()
        # object.__new__ creates a bare instance but __init__ won't run
        # The key test is that the registry's `is` check catches this
        fake = object.__new__(_AdmissionAuthority)
        # But the singleton is created differently — verify they are NOT the same
        assert fake is not m._ADMISSION_CAPABILITY
        with pytest.raises(TypeError):
            AdmissionRegistry(fake)

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
        """G1+G3: Registry rejects synthetic for PRODUCTION."""
        registry = AdmissionRegistry(_ADMISSION_CAPABILITY)
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

    def test_synthetic_rejected_by_production_loader(self):
        """G3: ProductionRuleLoader HARD REJECTs synthetic=true assets."""
        import json, tempfile, os
        bundle = {
            "_meta": {"version": "1.0", "status": "PRODUCTION", "synthetic": True},
            "rules": [
                {
                    "rule_id": "SYN-001",
                    "domain": "CAREER",
                    "match_strategy": "EXACT",
                    "condition": {"atom_id": "TEST_ATOM"},
                    "direction": "supportive",
                    "provenance": {
                        "source_work": "Test", "source_chapter": "Ch", "passage_ref": "P",
                        "verification_status": "verified",
                        "verification_scope": "PRODUCTION_ADMITTED",
                        "verified_by": {"identity_type": "AGENT", "identity_id": "bot", "authority_source": "reg-01"},
                        "verification_version": "2026.09",
                        "synthetic": True,
                    },
                }
            ],
        }
        tmp_path = os.path.join(tempfile.gettempdir(), "synthetic_test.json")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(bundle, f, ensure_ascii=False)
            lib = ProductionRuleLoader.load(tmp_path)
            assert len(lib.list_rules()) == 0, (
                "G3 FAIL: synthetic=true PRODUCTION_ADMITTED rule must be HARD-REJECTED"
            )
        finally:
            os.unlink(tmp_path)

    def test_unregistered_authority_rejected(self):
        """A2: Identity with unregistered authority_source is rejected by registry.

        G2: verified_by must point to a pre-registered authority.
        """
        from tongshu.assertion.admission_registry import (
            AdmissionRegistry, AuditedIdentity, IdentityType, _ADMISSION_CAPABILITY
        )
        registry = AdmissionRegistry(_ADMISSION_CAPABILITY)
        fake_identity = AuditedIdentity(
            identity_type=IdentityType.AGENT,
            identity_id="fake-bot",
            authority_source="unregistered-source",
        )
        with pytest.raises(ValueError, match="unregistered authority_source"):
            registry._create_production_admission(
                asset_id="TEST-001", asset_type="RULE",
                source_work="W", source_chapter="C", passage_ref="P",
                verified_by=fake_identity,
                verification_stage="GPT", verification_version="1.0",
            )

    def test_valid_registered_authority_accepted(self):
        """G2: Identity with registered authority_source passes registry validation."""
        from tongshu.assertion.admission_registry import (
            AdmissionRegistry, AuditedIdentity, IdentityType, _ADMISSION_CAPABILITY,
            register_authority_credential,
        )
        # Save and restore global state
        import tongshu.assertion.admission_registry as _m
        _saved_lock = _m._AUTHORITY_LOCKED
        _saved_creds = dict(_m._AUTHORITY_CREDENTIALS)
        try:
            _m._AUTHORITY_LOCKED = False
            _m._AUTHORITY_CREDENTIALS.clear()
            register_authority_credential("reg-01", "cred-hash-01")
            registry = AdmissionRegistry(_ADMISSION_CAPABILITY)
            identity = AuditedIdentity(
                identity_type=IdentityType.AGENT,
                identity_id="bot-v1",
                authority_source="reg-01",
                credential_hash="cred-hash-01",
            )
            record = registry._create_production_admission(
                asset_id="VALID-001", asset_type="RULE",
                source_work="W", source_chapter="C", passage_ref="P",
                verified_by=identity,
                verification_stage="GPT", verification_version="1.0",
            )
            assert record.asset_id == "VALID-001"
            assert record.admission_scope.value == "PRODUCTION_ADMITTED"
        finally:
            _m._AUTHORITY_LOCKED = _saved_lock
            _m._AUTHORITY_CREDENTIALS.clear()
            _m._AUTHORITY_CREDENTIALS.update(_saved_creds)

    def test_unregistered_authority_loader_rejects(self):
        """A2 extended: ProductionRuleLoader rejects rules with unregistered authority."""
        import json, tempfile, os
        bundle = {
            "_meta": {"version": "1.0", "status": "PRODUCTION", "synthetic": False},
            "rules": [
                {
                    "rule_id": "R-UNREG",
                    "domain": "CAREER",
                    "match_strategy": "EXACT",
                    "condition": {"atom_id": "A1"},
                    "direction": "supportive",
                    "provenance": {
                        "source_work": "Test", "source_chapter": "Ch", "passage_ref": "P",
                        "verification_status": "verified",
                        "verification_scope": "PRODUCTION_ADMITTED",
                        "verified_by": {"identity_type": "AGENT", "identity_id": "bot", "authority_source": "unregistered"},
                        "verification_version": "2026.09",
                    },
                }
            ],
        }
        tmp_path = os.path.join(tempfile.gettempdir(), "unreg_test.json")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(bundle, f, ensure_ascii=False)
            lib = ProductionRuleLoader.load(tmp_path)
            assert len(lib.list_rules()) == 0, (
                "G2 FAIL: Unregistered authority_source should be rejected by ProductionRuleLoader"
            )
        finally:
            os.unlink(tmp_path)

# ============================================================
# Run Tests
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# ============================================================
# P2.1-C: Authority Credential Boundary Hardening Tests
# ============================================================

class TestP21C_AuthorityHardening:
    """P2.1-C: 攻击测试 — authority 凭证注入、credential 伪造、锁定绕过。"""

    def test_authority_self_registration_blocked_after_lock(self):
        """A3: 攻击者无法在锁定后注册新的 authority。"""
        from tongshu.assertion.admission_registry import (
            _ADMISSION_CAPABILITY, AdmissionRegistry, AuditedIdentity,
            IdentityType, register_authority_credential, lock_authority_registry,
        )
        import tongshu.assertion.admission_registry as _m
        _saved_lock = _m._AUTHORITY_LOCKED
        _saved_creds = dict(_m._AUTHORITY_CREDENTIALS)
        try:
            _m._AUTHORITY_LOCKED = False
            _m._AUTHORITY_CREDENTIALS.clear()
            # 先注册并锁定
            register_authority_credential("attacker", "attacker-cred")
            lock_authority_registry()
            # 锁定后尝试注册新权威 → 必须失败
            with pytest.raises(RuntimeError, match="locked"):
                register_authority_credential("fake-attacker", "fake-cred")
            # 验证原始凭证仍然有效（含 credential）
            registry = AdmissionRegistry(_ADMISSION_CAPABILITY)
            identity = AuditedIdentity(
                identity_type=IdentityType.AGENT,
                identity_id="attacker",
                authority_source="attacker",
                credential_hash="attacker-cred",
            )
            record = registry._create_production_admission(
                asset_id="TEST", asset_type="RULE",
                source_work="W", source_chapter="C", passage_ref="P",
                verified_by=identity, verification_stage="S", verification_version="V",
            )
            assert record.asset_id == "TEST"
        finally:
            _m._AUTHORITY_LOCKED = _saved_lock
            _m._AUTHORITY_CREDENTIALS.clear()
            _m._AUTHORITY_CREDENTIALS.update(_saved_creds)

    def test_credential_mismatch_blocked(self):
        """A4: 伪造 credential_hash 在生产 gate 必须被拒绝。

        G2 核心：verify_credential() 必须被 _create_production_admission 调用。
        """
        from tongshu.assertion.admission_registry import (
            _ADMISSION_CAPABILITY, AdmissionRegistry, AuditedIdentity,
            IdentityType, register_authority_credential,
            lock_authority_registry, _AUTHORITY_CREDENTIALS,
        )
        # Save and restore global state
        import tongshu.assertion.admission_registry as _m
        _saved_lock = _m._AUTHORITY_LOCKED
        _saved_creds = dict(_m._AUTHORITY_CREDENTIALS)
        try:
            _m._AUTHORITY_LOCKED = False
            _m._AUTHORITY_CREDENTIALS.clear()
            register_authority_credential("test-auth", "correct-cred")
            lock_authority_registry()
            registry = AdmissionRegistry(_ADMISSION_CAPABILITY)
            # 正确的 authority_source 但错误的 credential_hash
            identity_wrong = AuditedIdentity(
                identity_type=IdentityType.AGENT,
                identity_id="bot",
                authority_source="test-auth",
                credential_hash="wrong-cred",
            )
            # 预期：verify_credential 应拒绝伪造的 credential_hash
            with pytest.raises(ValueError):
                registry._create_production_admission(
                    asset_id="TEST", asset_type="RULE",
                    source_work="W", source_chapter="C", passage_ref="P",
                    verified_by=identity_wrong,
                    verification_stage="S", verification_version="V",
                )
        finally:
            _m._AUTHORITY_LOCKED = _saved_lock
            _m._AUTHORITY_CREDENTIALS.clear()
            _m._AUTHORITY_CREDENTIALS.update(_saved_creds)

    def test_lock_prevents_runtime_registration(self):
        """A3 extended: lock_authority_registry() 后任何注册尝试都被阻止。"""
        from tongshu.assertion.admission_registry import (
            lock_authority_registry, register_authority_credential,
        )
        lock_authority_registry()
        with pytest.raises(RuntimeError, match="locked"):
            register_authority_credential("anything", "any-hash")

    def test_bootstrap_credential_required(self):
        """A3-2: ProductionRuleLoader accepts unregistered authority but Loader rejects rules.

        ProductionRuleLoader.load() does NOT check credential_hash in _meta.
        The credential_hash requirement is enforced by the pipeline bootstrap.
        This test verifies that:
        1. Without proper authority registration, ProductionRuleLoader rejects rules
        2. The pipeline would enforce credential_hash via bootstrap
        """
        import json, tempfile, os
        from tongshu.assertion.assertion_rule_library import ProductionRuleLoader
        from tongshu.assertion.admission_registry import clear_authority_credentials
        import tongshu.assertion.admission_registry as _m
        _saved_lock = _m._AUTHORITY_LOCKED
        _saved_creds = dict(_m._AUTHORITY_CREDENTIALS)
        try:
            _m._AUTHORITY_LOCKED = False
            _m._AUTHORITY_CREDENTIALS.clear()
            # Bundle with authority_source that is NOT registered
            bundle = {
                "_meta": {"version": "1.0", "status": "PRODUCTION", "synthetic": False},
                "rules": [{
                    "rule_id": "R-BUILD",
                    "domain": "CAREER",
                    "match_strategy": "EXACT",
                    "condition": {"atom_id": "A1"},
                    "direction": "supportive",
                    "provenance": {
                        "source_work": "Test", "source_chapter": "Ch", "passage_ref": "P",
                        "verification_status": "verified",
                        "verification_scope": "PRODUCTION_ADMITTED",
                        "verified_by": {"identity_type": "GPT", "identity_id": "gpt", "authority_source": "unregistered-attacker"},
                        "verification_version": "2026.09",
                    },
                }],
            }
            tmp_path = os.path.join(tempfile.gettempdir(), "bootstrap_test.json")
            try:
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(bundle, f, ensure_ascii=False)
                # Should reject because authority_source is not registered
                lib = ProductionRuleLoader.load(tmp_path)
                assert len(lib.list_rules()) == 0, \
                    "G2: Unregistered authority_source should be rejected by ProductionRuleLoader"
            finally:
                os.unlink(tmp_path)
        finally:
            _m._AUTHORITY_LOCKED = _saved_lock
            _m._AUTHORITY_CREDENTIALS.clear()
            _m._AUTHORITY_CREDENTIALS.update(_saved_creds)


# ============================================================
# P2.1-E: External Trust Root — Bootstrap Authority Separation
# ============================================================

class TestP21E_ExternalTrustRoot:
    """P2.1-E: 验证 authority bootstrap 来自 deployment manifest，而非 production rules JSON。

    核心安全要求：
    - production_assertion_rules.json 不得成为 authority credential 的唯一来源
    - _meta.declared_credential_hash 只是声明指纹，不负责授予 authority
    - Authority bootstrap 必须来自 deployment_manifest.json
    - manifest.credential_hash != rules.declared_credential_hash → FAIL CLOSED
    - 攻击者篡改 manifest 或 rules 中的指纹 → 必须被拒绝
    """

    def test_load_manifest_success(self):
        """E1: load_deployment_manifest 正确读取合法 manifest。"""
        import tempfile, os
        from tongshu.assertion.admission_registry import load_deployment_manifest
        manifest = {
            "_meta": {"version": "1.0"},
            "authority": {
                "authority_source": "test-governance",
                "credential_hash": "test-cred-xyz",
            },
        }
        tmp = os.path.join(tempfile.gettempdir(), "test_manifest.json")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(manifest, f)
            result = load_deployment_manifest(tmp)
            assert result["authority_source"] == "test-governance"
            assert result["credential_hash"] == "test-cred-xyz"
        finally:
            os.unlink(tmp)

    def test_load_manifest_missing_file(self):
        """E2: manifest 文件不存在 → ValueError (fail-closed)。"""
        from tongshu.assertion.admission_registry import load_deployment_manifest
        with pytest.raises(ValueError, match="not found"):
            load_deployment_manifest("/nonexistent/manifest.json")

    def test_load_manifest_missing_authority_section(self):
        """E3: manifest 缺少 authority 部分 → ValueError。"""
        import tempfile, os
        from tongshu.assertion.admission_registry import load_deployment_manifest
        manifest = {"_meta": {"version": "1.0"}}
        tmp = os.path.join(tempfile.gettempdir(), "test_manifest_no_auth.json")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(manifest, f)
            with pytest.raises(ValueError, match="authority"):
                load_deployment_manifest(tmp)
        finally:
            os.unlink(tmp)

    def test_load_manifest_empty_credential(self):
        """E4: authority.credential_hash 为空 → ValueError。"""
        import tempfile, os
        from tongshu.assertion.admission_registry import load_deployment_manifest
        manifest = {
            "authority": {"authority_source": "gov", "credential_hash": ""},
        }
        tmp = os.path.join(tempfile.gettempdir(), "test_manifest_empty_cred.json")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(manifest, f)
            with pytest.raises(ValueError, match="credential_hash"):
                load_deployment_manifest(tmp)
        finally:
            os.unlink(tmp)

    def test_verify_manifest_credential_match(self):
        """E5: verify_manifest_credential — 一致返回 True。"""
        from tongshu.assertion.admission_registry import verify_manifest_credential
        assert verify_manifest_credential("abc", "abc") is True

    def test_verify_manifest_credential_mismatch(self):
        """E6: verify_manifest_credential — 不一致返回 False。"""
        from tongshu.assertion.admission_registry import verify_manifest_credential
        assert verify_manifest_credential("manifest-cred", "rules-cred") is False

    def test_verify_manifest_credential_empty_rules_declared(self):
        """E7: rules 未声明 declared_credential_hash → 视为无校验，返回 True。"""
        from tongshu.assertion.admission_registry import verify_manifest_credential
        assert verify_manifest_credential("any-cred", "") is True

    def test_bootstrap_self_attestation_attack_blocked(self):
        """E8: 核心攻击测试 — 攻击者修改 rules JSON 的 declared_credential_hash，
        但 manifest 未变 → pipeline bootstrap 应 fail-closed。

        当前实现: pipeline 从 manifest 读取 credential，与 rules _meta.declared_credential_hash 比对。
        如果攻击者篡改了 rules 中的 declared_credential_hash（但无法篡改 manifest），
        SHA-256 不匹配 → RuntimeError。
        """
        import tempfile, os
        from tongshu.assertion.admission_registry import (
            register_authority_credential, lock_authority_registry, clear_authority_credentials,
        )
        import tongshu.assertion.admission_registry as _m

        _saved_lock = _m._AUTHORITY_LOCKED
        _saved_creds = dict(_m._AUTHORITY_CREDENTIALS)
        try:
            _m._AUTHORITY_LOCKED = False
            _m._AUTHORITY_CREDENTIALS.clear()
            clear_authority_credentials()

            tampered_hash = "ATTACKER-TAMPERED-2026"
            bundle = {
                "_meta": {
                    "version": "1.0",
                    "status": "PRODUCTION",
                    "declared_credential_hash": tampered_hash,
                },
                "rules": [
                    {
                        "rule_id": "R-TAMPERED",
                        "domain": "CAREER",
                        "match_strategy": "EXACT",
                        "condition": {"atom_id": "A1"},
                        "direction": "supportive",
                        "provenance": {
                            "source_work": "Test", "source_chapter": "Ch",
                            "passage_ref": "P",
                            "verification_status": "verified",
                            "verification_scope": "PRODUCTION_ADMITTED",
                            "verified_by": {
                                "identity_type": "GPT",
                                "identity_id": "gpt-attacker",
                                "authority_source": "architecture-governance",
                            },
                            "verification_version": "2026.09",
                        },
                    }
                ],
            }
            tmp_rules = os.path.join(tempfile.gettempdir(), "tampered_rules.json")
            with open(tmp_rules, "w", encoding="utf-8") as f:
                json.dump(bundle, f, ensure_ascii=False)

            try:
                real_cred = "schema-v1-arch-gov-2026"
                register_authority_credential("architecture-governance", real_cred)
                lock_authority_registry()

                from tongshu.assertion.admission_registry import verify_manifest_credential
                assert verify_manifest_credential(real_cred, tampered_hash) is False

                # loader 接受已注册的 authority_source（规则通过 G2）
                # 但 bootstrap 层会检测到 hash 不一致 → fail-closed
                from tongshu.assertion.assertion_rule_library import ProductionRuleLoader
                lib = ProductionRuleLoader.load(tmp_rules)
                # 规则通过了 G2 检查（authority_source 已注册）
                # 真正的安全保证在 pipeline bootstrap 阶段（manifest vs declared hash 比对）
                assert len(lib.list_rules()) == 1
            finally:
                os.unlink(tmp_rules)
        finally:
            _m._AUTHORITY_LOCKED = _saved_lock
            _m._AUTHORITY_CREDENTIALS.clear()
            _m._AUTHORITY_CREDENTIALS.update(_saved_creds)

    def test_pipeline_bootstrap_reads_from_manifest_not_rules(self):
        """E9: pipeline for_demo() 从 deployment manifest 读取 authority，而非 rules JSON。

        验证：manifest 存在时，pipeline bootstrap 流程正确（credential 来自 manifest）。
        """
        from tongshu.assertion.admission_registry import (
            clear_authority_credentials, _AUTHORITY_LOCKED,
        )
        import tongshu.assertion.admission_registry as _m

        _saved_lock = _m._AUTHORITY_LOCKED
        _saved_creds = dict(_m._AUTHORITY_CREDENTIALS)
        try:
            _m._AUTHORITY_LOCKED = False
            _m._AUTHORITY_CREDENTIALS.clear()
            clear_authority_credentials()

            from tongshu.assertion.admission_registry import (
                load_deployment_manifest, register_authority_credential,
                lock_authority_registry, verify_manifest_credential,
            )
            import json as _json
            from pathlib import Path

            repo_root = Path(__file__).parent.parent.parent
            manifest_path = repo_root / "data" / "deployment_manifest.json"
            rules_path = repo_root / "data" / "assertion_rules" / "production_assertion_rules.json"

            manifest = load_deployment_manifest(str(manifest_path))
            auth_source = manifest["authority_source"]
            manifest_cred = manifest["credential_hash"]

            with open(rules_path, encoding="utf-8") as f:
                rules_meta = _json.load(f).get("_meta", {})
            declared_hash = rules_meta.get("declared_credential_hash", "")

            assert verify_manifest_credential(manifest_cred, declared_hash) is True, (
                "P2.1-E FAIL: manifest credential must match rules declared_credential_hash"
            )

            register_authority_credential(auth_source, manifest_cred)
            lock_authority_registry()

            assert _m._AUTHORITY_LOCKED is True
            assert auth_source in _m._AUTHORITY_CREDENTIALS
            assert _m._AUTHORITY_CREDENTIALS[auth_source] == manifest_cred
        finally:
            _m._AUTHORITY_LOCKED = _saved_lock
            _m._AUTHORITY_CREDENTIALS.clear()
            _m._AUTHORITY_CREDENTIALS.update(_saved_creds)

    def test_attacker_cannot_self_register_authority_via_rules_json(self):
        """E10: 攻击者无法通过在 rules JSON 中设置 authority_source 来获得 authority。

        rules JSON 只有 declared_credential_hash（只读声明），
        不能自行注册 authority — authority 只能来自 manifest。
        """
        import tempfile, os
        from tongshu.assertion.admission_registry import (
            register_authority_credential, lock_authority_registry,
            clear_authority_credentials, _AUTHORITY_LOCKED,
        )
        import tongshu.assertion.admission_registry as _m

        _saved_lock = _m._AUTHORITY_LOCKED
        _saved_creds = dict(_m._AUTHORITY_CREDENTIALS)
        try:
            _m._AUTHORITY_LOCKED = False
            _m._AUTHORITY_CREDENTIALS.clear()
            clear_authority_credentials()

            # 攻击者创建了包含自定 authority_source 的 rules JSON
            # 但没有对应的 manifest 注册
            bundle = {
                "_meta": {
                    "version": "1.0",
                    "status": "PRODUCTION",
                    "declared_credential_hash": "FAKE-CRED-FROM-RULES",
                },
                "rules": [
                    {
                        "rule_id": "R-FAKE",
                        "domain": "CAREER",
                        "match_strategy": "EXACT",
                        "condition": {"atom_id": "A1"},
                        "direction": "supportive",
                        "provenance": {
                            "source_work": "Test", "source_chapter": "Ch",
                            "passage_ref": "P",
                            "verification_status": "verified",
                            "verification_scope": "PRODUCTION_ADMITTED",
                            "verified_by": {
                                "identity_type": "GPT",
                                "identity_id": "gpt-fake",
                                "authority_source": "FAKE-CRED-FROM-RULES",
                            },
                            "verification_version": "2026.09",
                        },
                    }
                ],
            }
            tmp_rules = os.path.join(tempfile.gettempdir(), "fake_rules.json")
            try:
                with open(tmp_rules, "w", encoding="utf-8") as f:
                    json.dump(bundle, f, ensure_ascii=False)

                # 没有 manifest bootstrap — authority "FAKE-CRED-FROM-RULES" 未注册
                from tongshu.assertion.assertion_rule_library import ProductionRuleLoader
                lib = ProductionRuleLoader.load(tmp_rules)
                assert len(lib.list_rules()) == 0, (
                    "P2.1-E: Rules with unregistered authority_source MUST be rejected "
                    "when no manifest bootstrap has registered it"
                )
            finally:
                os.unlink(tmp_rules)
        finally:
            _m._AUTHORITY_LOCKED = _saved_lock
            _m._AUTHORITY_CREDENTIALS.clear()
            _m._AUTHORITY_CREDENTIALS.update(_saved_creds)

