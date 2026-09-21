# -*- coding: utf-8 -*-
"""账A·化气格漏判分析"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from scripts.dayun_align import cases
import json

# 原文自述化气格关键词
HUAQI_KEYWORDS = ['化气', '化木', '化火', '化土', '化金', '化水', '乙庚化', '甲己化', '丙辛化', '丁壬化', '戊癸化']

# 找账A·化气格
account_a_huaqi = []
for idx, (li, fp, dy, txt) in enumerate(cases, 1):
    text = txt[:200] if txt else ''
    for kw in HUAQI_KEYWORDS:
        if kw in text:
            account_a_huaqi.append((idx, li, fp, txt))
            break

print('账A·化气格总数:', len(account_a_huaqi))
print()

# 读基线
baseline = json.load(open('baseline_special_20260922.json', encoding='utf-8'))
special_map = {b['li']: b.get('special', '') for b in baseline}

# 化气格判断
def is_huaqi(special):
    return '化' in special and '气格' in special

# 分类：kept_tp / lost_tp
kept_tp = []
lost_tp = []
for idx, li, fp, txt in account_a_huaqi:
    sp = special_map.get(idx, '')
    if is_huaqi(sp):
        kept_tp.append((idx, li, fp, sp, txt))
    else:
        lost_tp.append((idx, li, fp, sp, txt))

print('kept_tp（仍判化气）:', len(kept_tp))
print('lost_tp（流失）:', len(lost_tp))
print()

print('=== lost_tp前10条 ===')
for idx, li, fp, sp, txt in lost_tp[:10]:
    print('li=%d: %s' % (idx, sp))
    print('  八字: %s' % ''.join(g+z for g,z in fp))
    print('  原文: %s' % txt[:80].replace('\n', ' '))
    print()
