import json
with open('tests/cases_l1_v1.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

for c in data:
    if c['id'] == 'Q1':
        c['expect_confidence'] = 'MID'
        c['provenance_note'] += '；修正：辰中癸水余气算根（root_qi口径统一）'

with open('tests/cases_l1_v1.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('updated Q1')
