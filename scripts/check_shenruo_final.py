# -*- coding: utf-8 -*-
import csv, sys, json
sys.path.insert(0,'.')
rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

def check_shenruo(r):
    qs=r['queries']
    root=r['root_class']
    if 'LIGHT-ROOT' in qs or 'JIRUO-WUGEN' in qs or 'JISHUAI-CONGSHENG' in qs or 'CAIDUO-SHENRUAN' in qs or 'SHAZHONG-SHENQING' in qs or 'HE-HUASHEN-DESHI' in qs:
        return True
    if 'ROOT-STRUCK' in qs and root=='HEAVY':
        return True
    if root=='HEAVY' and 'HEAVY-ROOT' not in qs:
        return True
    return False

exclude=['俗以','俗见','俗论','俗','财多','煞重','泄重','似乎','看似','弱中','弱变','弱不','非身弱','不论身','身弱者']

mismatch=[]
for r in rows:
    text=r['judgment']
    if '身弱' not in text:
        continue
    idx=text.find('身弱')
    context=text[max(0,idx-20):idx+len('身弱')+20]
    if any(ex in context for ex in exclude):
        continue
    if not check_shenruo(r):
        mismatch.append(r)

print(f'身弱不匹配: {len(mismatch)}')
for r in mismatch:
    print(f"\n{'='*60}")
    print(f"chart: {r['chart']}")
    print(f"root_class: {r['root_class']}")
    print(f"queries: {r['queries']}")
    idx=r['judgment'].find('身弱')
    print(f"身弱上下文: ...{r['judgment'][max(0,idx-40):idx+len('身弱')+40]}...")
