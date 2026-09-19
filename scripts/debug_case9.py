# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'D:\shuntian-ziping-p0')
from engines.common.l0_fact_builder import build
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_topology
from engines.common.special_pattern import build_special_patterns
from engines.common.climate_candidates import build_climate_candidates
from engines.common.yongshen_engine import build_yongshen_engine

pillars = {
    'year': ['己', '丑'],
    'month': ['丙', '子'],
    'day': ['辛', '酉'],
    'hour': ['壬', '辰'],
}

facts = build(pillars)
wpo = build_wuxing_power(pillars, facts)
spt = build_spectrum_topology(wpo)
spc = build_special_patterns(pillars, facts, wpo)
clc = build_climate_candidates(facts)
ys = build_yongshen_engine(pillars, facts, wpo, spt, spc, clc)

print('spectrum:', spt.get('spectrum'))
print('tier in ys:', ys.get('tier'))
print('ys primary:', ys.get('primary'))
print('ys path:', ys.get('paths'))

wp = wpo.get('wuxing_power', {})
for w in ['金','水','土','火','木']:
    d = wp.get(w, {})
    print(f'{w}: ben={d.get("ben_n")}, stem={d.get("stem_n")}, ling={d.get("ling_state")}, zhong={d.get("zhong_n")}, yu={d.get("yu_n")}')
