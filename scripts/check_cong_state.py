# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'D:\shuntian-ziping-p0')
from engines.common.l0_fact_builder import build
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.wuxing_power import build_wuxing_power
from engines.common.climate_structure import build_climate_structure
from engines.common.special_pattern import build_special_patterns

for chart in ['丙戌 癸巳 乙亥 癸未', '辛卯 壬辰 癸未 丙辰']:
    p = chart.split()
    pillars = {
        'year': (p[0][0], p[0][1]),
        'month': (p[1][0], p[1][1]),
        'day': (p[2][0], p[2][1]),
        'hour': (p[3][0], p[3][1]),
    }
    f = build(pillars)
    th = build_tian_he(pillars, f)
    wpo = build_wuxing_power(pillars, f, th)
    cl = build_climate_structure(pillars, f, th)
    spc = build_special_patterns(pillars, f, wpo, th, cl)
    ct = spc.get('cong_type')
    cs = spc.get('cong_state')
    print(f'{chart}: cong={ct}, cong_state={cs}')
