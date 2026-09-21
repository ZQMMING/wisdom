# -*- coding: utf-8 -*-
"""扫txt挖原著自述格局词, 得到弱金标子集"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from scripts.dayun_align import cases

# 原著自述格局词
GE_KEYWORDS = {
    '从格': ['从势', '从财', '从杀', '从官', '从儿', '弃命从', '二人同心', '顺其性', '顺其气势'],
    '专旺格': ['曲直', '炎上', '稼穑', '从革', '润下', '一行得气', '专旺', '一行'],
    '化气格': ['化气', '化木', '化火', '化土', '化金', '化水', '化出'],
    '两神成象': ['两神成象', '两气成象', '二人同心'],
}

stats = {
    'total': 0,
    'has_ge': 0,
    'by_type': {},
    'examples': {},
}

for li, fp, dy, txt in cases:
    if len(dy) < 4:
        continue
    stats['total'] += 1
    
    has_ge = False
    for ge_type, keywords in GE_KEYWORDS.items():
        for kw in keywords:
            if kw in txt:
                has_ge = True
                stats['by_type'][ge_type] = stats['by_type'].get(ge_type, 0) + 1
                if ge_type not in stats['examples']:
                    stats['examples'][ge_type] = []
                if len(stats['examples'][ge_type]) < 5:
                    stats['examples'][ge_type].append({
                        'li': li + 1,
                        'kw': kw,
                        'txt': txt[:80],
                    })
                break
    
    if has_ge:
        stats['has_ge'] += 1

print('=== 原著自述格局词扫描 ===')
print('总案例数: %d' % stats['total'])
print('提到格局的案例数: %d (%.1f%%)' % (
    stats['has_ge'], 100 * stats['has_ge'] / max(stats['total'], 1)))
print()
print('按格局类型分布:')
for ge_type, count in sorted(stats['by_type'].items(), key=lambda x: -x[1]):
    print('  %s: %d (%.1f%%)' % (
        ge_type, count, 100 * count / max(stats['total'], 1)))
print()
print('--- 示例 ---')
for ge_type, examples in stats['examples'].items():
    print('  [%s]' % ge_type)
    for ex in examples:
        print('    L%d (%s): %s' % (ex['li'], ex['kw'], ex['txt'][:50]))
