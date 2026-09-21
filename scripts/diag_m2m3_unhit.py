# -*- coding: utf-8 -*-
"""未命中案例M2/M3专项诊断(独立版)"""
import sys
sys.path.insert(0, '.')

from engines.common.l0_fact_builder import build as l0build
from engines.common.daymaster_tian_he import build_tian_he

# 5个未命中案例 (年,月,日,时,大运)
cases = [
    (270, '戊寅', '乙丑', '丙寅', '庚寅', '庚午'),
    (811, '壬辰', '丙午', '丙午', '壬辰', '乙酉'),
    (1013, '癸酉', '甲子', '庚辰', '甲申', '癸亥'),
    (1430, '丙寅', '辛卯', '癸酉', '戊午', '丁亥'),
    (1827, '戊子', '庚申', '壬寅', '辛丑', '甲子'),
]

print('=== 未命中案例M2/M3专项诊断 ===')
print()

for li, y, m, d, h, dy in cases:
    p = {'year': list(y), 'month': list(m), 'day': list(d), 'hour': list(h)}
    f = l0build(p)
    th = build_tian_he(p, f)
    print('--- L{}: {} {} {} {} 运{} ---'.format(li, y, m, d, h, dy))
    
    if not th.get('he_pairs'):
        print('  [命局无天干五合]')
    else:
        for i, pair in enumerate(th['he_pairs']):
            print('  合对{}: {}↔{}'.format(i+1, pair['stems'][0], pair['stems'][1]))
            print('    M2-A 位置:', pair.get('position_distance'))
            print('    M2-B 阻隔:', pair.get('has_blocking_intervening'), '间干:', pair.get('intervening_stems'))
            print('    M3-A 日主自合:', pair.get('is_daymaster_self_he'))
            print('    M3-A 主体:{}({}) 目标:{}({})'.format(
                pair.get('he_subject'), pair.get('he_subject_pos'),
                pair.get('he_target'), pair.get('he_target_pos')))
            print('    M3-B 争合:', pair.get('is_competition'), pair.get('competition_type'))
            print('    M3-C 目标十神:', pair.get('he_target_shishen'))
    
    print()
