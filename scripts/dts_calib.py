# -*- coding: utf-8 -*-
"""DTS命例语义自校: 5个任氏明确描述根气的命例, 跑我们20个query, 对照."""
import sys, json
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
    ("DTS-159 甲寅日亥月(长生+禄)", {'year':['甲','子'],'month':['乙','亥'],'day':['甲','寅'],'hour':['丙','寅']}),
    ("DTS-176 壬子日子月(羊刃)",   {'year':['丙','子'],'month':['戊','子'],'day':['壬','子'],'hour':['庚','子']}),
    ("DTS-272 丙寅日寅月(三寅长生)",{'year':['丙','寅'],'month':['庚','寅'],'day':['丙','寅'],'hour':['甲','午']}),
    ("DTS-179 庚辰日未月",         {'year':['甲','子'],'month':['辛','未'],'day':['庚','辰'],'hour':['丁','丑']}),
    ("DTS-309 甲申日酉月(绝)",     {'year':['甲','子'],'month':['癸','酉'],'day':['甲','申'],'hour':['丙','寅']}),
]
for name, p in cases:
    f = build(p); pa = build_power_structure(p)
    hst = {p[k][1]: f['hidden_stems'][k] for k in ('year','month','day','hour')}
    rc = build_root_classes(p, hst); tc = build_tou_cang(f); wx = build_wang_xiang(f, f['day_stem'])
    rr = build_root_relations(rc, f['combination_facts']); ts = build_two_side(rc, tc, rr)
    bt = build_branch_tiers(p, f); th = build_tian_he(p, f)
    net = build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th)
    qs = {q['query_id'].split('QUERY-')[-1]: (q['state'], q['match_type']) for q in run_queries(net)}
    rw = net['dimensions']['ROOT'].get('root_weight_class')
    print(f"\n=== {name}")
    print(f"  root_weight_class={rw}")
    for k in ('HEAVY-ROOT','LIGHT-ROOT','CAN-REN-CAIGUAN','JIRUO-WUGEN','SHI-GUI-LU','RI-BEI-HE'):
        if k in qs: print(f"  {k:20s} {qs[k][0]:12s} {qs[k][1]}")
