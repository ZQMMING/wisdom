# -*- coding: utf-8 -*-
"""验证大运与原局地支关系"""
import sys
sys.path.insert(0, '.')

from engines.common.transit_power import build_transit_power

# 三个未命中案例
cases = [
    (270, '戊寅', '乙丑', '丙寅', '庚寅', '庚午', '午运暗会劫局'),
    (811, '壬辰', '丙午', '丙午', '壬辰', '乙酉', '酉运合去辰土'),
    (1430, '丙寅', '辛卯', '癸酉', '戊午', '丁亥', '午破酉'),
]

print('=== 大运与原局地支关系验证 ===')
print()

for li, y, m, d, h, dy, desc in cases:
    p = {'year': list(y), 'month': list(m), 'day': list(d), 'hour': list(h)}
    tp = build_transit_power(p, extra_pillars=[list(dy)])
    
    print('--- L{}: {} {} {} {} 运{} ({}) ---'.format(li, y, m, d, h, dy, desc))
    print('  原局地支:', [p[k][1] for k in ['year', 'month', 'day', 'hour']])
    print('  大运地支:', dy[1])
    print()
    
    cf = tp.get('combination_facts', {})
    print('  六合:', cf.get('liuhe', []))
    print('  六冲:', cf.get('liuchong', []))
    print('  六破:', cf.get('liupo', []))
    print()
