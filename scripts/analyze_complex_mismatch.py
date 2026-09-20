# -*- coding: utf-8 -*-
"""深度分析干支不同的不匹配案例"""
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

STEM_WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
BRANCH_WX = {'子':'水','亥':'水','寅':'木','卯':'木','巳':'火','午':'火','申':'金','酉':'金','辰':'土','戌':'土','丑':'土','未':'土'}
KE = {'木':'土','土':'水','水':'火','火':'金','金':'木'}
KE_ME = {v: k for k, v in KE.items()}
SHENG = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
SHENG_ME = {v: k for k, v in SHENG.items()}

with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', encoding='utf-8') as f:
    mismatches = json.load(f)

# 只分析干支不同的案例
print(f'不匹配案例总数: {len(mismatches)}')
print(f'\n{"="*120}')
print('干支不同的不匹配案例分析:')

count = 0
for i, m in enumerate(mismatches):
    chart = m.get('chart', '')
    dayun_str = m.get('dayun', '')
    engine_label = m.get('engine_label', '') or m.get('engine', '')
    text = m.get('text', '')[:80]
    
    if len(chart) != 8 or not dayun_str or len(dayun_str) != 2:
        continue
    
    dm = chart[4]
    dm_wx = STEM_WX.get(dm, '')
    gan = dayun_str[0]
    zhi = dayun_str[1]
    gan_wx = STEM_WX.get(gan, '')
    zhi_wx = BRANCH_WX.get(zhi, '')
    
    # 跳过干支同的案例
    if gan_wx == zhi_wx:
        continue
    
    count += 1
    if count > 20:
        break
    
    pillars = {'year': chart[0:2], 'month': chart[2:4], 'day': chart[4:6], 'hour': chart[6:8]}
    try:
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
        
        primary = ye.get('yongshen_primary', '')
        secondary = ye.get('yongshen_secondary', [])
        avoid = ye.get('yongshen_avoid', [])
        theory = ye.get('theory_source', '')
        tier = ye.get('spectrum_tier', '')
        
        dy = build_dayun_xiji(pillars, ye, [dayun_str], wpo)
        step = dy['per_step'][0]
        xiji_label = step.get('xiji_label', '')
        relations = step.get('relations', [])
        
        # 天干十神
        gan_ten_god = ''
        if gan_wx == dm_wx: gan_ten_god = '比劫'
        elif gan_wx == SHENG_ME.get(dm_wx): gan_ten_god = '印'
        elif gan_wx == KE_ME.get(dm_wx): gan_ten_god = '官杀'
        elif gan_wx == SHENG.get(dm_wx): gan_ten_god = '食伤'
        elif gan_wx == KE.get(dm_wx): gan_ten_god = '财'
        
        # 地支十神
        zhi_ten_god = ''
        if zhi_wx == dm_wx: zhi_ten_god = '比劫'
        elif zhi_wx == SHENG_ME.get(dm_wx): zhi_ten_god = '印'
        elif zhi_wx == KE_ME.get(dm_wx): zhi_ten_god = '官杀'
        elif zhi_wx == SHENG.get(dm_wx): zhi_ten_god = '食伤'
        elif zhi_wx == KE.get(dm_wx): zhi_ten_god = '财'
        
        print(f'\n[{count}] {chart} 日主={dm}({dm_wx}) tier={tier}')
        print(f'  大运={dayun_str}: 天干{gan}({gan_wx}/{gan_ten_god}) + 地支{zhi}({zhi_wx}/{zhi_ten_god})')
        print(f'  用神: primary={primary}, secondary={secondary}, avoid={avoid}, theory={theory}')
        print(f'  引擎: {xiji_label}, relations={relations[:6]}')
        print(f'  原文: {text}')
        
    except Exception as e:
        print(f'  ERROR: {e}')

print(f'\n{"="*120}')
print(f'干支不同的不匹配案例总数: {count}')
