# -*- coding: utf-8 -*-
"""D1/D2地支关系事实层验证"""
import sys
sys.path.insert(0, '.')

from engines.common.l0_fact_builder import build as l0build

# 三个验证用例
cases = [
    (270, '戊寅', '乙丑', '丙寅', '庚寅', '午运暗会劫局'),
    (811, '壬辰', '丙午', '丙午', '壬辰', '酉运合去辰土'),
    (1430, '丙寅', '辛卯', '癸酉', '戊午', '午破酉'),
]

print('=== D1/D2地支关系事实层验证 ===')
print()

for li, y, m, d, h, desc in cases:
    p = {'year': list(y), 'month': list(m), 'day': list(d), 'hour': list(h)}
    f = l0build(p)
    print('--- L{}: {} {} {} {} ({}) ---'.format(li, y, m, d, h, desc))
    
    relations = f.get('branch_relations', [])
    if not relations:
        print('  [无地支关系]')
    else:
        for r in relations:
            print('  类型: {} {}↔{}'.format(r['type'], r['branches'][0], r['branches'][1]))
            print('    位置: {} {}'.format(r['position'], r['positions']))
            if r['type'] == 'liuhe':
                print('    化神: {}'.format(r['huashen']))
                print('    中间支: {} 阻隔: {}'.format(r['intervening_branches'], r['has_blocking']))
            if r['type'] == 'anhui':
                print('    暗会之神: {} 证据等级: {}'.format(r['anhui_shen'], r.get('evidence_grade')))
    
    print()
