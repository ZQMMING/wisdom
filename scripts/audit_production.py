# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.')
from engines.production_entry import production_entry, FrozenCanonicalBaziChart

# 测试生产入口
pillars = {'year':('甲','子'),'month':('丙','寅'),'day':('戊','午'),'hour':('庚','申')}
chart = FrozenCanonicalBaziChart(pillars=pillars, canonical=True, frozen=True, source='test')
result = production_entry(chart)

print('=== Production Entry 审计 ===')
print(f'EngineResult keys: {list(result.keys()) if isinstance(result, dict) else type(result)}')
if isinstance(result, dict):
    for k in sorted(result.keys()):
        v = result[k]
        if isinstance(v, list):
            print(f'  {k}: list[{len(v)}]')
        elif isinstance(v, dict):
            print(f'  {k}: dict[{len(v)}]')
        else:
            s = str(v)[:80]
            print(f'  {k}: {type(v).__name__} = {s}')

# 测试大运
print('\n=== 大运层审计 ===')
dayun = result.get('dayun', {})
if dayun:
    print(f'  dayun keys: {list(dayun.keys())}')
    if 'dayun_list' in dayun:
        print(f'  大运数量: {len(dayun["dayun_list"])}')
        if dayun['dayun_list']:
            print(f'  第一步大运: {dayun["dayun_list"][0]}')
else:
    print('  无大运数据')

# 测试流年
print('\n=== 流年层审计 ===')
liunian = result.get('liunian', {})
if liunian:
    print(f'  liunian keys: {list(liunian.keys())}')
else:
    print('  无流年数据')
