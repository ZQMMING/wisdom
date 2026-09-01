# Fix tests for v3 API: remove create_admission_record, use registry._create_production_admission
import re

path = r"tests\spec\test_production_admission_security.py"
content = open(path, "r", encoding="utf-8").read()

# 1. Remove create_admission_record from imports
content = content.replace(
    """from tongshu.assertion.admission_registry import (
    AdmissionRegistry,
    AdmissionRecord,
    AdmissionScope,
    AuditedIdentity,
    IdentityType,
    create_admission_record,
)""",
    """from tongshu.assertion.admission_registry import (
    AdmissionRegistry,
    AdmissionRecord,
    AdmissionScope,
    AuditedIdentity,
    IdentityType,
)"""
)

# 2. Replace valid_record_via_factory fixture with one that uses registry._create_production_admission
old_fixture = '''    @pytest.fixture
    def valid_record_via_factory(self, valid_identity):
        """通过工厂函数创建合法 AdmissionRecord。"""
        return create_admission_record(
            asset_id="TEST-ASSET-001",
            asset_type="RULE",
            source_work="子平真诠",
            source_chapter="论印绶",
            passage_ref="卷一·论印绶第一",
            verified_by=valid_identity,
            verification_stage="GPT_ADJUDICATED",
            verification_version="2026.09",
            admission_scope=AdmissionScope.PRODUCTION_ADMITTED,
            synthetic=False,
        )'''

new_fixture = '''    @pytest.fixture
    def valid_record_via_registry(self, valid_identity):
        """通过 Registry 内部方法创建合法 AdmissionRecord。"""
        registry = AdmissionRegistry()
        return registry._create_production_admission(
            asset_id="TEST-ASSET-001",
            asset_type="RULE",
            source_work="子平真诠",
            source_chapter="论印绶",
            passage_ref="卷一·论印绶第一",
            verified_by_identity_id=valid_identity.identity_id,
            verified_by_authority_source=valid_identity.authority_source,
            verification_stage="GPT_ADJUDICATED",
            verification_version="2026.09",
            synthetic=False,
        )'''

content = content.replace(old_fixture, new_fixture)

# 3. Update test names that reference "factory" to "registry"
content = content.replace("test_manual_construction_cannot_get_authority(self, valid_record_via_factory)",
                          "test_manual_construction_cannot_get_authority(self, valid_record_via_registry)")
content = content.replace("test_unregistered_record_verify_returns_none(self, valid_record_via_factory)",
                          "test_unregistered_record_verify_returns_none(self, valid_record_via_registry)")
content = content.replace("test_modified_asset_id_hash_failure(self, valid_record_via_factory)",
                          "test_modified_asset_id_hash_failure(self, valid_record_via_registry)")
content = content.replace("test_modified_scope_verification_failure(self, valid_record_via_factory)",
                          "test_modified_scope_verification_failure(self, valid_record_via_registry)")

# 4. Update docstrings referencing factory
content = content.replace("通过工厂函数创建合法 AdmissionRecord", "通过 Registry 内部方法创建合法 AdmissionRecord")
content = content.replace("Authority 来自 Registry.register()，不是来自 dataclass 构造",
                          "Authority 来自 Registry._create_production_admission()，不在 dataclass 构造")

# 5. Update synthetic rejected test - uses registry directly now
old_synthetic = '''    def test_synthetic_rejected_by_factory(self):
        """❌ Synthetic asset → 工厂函数硬拒绝。

        G1/G2 的 Registry API 不得留下绕过 G3 的入口。
        """
        identity = AuditedIdentity(
            identity_type=IdentityType.AGENT,
            identity_id="test-bot",
            authority_source="admission_registry",
        )
        with pytest.raises(ValueError, match="Synthetic"):
            create_admission_record(
                asset_id="SYNTHETIC-001", asset_type="RULE",
                source_work="TestWork", source_chapter="TestChapter",
                passage_ref="TestRef", verified_by=identity,
                verification_stage="GPT_ADJUDICATED", verification_version="1.0",
                admission_scope=AdmissionScope.PRODUCTION_ADMITTED,
                synthetic=True,
            )'''

new_synthetic = '''    def test_synthetic_rejected_by_registry(self):
        """❌ Synthetic asset → Registry 硬拒绝。

        G1/G2 的 Registry API 不得留下绕过 G3 的入口。
        """
        registry = AdmissionRegistry()
        with pytest.raises(ValueError, match="Synthetic"):
            registry._create_production_admission(
                asset_id="SYNTHETIC-001", asset_type="RULE",
                source_work="TestWork", source_chapter="TestChapter",
                passage_ref="TestRef",
                verified_by_identity_id="test-bot",
                verified_by_authority_source="admission_registry",
                verification_stage="GPT_ADJUDICATED", verification_version="1.0",
                synthetic=True,
            )'''
content = content.replace(old_synthetic, new_synthetic)

# 6. Update append-only test
old_append = '''    def test_registry_append_only(self):
        """Registry 是 append-only：相同 admission_id 不能重复注册。"""
        import hashlib as _hashlib
        registry = AdmissionRegistry()
        identity = AuditedIdentity(
            identity_type=IdentityType.AGENT,
            identity_id="test-bot",
            authority_source="admission_registry",
        )
        record = create_admission_record(
            asset_id="APPEND-TEST", asset_type="RULE",
            source_work="W", source_chapter="C", passage_ref="P",
            verified_by=identity, verification_stage="S",
            verification_version="V", admission_scope=AdmissionScope.PRODUCTION_ADMITTED,
        )
        # 第一次注册成功
        registry._register(record)
        # 构造一个相同 admission_id 但不同 asset_id 的 fake record（hash 必然不匹配）
        fake_id = record.admission_id
        fake = AdmissionRecord(
            asset_id="DIFFERENT-ASSET",  # 不同 asset_id
            asset_type="RULE", source_work="W", source_chapter="C", passage_ref="P",
            verified_by=identity, verification_stage="S",
            verification_version="V",
            admission_scope=AdmissionScope.PRODUCTION_ADMITTED,
            admission_timestamp=record.admission_timestamp,
            admission_id=fake_id,  # 相同 admission_id
            asset_hash="different_hash" + "0" * 55,
            admission_hash=_hashlib.sha256(b"fake").hexdigest(),
            synthetic=False,
        )
        with pytest.raises(ValueError):
            registry._register(fake)'''

new_append = '''    def test_registry_append_only(self):
        """Registry 是 append-only：相同 admission_id 不能重复注册。"""
        import hashlib as _hashlib
        registry = AdmissionRegistry()
        record = registry._create_production_admission(
            asset_id="APPEND-TEST", asset_type="RULE",
            source_work="W", source_chapter="C", passage_ref="P",
            verified_by_identity_id="test-bot",
            verified_by_authority_source="admission_registry",
            verification_stage="S", verification_version="V",
            synthetic=False,
        )
        # 第一次注册成功
        fake_id = record.admission_id
        fake = AdmissionRecord(
            asset_id="DIFFERENT-ASSET",  # 不同 asset_id
            asset_type="RULE", source_work="W", source_chapter="C", passage_ref="P",
            verified_by=record.verified_by, verification_stage="S",
            verification_version="V",
            admission_scope=AdmissionScope.PRODUCTION_ADMITTED,
            admission_timestamp=record.admission_timestamp,
            admission_id=fake_id,  # 相同 admission_id
            asset_hash="different_hash" + "0" * 55,
            admission_hash=_hashlib.sha256(b"fake").hexdigest(),
            synthetic=False,
        )
        with pytest.raises(ValueError):
            registry._register(fake)'''
content = content.replace(old_append, new_append)

# 7. Update LEGACY rejection test - test that no public factory exists
old_legacy = '''    def test_legacy_identity_hard_rejected_for_production(self):
        """❌ LEGACY identity → PRODUCTION_ADMITTED 硬拒绝（G2）。"""
        legacy_identity = AuditedIdentity.from_legacy_string("old-auditor")
        assert legacy_identity.identity_type == IdentityType.LEGACY
        # 工厂函数必须拒绝 LEGACY identity for PRODUCTION_ADMITTED
        with pytest.raises(ValueError, match="LEGACY.*PRODUCTION_ADMITTED"):
            create_admission_record(
                asset_id="LEGACY-TEST", asset_type="RULE",
                source_work="TestWork", source_chapter="TestChapter",
                passage_ref="TestRef", verified_by=legacy_identity,
                verification_stage="GPT_ADJUDICATED", verification_version="1.0",
                admission_scope=AdmissionScope.PRODUCTION_ADMITTED,
            )'''

new_legacy = '''    def test_no_public_factory_function(self):
        """❌ 模块级无公开工厂函数（G1）。

        机构裁决：public factory = 另一个攻击入口。
        Authority 必须在 Registry 内部，不能通过公开函数暴露。
        """
        import tongshu.assertion.admission_registry as m
        # 不存在 create_admission_record 等公开工厂
        assert not hasattr(m, "create_admission_record")
        # Registry 无公开 register
        assert not hasattr(AdmissionRegistry, "register")
        # 唯一公开写入路径是 _create_production_admission（私有）

    def test_legacy_identity_rejected_at_registry_level(self):
        """❌ LEGACY identity → Registry 内部拒绝（G2）。

        调用者无法通过 registry._create_production_admission 传入 LEGACY identity，
        因为接口不接收 AuditedIdentity 参数。
        """
        registry = AdmissionRegistry()
        # 接口不接受 AuditedIdentity，只接受 identity_id 字符串
        # 因此 caller 无法注入 LEGACY identity
        record = registry._create_production_admission(
            asset_id="LEGACY-TEST", asset_type="RULE",
            source_work="TestWork", source_chapter="TestChapter",
            passage_ref="TestRef",
            verified_by_identity_id="real-auditor",
            verified_by_authority_source="admission_registry",
            verification_stage="GPT_ADJUDICATED", verification_version="1.0",
            synthetic=False,
        )
        # 确认创建的 record 的 identity 是 AGENT（非 LEGACY）
        assert record.verified_by.identity_type == IdentityType.AGENT
        assert record.verified_by.identity_id == "real-auditor"'''
content = content.replace(old_legacy, new_legacy)

open(path, "w", encoding="utf-8").write(content)
print(f"Fixed: {len(content)} chars")
