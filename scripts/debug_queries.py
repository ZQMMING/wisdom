# -*- coding: utf-8 -*-
import sys
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

def net(p):
    f = build(p)
    pa = build_power_structure(p)
    hst = {p[k][1]: f['hidden_stems'][k] for k in ('year','month','day','hour')}
    rc = build_root_classes(p, hst)
    tc = build_tou_cang(f)
    wx = build_wang_xiang(f, f['day_stem'])
    rr = build_root_relations(rc, f['combination_facts'])
    ts = build_two_side(rc, tc, rr)
    bt = build_branch_tiers(p, f)
    th = build_tian_he(p, f)
    return build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th, facts=f)

tests = {
    'HEHUASHEN-CHENGGONG': {'year':['甲','子'],'month':['己','巳'],'day':['甲','子'],'hour':['己','巳']},
    'SHIYONG-YUELING-XIANGFU': {'year':['甲','寅'],'month':['丙','寅'],'day':['甲','寅'],'hour':['丁','卯']},
    'WANGJI-SIWO-SHENG': {'year':['甲','寅'],'month':['丙','寅'],'day':['甲','寅'],'hour':['丁','卯']},
    'SHUAIJI-SIWO-KE': {'year':['庚','申'],'month':['庚','申'],'day':['甲','申'],'hour':['庚','申']},
    'MU-CHONG-KAI': {'year':['甲','辰'],'month':['丙','戌'],'day':['甲','寅'],'hour':['丁','卯']},
    'SHI-ZHU-JI': {'year':['甲','寅'],'month':['丙','寅'],'day':['甲','寅'],'hour':['丁','卯']},
    'SHI-LIN-WANG': {'year':['甲','寅'],'month':['丙','寅'],'day':['甲','寅'],'hour':['甲','寅']},
    'TIANGAN-XINGQING': {'year':['甲','寅'],'month':['丙','寅'],'day':['甲','寅'],'hour':['丁','卯']},
    'YONGSHEN-STRUCTURE': {'year':['甲','寅'],'month':['丙','寅'],'day':['甲','寅'],'hour':['丁','卯']},
    'JIXIONG-STRUCTURE': {'year':['甲','寅'],'month':['丙','寅'],'day':['甲','寅'],'hour':['丁','卯']},
}
for qn, p in tests.items():
    n = net(p)
    qs = {q['query_id'].split('QUERY-')[-1]: q for q in run_queries(n)}
    q = qs.get(qn)
    if q:
        print(qn.ljust(28), 'state=' + q['state'].ljust(12), 'match=' + q['match_type'])
    else:
        print(qn.ljust(28), 'NOT FOUND')
