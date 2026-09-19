# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'D:\shuntian-ziping-p0')
from engines.common.l0_fact_builder import build
from engines.common.wuxing_power import build_wuxing_power
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.qtbj_climate_candidates import build_climate_candidates

WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}

for chart in ['丙申 己亥 庚辰 戊寅', '辛卯 辛丑 丁卯 癸卯', '辛丑 丙申 壬申 辛亥', '庚辰 丙戌 乙亥 庚辰']:
    parts = chart.split()
    pillars = {
        'year': (parts[0][0], parts[0][1]),
        'month': (parts[1][0], parts[1][1]),
        'day': (parts[2][0], parts[2][1]),
        'hour': (parts[3][0], parts[3][1]),
    }
    f = build(pillars)
    th = build_tian_he(pillars, f)
    wpo = build_wuxing_power(pillars, f, th)
    clc = build_climate_candidates(f)
    hou = [WX.get(c.get('stem',''), c.get('stem','')) for c in (clc.get('climate_candidates') or []) if isinstance(c, dict)]
    wp = wpo.get('wuxing_power', {})
    print(f'{chart}: 调候候选={hou}')
    for h in set(hou):
        p = wp.get(h, {})
        print(f'  {h}: ben_n={p.get("ben_n")}, stem_n={p.get("stem_n")}, ling={p.get("ling_state")}, zhong_n={p.get("zhong_n")}, yu_n={p.get("yu_n")}')
