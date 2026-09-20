# -*- coding: utf-8 -*-
"""深度分析V4.44大运喜忌不匹配案例"""
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

with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', encoding='utf-8') as f:
    mismatches = json.load(f)

print(f'不匹配案例总数: {len(mismatches)}')
print(f'\n{"="*100}')

# 统计错误类型
error_types = {}
avoid_empty = 0
primary_empty = 0

for i, m in enumerate(mismatches[:20]):  # 先看前20个
    chart = m.get('chart', '')
    dayun = m.get('dayun', '')
    text = m.get('text', '')
    
    if len(chart) != 8:
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
        theory = ye.get('theory_source', '')
        tier = ye.get('spectrum_tier', '')
        
        if not primary:
            primary_empty += 1
        if not avoid:
            avoid_empty += 1
        
        # 跑大运喜忌
        dy_result = build_dayun_xiji(pillars, f, ye, wpo, spt, spc, dayun=dayun)
        has_xi = dy_result.get('has_xi', False)
        has_ji = dy_result.get('has_ji', False)
        
        # 原文判断
        text_xi = '喜' in text or '发' in text or '吉' in text
        text_ji = '忌' in text or '凶' in text or '败' in text
        
        print(f'\n[{i+1}] {chart} 月支={chart[3]} 大运={dayun}')
        print(f'  用神: primary={primary}, secondary={secondary}, avoid={avoid}, theory={theory}, tier={tier}')
        print(f'  引擎: has_xi={has_xi}, has_ji={has_ji}')
        print(f'  原文: {text[:80]}')
        print(f'  原文判断: xi={text_xi}, ji={text_ji}')
        
    except Exception as e:
        print(f'  ERROR: {e}')

print(f'\n{"="*100}')
print(f'统计: primary_empty={primary_empty}, avoid_empty={avoid_empty}')
