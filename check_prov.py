import json
with open('tests/cases_l1_v1.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

for c in data:
    if c['id'] in ['P2', 'Q4']:
        print(f"{c['id']}: provenance={c.get('provenance','?')}, kind={c.get('kind','?')}")
