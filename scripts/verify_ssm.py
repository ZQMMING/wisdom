# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build as l0build, WUXING
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.wuxing_power import build_wuxing_power

p = {'year': '甲子', 'month': '辛未', 'day': '戊午', 'hour': '己未'}
f = l0build(p)
th = build_tian_he(p, f)
wp = build_wuxing_power(p, f, th)

print('=== 戊土日主(甲子辛未戊午己未) ===')
print('daymaster:', wp.get('daymaster'))
print('daymaster_element:', wp.get('daymaster_element'))
print()
print('stem_strength_modifier:')
ssm = wp.get('stem_strength_modifier', {})
for k, v in ssm.items():
    print(f'  {k}: {v}')
