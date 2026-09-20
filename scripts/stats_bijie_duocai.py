# -*- coding: utf-8 -*-
"""统计不匹配案例中的比劫夺财等类型"""
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

WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
KE = {'木':'土','土':'水','水':'火','火':'金','金':'木'}  # 我克
SHENG = {'木':'火','火':'土','土':'金','金':'水','水':'木'}  # 我生

with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', encoding='utf-8') as f:
    mismatches = json.load(f)

bijie_duocai = 0  # 比劫夺财
guansha_keshen = 0  # 官杀克身
shishang_xiexiu = 0  # 食伤泄秀
other = 0

print(f'不匹配案例总数: {len(mismatches)}')
print(f'\n{"="*100}')

for i, m in enumerate(mismatches):
    chart = m.get('chart', '')
    dayun_str = m.get('dayun', '')
    
    if len(chart) != 8 or not dayun_str:
        continue
    
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
        dm_wx = WX.get(f['day_stem'], '')
        
        gan = dayun_str[0]
        zhi = dayun_str[1]
        gan_wx = WX.get(gan, '')
        zhi_wx = WX.get(zhi, '')
        
        # 比劫夺财: 天干比劫(同五行) + 地支财星(我克)
        is_bijie = gan_wx == dm_wx
        is_cai = zhi_wx == KE.get(dm_wx, '')
        if is_bijie and is_cai:
            bijie_duocai += 1
            print(f'[比劫夺财] {chart} 大运={dayun_str} 用神={primary} 喜神={secondary} 忌神={avoid}')
        
        # 官杀克身: 天干官杀(克我) + 地支官杀
        is_guansha_gan = gan_wx == SHENG.get(dm_wx, '')  # 生我=印? 不对
        # 克我者为官杀: KE的反函数
        KE_ME = {v: k for k, v in KE.items()}
        is_guansha_gan = gan_wx == KE_ME.get(dm_wx, '')
        is_guansha_zhi = zhi_wx == KE_ME.get(dm_wx, '')
        if is_guansha_gan and is_guansha_zhi:
            guansha_keshen += 1
        
        # 食伤泄秀: 天干食伤(我生) + 地支食伤
        is_shishang_gan = gan_wx == SHENG.get(dm_wx, '')
        is_shishang_zhi = zhi_wx == SHENG.get(dm_wx, '')
        if is_shishang_gan and is_shishang_zhi:
            shishang_xiexiu += 1
        
    except Exception as e:
        pass

print(f'\n{"="*100}')
print(f'统计:')
print(f'  比劫夺财: {bijie_duocai}')
print(f'  官杀克身(干支同): {guansha_keshen}')
print(f'  食伤泄秀(干支同): {shishang_xiexiu}')
