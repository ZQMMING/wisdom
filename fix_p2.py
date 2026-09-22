import json
with open('tests/cases_l1_v1.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

for c in data:
    if c['id'] == 'P2':
        c['expect_pattern'] = None
        c['expect_type'] = None
        c['expect_confidence'] = 'REJECT'
        c['provenance_note'] += '；修正：局不全+不见辰→REJECT（b3逢龙升档键生效）'

with open('tests/cases_l1_v1.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('updated')
