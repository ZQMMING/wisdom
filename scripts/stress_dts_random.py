# -*- coding: utf-8 -*-
"""从 DTS 全文批量提取 八字：YYYY MMMM DDDD HHHH, 跑引擎看整体分布."""
import re, sys, random, collections
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_branch_tier import build_branch_tiers
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.daymaster_power_network import build_power_network
from engines.common.daymaster_power_queries import run_queries

# 干支拼音->中文 (DTS用中文干支)
GZ = {'甲':'甲','乙':'乙','丙':'丙','丁':'丁','戊':'戊','己':'己','庚':'庚','辛':'辛','壬':'壬','癸':'癸',
      '子':'子','丑':'丑','寅':'寅','卯':'卯','辰':'辰','巳':'巳','午':'午','未':'未','申':'申','酉':'酉','戌':'戌','亥':'亥'}

lines = open(r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt', encoding='utf-8').read().splitlines()
pat = re.compile(r'八字[：:]\s*([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s*([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s*([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s*([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])')
charts = []
for ln in lines:
    m = pat.search(ln)
    if m:
        four = [list(m.group(i)) for i in range(1, 5)]  # [年柱干/支, ...]
        charts.append({'year': four[0], 'month': four[1], 'day': four[2], 'hour': four[3]})
print(f'提取四柱: {len(charts)}')

random.seed(42)
sample = random.sample(charts, min(150, len(charts)))
root_dist = collections.Counter()
q_dist = collections.Counter()
errors = []
for i, p in enumerate(sample):
    try:
        f = build(p); pa = build_power_structure(p)
        hst = {p[k][1]: f['hidden_stems'][k] for k in ('year','month','day','hour')}
        rc = build_root_classes(p, hst); tc = build_tou_cang(f); wx = build_wang_xiang(f, f['day_stem'])
        rr = build_root_relations(rc, f['combination_facts']); ts = build_two_side(rc, tc, rr)
        bt = build_branch_tiers(p, f); th = build_tian_he(p, f)
        net = build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th)
        root_dist[net['dimensions']['ROOT']['root_weight_class']] += 1
        for q in run_queries(net):
            q_dist[(q['query_id'].split('QUERY-')[-1], q['state'])] += 1
    except Exception as e:
        errors.append((i, ''.join(p['year']+p['month']+p['day']+p['hour']), repr(e)[:100]))

print(f'\n成功: {len(sample)-len(errors)}/{len(sample)}, 崩溃: {len(errors)}')
for e in errors[:10]: print('  ERR', e)
print('\n--- root_weight_class 分布 ---')
for k, v in root_dist.most_common(): print(f'  {k:10s} {v}')
print('\n--- query state 分布 (只看SUPPORTED) ---')
for q in sorted(set(q for q, _ in q_dist)):
    s = q_dist[(q, 'SUPPORTED')]
    if s: print(f'  {q:22s} SUPPORTED={s}')
