# Add registry = AdmissionRegistry() to three failing tests
path = r"tests\spec\test_production_admission_security.py"
content = open(path, "r", encoding="utf-8").read()

# Fix test_modified_asset_id_hash_failure
content = content.replace(
    "def test_modified_asset_id_hash_failure(self, valid_record_via_registry):\n        \"\"\"❌ 修改 asset_id → hash/integrity failure。\"",
    "def test_modified_asset_id_hash_failure(self, valid_record_via_registry):\n        registry = AdmissionRegistry()\n        \"\"\"❌ 修改 asset_id → hash/integrity failure。"
)

# Fix test_modified_identity_verification_failure
content = content.replace(
    "def test_modified_identity_verification_failure(self):\n        \"\"\"❌ 修改 identity → verification failure。\"",
    "def test_modified_identity_verification_failure(self):\n        registry = AdmissionRegistry()\n        \"\"\"❌ 修改 identity → verification failure。"
)

# Fix test_modified_scope_verification_failure
content = content.replace(
    "def test_modified_scope_verification_failure(self, valid_record_via_registry):\n        \"\"\"❌ 修改 scope → verification failure。\"",
    "def test_modified_scope_verification_failure(self, valid_record_via_registry):\n        registry = AdmissionRegistry()\n        \"\"\"❌ 修改 scope → verification failure。"
)

open(path, "w", encoding="utf-8").write(content)
print("Fixed")
