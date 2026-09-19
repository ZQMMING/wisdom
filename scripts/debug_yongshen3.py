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

def debug_case(bazi_str, name=''):
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

    print(f'=== {name} {bazi_str} ===')
    print(f'日主: {f["day_stem"]}, 月令: {pillars["month"][1]}')
    print(f'旺衰谱: {spt.get("spectrum")}')
    print(f'调候候选: {[c.get("stem") for c in (clc.get("climate_candidates") or []) if isinstance(c, dict)]}')
    print(f'气候结构: cold={cl.get("cold")}, hot={cl.get("hot")}, dry={cl.get("dry")}, wet={cl.get("wet")}')
    print(f'特殊格局: cong={spc.get("cong_type")}, zw={spc.get("zhuanwang")}, hua={spc.get("hua_qi")}, hua_state={spc.get("hua_qi_state")}')
    print(f'用神: primary={ye.get("yongshen_primary")}, paths={ye.get("yongshen_paths")}')
    print()

cases = [
    ('戊子 庚申 乙丑 壬午', 'QT-0040: 原文=火(专用丁火), 引擎=金'),
    ('丁亥 丁未 乙酉 丁亥', 'QT-0147: 原文=水(专此壬水), 引擎=金'),
    ('庚辰 丙戌 乙亥 庚辰', 'QT-0168: 原文=火(只能用丙火), 引擎=水'),
]

for bazi, name in cases:
    debug_case(bazi, name)
