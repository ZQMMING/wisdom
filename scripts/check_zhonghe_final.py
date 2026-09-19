# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0,'.')
rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

exclude=['俗以','俗见','俗论','俗','似乎','看似']

mismatch=[]
for r in rows:
    text=r['judgment']
    if '中和' not in text:
        continue
    idx=text.find('中和')
    context=text[max(0,idx-10):idx+len('中和')+10]
    if any(ex in context for ex in exclude):
        continue
    if 'ZHONG-HE' not in r['queries']:
        mismatch.append(r)

print(f'中和不匹配: {len(mismatch)}')
for r in mismatch:
    print(f"\nchart: {r['chart']}")
    print(f"root_class: {r['root_class']}")
    print(f"queries: {r['queries'][:200]}")
    idx=r['judgment'].find('中和')
    print(f"中和上下文: ...{r['judgment'][max(0,idx-50):idx+len('中和')+50]}...")
