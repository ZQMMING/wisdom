# -*- coding: utf-8 -*-
import json
from collections import Counter

with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', encoding='utf-8') as f:
    details = json.load(f)

print(f'总不匹配: {len(details)}')
print()

# 按错误类型统计
error_types = Counter(f"{d['engine']} -> {d['text']}" for d in details)
print('错误类型分布:')
for k, v in error_types.most_common():
    print(f'  {k}: {v} ({v/len(details)*100:.1f}%)')
print()

# 按命局统计（同一个命局的多个大运不匹配）
bazi_counts = Counter(d['chart'] for d in details)
print('不匹配大运数>=3的命局 (前20):')
for bazi, cnt in bazi_counts.most_common(20):
    if cnt >= 3:
        # 获取这个命局的所有不匹配大运
        dayuns = [d['dayun'] for d in details if d['chart'] == bazi]
        engines = [d['engine'] for d in details if d['chart'] == bazi]
        texts = [d['text'] for d in details if d['chart'] == bazi]
        print(f'  {bazi}: {cnt}个大运不匹配')
        print(f'    大运: {dayuns}')
        print(f'    引擎: {engines}')
        print(f'    原文: {texts}')
print()

# 按引擎判断类型统计
engine_types = Counter(d['engine'] for d in details)
print('引擎判断类型分布:')
for k, v in engine_types.most_common():
    print(f'  {k}: {v} ({v/len(details)*100:.1f}%)')
print()

# 按原文判断类型统计
original_types = Counter(d['text'] for d in details)
print('原文判断类型分布:')
for k, v in original_types.most_common():
    print(f'  {k}: {v} ({v/len(details)*100:.1f}%)')
