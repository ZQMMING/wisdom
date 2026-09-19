# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0,'.')

rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

shenwang_mismatch=[]
for r in rows:
    qs = r.get('queries','')
    text = r.get('judgment','')
    if '身旺' in text:
        idx = text.find('身旺')
        context = text[max(0,idx-20):idx+len('身旺')+20]
        exclude=['俗以', '俗见', '俗论', '俗', '似乎', '看似', '身旺者', '身旺逢', '必要身旺']
        if any(ex in context for ex in exclude):
            continue
        if not ('HEAVY-ROOT' in qs or 'YIN-PARTY' in qs or 'BIJIE-PARTY' in qs):
            shenwang_mismatch.append(r)

print(f'身旺不匹配: {len(shenwang_mismatch)}')
print()
for r in shenwang_mismatch[:15]:
    print(f'{r["chart"]}: root={r["root_class"]}')
    print(f'  queries: {r["queries"][:100]}')
    print(f'  judgment: {r["judgment"][:100]}')
    print()
