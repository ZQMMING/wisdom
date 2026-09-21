# -*- coding: utf-8 -*-
"""诊断L1827未命中案例
"""
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
import json

# 先找到L1827案例
with open('scripts/dts_cases_extracted.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

target_case = None
for case in cases:
    if str(case.get('src_line', '')) == '1827':
        target_case = case
        break

if not target_case:
    print('未找到L1827案例')
    sys.exit(1)

pillars = target_case.get('pillars', [])
p = {
    'year': pillars[0],
    'month': pillars[1],
    'day': pillars[2],
    'hour': pillars[3],
}

print('=' * 70)
print(f'L1827诊断: {p["year"]} {p["month"]} {p["day"]} {p["hour"]}')
print('=' * 70)
print()

# 排盘
f = l0build(p)
ds = f['day_stem']
hst = {p[k][1]: f['hidden_stems'][k] for k in ('year','month','day','hour')}

print('日主:', ds)
print('月令:', p['month'][1])
print('日主五行:', WUXING[ds])
print()

# 身强弱
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

print('--- 旺衰强弱 ---')
ws = sp.get('wang_shuai', {})
if isinstance(ws, dict):
    print('旺衰:', ws.get('result', '未知'))
else:
    print('旺衰:', ws)

qr = sp.get('qiang_ruo', {})
if isinstance(qr, dict):
    print('强弱:', qr.get('result', '未知'))
else:
    print('强弱:', qr)
print()

# 格局
cls = build_climate_structure(p, f, th)
spp = build_special_patterns(p, f, wp, th, cls)
print('--- 格局 ---')
print('special:', spp.get('special_name', '正格'))
print()

# 用神
clc = build_climate_candidates(f)
ye = build_yongshen_engine(p, f, wp, sp, spp, clc)

print('--- 用神 ---')
print('primary:', ye.get('yongshen_primary', ''))
print('secondary:', ye.get('yongshen_secondary', []))
print('avoid:', ye.get('yongshen_avoid', []))
print()

print('--- 调候十干级 ---')
csc = ye.get('climate_stem_candidates', [])
for c in csc:
    print(f"  {c['stem']}({c['element']}) P{c['priority']} | {c['applicability']}")
print()

# 原典标准
print('--- 原典标准 ---')
print('注: 需要从DTS原文中找L1827的大运断语')
print('大运:', target_case.get('dayun', '未知'))
print('断语:', target_case.get('verdict', '未知'))
print()

print('=' * 70)
print('诊断方向:')
print('  A类: 用神五行错(用神候选与原典所需五行不一致)')
print('  B类: 大运喜忌逻辑错(用神对但判断反了)')
print('  C类: 原典模糊')
print('=' * 70)
