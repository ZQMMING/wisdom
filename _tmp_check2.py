import json
with open('tests/cases_l1_v1.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

# 风险月份：新G2会新增当令的月份
risk_months = {
    '木': ['亥', '未'],
    '火': ['寅', '戌'],
    '土': ['午'],
    '金': ['巳', '丑'],
    '水': ['申', '辰'],
}

print('=== 风险月份用例清单 ===')
for c in data:
    key = c.get('key', '')
    if len(key) >= 4:
        month_branch = key[3]
        for hx, months in risk_months.items():
            if month_branch in months:
                print(f"{c['id']:8s} key={key} 月支={month_branch} 化神={hx}? 期望={c.get('expect_confidence', '?')}")
                break
