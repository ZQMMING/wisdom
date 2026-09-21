# -*- coding: utf-8 -*-
"""统计全量案例的M2/M3分布"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')

# 复用dayun_align的解析逻辑
from scripts.dayun_align import cases, engine

stats = {
    'total_cases': 0,
    'total_he_pairs': 0,
    'by_position_distance': {},
    'by_blocking': 0,
    'by_self_he': 0,
    'by_competition': 0,
    'by_competition_type': {},
    'by_target_shishen': {},
}

for li, fp, dy, txt in cases:
    try:
        p, f, ye, tp0, wp, th = engine(fp)
        stats['total_cases'] += 1
        for pair in th.get('he_pairs', []):
            stats['total_he_pairs'] += 1
            pd = pair.get('position_distance', 'unknown')
            stats['by_position_distance'][pd] = stats['by_position_distance'].get(pd, 0) + 1
            if pair.get('has_blocking_intervening'):
                stats['by_blocking'] += 1
            if pair.get('is_daymaster_self_he'):
                stats['by_self_he'] += 1
            if pair.get('is_competition'):
                stats['by_competition'] += 1
            ct = pair.get('competition_type')
            if ct:
                stats['by_competition_type'][ct] = stats['by_competition_type'].get(ct, 0) + 1
            ss = pair.get('he_target_shishen', 'unknown')
            stats['by_target_shishen'][ss] = stats['by_target_shishen'].get(ss, 0) + 1
    except Exception:
        pass

print('=== M2/M3 全量分布统计 ===')
print('总案例数:', stats['total_cases'])
print('总合对数:', stats['total_he_pairs'])
print()
print('M2-A 位置距离:')
for k, v in sorted(stats['by_position_distance'].items(), key=lambda x: -x[1]):
    print('  {}: {} ({:.1f}%)'.format(k, v, v/stats['total_he_pairs']*100))
print()
print('M2-B 有阻隔:', stats['by_blocking'])
print('M3-A 日主本身之合:', stats['by_self_he'])
print('M3-B 争合:', stats['by_competition'])
print()
print('M3-B 争合类型:')
for k, v in sorted(stats['by_competition_type'].items(), key=lambda x: -x[1]):
    print('  {}: {}'.format(k, v))
print()
print('M3-C/E 合去目标十神:')
for k, v in sorted(stats['by_target_shishen'].items(), key=lambda x: -x[1]):
    print('  {}: {} ({:.1f}%)'.format(k, v, v/stats['total_he_pairs']*100))
