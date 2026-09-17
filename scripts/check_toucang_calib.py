# -*- coding: utf-8 -*-
"""校透藏query: 逐一看TENGLUO/JUECHU/HE-HUASHEN触发是否合理."""
import csv, sys, re
sys.path.insert(0, '.')
path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines = open(path, encoding='utf-8').read().splitlines()
rows = list(csv.DictReader(open('scripts/dts_513_output.csv', encoding='utf-8-sig')))

# JUECHU=绝处逢生: 日主在月支绝, 但月令藏干有日主之根
print('=== JUECHU 16个, 逐个看 ===')
n=0
for r in rows:
    if 'JUECHU-FENGSHENG' in r['queries']:
        n+=1
        if n<=8:
            print(f"  L{r['line']} {r['chart']}")
print(f'  共{n}个')

# HE-HUASHEN=合化神得令
print('\n=== HE-HUASHEN 57个, 看是否合理 ===')
n=0
for r in rows:
    if 'HE-HUASHEN-DESHI' in r['queries']:
        n+=1
        if n<=8:
            print(f"  L{r['line']} {r['chart']}")
print(f'  共{n}个')
