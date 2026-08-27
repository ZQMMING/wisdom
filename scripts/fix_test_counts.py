"""Fix all test reference counts for T4 activated rules (28 total, not 12/22)."""
from pathlib import Path

test_file = Path("tests/test_rule_engine.py")
content = test_file.read_text(encoding="utf-8")

# Fix docstrings and comments
content = content.replace("# C. 12 activated rules", "# C. 28 activated rules")
content = content.replace(
    '"""12 EVENT_TOPIC rules must be loadable, schema-valid, and semantically sound."""',
    '"""28 EVENT_TOPIC rules must be loadable, schema-valid, and semantically sound."""'
)
content = content.replace("test_all_22_have_required_schema_fields", "test_all_28_have_required_schema_fields")
content = content.replace("test_all_12_have_resolvable_evidence", "test_all_28_have_resolvable_evidence")
content = content.replace(
    "Every evidence_ref points to a real .json file (E-K2G-SHIPI-XXX)",
    "Every evidence_ref points to a real .json file"
)

# Fix test names and assertions
content = content.replace("test_loads_22_event_topic_rules", "test_loads_28_event_topic_rules")
content = content.replace("Exactly 22 active EVENT_TOPIC rules loaded", "Exactly 28 active EVENT_TOPIC rules loaded")
content = content.replace('expected 22 EVENT_TOPIC rules, got', 'expected 28 EVENT_TOPIC rules, got')
content = content.replace('expected 12 EVENT_TOPIC rules, got', 'expected 28 EVENT_TOPIC rules, got')
content = content.replace("Should match the 28 active EVENT_TOPIC rules", "Should match the 28 active EVENT_TOPIC rules")
content = content.replace('self.assertEqual(len(engine.rules), 12)', 'self.assertEqual(len(engine.rules), 28)')

# Fix the ontology_type assertion (should include all types, not just 3)
content = content.replace(
    '(\"MARRIAGE_RISK\", \"HEALTH_RISK\", \"MARRIAGE_OPPORTUNITY\"))',
    '(\"MARRIAGE_RISK\", \"HEALTH_RISK\", \"MARRIAGE_OPPORTUNITY\", \"WEALTH_OPPORTUNITY\", \"CAREER_RISK\", \"ACADEMIC_OPPORTUNITY\"))'
)

test_file.write_text(content, encoding="utf-8")
print("Fixed test_rule_engine.py")

# Also fix test_db_runtime.py count
db_file = Path("tests/test_db_runtime.py")
content2 = db_file.read_text(encoding="utf-8")
content2 = content2.replace('self.assertEqual(first["rules"], 55)', 'self.assertEqual(first["rules"], 88)')
content2 = content2.replace('self.assertEqual(first["evidence"], 52)', 'self.assertEqual(first["evidence"], 66)')
content2 = content2.replace('self.assertEqual(cur.fetchone()[0], 55)', 'self.assertEqual(cur.fetchone()[0], 88)')
db_file.write_text(content2, encoding="utf-8")
print("Fixed test_db_runtime.py")
