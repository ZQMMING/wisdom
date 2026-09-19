# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0,'.')
rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

def check_shenwang(r):
    qs=r['queries']
    return 'HEAVY-ROOT' in qs or 'YIN-PARTY' in qs or 'BIJIE-PARTY' in qs or 'JIWANG-HUAIJI' in qs

exclude=['俗以','俗见','俗论','俗','似乎','看似','身旺者','身旺逢','必要身旺','不宜身旺','身旺之地','非原命','身旺财旺','身旺用财','身旺喜','身旺也','此命身旺','举例如','又如','若逢','若月令','运行身旺','行运身旺','岁运身旺','身旺/身弱','若身旺','身旺无杂','身旺为官','最重日元身旺']

mismatch=[]
for r in rows:
    text=r['judgment']
    if '身旺' not in text:
        continue
    idx=text.find('身旺')
    context=text[max(0,idx-10):idx+len('身旺')+10]
    if any(ex in context for ex in exclude):
        continue
    if not check_shenwang(r):
        mismatch.append(r)

print(f'身旺不匹配: {len(mismatch)}')
for r in mismatch:
    print(f"\nchart: {r['chart']}")
    print(f"root_class: {r['root_class']}")
    print(f"queries: {r['queries'][:200]}")
    idx=r['judgment'].find('身旺')
    print(f"身旺上下文: ...{r['judgment'][max(0,idx-40):idx+len('身旺')+40]}...")
