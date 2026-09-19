# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'D:\shuntian-ziping-p0')
from engines.common.l0_fact_builder import build
from engines.common.wuxing_power import build_wuxing_power

pillars = {'year': ('丁', '巳'), 'month': ('癸', '丑'), 'day': ('丁', '卯'), 'hour': ('丙', '午')}
facts = build(pillars)
wpo = build_wuxing_power(pillars, facts)

print('wpo[wuxing_power] type:', type(wpo['wuxing_power']))
print('wpo[wuxing_power]:', wpo['wuxing_power'])
print()

# 如果是列表，查看每个元素
if isinstance(wpo['wuxing_power'], list):
    for i, item in enumerate(wpo['wuxing_power']):
        print(f'[{i}]: {item}')
