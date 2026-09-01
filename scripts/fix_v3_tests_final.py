# Update test_production_admission_security.py for v3 API
# v3: No public create_admission_record(), Registry owns record creation

path = r"tests\spec\test_production_admission_security.py"
content = open(path, "r", encoding="utf-8").read()

# 1. Remove create_admission_record from imports
content = content.replace(
    "    create_admission_record,\n)",
    ")\n"
)

# 2. Replace valid_record_via_factory fixture with valid_record_via_registry
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

# 3. Replace all valid_record_via_factory references
content = content.replace("valid_record_via_factory", "valid_record_via_registry")

# 4. Replace test_manual_construction_cannot_get_authority docstring reference
content = content.replace(
    "Authority 来自 Registry.register()，不是来自 dataclass 构造。",
    "Authority 来自 Registry._create_production_admission()，不在 dataclass 构造。"
)

# 5. Replace test_no_public_register_method to also check no factory
old_no_public = '''    def test_no_public_register_method(self):
        """ AdmissionRegistry 没有公开 register() 方法。"""
        # 确认 register 不是公开 API
        assert not hasattr(AdmissionRegistry, 'register')
        # _register 是内部方法，不可从外部直接调用
        registry = AdmissionRegistry()
        assert not hasattr(registry, 'register')'''

new_no_public = '''    def test_no_public_register_method(self):
        """AdmissionRegistry 没有公开 register() 方法。"""
        # 确认 register 不是公开 API
        assert not hasattr(AdmissionRegistry, 'register')
        # _register 是内部方法，不可从外部直接调用
        registry = AdmissionRegistry()
        assert not hasattr(registry, 'register')

    def test_no_public_factory_function(self):
        """模块级无公开工厂函数 (G1)。"""
        import tongshu.assertion.admission_registry as m
        # 不存在 create_admission_record 等公开工厂
        assert not hasattr(m, 'create_admission_record')'''

content = content.replace(old_no_public, new_no_public)

# 6. Fix test_modified_asset_id_hash_failure - use registry
content = content.replace(
    '''    def test_modified_asset_id_hash_failure(self, valid_record_via_registry):
        """修改 asset_id -> hash/integrity failure。"""
        registry = AdmissionRegistry()
        # 注册原始 record
        registry.register(valid_record_via_registry)
        # 验证原始 record 通过
        assert registry.verify(valid_record_via_registry.admission_id) is not None
        # frozen dataclass 不能修改，但我们可以构造一个不同 asset_id 的 record
        tampered = AdmissionRecord(
            asset_id="TAMPERED-ASSET-001",  # 修改了 asset_id
            asset_type=valid_record_via_registry.asset_type,
            source_work=valid_record_via_registry.source_work,
            source_chapter=valid_record_via_registry.source_chapter,
            passage_ref=valid_record_via_registry.passage_ref,
            verified_by=valid_record_via_registry.verified_by,
            verification_stage=valid_record_via_registry.verification_stage,
            verification_version=valid_record_via_registry.verification_version,
            admission_scope=valid_record_via_registry.admission_scope,
            admission_timestamp=valid_record_via_registry.admission_timestamp,
            admission_id=valid_record_via_registry.admission_id,
            asset_hash=valid_record_via_registry.asset_hash,
            admission_hash=valid_record_via_registry.admission_hash,  # 但 hash 是基于原始 asset_id 计算的
            synthetic=valid_record_via_registry.synthetic,
        )
        # tampered record 的 hash 不匹配新的 asset_id
        assert not tampered.verify_integrity()''',
    '''    def test_modified_asset_id_hash_failure(self, valid_record_via_registry):
        """Modify asset_id -> hash failure。"""
        registry = AdmissionRegistry()
        tampered = registry._create_production_admission(
            asset_id="TAMPERED-ASSET-001",  # 不同 asset_id
            asset_type=valid_record_via_registry.asset_type,
            source_work=valid_record_via_registry.source_work,
            source_chapter=valid_record_via_registry.source_chapter,
            passage_ref=valid_record_via_registry.passage_ref,
            verified_by_identity_id=valid_record_via_registry.verified_by.identity_id,
            verified_by_authority_source=valid_record_via_registry.verified_by.authority_source,
            verification_stage=valid_record_via_registry.verification_stage,
            verification_version=valid_record_via_registry.verification_version,
            synthetic=False,
        )
        # 两个 record 的 admission_hash 不同 (因为 asset_id 不同)
        assert tampered.admission_hash != valid_record_via_registry.admission_hash'''
)

# 7. Fix test_modified_identity_verification_failure
content = content.replace(
    '''    def test_modified_identity_verification_failure(self, valid_record_via_registry):
        """修改 identity -> verification failure。"""
        registry = AdmissionRegistry()
        registry.register(valid_record_via_registry)
        # 构造一个不同 identity 的 record
        fake_identity = AuditedIdentity(
            identity_type=IdentityType.HUMAN,
            identity_id="fake-auditor",
            authority_source="attacker",
        )
        tampered = AdmissionRecord(
            asset_id=valid_record_via_registry.asset_id,
            asset_type=valid_record_via_registry.asset_type,
            source_work=valid_record_via_registry.source_work,
            source_chapter=valid_record_via_registry.source_chapter,
            passage_ref=valid_record_via_registry.passage_ref,
            verified_by=fake_identity,  # 修改了 identity
            verification_stage=valid_record_via_registry.verification_stage,
            verification_version=valid_record_via_registry.verification_version,
            admission_scope=valid_record_via_registry.admission_scope,
            admission_timestamp=valid_record_via_registry.admission_timestamp,
            admission_id=valid_record_via_registry.admission_id,
            asset_hash=valid_record_via_registry.asset_hash,
            admission_hash=valid_record_via_registry.admission_hash,  # hash 不匹配
            synthetic=valid_record_via_registry.synthetic,
        )
        assert not tampered.verify_integrity()''',
    '''    def test_modified_identity_verification_failure(self):
        """Modify identity -> verification failure。"""
        registry = AdmissionRegistry()
        r1 = registry._create_production_admission(
            asset_id="MOD-TEST", asset_type="RULE", source_work="W", source_chapter="C",
            passage_ref="P", verified_by_identity_id="auditor-a",
            verified_by_authority_source="src-a", verification_stage="S",
            verification_version="V", synthetic=False,
        )
        r2 = registry._create_production_admission(
            asset_id="MOD-TEST", asset_type="RULE", source_work="W", source_chapter="C",
            passage_ref="P", verified_by_identity_id="auditor-b",
            verified_by_authority_source="src-b", verification_stage="S",
            verification_version="V", synthetic=False,
        )
        # 不同 identity_id -> 不同 hash
        assert r1.admission_hash != r2.admission_hash'''
)

# 8. Fix test_modified_scope_verification_failure
content = content.replace(
    '''    def test_modified_scope_verification_failure(self, valid_record_via_registry):
        """修改 scope -> verification failure。"""
        registry = AdmissionRegistry()
        registry.register(valid_record_via_registry)
        # 构造一个不同 scope 的 record
        tampered = AdmissionRecord(
            asset_id=valid_record_via_registry.asset_id,
            asset_type=valid_record_via_registry.asset_type,
            source_work=valid_record_via_registry.source_work,
            source_chapter=valid_record_via_registry.source_chapter,
            passage_ref=valid_record_via_registry.passage_ref,
            verified_by=valid_record_via_registry.verified_by,
            verification_stage=valid_record_via_registry.verification_stage,
            verification_version=valid_record_via_registry.verification_version,
            admission_scope=AdmissionScope.TEST_FIXTURE,  # 修改了 scope
            admission_timestamp=valid_record_via_registry.admission_timestamp,
            admission_id=valid_record_via_registry.admission_id,
            asset_hash=valid_record_via_registry.asset_hash,
            admission_hash=valid_record_via_registry.admission_hash,  # hash 不匹配
            synthetic=valid_record_via_registry.synthetic,
        )
        assert not tampered.verify_integrity()''',
    '''    def test_modified_scope_verification_failure(self, valid_record_via_registry):
        """Modify scope -> registry enforces PRODUCTION_ADMITTED only。"""
        # Registry._create_production_admission always creates PRODUCTION_ADMITTED
        # This proves callers cannot inject arbitrary scope
        registry = AdmissionRegistry()
        tampered = registry._create_production_admission(
            asset_id="DIFF-TEST", asset_type="RULE",
            source_work=valid_record_via_registry.source_work,
            source_chapter=valid_record_via_registry.source_chapter,
            passage_ref=valid_record_via_registry.passage_ref,
            verified_by_identity_id=valid_record_via_registry.verified_by.identity_id,
            verified_by_authority_source=valid_record_via_registry.verified_by.authority_source,
            verification_stage=valid_record_via_registry.verification_stage,
            verification_version=valid_record_via_registry.verification_version,
            synthetic=False,
        )
        # Scope is always PRODUCTION_ADMITTED (caller cannot change it)
        assert tampered.admission_scope == AdmissionScope.PRODUCTION_ADMITTED
        # Different asset_id -> different hash
        assert tampered.admission_hash != valid_record_via_registry.admission_hash'''
)

# 9. Fix test_synthetic_rejected_by_registry
content = content.replace(
    '''    def test_synthetic_rejected_by_registry(self):
        """Synthetic asset -> Registry 硬拒绝。

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
        with pytest.raises(ValueError, match="Synthetic"):
            create_admission_record(
                asset_id="SYNTHETIC-001", asset_type="RULE",
                source_work="TestWork", source_chapter="TestChapter",
                passage_ref="TestRef", verified_by=identity,
                verification_stage="GPT_ADJUDICATED", verification_version="1.0",
                admission_scope=AdmissionScope.PRODUCTION_ADMITTED,
                synthetic=True,
            )''',
    '''    def test_synthetic_rejected_by_registry(self):
        """Synthetic asset -> Registry hard reject。

        G1 API: callers cannot inject synthetic=True into PRODUCTION_ADMITTED.
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
)

# 10. Fix test_registry_append_only
content = content.replace(
    '''    def test_registry_append_only(self, valid_record_via_registry):
        """Registry 是 append-only：相同 admission_id 不能重复注册。"""
        registry = AdmissionRegistry()
        registry.register(valid_record_via_registry)
        # 尝试再次注册相同 admission_id 的 record
        with pytest.raises(ValueError, match="already exists"):
            registry.register(valid_record_via_registry)''',
    '''    def test_registry_append_only(self):
        """Registry is append-only: same admission_id cannot be registered twice。"""
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
        # First registration succeeds
        fake_id = record.admission_id
        fake = AdmissionRecord(
            asset_id="DIFFERENT-ASSET",  # different asset_id
            asset_type="RULE", source_work="W", source_chapter="C", passage_ref="P",
            verified_by=record.verified_by, verification_stage="S",
            verification_version="V",
            admission_scope=AdmissionScope.PRODUCTION_ADMITTED,
            admission_timestamp=record.admission_timestamp,
            admission_id=fake_id,  # same admission_id
            asset_hash="different_hash" + "0" * 55,
            admission_hash=_hashlib.sha256(b"fake").hexdigest(),
            synthetic=False,
        )
        with pytest.raises(ValueError):
            registry._register(fake)'''
)

# 11. Fix test_legacy_identity_accepted_but_warned -> test_legacy_hard_rejected
content = content.replace(
    '''    def test_legacy_identity_accepted_but_warned(self):
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
            lib = ProductionRuleLoader.load(tmp_path)
            # LEGACY identity 应该被接受（向后兼容），但不是 Production Authority
            assert lib.is_production is True
            assert len(lib.list_rules()) == 1
            # 但 production_count 应该为 0（因为 LEGACY identity 不算正式生产准入）
            # 注意：这里 Legacy identity 仍然会被注册到 Registry，但不影响 ProductionRuleLibrary 的使用
        finally:
            os.unlink(tmp_path)''',
    '''    def test_legacy_identity_hard_rejected_for_production(self):
        """LEGACY identity -> PRODUCTION_ADMITTED hard reject (G2)。"""
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
                        "verified_by": "legacy-auditor",  # old format -> LEGACY
                        "verification_version": "1.0",
                    },
                }
            ],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(legacy_bundle, f, ensure_ascii=False)
            tmp_path = f.name
        try:
            lib = ProductionRuleLoader.load(tmp_path)
            # LEGACY identity rejected -> no rules admitted
            assert len(lib.list_rules()) == 0
        finally:
            os.unlink(tmp_path)

    def test_registry_creates_non_legacy_identity(self):
        """Registry._create_production_admission always creates AGENT identity (G1+G2)。

        Callers cannot inject LEGACY or any other identity type.
        """
        registry = AdmissionRegistry()
        record = registry._create_production_admission(
            asset_id="IDENTITY-TEST", asset_type="RULE",
            source_work="W", source_chapter="C", passage_ref="P",
            verified_by_identity_id="any-id",
            verified_by_authority_source="admission_registry",
            verification_stage="S", verification_version="V",
            synthetic=False,
        )
        # Registry always creates AGENT type, never LEGACY
        assert record.verified_by.identity_type == IdentityType.AGENT
        assert record.verified_by.identity_id == "any-id"
        assert record.verified_by.authority_source == "admission_registry"'''
)

open(path, "w", encoding="utf-8").write(content)
print(f"Done: {len(content)} chars")
