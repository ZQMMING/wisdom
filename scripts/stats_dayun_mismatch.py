# -*- coding: utf-8 -*-
"""大运喜忌不匹配案例类型统计"""
import sys, json, re
sys.path.insert(0, r'D:\shuntian-ziping-p0')

# 读取评估脚本的不匹配输出
import subprocess
result = subprocess.run([r'D:\shuntian\.venv\Scripts\python.exe', r'scripts\calc_dayun_xiji_accuracy.py'],
                       capture_output=True, text=True, cwd=r'D:\shuntian-ziping-p0')
output = result.stdout

# 解析不匹配案例
mismatches = []
lines = output.split('\n')
for i, line in enumerate(lines):
    if ': 引擎=' in line and '原文=' in line:
        parts = line.split(': 引擎=')
        bazi_dayun = parts[0].strip()
        rest = parts[1].split(', 原文=')
        engine = rest[0].strip()
        original = rest[1].strip()
        mismatches.append({'bazi_dayun': bazi_dayun, 'engine': engine, 'original': original})

print(f'总不匹配: {len(mismatches)}')
print()

# 按引擎判断类型统计
from collections import Counter
engine_types = Counter(m['engine'] for m in mismatches)
print('引擎判断类型分布:')
for k, v in engine_types.most_common():
    print(f'  {k}: {v} ({v/len(mismatches)*100:.1f}%)')
print()

# 按原文判断类型统计
original_types = Counter(m['original'] for m in mismatches)
print('原文判断类型分布:')
for k, v in original_types.most_common():
    print(f'  {k}: {v} ({v/len(mismatches)*100:.1f}%)')
print()

# 按错误类型统计
error_types = Counter()
for m in mismatches:
    key = f"{m['engine']} -> {m['original']}"
    error_types[key] += 1
print('错误类型分布:')
for k, v in error_types.most_common():
    print(f'  {k}: {v} ({v/len(mismatches)*100:.1f}%)')
print()

# 按命局统计（同一个命局的多个大运不匹配）
bazi_counts = Counter(m['bazi_dayun'].rsplit(' ', 1)[0] for m in mismatches)
print('不匹配大运数>=3的命局:')
for bazi, cnt in bazi_counts.most_common(10):
    if cnt >= 3:
        print(f'  {bazi}: {cnt}个大运不匹配')
