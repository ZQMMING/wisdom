# -*- coding: utf-8 -*-
"""调候共现过滤: 只计数与寒暖燥湿等核心调候词同句出现的记录"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from scripts.dayun_align import cases

# 核心调候词(必须同句出现才算)
CORE_TIAOHOU = ['寒', '暖', '燥', '湿', '调候', '解冻', '既济', '炎上', '润下', '枯', '凋']

# 辅助调候词(出现但不单独算, 需要与核心词同句)
AUX_TIAOHOU = ['丙火', '癸水', '甲木', '丁火', '水冷', '火炎', '金寒', '木凋', '寒木', '暖土', '燥土', '湿土']

stats = {
    'total': 0,
    'has_core': 0,  # 有核心调候词
    'has_core_and_aux': 0,  # 核心+辅助同句
    'core_only': 0,  # 只有核心词
}

for li, fp, dy, txt in cases:
    if len(dy) < 4:
        continue
    stats['total'] += 1
    
    has_core = any(kw in txt for kw in CORE_TIAOHOU)
    has_aux = any(kw in txt for kw in AUX_TIAOHOU)
    
    if has_core:
        stats['has_core'] += 1
        if has_aux:
            stats['has_core_and_aux'] += 1
        else:
            stats['core_only'] += 1

print('=== 调候共现过滤 ===')
print('总案例数: %d' % stats['total'])
print()
print('有核心调候词(寒/暖/燥/湿/调候/解冻/既济/炎上/润下/枯/凋): %d (%.1f%%)' % (
    stats['has_core'], 100 * stats['has_core'] / max(stats['total'], 1)))
print('  核心+辅助同句: %d (%.1f%%)' % (
    stats['has_core_and_aux'],
    100 * stats['has_core_and_aux'] / max(stats['total'], 1)))
print('  只有核心词: %d (%.1f%%)' % (
    stats['core_only'],
    100 * stats['core_only'] / max(stats['total'], 1)))
print()
print('对比:')
print('  原始扫描(含日主常规提及): 48.7%')
print('  核心词过滤后: %.1f%%' % (100 * stats['has_core'] / max(stats['total'], 1)))
print('  核心+辅助共现: %.1f%%' % (100 * stats['has_core_and_aux'] / max(stats['total'], 1)))
