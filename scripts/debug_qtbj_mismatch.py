# -*- coding: utf-8 -*-
"""调试QTBJ用神不匹配案例"""
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

cases = [
    ('甲辰 甲戌 甲辰 甲戌', '火'),
    ('壬申 壬子 辛亥 癸巳', '火'),
    ('辛卯 壬辰 癸未 丙辰', '火'),
]

for bazi, expected in cases:
    parts = bazi.split()
    pillars = {
        'year': (parts[0][0], parts[0][1]),
        'month': (parts[1][0], parts[1][1]),
        'day': (parts[2][0], parts[2][1]),
        'hour': (parts[3][0], parts[3][1]),
    }
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
        
        print(f'\n{"="*60}')
        print(f'八字: {bazi}')
        print(f'日主: {f["day_stem"]}')
        print(f'spectrum_tier: {ye.get("spectrum_tier", "")}')
        print(f'调候候选: {clc}')
        print(f'用神primary: {ye.get("yongshen_primary", "")}')
        print(f'用神secondary: {ye.get("yongshen_secondary", [])}')
        print(f'忌神avoid: {ye.get("yongshen_avoid", [])}')
        print(f'theory_source: {ye.get("theory_source", "")}')
        print(f'原文期望: {expected}')
        
    except Exception as e:
        print(f'ERROR: {e}')
        import traceback
        traceback.print_exc()
