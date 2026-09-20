# -*- coding: utf-8 -*-
"""统计剩余不匹配案例中,大运干支在avoid但原文判喜的模式"""
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

with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', encoding='utf-8') as f:
    mismatches = json.load(f)

avoid_but_xi = []  # 大运干支在avoid但原文判喜
avoid_and_ji = []  # 大运干支在avoid且原文判忌(引擎判忌正确)
not_avoid = []  # 大运干支不在avoid

for m in mismatches:
    chart = m.get('chart', '')
    dayun_str = m.get('dayun', '')
    text = m.get('text', '')
    
    if len(chart) != 8 or not dayun_str or len(dayun_str) != 2:
        continue
    
    gan = dayun_str[0]
    zhi = dayun_str[1]
    gan_wx = STEM_WX.get(gan, '')
    zhi_wx = BRANCH_WX.get(zhi, '')
    
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
        
        avoid = ye.get('yongshen_avoid', [])
        tier = ye.get('spectrum_tier', '')
        primary = ye.get('yongshen_primary', '')
        
        gan_in_avoid = gan_wx in avoid
        zhi_in_avoid = zhi_wx in avoid
        both_in_avoid = gan_in_avoid and zhi_in_avoid
        any_in_avoid = gan_in_avoid or zhi_in_avoid
        
        text_is_xi = (text == 'XI')
        
        if any_in_avoid and text_is_xi:
            avoid_but_xi.append({
                'chart': chart, 'dayun': dayun_str, 'tier': tier,
                'primary': primary, 'avoid': avoid,
                'gan_wx': gan_wx, 'zhi_wx': zhi_wx,
                'gan_in_avoid': gan_in_avoid, 'zhi_in_avoid': zhi_in_avoid
            })
        elif any_in_avoid and not text_is_xi:
            avoid_and_ji.append(chart + ' ' + dayun_str)
        else:
            not_avoid.append(chart + ' ' + dayun_str)
        
    except Exception as e:
        pass

print(f'剩余不匹配案例总数: {len(mismatches)}')
print(f'\n=== 大运干支在avoid但原文判喜(引擎可能误判忌): {len(avoid_but_xi)} ===')
for item in avoid_but_xi:
    print(f"  {item['chart']} {item['dayun']}: tier={item['tier']}, primary={item['primary']}, avoid={item['avoid']}")
    print(f"    大运: {item['gan_wx']}(avoid={item['gan_in_avoid']}) + {item['zhi_wx']}(avoid={item['zhi_in_avoid']})")

print(f'\n=== 大运干支在avoid且原文判忌(引擎判忌正确): {len(avoid_and_ji)} ===')
print(f'\n=== 大运干支不在avoid: {len(not_avoid)} ===')
