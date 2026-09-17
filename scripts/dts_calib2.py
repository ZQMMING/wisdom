# -*- coding: utf-8 -*-
"""DTS命例自校R2: 财多身弱(440) + 印比重(60), 跑全query."""
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

cases = [
    ("DTS-440 丙火巳月庚辛重叠=财多身弱", {'year':['辛','巳'],'month':['癸','巳'],'day':['丙','申'],'hour':['丁','酉']}),
    ("DTS-60 甲日两寅两壬=印比重杀轻",   {'year':['丙','寅'],'month':['庚','寅'],'day':['甲','寅'],'hour':['壬','申']}),
]
for name, p in cases:
    f = build(p); pa = build_power_structure(p)
    hst = {p[k][1]: f['hidden_stems'][k] for k in ('year','month','day','hour')}
    rc = build_root_classes(p, hst); tc = build_tou_cang(f); wx = build_wang_xiang(f, f['day_stem'])
    rr = build_root_relations(rc, f['combination_facts']); ts = build_two_side(rc, tc, rr)
    bt = build_branch_tiers(p, f); th = build_tian_he(p, f)
    net = build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th)
    print(f"\n=== {name}")
    print(f"  root_weight_class={net['dimensions']['ROOT']['root_weight_class']}")
    for q in run_queries(net):
        if q['state'] != 'NOT_SUPPORTED':
            print(f"  {q['query_id'].split('QUERY-')[-1]:22s} {q['state']:12s} {q['match_type']}")
