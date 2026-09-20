# -*- coding: utf-8 -*-
"""显示用神不匹配案例的原文"""
import json, os

# 读取用神_all.jsonl
p = r'D:\顺天系统资料\用神案例JSONL\用神专项\用神_all.jsonl'
all_cases = []
with open(p, encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            case = json.loads(line)
            all_cases.append(case)

print(f'总案例数: {len(all_cases)}')

# 不匹配案例的八字
mismatch_bazi = [
    '辛亥 庚寅 丙子 乙未',
    '庚寅 己丑 丙子 乙未',
    '丁亥 辛亥 辛未 壬辰',
    '壬辰 甲辰 庚午 丙戌',
    '乙亥 庚辰 丙子 庚寅',
    '丁亥 壬子 庚子 辛巳',
]

for bazi in mismatch_bazi:
    found = False
    for case in all_cases:
        chart = case.get('bazi', '')
        if chart.replace(' ', '') == bazi.replace(' ', ''):
            print(f'\n{"="*80}')
            print(f'八字: {bazi}')
            print(f'case_id: {case.get("case_id", "")}')
            print(f'书籍: {case.get("book", "")}')
            raw = case.get('raw', '')
            print(f'原文: {raw[:400]}')
            found = True
            break
    if not found:
        print(f'\n未找到: {bazi}')
