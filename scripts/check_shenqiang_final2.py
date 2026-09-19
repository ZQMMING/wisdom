# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0,'.')
rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

def check_shenqiang(r):
    qs=r['queries']
    return 'HEAVY-ROOT' in qs or 'YIN-PARTY' in qs or 'BIJIE-PARTY' in qs or 'JIWANG-HUAIJI' in qs

exclude=['俗以','俗见','俗论','俗','似乎','看似','身强者','身强敌杀','身强财弱','身强杀浅','微论身强身弱']

mismatch=[]
for r in rows:
    text=r['judgment']
    if '身强' not in text:
        continue
    idx=text.find('身强')
    context=text[max(0,idx-10):idx+len('身强')+10]
    if any(ex in context for ex in exclude):
        continue
    if not check_shenqiang(r):
        mismatch.append(r)

print(f'身强不匹配: {len(mismatch)}')
for r in mismatch:
    print(f"\nchart: {r['chart']}")
    print(f"root_class: {r['root_class']}")
    print(f"queries: {r['queries'][:200]}")
    idx=r['judgment'].find('身强')
    print(f"身强上下文: ...{r['judgment'][max(0,idx-60):idx+len('身强')+60]}...")
