# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.')
from engines.production_entry import production_entry, FrozenCanonicalBaziChart

pillars = {'year':('甲','子'),'month':('丙','寅'),'day':('戊','午'),'hour':('庚','申')}
chart = FrozenCanonicalBaziChart(pillars=pillars, canonical=True, frozen=True, source='test')
result = production_entry(chart)
er = result['engine_result']

print('=== EngineResult 33字段 ===')
for k in sorted(er.keys()):
    v = er[k]
    if isinstance(v, list):
        print(f'  {k}: list[{len(v)}]')
    elif isinstance(v, dict):
        print(f'  {k}: dict[{len(v)}]')
    elif isinstance(v, bool):
        print(f'  {k}: bool = {v}')
    else:
        s = str(v)[:100]
        print(f'  {k}: {type(v).__name__} = {s}')
