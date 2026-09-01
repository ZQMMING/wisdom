# Fix remaining test references for v3 API
import re

path = r"tests\spec\test_production_admission_security.py"
content = open(path, "r", encoding="utf-8").read()

# 1. Replace all valid_record_via_factory -> valid_record_via_registry
content = content.replace("valid_record_via_factory", "valid_record_via_registry")

# 2. Replace create_admission_record calls with registry._create_production_admission
# Pattern: create_admission_record(\n            asset_id=..., verified_by=valid_record..., ...)
# We need to replace these specific blocks

# Fix test_modified_asset_id_hash_failure
content = content.replace(
    '        tampered = create_admission_record(\n            asset_id="TAMPERED-ASSET-001",  # 不同 asset_id\n            asset_type=valid_record_via_registry.asset_type,\n            source_work=valid_record_via_registry.source_work,\n            source_chapter=valid_record_via_registry.source_chapter,\n            passage_ref=valid_record_via_registry.passage_ref,\n            verified_by=valid_record_via_registry.verified_by,\n            verification_stage=valid_record_via_registry.verification_stage,\n            verification_version=valid_record_via_registry.verification_version,\n            admission_scope=valid_record_via_registry.admission_scope,\n            synthetic=False,\n        )',
    '        tampered = registry._create_production_admission(\n            asset_id="TAMPERED-ASSET-001",  # 不同 asset_id\n            asset_type=valid_record_via_registry.asset_type,\n            source_work=valid_record_via_registry.source_work,\n            source_chapter=valid_record_via_registry.source_chapter,\n            passage_ref=valid_record_via_registry.passage_ref,\n            verified_by_identity_id=valid_record_via_registry.verified_by.identity_id,\n            verified_by_authority_source=valid_record_via_registry.verified_by.authority_source,\n            verification_stage=valid_record_via_registry.verification_stage,\n            verification_version=valid_record_via_registry.verification_version,\n            synthetic=False,\n        )'
)

# Fix test_modified_identity_verification_failure
content = content.replace(
    '        r1 = create_admission_record(\n            asset_id="MOD-TEST", asset_type="RULE", source_work="W", source_chapter="C",\n            passage_ref="P", verified_by=identity1, verification_stage="S",\n            verification_version="V", admission_scope=AdmissionScope.PRODUCTION_ADMITTED,\n        )\n        r2 = create_admission_record(\n            asset_id="MOD-TEST", asset_type="RULE", source_work="W", source_chapter="C",\n            passage_ref="P", verified_by=identity2, verification_stage="S",\n            verification_version="V", admission_scope=AdmissionScope.PRODUCTION_ADMITTED,\n        )',
    '        r1 = registry._create_production_admission(\n            asset_id="MOD-TEST", asset_type="RULE", source_work="W", source_chapter="C",\n            passage_ref="P", verified_by_identity_id="auditor-a",\n            verified_by_authority_source="src-a", verification_stage="S",\n            verification_version="V", synthetic=False,\n        )\n        r2 = registry._create_production_admission(\n            asset_id="MOD-TEST", asset_type="RULE", source_work="W", source_chapter="C",\n            passage_ref="P", verified_by_identity_id="auditor-b",\n            verified_by_authority_source="src-b", verification_stage="S",\n            verification_version="V", synthetic=False,\n        )'
)

# Fix test_modified_scope_verification_failure
content = content.replace(
    '        tampered = create_admission_record(\n            asset_id=valid_record_via_registry.asset_id,\n            asset_type=valid_record_via_registry.asset_type,\n            source_work=valid_record_via_registry.source_work,\n            source_chapter=valid_record_via_registry.source_chapter,\n            passage_ref=valid_record_via_registry.passage_ref,\n            verified_by=valid_record_via_registry.verified_by,\n            verification_stage=valid_record_via_registry.verification_stage,\n            verification_version=valid_record_via_registry.verification_version,\n            admission_scope=AdmissionScope.TEST_FIXTURE,  # 修改了 scope\n            synthetic=False,\n        )',
    '        # 不能构造不同 scope 的 record：registry 固定创建 PRODUCTION_ADMITTED\n        # 此处只验证 hash 唯一性：不同参数产生不同 hash\n        tampered = registry._create_production_admission(\n            asset_id="DIFF-SCOPE-TEST",  # 不同 asset_id\n            asset_type=valid_record_via_registry.asset_type,\n            source_work=valid_record_via_registry.source_work,\n            source_chapter=valid_record_via_registry.source_chapter,\n            passage_ref=valid_record_via_registry.passage_ref,\n            verified_by_identity_id=valid_record_via_registry.verified_by.identity_id,\n            verified_by_authority_source=valid_record_via_registry.verified_by.authority_source,\n            verification_stage=valid_record_via_registry.verification_stage,\n            verification_version=valid_record_via_registry.verification_version,\n            synthetic=False,\n        )'
)

open(path, "w", encoding="utf-8").write(content)
print(f"Fixed: {len(content)} chars")
