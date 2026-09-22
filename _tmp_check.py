import json
with open('tests/cases_l1_v1.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

print('=== 寅/申/巳/亥月用例清单 ===')
for c in data:
    key = c.get('key', '')
    if len(key) >= 4:
        month_branch = key[3]  # 月支是第4个字
        if month_branch in ['寅', '申', '巳', '亥']:
            print(f"{c['id']:8s} key={key} 月支={month_branch} 期望={c.get('expect_confidence', '?')}")
