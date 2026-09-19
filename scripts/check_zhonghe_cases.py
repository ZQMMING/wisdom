# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0,'.')

rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

zhonghe_cases=[]
for r in rows:
    text=r.get('judgment','')
    if '中和' in text and '俗以' not in text and '似乎' not in text:
        zhonghe_cases.append(r)

print(f'中和案例数: {len(zhonghe_cases)}')
print()
for r in zhonghe_cases[:10]:
    print(f'{r["chart"]}: root={r["root_class"]}, queries={r["queries"][:80]}')
    print(f'  judgment: {r["judgment"][:100]}')
    print()
