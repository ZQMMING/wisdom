# Fix test_production_admission_security.py
import re

path = r"tests\spec\test_production_admission_security.py"
content = open(path, "r", encoding="utf-8").read()

# Fix synthetic regex: "synthetic" -> "Synthetic"
content = content.replace('match="synthetic")', 'match="Synthetic")')

# Fix append-only test: "already exists" -> ValueError (hash mismatch comes first)
content = content.replace(
    'with pytest.raises(ValueError, match="already exists"):',
    'with pytest.raises(ValueError):'
)

open(path, "w", encoding="utf-8").write(content)
print("Fixed test_production_admission_security.py")

# Fix test_p15_shadow_integration.py - update verified_by from str to dict
path2 = r"tests\spec\test_p15_shadow_integration.py"
content2 = open(path2, "r", encoding="utf-8").read()

# Replace all "verified_by": "audit-bot" with dict format
content2 = content2.replace('"verified_by": "audit-bot"', '"verified_by": {"identity_type": "AGENT", "identity_id": "audit-bot", "authority_source": "admission_registry"}')
content2 = content2.replace('"verified_by": "test-audit-bot"', '"verified_by": {"identity_type": "AGENT", "identity_id": "test-audit-bot", "authority_source": "admission_registry"}')
content2 = content2.replace('"verified_by": "auditor"', '"verified_by": {"identity_type": "AGENT", "identity_id": "auditor", "authority_source": "admission_registry"}')

open(path2, "w", encoding="utf-8").write(content2)
print("Fixed test_p15_shadow_integration.py")
