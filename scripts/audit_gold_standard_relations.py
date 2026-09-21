# -*- coding: utf-8 -*-
"""金标审计: 502条案例断语中, 多少条提到地支/天干关系"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')

from scripts.dayun_align import cases

# 地支/天干关系关键词
RELATION_KEYWORDS = {
    '六合': ['合去', '合住', '合绊', '合化', '合局', '合而', '合之', '合为'],
    '三合三会': ['三合', '三会', '会局', '合局'],
    '六冲': ['冲去', '冲散', '冲开', '冲克', '冲战', '冲之', '冲而', '相冲'],
    '三刑': ['三刑', '刑伤', '刑出', '刑入', '刑至'],
    '六害': ['六害', '害之', '相害'],
    '六破': ['破之', '相破', '破出', '破入'],
    '暗会拱合': ['暗会', '暗拱', '拱合', '拱出'],
    '天干合': ['合官', '合煞', '合财', '合印', '合食', '合伤', '合比', '合劫'],
}

# 统计
stats = {
    'total': 0,
    'has_relation': 0,
    'by_type': {k: 0 for k in RELATION_KEYWORDS.keys()},
    'no_relation_examples': [],
    'relation_examples': [],
}

for li, fp, dy, txt in cases:
    if len(dy) < 4:
        continue
    stats['total'] += 1
    
    # 检查断语中是否提到关系
    has_rel = False
    rel_types = []
    for rel_type, keywords in RELATION_KEYWORDS.items():
        if isinstance(keywords, list):
            for kw in keywords:
                if kw in txt:
                    has_rel = True
                    rel_types.append(rel_type)
                    stats['by_type'][rel_type] += 1
                    break
        else:
            if keywords in txt:
                has_rel = True
                rel_types.append(rel_type)
                stats['by_type'][rel_type] += 1
    
    if has_rel:
        stats['has_relation'] += 1
        if len(stats['relation_examples']) < 10:
            stats['relation_examples'].append({
                'li': li + 1,
                'rel_types': rel_types,
                'txt': txt[:100],
            })
    else:
        if len(stats['no_relation_examples']) < 10:
            stats['no_relation_examples'].append({
                'li': li + 1,
                'txt': txt[:100],
            })

print('=== 金标审计: 断语中地支/天干关系统计 ===')
print()
print('总案例数: %d' % stats['total'])
print('提到关系的案例数: %d (%.1f%%)' % (
    stats['has_relation'], 100 * stats['has_relation'] / max(stats['total'], 1)))
print('未提到关系的案例数: %d (%.1f%%)' % (
    stats['total'] - stats['has_relation'],
    100 * (stats['total'] - stats['has_relation']) / max(stats['total'], 1)))
print()
print('按关系类型分布:')
for rel_type, count in sorted(stats['by_type'].items(), key=lambda x: -x[1]):
    print('  %s: %d (%.1f%%)' % (
        rel_type, count, 100 * count / max(stats['total'], 1)))
print()
print('--- 提到关系的案例示例(前10) ---')
for ex in stats['relation_examples']:
    print('  L%d [%s]: %s' % (ex['li'], '/'.join(ex['rel_types']), ex['txt'][:60]))
print()
print('--- 未提到关系的案例示例(前10) ---')
for ex in stats['no_relation_examples']:
    print('  L%d: %s' % (ex['li'], ex['txt'][:60]))
