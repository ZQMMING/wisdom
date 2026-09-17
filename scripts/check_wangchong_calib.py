# -*- coding: utf-8 -*-
"""校WANGCHONG: 任氏说旺者冲衰/衰者拔/旺神发的盘."""
import csv, sys, re
sys.path.insert(0, '.')
path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines = open(path, encoding='utf-8').read().splitlines()
rows = list(csv.DictReader(open('scripts/dts_513_output.csv', encoding='utf-8-sig')))

# 任氏说"旺者冲衰衰者拔/衰神冲旺旺神发"的盘
for i, r in enumerate(rows):
    if 'WANGCHONG-SHUAI' not in r['queries']: continue
    li = int(r['line'])-1
    next_li = len(lines)
    for j in range(i+1, len(rows)):
        next_li = int(rows[j]['line'])-1; break
    seg = '\n'.join(lines[li:min(next_li, li+25)])
    if re.search(r'冲.*拔|拔.*根|冲.*发|冲.*旺|冲.*衰|衰.*冲|旺.*冲', seg):
        print(f"L{r['line']} {r['chart']}")
        print(f"  {seg[:200]}")
        print()
