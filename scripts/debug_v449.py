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

STEM_WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
BRANCH_WX = {'子':'水','亥':'水','寅':'木','卯':'木','巳':'火','午':'火','申':'金','酉':'金','辰':'土','戌':'土','丑':'土','未':'土'}
SHENG = {'木':'火','火':'土','土':'金','金':'水','水':'木'}

chart = '壬子辛亥壬子癸卯'
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
print('用神:', ye.get('yongshen_primary'), '忌神:', ye.get('yongshen_avoid'), 'spectrum_tier:', ye.get('spectrum_tier'))

dy = build_dayun_xiji(pillars, ye, ['乙卯'], wpo)
step = dy['per_step'][0]
print('大运:', step['ganzhi'])
print('relations:', step['relations'])
print('xiji_label:', step['xiji_label'])

# 手动计算
dm = '壬'
dm_wx = STEM_WX[dm]
gan = '乙'; zhi = '卯'
gan_wx = STEM_WX[gan]; zhi_wx = BRANCH_WX[zhi]
spectrum_tier = ye.get('spectrum_tier', '')
is_shenwang = spectrum_tier in ['太旺', '旺极', '旺']
_shishang_wx_local = SHENG.get(dm_wx, '')
print(f'dm_wx={dm_wx}, gan_wx={gan_wx}, zhi_wx={zhi_wx}')
print(f'spectrum_tier={spectrum_tier}, is_shenwang={is_shenwang}')
print(f'_shishang_wx_local={_shishang_wx_local}')
print(f'gan_wx==shishang: {gan_wx==_shishang_wx_local}')
print(f'zhi_wx==shishang: {zhi_wx==_shishang_wx_local}')
shenwang_shishang_xiexiu_v2 = (is_shenwang and gan_wx == _shishang_wx_local and zhi_wx == _shishang_wx_local)
print(f'shenwang_shishang_xiexiu_v2={shenwang_shishang_xiexiu_v2}')
