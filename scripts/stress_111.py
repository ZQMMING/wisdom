# -*- coding: utf-8 -*-
"""压测: 111 个真实命例 -> 160-C 整条 network -> 18 query 分布统计.
只做工程压测(不崩/分布合理), 不判吉凶/对错."""
import sys, collections
sys.path.insert(0, '.')
import json
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

PY2CN_S = {'JIA':'甲','YI':'乙','BING':'丙','DING':'丁','WU':'戊','JI':'己',
           'GENG':'庚','XIN':'辛','REN':'壬','GUI':'癸'}
PY2CN_B = {'ZI':'子','CHOU':'丑','YIN':'寅','MAO':'卯','CHEN':'辰','SI':'巳',
           'WU':'午','WEI':'未','SHEN':'申','YOU':'酉','XU':'戌','HAI':'亥'}

d = json.load(open(r'D:\顺天系统资料\shuntian\cases\global_mingli.json', encoding='utf-8'))
cases = [c for grp in d for c in grp['cases'] if c.get('chart')]

hits = collections.Counter()
errors = []
n = 0
for c in cases:
    ch = c['chart']
    try:
        pillars = {k: [PY2CN_S[ch['four_stems'][i]], PY2CN_B[ch['four_branches'][i]]]
                   for i, k in enumerate(('year', 'month', 'day', 'hour'))}
        facts = build(pillars)
        pa = build_power_structure(pillars)
        hst = {pillars[k][1]: facts['hidden_stems'][k] for k in ('year', 'month', 'day', 'hour')}
        rc = build_root_classes(pillars, hst)
        tc = build_tou_cang(facts)
        wx = build_wang_xiang(facts, facts['day_stem'])
        rr = build_root_relations(rc, facts['combination_facts'])
        ts = build_two_side(rc, tc, rr)
        bt = build_branch_tiers(pillars, facts)
        th = build_tian_he(pillars, facts)
        net = build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th)
        for q in run_queries(net):
            hits[(q['query_id'], q['state'])] += 1
        n += 1
    except Exception as e:
        errors.append((c.get('case_no'), repr(e)[:120]))

print(f'成功跑通: {n}/{len(cases)}')
print(f'崩溃: {len(errors)}')
for e in errors[:10]:
    print('  ERR', e)
print('--- query 状态分布 ---')
for qid in sorted(set(q for q, _ in hits)):
    row = [(s, hits[(qid, s)]) for s in ('SUPPORTED','NOT_SUPPORTED','UNKNOWN')]
    print(f'{qid:45s}', ' '.join(f'{s}={v}' for s, v in row))
