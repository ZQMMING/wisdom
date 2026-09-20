# -*- coding: utf-8 -*-
"""分析19个avoid但原文判喜案例的has_xi/has_ji状态和relations"""
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

with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', encoding='utf-8') as f:
    mismatches = json.load(f)

both_xi_ji = []  # has_xi and has_ji
ji_only = []  # has_ji only
xi_only = []  # has_xi only

for m in mismatches:
    chart = m.get('chart', '')
    dayun_str = m.get('dayun', '')
    text = m.get('text', '')
    
    if len(chart) != 8 or not dayun_str or len(dayun_str) != 2:
        continue
    if text != 'XI':
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
        if gan_wx not in avoid and zhi_wx not in avoid:
            continue
        
        dy = build_dayun_xiji(pillars, ye, [dayun_str], wpo)
        step = dy['per_step'][0]
        xiji_labels = step.get('xiji_labels', [])
        relations = step.get('relations', [])
        
        has_xi = any('SUPPORT' in l for l in xiji_labels)
        has_ji = any('SUPPRESS' in l for l in xiji_labels)
        
        if has_xi and has_ji:
            both_xi_ji.append({'chart': chart, 'dayun': dayun_str, 'labels': xiji_labels, 'relations': relations[:10]})
        elif has_ji:
            ji_only.append({'chart': chart, 'dayun': dayun_str, 'labels': xiji_labels, 'relations': relations[:10]})
        elif has_xi:
            xi_only.append({'chart': chart, 'dayun': dayun_str, 'labels': xiji_labels, 'relations': relations[:10]})
        
    except Exception as e:
        pass

print(f'avoid但原文判喜案例总数: {len(both_xi_ji) + len(ji_only) + len(xi_only)}')
print(f'\n=== has_xi and has_ji (喜的逻辑被avoid覆盖): {len(both_xi_ji)} ===')
for item in both_xi_ji:
    print(f"  {item['chart']} {item['dayun']}: labels={item['labels']}")
    print(f"    relations={item['relations']}")

print(f'\n=== has_ji only (只有忌,没有喜的逻辑): {len(ji_only)} ===')
for item in ji_only:
    print(f"  {item['chart']} {item['dayun']}: labels={item['labels']}")
    print(f"    relations={item['relations']}")

print(f'\n=== has_xi only (只有喜,但引擎判忌?): {len(xi_only)} ===')
for item in xi_only:
    print(f"  {item['chart']} {item['dayun']}: labels={item['labels']}")
