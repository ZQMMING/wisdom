# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0,'.')

rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

ruoji_cases=[]
for r in rows:
    text=r.get('judgment','')
    if '弱极' in text and '俗以' not in text and '似乎' not in text:
        ruoji_cases.append(r)

print(f'弱极案例数: {len(ruoji_cases)}')
print()
for r in ruoji_cases:
    print(f'{r["chart"]}: root={r["root_class"]}')
    print(f'  queries: {r["queries"]}')
    print(f'  two_side: {r.get("two_side","")[:100]}')
    print()
