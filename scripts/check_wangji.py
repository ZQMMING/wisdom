# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0,'.')

rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

wangji_cases=[]
for r in rows:
    text=r.get('judgment','')
    if '旺极' in text:
        idx=text.find('旺极')
        ctx=text[max(0,idx-10):idx+10]
        if not any(x in ctx for x in ['地旺极','火旺极','土旺极','金旺极','水旺极','木旺极','俗以','似乎']):
            wangji_cases.append(r)

print(f'旺极案例数: {len(wangji_cases)}')
print()
for r in wangji_cases:
    print(f'{r["chart"]}: root={r["root_class"]}')
    print(f'  queries: {r["queries"][:120]}')
    print(f'  judgment: {r["judgment"][:120]}')
    print()
