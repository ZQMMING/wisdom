# -*- coding: utf-8 -*-
"""显示用神不匹配案例的原文"""
import json

# 读取用神专项案例
books = ['滴天髓', '穷通宝鉴', '子平真诠', '渊海子平', '千里命稿', '神峰通考']
all_cases = []
for book in books:
    p = rf'D:\顺天系统资料\用神案例JSONL\用神专项\{book}.jsonl'
    try:
        with open(p, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    case = json.loads(line)
                    case['book'] = book
                    all_cases.append(case)
    except Exception as e:
        pass

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
    for case in all_cases:
        chart = case.get('chart', '') or case.get('bazi', '')
        if chart.replace(' ', '') == bazi.replace(' ', ''):
            print(f'\n{"="*80}')
            print(f'八字: {bazi}')
            print(f'书籍: {case.get("book", "")}')
            print(f'名称: {case.get("name", "")}')
            judgment = case.get('judgment', '') or case.get('text', '') or ''
            print(f'原文: {judgment[:300]}')
            break
