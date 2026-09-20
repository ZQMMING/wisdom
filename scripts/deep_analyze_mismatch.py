# -*- coding: utf-8 -*-
"""深度分析不匹配案例的用神/忌神/relations"""
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

# 分析前10个不匹配案例
print(f'{"="*120}')
print('深度分析前10个不匹配案例:')
for i, m in enumerate(mismatches[:10]):
    chart = m.get('chart', '')
    dayun_str = m.get('dayun', '')
    text = m.get('text', '')[:120]
    engine_label = m.get('engine_label', '') or m.get('engine', '')
    
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
        
        # 跑大运喜忌
        dayun_list = [dayun_str]
        dy_result = build_dayun_xiji(pillars, ye, dayun_list, wpo)
        per_step = dy_result.get('per_step', {})
        step_result = per_step.get(dayun_str, {})
        xiji_label = step_result.get('xiji_label', '')
        relations = step_result.get('relations', [])
        has_xi = step_result.get('has_xi', False)
        has_ji = step_result.get('has_ji', False)
        
        print(f'\n[{i+1}] {chart} 日主={f["day_stem"]} 月支={chart[3]} 大运={dayun_str}')
        print(f'  用神: primary={primary}, secondary={secondary}, avoid={avoid}')
        print(f'  theory={theory}, tier={tier}')
        print(f'  引擎: label={xiji_label}, has_xi={has_xi}, has_ji={has_ji}')
        print(f'  relations={relations}')
        print(f'  原文: {text}')
        
    except Exception as e:
        print(f'  ERROR: {e}')
        import traceback
        traceback.print_exc()
