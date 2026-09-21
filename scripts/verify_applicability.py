# -*- coding: utf-8 -*-
"""验证applicability字段输出"""
import sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build as l0build, WUXING
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_branch_tier import build_branch_tiers
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_topology, build_spectrum_from_power
from engines.common.daymaster_power_network import build_power_network
from engines.common.climate_structure import build_climate_structure
from engines.common.special_pattern import build_special_patterns
from engines.common.qtbj_climate_candidates import build_climate_candidates
from engines.common.yongshen_engine import build_yongshen_engine

# 测试案例: 炎上格(丁日主, 火专旺)
p = {'year': '丙午', 'month': '癸巳', 'day': '丁巳', 'hour': '丙午'}
f = l0build(p)
ds = f['day_stem']
hst = {p[k][1]: f['hidden_stems'][k] for k in ('year','month','day','hour')}
pa = build_power_structure(p)
rc = build_root_classes(p, hst)
tc = build_tou_cang(f)
wxo = build_wang_xiang(f, ds)
rr = build_root_relations(rc, f['combination_facts'])
ts = build_two_side(rc, tc, rr)
bt = build_branch_tiers(p, f)
th = build_tian_he(p, f)
wp = build_wuxing_power(p, f, th)
net = build_power_network(pa, rc, tc, wxo, rr, ts, branch_tier=bt, tian_he=th, facts=f)
net.setdefault('facts', {})['daymaster_element'] = WUXING[ds]
sp = build_spectrum_topology(net, wp)
_spd = build_spectrum_from_power(wp, p)
sp['wang_shuai'] = _spd.get('wang_shuai')
sp['qiang_ruo'] = _spd.get('qiang_ruo')
clc = build_climate_candidates(f)
cls = build_climate_structure(p, f, th)
spp = build_special_patterns(p, f, wp, th, cls)
ye = build_yongshen_engine(p, f, wp, sp, spp, clc)

print('=== 炎上格测试 ===')
print('special:', ye.get('special'))
print('climate_stem_candidates:')
for c in ye.get('climate_stem_candidates', []):
    print(f"  {c['stem']}({c['element']}) P{c['priority']} | {c['applicability']} | {c['applicability_reason']}")
print()

# 测试正格案例
p2 = {'year': '甲子', 'month': '辛未', 'day': '戊午', 'hour': '己未'}
f2 = l0build(p2)
ds2 = f2['day_stem']
hst2 = {p2[k][1]: f2['hidden_stems'][k] for k in ('year','month','day','hour')}
pa2 = build_power_structure(p2)
rc2 = build_root_classes(p2, hst2)
tc2 = build_tou_cang(f2)
wxo2 = build_wang_xiang(f2, ds2)
rr2 = build_root_relations(rc2, f2['combination_facts'])
ts2 = build_two_side(rc2, tc2, rr2)
bt2 = build_branch_tiers(p2, f2)
th2 = build_tian_he(p2, f2)
wp2 = build_wuxing_power(p2, f2, th2)
net2 = build_power_network(pa2, rc2, tc2, wxo2, rr2, ts2, branch_tier=bt2, tian_he=th2, facts=f2)
net2.setdefault('facts', {})['daymaster_element'] = WUXING[ds2]
sp2 = build_spectrum_topology(net2, wp2)
_spd2 = build_spectrum_from_power(wp2, p2)
sp2['wang_shuai'] = _spd2.get('wang_shuai')
sp2['qiang_ruo'] = _spd2.get('qiang_ruo')
clc2 = build_climate_candidates(f2)
cls2 = build_climate_structure(p2, f2, th2)
spp2 = build_special_patterns(p2, f2, wp2, th2, cls2)
ye2 = build_yongshen_engine(p2, f2, wp2, sp2, spp2, clc2)

print('=== 稼穑格测试 ===')
print('special:', ye2.get('special'))
print('climate_stem_candidates:')
for c in ye2.get('climate_stem_candidates', []):
    print(f"  {c['stem']}({c['element']}) P{c['priority']} | {c['applicability']} | {c['applicability_reason']}")
