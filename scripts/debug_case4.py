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

# 案例4: 丁巳 壬子 辛巳 丁酉, 辛金子月, 原文用火, 引擎用水
pillars = {'year': '丁巳', 'month': '壬子', 'day': '辛巳', 'hour': '丁酉'}
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

print('=== 案例4: 丁巳 壬子 辛巳 丁酉 ===')
print('day_stem:', f['day_stem'])
print('month_branch:', f['month_branch'])
print('spectrum tier:', spt.get('spectrum'))
print()
print('调候候选:', [(c.get('stem'), c.get('order')) for c in clc.get('climate_candidates',[])])
print()
wp = wpo['wuxing_power']
for elem in ['金','水','木','火','土']:
    d = wp[elem]
    print('%s: ben=%s zhong=%s yu=%s stem=%s ju=%s ling=%s' % (
        elem, d.get('ben_n'), d.get('zhong_n'), d.get('yu_n'), d.get('stem_n'), d.get('ju_n'), d.get('ling_state')))
print()
ye = build_yongshen_engine(pillars, f, wpo, spt, spc, clc)
print('primary:', ye.get('yongshen_primary'))
print('secondary:', ye.get('yongshen_secondary'))
print('avoid:', ye.get('yongshen_avoid'))
print('paths:', ye.get('paths'))
print('notes:', ye.get('notes'))
print('special: cong=%s zw=%s hua=%s' % (spc.get('cong_type'), spc.get('zhuanwang'), spc.get('hua_qi')))
