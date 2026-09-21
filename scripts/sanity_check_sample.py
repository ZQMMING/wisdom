# -*- coding: utf-8 -*-
"""sanity check: 20条抽样案例的基线输出核对"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
import json

# 读基线
with open('baseline_special_20260922.json', 'r', encoding='utf-8') as f:
    baseline = json.load(f)

# 20条抽样案例(按li编号, 从0开始)
sample_li = [1897, 471, 190, 2035, 902, 849, 726, 491, 461, 1986, 1606, 396, 1839, 1363, 244, 656, 729, 1520, 1865, 1811]

print('=== sanity check: 20条抽样案例基线输出 ===')
print()
print('基线条数: %d' % len(baseline))
print()

# 检查每条抽样案例的输出
all_zhuanwang = True
not_zhuanwang = []

for li in sample_li:
    # 找基线中对应的案例
    case = None
    for b in baseline:
        if b['li'] == li + 1:  # 基线li从1开始, 我们从0开始
            case = b
            break
    
    if not case:
        print('L%d: 未找到!' % (li+1))
        not_zhuanwang.append(li)
        all_zhuanwang = False
        continue
    
    special = case.get('special', '')
    is_zhuanwang = any(x in special for x in ['曲直格', '炎上格', '稼穑格', '从革格', '润下格'])
    
    status = '专旺' if is_zhuanwang else '非专旺'
    print('L%d [%s]: %s' % (li+1, status, special))
    
    if not is_zhuanwang:
        all_zhuanwang = False
        not_zhuanwang.append(li)

print()
print('=== 结果 ===')
print('20条全是专旺: %s' % ('✅ 通过' if all_zhuanwang else '❌ 不通过'))
if not all_zhuanwang:
    print('非专旺的案例: %s' % [x+1 for x in not_zhuanwang])

# 检查有描述组的9条真阳性
print()
print('=== 有描述组9条真阳性核对 ===')
desc_group = [902, 491, 461, 396, 1606, 244, 656, 729, 1520]
for li in desc_group:
    case = None
    for b in baseline:
        if b['li'] == li + 1:
            case = b
            break
    if case:
        print('L%d: %s' % (li+1, case.get('special', '')))

# 检查反证组4条
print()
print('=== 反证组4条核对 ===')
anti_group = [471, 2035, 726, 1811]
for li in anti_group:
    case = None
    for b in baseline:
        if b['li'] == li + 1:
            case = b
            break
    if case:
        print('L%d: %s' % (li+1, case.get('special', '')))
