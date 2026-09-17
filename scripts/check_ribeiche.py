# -*- coding: utf-8 -*-
"""校RI-BEI-HE: 日主被合(甲己/乙庚/丙辛/丁壬/戊癸)."""
import csv, sys, re
sys.path.insert(0, '.')
path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines = open(path, encoding='utf-8').read().splitlines()
rows = list(csv.DictReader(open('scripts/dts_513_output.csv', encoding='utf-8-sig')))

# RI-BEI-HE: 日干被邻干合
n=0
for r in rows:
    if 'RI-BEI-HE' in r['queries']:
        n+=1
        if n<=10:
            print(f"  L{r['line']} {r['chart']}")
print(f'共{n}个')

# 任氏说"日主被合/合去/合绊/合而不化"的盘
print('\n=== 任氏说日主被合 ===')
for i, r in enumerate(rows):
    li = int(r['line'])-1
    next_li = len(lines)
    for j in range(i+1, len(rows)):
        next_li = int(rows[j]['line'])-1; break
    seg = '\n'.join(lines[li:min(next_li, li+20)])
    if re.search(r'日主合|日主被合|合去日主|合而不化|合绊', seg):
        has = 'RI-BEI-HE' in r['queries']
        print(f"  L{r['line']} {r['chart']} 识别={has}")
