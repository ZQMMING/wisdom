# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0,'.')
rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

exclude=['俗以','俗见','俗论','俗','似乎','看似','臣盛君衰极','地衰极','火衰极','土衰极','金衰极','水衰极','木衰极','财衰极','印衰极','官衰极','杀衰极','衰极矣']

mismatch=[]
for r in rows:
    text=r['judgment']
    if '衰极' not in text:
        continue
    idx=text.find('衰极')
    context=text[max(0,idx-20):idx+len('衰极')+20]
    if any(ex in context for ex in exclude):
        continue
    if 'JISHUAI-CONGSHENG' not in r['queries']:
        mismatch.append(r)

print(f'衰极不匹配: {len(mismatch)}')
for r in mismatch:
    print(f"\nchart: {r['chart']}")
    print(f"root_class: {r['root_class']}")
    print(f"queries: {r['queries'][:200]}")
    idx=r['judgment'].find('衰极')
    print(f"衰极上下文: ...{r['judgment'][max(0,idx-40):idx+len('衰极')+40]}...")
