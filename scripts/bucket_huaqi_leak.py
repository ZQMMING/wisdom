# -*- coding: utf-8 -*-
"""自动分桶化气格漏判38条：岁运化/地支合化/隔位合/关键词噪声"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from scripts.dayun_align import cases
import json
import re

# 化气格关键词
HUAQI_KEYWORDS = ['化气', '化木', '化火', '化土', '化金', '化水', '乙庚化', '甲己化', '丙辛化', '丁壬化', '戊癸化']

# 读基线
baseline = json.load(open('baseline_special_20260922.json', encoding='utf-8'))
special_by_key = {}
for b in baseline:
    key = b['key']
    special_by_key[key] = b.get('special', '')

# 化气格判断
def is_huaqi(special):
    return '化' in special and '气格' in special

# 找账A·化气格（用key匹配）
lost_list = []
for idx, (li, fp, dy, txt) in enumerate(cases, 1):
    text = txt[:300] if txt else ''
    # 检查是否命中化气关键词
    is_account_a = False
    for kw in HUAQI_KEYWORDS:
        if kw in text:
            is_account_a = True
            break
    if not is_account_a:
        continue
    
    # 用key匹配基线
    key = ''.join(g+z for g,z in fp)
    sp = special_by_key.get(key, '')
    
    if not is_huaqi(sp):
        lost_list.append((idx, key, sp, text, fp))

print('账A·化气格lost_tp总数:', len(lost_list))
print()

# 自动分桶
buckets = {
    '岁运化': [],
    '地支合化': [],
    '隔位合': [],
    '关键词噪声': [],
    '其他': [],
}

for idx, key, sp, text, fp in lost_list:
    tags = []
    
    # 1. 岁运化
    if re.search(r'(大运|流年|行运|运至|岁运|运走|运转).{0,10}化', text):
        tags.append('岁运化')
    
    # 2. 地支合化
    if re.search(r'(子丑|寅亥|卯戌|辰酉|巳申|午未).{0,10}化', text):
        tags.append('地支合化')
    
    # 3. 关键词噪声（没有明确的化气格表述）
    if not re.search(r'(化气|格成.*化|化合|化神)', text):
        tags.append('关键词噪声')
    
    # 分桶（按优先级）
    if '岁运化' in tags:
        buckets['岁运化'].append(idx)
    elif '地支合化' in tags:
        buckets['地支合化'].append(idx)
    elif '关键词噪声' in tags:
        buckets['关键词噪声'].append(idx)
    else:
        buckets['其他'].append(idx)

print('=== 自动分桶结果 ===')
for bucket, ids in buckets.items():
    print('%s: %d条' % (bucket, len(ids)))
print()

# 打印"其他"桶（可能是规则可修的）
print('=== 其他桶（规则可修候选）===')
for idx in buckets['其他'][:10]:
    # 找原文
    for i, (li, fp, dy, txt) in enumerate(cases, 1):
        if i == idx:
            print('li=%d: %s' % (idx, txt[:80].replace('\n', ' ')))
            break
