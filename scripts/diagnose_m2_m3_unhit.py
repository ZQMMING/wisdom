# -*- coding: utf-8 -*-
"""未命中案例M2/M3专项诊断"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')

from scripts.dayun_align import cases, engine

# 5个未命中案例
target_li = [270, 811, 1013, 1430, 1827]

print('=== 未命中案例M2/M3专项诊断 ===')
print()

for li, fp, dy, txt in cases:
    if li not in target_li:
        continue
    p, f, ye, tp0, wp, th = engine(fp)
    print('--- L{}: {} {} {} {} 运{} ---'.format(li, fp[0], fp[1], fp[2], fp[3], dy))
    print('原文:', txt[:80])
    print()
    
    if not th.get('he_pairs'):
        print('  [无天干五合]')
        print()
        continue
    
    for i, pair in enumerate(th['he_pairs']):
        print('  合对{}: {}↔{}'.format(i+1, pair['stems'][0], pair['stems'][1]))
        print('    M2-A 位置距离:', pair.get('position_distance'))
        print('    M2-B 间干:', pair.get('intervening_stems'), '阻隔:', pair.get('has_blocking_intervening'))
        print('    M3-A 日主自合:', pair.get('is_daymaster_self_he'))
        print('    M3-A 主体:{}({}) 目标:{}({})'.format(
            pair.get('he_subject'), pair.get('he_subject_pos'),
            pair.get('he_target'), pair.get('he_target_pos')))
        print('    M3-B 有竞争者:', pair.get('has_rival'), '争合:', pair.get('is_competition'))
        if pair.get('competition_type'):
            print('    M3-B 类型:', pair.get('competition_type'))
        print('    M3-C 目标十神:', pair.get('he_target_shishen'))
        print()
    
    print()
