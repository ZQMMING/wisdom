# -*- coding: utf-8 -*-
"""dump基线标签: 当前引擎对509条的special输出"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from scripts.dayun_align import cases, engine
import json

baseline = []
for idx, (li, fp, dy, txt) in enumerate(cases, 1):  # 索引从1开始
    if len(dy) < 4:
        continue
    try:
        p, f, ye, tp0, wp, th = engine(fp)
        special = ye.get('special') or ''
        yongshen_primary = ye.get('yongshen_primary') or ''
        yongshen_secondary = ye.get('yongshen_secondary') or []
        yongshen_avoid = ye.get('yongshen_avoid') or []
        
        baseline.append({
            'li': idx,  # 用索引代替原文行号
            'fp': fp,
            'special': special,
            'yongshen_primary': yongshen_primary,
            'yongshen_secondary': yongshen_secondary,
            'yongshen_avoid': yongshen_avoid,
        })
    except Exception as e:
        baseline.append({
            'li': idx,  # 用索引代替原文行号
            'fp': fp,
            'error': str(e),
        })

# 保存到文件
with open('baseline_special_20260922.json', 'w', encoding='utf-8') as f:
    json.dump(baseline, f, ensure_ascii=False, indent=2)

print('基线已保存: baseline_special_20260922.json')
print('总案例数: %d' % len(baseline))
print()
print('special分布:')
from collections import Counter
special_dist = Counter(b['special'] for b in baseline if 'special' in b)
for sp, count in special_dist.most_common():
    print('  %s: %d' % (sp, count))

