# -*- coding: utf-8 -*-
"""从 DTS 段落JSON提取四柱, 随机150跑引擎看分布."""
import re, json, random, sys, collections
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

d = json.load(open(r'D:\顺天系统资料\shuntian\data\classics\original\DTS_滴天髓_段落数据.json', encoding='utf-8'))
pat = re.compile(r'([甲乙丙丁戊己庚辛壬癸])([子丑寅卯辰巳午未申酉戌亥])')
# 从每段抓所有干支对, 每4个组成一柱
charts = []
for p in d['passages']:
    txt = p['text']
    pairs = pat.findall(txt)
    # 每4个连续干支对 = 一组四柱
    for i in range(0, len(pairs)-3, 4):
        four = pairs[i:i+4]
        # 校验: 日干必须合法, 4柱
        pillars = {'year': list(four[0]), 'month': list(four[1]), 'day': list(four[2]), 'hour': list(four[3])}
        charts.append(pillars)
print(f'提取四柱(每4对一组): {len(charts)}')

random.seed(42)
sample = random.sample(charts, min(150, len(charts)))
root_dist = collections.Counter()
q_sup = collections.Counter()
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
            if q['state'] == 'SUPPORTED':
                q_sup[q['query_id'].split('QUERY-')[-1]] += 1
    except Exception as e:
        errors.append((i, ''.join(sum(p.values(), [])), repr(e)[:80]))

print(f'成功: {len(sample)-len(errors)}/{len(sample)}, 崩溃: {len(errors)}')
for e in errors[:8]: print('  ERR', e)
print('\n--- root 分布 ---')
for k, v in root_dist.most_common(): print(f'  {str(k):10s} {v}')
print('\n--- query SUPPORTED 分布 ---')
for k, v in q_sup.most_common(): print(f'  {k:22s} {v}')
