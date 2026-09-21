# -*- coding: utf-8 -*-
"""从格12条错例方向分析：FP vs FN + 流向表"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from scripts.dayun_align import cases
import json
import re

# 读基线
baseline = json.load(open('baseline_special_20260922.json', encoding='utf-8'))
special_by_key = {}
for b in baseline:
    key = b['key']
    special_by_key[key] = b.get('special', '')

# 从格判断
def is_cong(special):
    return any(x in special for x in ['从财格', '从杀格', '从儿格', '从官格', '从势格'])

# 专旺格判断
def is_zhuanwang(special):
    return any(x in special for x in ['曲直格', '炎上格', '稼穑格', '从革格', '润下格'])

# 化气格判断
def is_huaqi(special):
    return '化' in special and '气格' in special

# 找账A·从格31条
CONG_INCLUDE = [r"从财", r"从杀", r"从儿", r"从官", r"弃命从", r"从势", r"从旺", r"从强", r"从化"]

cong_a_list = []
for idx, (li, fp, dy, txt) in enumerate(cases, 1):
    text = txt[:300] if txt else ''
    # 检查是否命中从格关键词
    hit = False
    for kw in CONG_INCLUDE:
        if re.search(kw, text):
            hit = True
            break
    if not hit:
        continue
    
    # 用key匹配基线
    key = ''.join(g+z for g,z in fp)
    sp = special_by_key.get(key, '')
    
    cong_a_list.append((idx, key, sp, text))

print('账A·从格总数:', len(cong_a_list))
print()

# 拆FP/FN
fp_list = []  # 原文非从格→引擎判从格
fn_list = []  # 原文从格→引擎非从格

for idx, key, sp, text in cong_a_list:
    engine_is_cong = is_cong(sp)
    original_is_cong = True  # 账A本来就是原文自述从格
    
    if not engine_is_cong:
        # FN：原文说从格，引擎没认
        fn_list.append((idx, key, sp, text))
    else:
        # 一致
        pass

print('FN（原文从格→引擎非从格）:', len(fn_list), '条')
print()

# FN流向表
print('=== FN流向表 ===')
flow_to = {}
for idx, key, sp, text in fn_list:
    if sp not in flow_to:
        flow_to[sp] = 0
    flow_to[sp] += 1

for target, count in sorted(flow_to.items(), key=lambda x: -x[1]):
    print('  →%s: %d条' % (target, count))
print()

# 找账B·从格FP（原文无格局→引擎判从格）
print('=== 账B·从格FP分析 ===')
fp_count = 0
for idx, (li, fp, dy, txt) in enumerate(cases, 1):
    text = txt[:300] if txt else ''
    
    # 检查是否命中从格关键词
    hit = False
    for kw in CONG_INCLUDE:
        if re.search(kw, text):
            hit = True
            break
    if hit:
        continue  # 账A跳过
    
    # 用key匹配基线
    key = ''.join(g+z for g,z in fp)
    sp = special_by_key.get(key, '')
    
    if is_cong(sp):
        fp_count += 1

print('账B·从格FP（原文无格局→引擎判从格）:', fp_count, '条')
print()

# 总结
print('=== 总结 ===')
print('账A·从格FN（需放宽）:', len(fn_list), '条')
print('账B·从格FP（需收紧）:', fp_count, '条')
print()

if len(fn_list) > fp_count:
    print('结论：以FN为主 → 需要放宽从格判定条件')
elif fp_count > len(fn_list):
    print('结论：以FP为主 → 需要收紧从格判定条件')
else:
    print('结论：FN和FP差不多 → 问题可能在结构，不在阈值')
