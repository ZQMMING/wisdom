# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'D:\shuntian-ziping-p0')
from engines.common.l0_fact_builder import build
from engines.common.wuxing_power import build_wuxing_power

pillars = {'year': ('丁', '巳'), 'month': ('癸', '丑'), 'day': ('丁', '卯'), 'hour': ('丙', '午')}
facts = build(pillars)
wpo = build_wuxing_power(pillars, facts)

print('wpo keys:', list(wpo.keys()))
print()
for k, v in wpo.items():
    if isinstance(v, dict):
        print(f'{k}: {list(v.keys())}')
        if k == 'wuxing' or k == 'power':
            for wx, d in v.items():
                print(f'  {wx}: {d}')
    else:
        print(f'{k}: {v}')
