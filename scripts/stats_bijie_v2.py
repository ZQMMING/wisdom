# -*- coding: utf-8 -*-
"""统计不匹配案例中的比劫夺财等类型(修正版)"""
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

STEM_WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
BRANCH_WX = {'子':'水','亥':'水','寅':'木','卯':'木','巳':'火','午':'火','申':'金','酉':'金','辰':'土','戌':'土','丑':'土','未':'土'}
KE = {'木':'土','土':'水','水':'火','火':'金','金':'木'}  # 我克=财
KE_ME = {v: k for k, v in KE.items()}  # 克我=官杀
SHENG = {'木':'火','火':'土','土':'金','金':'水','水':'木'}  # 我生=食伤
SHENG_ME = {v: k for k, v in SHENG.items()}  # 生我=印

with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', encoding='utf-8') as f:
    mismatches = json.load(f)

bijie_duocai = 0
guansha_keshen = 0
shishang_xiexiu = 0
yin_xing = 0
other = 0

print(f'不匹配案例总数: {len(mismatches)}')
print(f'\n{"="*100}')

for i, m in enumerate(mismatches):
    chart = m.get('chart', '')
    dayun_str = m.get('dayun', '')
    
    if len(chart) != 8 or not dayun_str or len(dayun_str) != 2:
        continue
    
    dm = chart[4]  # 日干
    dm_wx = STEM_WX.get(dm, '')
    gan = dayun_str[0]
    zhi = dayun_str[1]
    gan_wx = STEM_WX.get(gan, '')
    zhi_wx = BRANCH_WX.get(zhi, '')
    
    # 比劫夺财: 天干比劫 + 地支财星
    if gan_wx == dm_wx and zhi_wx == KE.get(dm_wx, ''):
        bijie_duocai += 1
        print(f'[比劫夺财] {chart} 大运={dayun_str}')
    # 官杀克身: 天干官杀 + 地支官杀
    elif gan_wx == KE_ME.get(dm_wx, '') and zhi_wx == KE_ME.get(dm_wx, ''):
        guansha_keshen += 1
        print(f'[官杀克身] {chart} 大运={dayun_str}')
    # 食伤泄秀: 天干食伤 + 地支食伤
    elif gan_wx == SHENG.get(dm_wx, '') and zhi_wx == SHENG.get(dm_wx, ''):
        shishang_xiexiu += 1
        print(f'[食伤泄秀] {chart} 大运={dayun_str}')
    # 印星: 天干印 + 地支印
    elif gan_wx == SHENG_ME.get(dm_wx, '') and zhi_wx == SHENG_ME.get(dm_wx, ''):
        yin_xing += 1
        print(f'[印星] {chart} 大运={dayun_str}')
    else:
        other += 1

print(f'\n{"="*100}')
print(f'统计:')
print(f'  比劫夺财(干支同): {bijie_duocai}')
print(f'  官杀克身(干支同): {guansha_keshen}')
print(f'  食伤泄秀(干支同): {shishang_xiexiu}')
print(f'  印星(干支同): {yin_xing}')
print(f'  其他(干支不同): {other}')
