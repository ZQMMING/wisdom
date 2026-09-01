# Fix all LEGACY verified_by strings in test files
import os

files = [
    r"tests\spec\test_cross_domain_integration.py",
    r"tests\spec\test_p14_semantic_audit.py",
]

replacements = [
    ('"verified_by": "test-audit-bot"', '"verified_by": {"identity_type": "AGENT", "identity_id": "test-audit-bot", "authority_source": "admission_registry"}'),
    ('"verified_by": "audit-bot-v1"', '"verified_by": {"identity_type": "AGENT", "identity_id": "audit-bot-v1", "authority_source": "admission_registry"}'),
    ('"verified_by": "auditor"', '"verified_by": {"identity_type": "AGENT", "identity_id": "auditor", "authority_source": "admission_registry"}'),
]

for fpath in files:
    content = open(fpath, "r", encoding="utf-8").read()
    before = len(content)
    for old, new in replacements:
        content = content.replace(old, new)
    after = len(content)
    open(fpath, "w", encoding="utf-8").write(content)
    print(f"Fixed {fpath}: {before} -> {after} ({after - before} chars)")
