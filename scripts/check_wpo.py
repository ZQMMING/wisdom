# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'D:\shuntian-ziping-p0')
from engines.common.wuxing_power import build_wuxing_power
from engines.common.l0_fact_builder import build as build_l0_facts

pillars = {'year':['甲','子'],'month':['乙','丑'],'day':['丙','寅'],'hour':['丁','卯']}
f = build_l0_facts(pillars)
wpo = build_wuxing_power(pillars, f, {})
print('wpo keys:', list(wpo.keys()))
if 'wuxing_power' in wpo:
    print('wuxing_power keys:', list(wpo['wuxing_power'].keys()))
    for k, v in wpo['wuxing_power'].items():
        print(f'  {k}: total={v.get("total")}, ling={v.get("ling_state")}')
