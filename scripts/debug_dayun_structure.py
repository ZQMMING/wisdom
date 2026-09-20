# -*- coding: utf-8 -*-
"""先看dayun_xiji输出结构"""
import sys, json
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

chart = '辛丑乙未庚辰丁丑'
pillars = {'year': chart[0:2], 'month': chart[2:4], 'day': chart[4:6], 'hour': chart[6:8]}
f = build(pillars)
pa = build_power_structure(pillars)
hst = {pillars[k][1]: f['hidden_stems'][k] for k in ('year', 'month', 'day', 'hour')}
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
ye = build_yongshen_engine(pillars, f, wpo, spt, spc, clc)

print('用神:', ye.get('yongshen_primary'), ye.get('yongshen_secondary'), ye.get('yongshen_avoid'))

dayun_list = ['辛卯']
dy = build_dayun_xiji(pillars, ye, dayun_list, wpo)
print('\ndayun_xiji keys:', list(dy.keys()))
print('per_step type:', type(dy.get('per_step')))
if isinstance(dy.get('per_step'), list):
    print('per_step[0]:', dy['per_step'][0] if dy['per_step'] else 'empty')
    print('per_step len:', len(dy['per_step']))
elif isinstance(dy.get('per_step'), dict):
    for k, v in list(dy['per_step'].items())[:2]:
        print(f'per_step[{k}]:', v)
