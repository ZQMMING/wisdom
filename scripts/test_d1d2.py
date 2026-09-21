# -*- coding: utf-8 -*-
"""测试原局内部六合"""
import sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build as l0build

test_cases = [
    ('甲子', '丙丑', '戊寅', '庚寅'),  # 子丑六合
    ('甲午', '丙未', '戊申', '庚酉'),  # 午未六合
    ('甲辰', '丙酉', '戊戌', '庚亥'),  # 辰酉六合
    ('甲寅', '丙亥', '戊子', '庚丑'),  # 寅亥六合
    ('甲子', '丙巳', '戊寅', '庚寅'),  # 子巳暗会
]

for y, m, d, h in test_cases:
    p = {'year': list(y), 'month': list(m), 'day': list(d), 'hour': list(h)}
    f = l0build(p)
    relations = f.get('branch_relations', [])
    print('%s%s%s%s: %d条关系' % (y, m, d, h, len(relations)))
    for r in relations:
        print('  %s %s-%s pos=%s huashen=%s' % (
            r['type'], r['branches'][0], r['branches'][1],
            r['position'], r.get('huashen', r.get('anhui_shen', ''))))
