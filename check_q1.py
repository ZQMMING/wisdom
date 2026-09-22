import json
with open('tests/cases_l1_v1.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

for c in data:
    if c['id'] == 'Q1':
        print(f"Q1 provenance: {c.get('provenance', '未知')}")
        print(f"Q1 note: {c.get('provenance_note', '无')}")
        print(f"Q1 expect: {c.get('expect_type')} / {c.get('expect_confidence')}")
