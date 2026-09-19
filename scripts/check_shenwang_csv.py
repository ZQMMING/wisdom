# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0,'.')
rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

def check_shenwang(r):
    qs=r['queries']
    return 'HEAVY-ROOT' in qs or 'YIN-PARTY' in qs or 'BIJIE-PARTY' in qs

exclude=['俗以','俗见','俗论','俗','似乎','看似','身旺者','身旺逢','必要身旺','不宜身旺','身旺之地','非原命','身旺财旺','身旺用财','身旺喜','身旺也','此命身旺','举例如','又如','若逢','若月令']

mismatch=[]
for r in rows:
    text=r['judgment']
    if '身旺' not in text:
        continue
    idx=text.find('身旺')
    context=text[max(0,idx-20):idx+len('身旺')+20]
    if any(ex in context for ex in exclude):
        continue
    if not check_shenwang(r):
        mismatch.append(r)

print(f'身旺不匹配: {len(mismatch)}')
for r in mismatch[:11]:
    print(f"\n{r['chart']}: root={r['root_class']}")
    print(f"  queries: {r['queries'][:150]}")
    idx=r['judgment'].find('身旺')
    print(f"  context: ...{r['judgment'][max(0,idx-30):idx+len('身旺')+30]}...")
