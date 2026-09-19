# -*- coding: utf-8 -*-
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

WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}

def debug_case(bazi_str, name='', expected=''):
    parts = bazi_str.split()
    pillars = {
        'year': (parts[0][0], parts[0][1]),
        'month': (parts[1][0], parts[1][1]),
        'day': (parts[2][0], parts[2][1]),
        'hour': (parts[3][0], parts[3][1]),
    }
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
    hou = [WX.get(c.get('stem',''), c.get('stem','')) for c in (clc.get('climate_candidates') or []) if isinstance(c, dict)]
    wp = wpo.get('wuxing_power', {})

    print(f'=== {name}: 原文={expected}, 引擎={ye.get("yongshen_primary")} {bazi_str} ===')
    print(f'  日主: {f["day_stem"]}, 月令: {pillars["month"][1]}, 旺衰谱: {spt.get("spectrum")}')
    print(f'  调候候选: {hou}')
    for h in set(hou):
        p = wp.get(h, {})
        print(f'    {h}: ben_n={p.get("ben_n")}, stem_n={p.get("stem_n")}, ling={p.get("ling_state")}')
    print(f'  特殊格局: cong={spc.get("cong_type")}, zw={spc.get("zhuanwang")}, hua={spc.get("hua_qi")}, hua_state={spc.get("hua_qi_state")}')
    print(f'  用神: primary={ye.get("yongshen_primary")}, paths={ye.get("yongshen_paths")}')
    print(f'  喜神: {ye.get("xishen")}, 忌神: {ye.get("jishen")}')
    print()

cases = [
    ('丙申 己亥 庚辰 戊寅', 'DT-0263', '土'),
    ('甲辰 甲戌 甲辰 甲戌', 'QT-0058', '金'),
    ('丙戌 癸巳 乙亥 癸未', 'QT-0137', '水'),
    ('庚辰 丙戌 乙亥 庚辰', 'QT-0168', '火'),
    ('丁丑 丁未 丙午 己丑', 'QT-0252', '土'),
    ('辛丑 丙申 壬申 辛亥', 'QT-0684', '火'),
    ('辛卯 壬辰 癸未 丙辰', 'QT-0734', '火'),
    ('辛卯 辛丑 丁卯 癸卯', 'SF-0083', '土'),
]

for bazi, name, expected in cases:
    debug_case(bazi, name, expected)
