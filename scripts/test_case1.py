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
from engines.common.dayun_xiji import build_dayun_xiji

p = {'year':('庚','寅'),'month':('壬','午'),'day':('丁','卯'),'hour':('癸','卯')}
f = build(p)
pa = build_power_structure(p)
hst = {p[k][1]: f['hidden_stems'][k] for k in ('year', 'month', 'day', 'hour')}
rc = build_root_classes(p, hst)
tc = build_tou_cang(f)
wx = build_wang_xiang(f, f['day_stem'])
rr = build_root_relations(rc, f['combination_facts'])
ts = build_two_side(rc, tc, rr)
bt = build_branch_tiers(p, f)
th = build_tian_he(p, f)
net = build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th, facts=f)
wpo = build_wuxing_power(p, f, th)
spt = build_spectrum_topology(net, wpo)
cl = build_climate_structure(p, f, th)
spc = build_special_patterns(p, f, wpo, th, cl)
clc = build_climate_candidates(f)
ye = build_yongshen_engine(p, f, wpo, spt, spc, clc)
print('用神primary:', ye.get('yongshen_primary'))
print('用神avoid:', ye.get('yongshen_avoid'))
print('spectrum_tier:', ye.get('spectrum_tier'))
dy = ['癸未','甲申','乙酉','丙戌','丁亥','戊子']
dx = build_dayun_xiji(p, ye, dy, wpo)
for step in dx.get('per_step', []):
    print(f"{step['ganzhi']}: label={step['xiji_label']}, labels={step['xiji_labels']}")
    print(f"  relations={step['relations'][:10]}")
