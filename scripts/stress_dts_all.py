# -*- coding: utf-8 -*-
"""全量1289组四柱跑引擎, 找异常."""
import re, json, sys, collections
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
charts = []
for p in d['passages']:
    pairs = pat.findall(p['text'])
    for i in range(0, len(pairs)-3, 4):
        four = pairs[i:i+4]
        charts.append({'year': list(four[0]), 'month': list(four[1]), 'day': list(four[2]), 'hour': list(four[3])})
print(f'总四柱: {len(charts)}')

root_dist = collections.Counter()
q_sup = collections.Counter()
q_unk = collections.Counter()
errors = []
jiruo_cases = []
none_root_cases = []
for i, p in enumerate(charts):
    try:
        f = build(p); pa = build_power_structure(p)
        hst = {p[k][1]: f['hidden_stems'][k] for k in ('year','month','day','hour')}
        rc = build_root_classes(p, hst); tc = build_tou_cang(f); wx = build_wang_xiang(f, f['day_stem'])
        rr = build_root_relations(rc, f['combination_facts']); ts = build_two_side(rc, tc, rr)
        bt = build_branch_tiers(p, f); th = build_tian_he(p, f)
        net = build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th)
        rw = net['dimensions']['ROOT']['root_weight_class']
        root_dist[rw] += 1
        s = ''.join(p['year']+p['month']+p['day']+p['hour'])
        if rw == 'NONE': none_root_cases.append(s)
        for q in run_queries(net):
            if q['state'] == 'SUPPORTED':
                q_sup[q['query_id'].split('QUERY-')[-1]] += 1
            elif q['state'] == 'UNKNOWN' and q['match_type'] == 'STRUCTURE_MATCH':
                q_unk[q['query_id'].split('QUERY-')[-1]] += 1
            if 'JIRUO' in q['query_id'] and q['state'] == 'SUPPORTED':
                jiruo_cases.append(s)
    except Exception as e:
        errors.append((i, ''.join(sum(p.values(), [])), repr(e)[:80]))

print(f'成功: {len(charts)-len(errors)}/{len(charts)}, 崩溃: {len(errors)}')
for e in errors[:10]: print('  ERR', e)
print('\n--- root 分布 ---')
for k, v in root_dist.most_common(): print(f'  {str(k):10s} {v}')
print('\n--- query SUPPORTED ---')
for k, v in q_sup.most_common(): print(f'  {k:22s} {v}')
print('\n--- query UNKNOWN但结构MATCH(待授权) ---')
for k, v in q_unk.most_common(): print(f'  {k:22s} {v}')
print(f'\n--- JIRUO极弱无根 {len(jiruo_cases)}例 ---')
for c in jiruo_cases: print('  ', c)
print(f'\n--- NONE无根 {len(none_root_cases)}例, 前20 ---')
for c in none_root_cases[:20]: print('  ', c)
