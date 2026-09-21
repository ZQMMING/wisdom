# -*- coding: utf-8 -*-
"""检查A: 调候在金标里出现多少次"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')

# 直接导入cases, 不调用main
from scripts.dayun_align import cases

TIAOHOU_KEYWORDS = [
    '寒', '暖', '燥', '湿',
    '调候', '水火既济',
    '丙火', '癸水',
    '冬生', '夏生',
    '寒木', '暖土', '燥土', '湿土',
    '水冷', '火炎', '金寒', '木凋',
    '解冻', '滋湿', '调候为急',
    '金水相涵', '木火通明',
    '水旺火熄', '火炎土燥',
    '水冷金寒',
    '寒极', '暖极',
    '丙癸', '丁甲',
]

stats = {'total': 0, 'has_th': 0, 'by_kw': {}}

for li, fp, dy, txt in cases:
    if len(dy) < 4:
        continue
    stats['total'] += 1
    has = False
    for kw in TIAOHOU_KEYWORDS:
        if kw in txt:
            has = True
            stats['by_kw'][kw] = stats['by_kw'].get(kw, 0) + 1
    if has:
        stats['has_th'] += 1

print('总案例数: %d' % stats['total'])
print('提到调候的案例数: %d (%.1f%%)' % (
    stats['has_th'], 100 * stats['has_th'] / max(stats['total'], 1)))
print()
print('按关键词分布:')
for kw, count in sorted(stats['by_kw'].items(), key=lambda x: -x[1])[:15]:
    print('  %s: %d' % (kw, count))
