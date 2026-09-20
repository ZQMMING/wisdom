# -*- coding: utf-8 -*-
"""统计V4.48后剩余不匹配案例的错误模式"""
import json
from collections import Counter

with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', encoding='utf-8') as f:
    mismatches = json.load(f)

STEM_WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
BRANCH_WX = {'子':'水','亥':'水','寅':'木','卯':'木','巳':'火','午':'火','申':'金','酉':'金','辰':'土','戌':'土','丑':'土','未':'土'}
KE = {'木':'土','土':'水','水':'火','火':'金','金':'木'}
KE_ME = {v:k for k,v in KE.items()}
SHENG = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
SHENG_ME = {v:k for k,v in SHENG.items()}

print(f'不匹配案例总数: {len(mismatches)}')
print(f'\n{"="*80}')

# 统计引擎判喜原文判忌 vs 引擎判忌原文判喜
xi_ji_count = 0  # 引擎判喜, 原文判忌
ji_xi_count = 0  # 引擎判忌, 原文判喜

# 统计干支同 vs 干支不同
gan_zhi_same = 0
gan_zhi_diff = 0

# 统计十神组合
ten_god_combos = Counter()

for m in mismatches:
    chart = m.get('chart', '')
    dayun_str = m.get('dayun', '')
    engine_label = m.get('engine_label', '') or m.get('engine', '')
    
    if len(chart) != 8 or not dayun_str or len(dayun_str) != 2:
        continue
    
    dm = chart[4]
    dm_wx = STEM_WX.get(dm, '')
    gan = dayun_str[0]
    zhi = dayun_str[1]
    gan_wx = STEM_WX.get(gan, '')
    zhi_wx = BRANCH_WX.get(zhi, '')
    
    # 天干十神
    if gan_wx == dm_wx: gan_tg = '比劫'
    elif gan_wx == SHENG_ME.get(dm_wx): gan_tg = '印'
    elif gan_wx == KE_ME.get(dm_wx): gan_tg = '官杀'
    elif gan_wx == SHENG.get(dm_wx): gan_tg = '食伤'
    elif gan_wx == KE.get(dm_wx): gan_tg = '财'
    else: gan_tg = '?'
    
    # 地支十神
    if zhi_wx == dm_wx: zhi_tg = '比劫'
    elif zhi_wx == SHENG_ME.get(dm_wx): zhi_tg = '印'
    elif zhi_wx == KE_ME.get(dm_wx): zhi_tg = '官杀'
    elif zhi_wx == SHENG.get(dm_wx): zhi_tg = '食伤'
    elif zhi_wx == KE.get(dm_wx): zhi_tg = '财'
    else: zhi_tg = '?'
    
    combo = f'{gan_tg}+{zhi_tg}'
    ten_god_combos[combo] += 1
    
    if gan_wx == zhi_wx:
        gan_zhi_same += 1
    else:
        gan_zhi_diff += 1
    
    # 引擎判喜原文判忌
    if 'SUPPORT' in engine_label or '喜' in engine_label:
        xi_ji_count += 1
    else:
        ji_xi_count += 1

print(f'引擎判喜原文判忌: {xi_ji_count}')
print(f'引擎判忌原文判喜: {ji_xi_count}')
print(f'干支同: {gan_zhi_same}')
print(f'干支不同: {gan_zhi_diff}')

print(f'\n{"="*80}')
print('十神组合统计(天干+地支):')
for combo, count in ten_god_combos.most_common(15):
    print(f'  {combo}: {count}')
