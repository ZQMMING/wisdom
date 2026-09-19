# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0,'.')
rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

def check_rizhuwang(r):
    qs=r['queries']
    return 'HEAVY-ROOT' in qs or 'JIWANG-HUAIJI' in qs or 'YIN-PARTY' in qs or 'BIJIE-PARTY' in qs

exclude=['俗以','俗见','俗论','俗','似乎','看似']

mismatch=[]
for r in rows:
    text=r['judgment']
    if '日主旺' not in text:
        continue
    idx=text.find('日主旺')
    context=text[max(0,idx-20):idx+len('日主旺')+20]
    if any(ex in context for ex in exclude):
        continue
    if not check_rizhuwang(r):
        mismatch.append(r)

print(f'日主旺不匹配: {len(mismatch)}')
for r in mismatch:
    print(f"\nchart: {r['chart']}")
    print(f"root_class: {r['root_class']}")
    print(f"queries: {r['queries'][:200]}")
    idx=r['judgment'].find('日主旺')
    print(f"日主旺上下文: ...{r['judgment'][max(0,idx-40):idx+len('日主旺')+40]}...")
