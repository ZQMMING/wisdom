# -*- coding: utf-8 -*-
"""分析财+财和比劫+官杀的不匹配案例"""
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
KE_ME = {v:k for k,v in KE.items()}

with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', encoding='utf-8') as f:
    mismatches = json.load(f)

print('财+财 和 比劫+官杀 的不匹配案例:')
print(f'{"="*100}')

count = 0
for m in mismatches:
    chart = m.get('chart', '')
    dayun_str = m.get('dayun', '')
    
    if len(chart) != 8 or not dayun_str or len(dayun_str) != 2:
        continue
    
    dm = chart[4]
    dm_wx = STEM_WX.get(dm, '')
    gan = dayun_str[0]
    zhi = dayun_str[1]
    gan_wx = STEM_WX.get(gan, '')
    zhi_wx = BRANCH_WX.get(zhi, '')
    
    # 财+财
    cai_wx = KE.get(dm_wx, '')
    is_cai_cai = (gan_wx == cai_wx and zhi_wx == cai_wx)
    # 比劫+官杀
    guansha_wx = KE_ME.get(dm_wx, '')
    is_bijie_guansha = (gan_wx == dm_wx and zhi_wx == guansha_wx)
    
    if not (is_cai_cai or is_bijie_guansha):
        continue
    
    count += 1
    if count > 12:
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
        tier = ye.get('spectrum_tier', '')
        
        dy = build_dayun_xiji(pillars, ye, [dayun_str], wpo)
        step = dy['per_step'][0]
        xiji_label = step.get('xiji_label', '')
        relations = step.get('relations', [])
        
        combo_type = '财+财' if is_cai_cai else '比劫+官杀'
        print(f'\n[{count}] {chart} 日主={dm}({dm_wx}) tier={tier} [{combo_type}]')
        print(f'  大运={dayun_str}: {gan}({gan_wx}) + {zhi}({zhi_wx})')
        print(f'  用神: primary={primary}, secondary={secondary}, avoid={avoid}')
        print(f'  引擎: {xiji_label}')
        print(f'  relations: {relations[:6]}')
        print(f'  原文: {m.get("text", "")[:60]}')
        
    except Exception as e:
        print(f'  ERROR: {e}')

print(f'\n{"="*100}')
print(f'分析了 {count} 个案例')
