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
from engines.common.wuxing_power import build_wuxing_power
from engines.common.special_pattern import build_special_patterns
from engines.common.climate_structure import build_climate_structure

# 案例11: 化气格
pillars = {'year': '癸丑', 'month': '丙辰', 'day': '丙申', 'hour': '辛卯'}
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
cl = build_climate_structure(pillars, f, th)
spc = build_special_patterns(pillars, f, wpo, th, cl)

print('=== 化气格调试 ===')
print('day_stem:', f['day_stem'])
print('tian_he he_pairs:', th.get('he_pairs', []))
print()
wp = wpo['wuxing_power']
for elem in ['水', '金', '木', '火', '土']:
    d = wp[elem]
    print('%s: ben_n=%s, ju_n=%s, stem_n=%s, total=%s' % (elem, d.get('ben_n'), d.get('ju_n'), d.get('stem_n'), d.get('total')))
print()
print('month_element:', wpo.get('month_element'))
print('patterns:', [p.get('pattern_name') for p in spc.get('patterns', [])])
print('hua_qi:', spc.get('hua_qi'))
print('cong_type:', spc.get('cong_type'))
print('zhuanwang:', spc.get('zhuanwang'))
