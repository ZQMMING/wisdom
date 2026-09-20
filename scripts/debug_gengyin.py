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

pillars = {'year': '庚寅', 'month': '壬午', 'day': '丁卯', 'hour': '癸卯'}
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

print('=== 庚寅 壬午 丁卯 癸卯 ===')
print('用神:', ye.get('yongshen_primary'))
print('喜神:', ye.get('yongshen_secondary'))
print('忌神:', ye.get('yongshen_avoid'))
print('theory_source:', ye.get('theory_source'))
print('spectrum_tier:', ye.get('spectrum_tier'))
print()
wp = wpo['wuxing_power']
for wx_name in ['木','火','土','金','水']:
    d = wp.get(wx_name, {})
    print(f'{wx_name}: stem_n={d.get("stem_n")}, ben_n={d.get("ben_n")}, ling={d.get("ling_state")}')

# 测试三个大运
print()
for dayun in ['癸未', '丙戌', '丁亥']:
    dx = build_dayun_xiji(pillars, f, wpo, ye, dayun, th=th)
    if dx and isinstance(dx, list) and len(dx) > 0:
        item = dx[0] if isinstance(dx[0], dict) else dx
        print(f'{dayun}: xiji_label={item.get("xiji_label")}, relations={item.get("relations", [])[:5]}')
    else:
        print(f'{dayun}: {dx}')
