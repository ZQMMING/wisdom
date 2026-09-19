# -*- coding: utf-8 -*-
import csv, sys
from collections import Counter
sys.path.insert(0,'.')

rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

shenruo_mismatch=[]
for r in rows:
    qs = r.get('queries','')
    text = r.get('judgment','')
    if '身弱' in text:
        idx = text.find('身弱')
        context = text[max(0,idx-20):idx+len('身弱')+20]
        exclude=['俗以', '俗见', '俗论', '俗', '财多', '煞重', '泄重', '似乎', '看似', '弱中', '弱变', '弱不', '非身弱', '不论身', '身弱者']
        if any(ex in context for ex in exclude):
            continue
        if not ('LIGHT-ROOT' in qs or 'JIRUO-WUGEN' in qs or 'JISHUAI-CONGSHENG' in qs):
            shenruo_mismatch.append(r)

root_dist=Counter(r['root_class'] for r in shenruo_mismatch)
print(f'身弱不匹配root分布: {dict(root_dist)}')
print()

# 看HEAVY的案例
heavy_cases=[r for r in shenruo_mismatch if r['root_class']=='HEAVY']
print(f'HEAVY案例数: {len(heavy_cases)}')
for r in heavy_cases[:10]:
    print(f'  {r["chart"]}: {r["queries"][:80]}')
    print(f'    {r["judgment"][:80]}')
