# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'D:\shuntian-ziping-p0')
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
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_topology
from engines.common.special_pattern import build_special_patterns
from engines.common.climate_structure import build_climate_structure
from engines.common.qtbj_climate_candidates import build_climate_candidates
from engines.common.yongshen_engine import build_yongshen_engine

pillars = {'year':['辛','亥'],'month':['庚','寅'],'day':['丙','子'],'hour':['乙','未']}
f = build(pillars)
pa = build_power_structure(pillars)
hst = {pillars[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}
rc = build_root_classes(pillars, hst)
tc = build_tou_cang(f)
wx = build_wang_xiang(f, f['day_stem'])
rr = build_root_relations(rc, f['combination_facts'])
ts = build_two_side(rc, tc, rr)
bt = build_branch_tiers(pillars, f)
th = build_tian_he(pillars, f)
net = build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th, facts=f)
wpo = build_wuxing_power(pillars, f, th)
spt = build_spectrum_topology(net, wpo)
cl = build_climate_structure(pillars, f, th)
spc = build_special_patterns(pillars, f, wpo, th, cl)
clc = build_climate_candidates(f)
ys = build_yongshen_engine(pillars, f, wpo, spt, spc, clc)

wp = wpo.get('wuxing_power', {})
for w in ['火','水','木','金','土']:
    d = wp.get(w, {})
    print(f'{w}: ben={d.get("ben_n")}, stem={d.get("stem_n")}, ling={d.get("ling_state")}, zhong={d.get("zhong_n")}, yu={d.get("yu_n")}')

print('spectrum:', spt.get('spectrum'))
print('tier:', ys.get('spectrum_tier'))
print('primary:', ys.get('yongshen_primary'))
print('paths:', ys.get('yongshen_paths'))
