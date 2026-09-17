# -*- coding: utf-8 -*-
"""从断语库旺衰类提取真命例: 四柱+日元/日主+大运+旺弱断语."""
import json, re, sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build

d = json.load(open(r'D:\顺天系统资料\五部经典断语库\03_综合索引\all_duanyu.json', encoding='utf-8'))
ws = [x for x in d if x['primary_category'] == '旺衰类']
gz = re.compile(r'([甲乙丙丁戊己庚辛壬癸])([子丑寅卯辰巳午未申酉戌亥])')

# 真命例特征: 含"日元"或"日主"或"此造", 且含>=8个干支对
cases = []
for x in ws:
    t = x['text']
    if not re.search(r'日元|日主|此造|此命', t): continue
    pairs = gz.findall(t)
    if len(pairs) < 8: continue
    # 提取前4对为四柱
    four = pairs[:4]
    pillars = {'year': list(four[0]), 'month': list(four[1]), 'day': list(four[2]), 'hour': list(four[3])}
    # 找旺弱断语
    tags = []
    for kw in ['身旺', '身弱', '日主旺', '日主弱', '得地', '得时', '得令', '失令', '得势', '身强', '身衰', '旺', '衰', '强', '弱']:
        if kw in t: tags.append(kw)
    cases.append({'classic': x['classic'], 'pillars': pillars, 'tags': tags, 'text': t[:150]})

print(f'旺衰类真命例: {len(cases)}')
# 跑引擎看 root 分布
from collections import Counter
root_dist = Counter()
ok = 0
for c in cases:
    try:
        f = build(c['pillars'])
        hst = {c['pillars'][k][1]: f['hidden_stems'][k] for k in ('year','month','day','hour')}
        from engines.common.daymaster_root_class import build_root_classes
        rc = build_root_classes(c['pillars'], hst)
        root_dist[rc['root_weight_class'] if 'root_weight_class' in rc else rc.get('has_root')] += 1
        ok += 1
    except Exception as e:
        pass
print(f'跑通: {ok}/{len(cases)}')
print('root分布:', dict(root_dist))
# 打印前10个案例
for i, c in enumerate(cases[:10]):
    s = ''.join(c['pillars']['year']+c['pillars']['month']+c['pillars']['day']+c['pillars']['hour'])
    print(f"  {i+1}. {c['classic'][:6]} {s} tags={c['tags'][:6]}")
