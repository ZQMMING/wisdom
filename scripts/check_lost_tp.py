# -*- coding: utf-8 -*-
"""查账A·专旺流失的2条真例：官杀是否有制"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from scripts.dayun_align import cases

# 原文自述格局关键词
SPECIAL_KEYWORDS = {
    '专旺': ['曲直', '炎上', '稼穑', '从革', '润下', '一行得气', '专旺'],
}

# 找账A·专旺格
account_a_zhuanwang = []
for idx, (li, fp, dy, txt) in enumerate(cases, 1):
    text = txt[:200] if txt else ''
    for kw in SPECIAL_KEYWORDS['专旺']:
        if kw in text:
            account_a_zhuanwang.append((idx, li, fp, txt))
            break

print('账A·专旺格总数:', len(account_a_zhuanwang))
print()

# 读基线
import json
baseline = json.load(open('baseline_special_20260922.json', encoding='utf-8'))
special_map = {b['li']: b.get('special', '') for b in baseline}

# 找流失的真例（原文自述专旺，但引擎没判专旺）
def is_zhuanwang(special):
    return any(x in special for x in ['曲直格', '炎上格', '稼穑格', '从革格', '润下格'])

lost_tp = []
kept_tp = []
for idx, li, fp, txt in account_a_zhuanwang:
    sp = special_map.get(idx, '')
    if is_zhuanwang(sp):
        kept_tp.append((idx, li, fp, sp, txt))
    else:
        lost_tp.append((idx, li, fp, sp, txt))

print('kept_tp（仍判专旺）:', len(kept_tp))
print('lost_tp（流失）:', len(lost_tp))
print()

print('=== lost_tp详细 ===')
for idx, li, fp, sp, txt in lost_tp:
    print('li=%d' % idx)
    print('  八字: %s' % ''.join(g+z for g,z in fp))
    print('  引擎判定: %s' % sp)
    print('  原文前100字: %s' % txt[:100].replace('\n', ' '))
    print()
