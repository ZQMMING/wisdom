# -*- coding: utf-8 -*-
"""查LIGHT盘里任氏说根重/禄旺/通根的真错."""
import csv, sys, re
sys.path.insert(0, '.')
path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines = open(path, encoding='utf-8').read().splitlines()
rows = list(csv.DictReader(open('scripts/dts_513_output.csv', encoding='utf-8-sig')))

suspect = []
for i, r in enumerate(rows):
    if r['root'] != 'LIGHT': continue
    li = int(r['line']) - 1
    next_li = len(lines)
    for j in range(i+1, len(rows)):
        next_li = int(rows[j]['line']) - 1; break
    seg = '\n'.join(lines[li:min(next_li, li+25)])
    # 任氏说日主根重/禄旺/通根/长生
    if re.search(r'日主.*(根重|禄旺|长生|通根|临官|帝旺|羊刃)', seg) or re.search(r'(根重|禄旺|通根身旺)', seg):
        suspect.append((r['line'], r['chart'], seg[:220]))

print(f'LIGHT盘中任氏说日主根重/禄旺的: {len(suspect)}')
for s in suspect[:15]:
    print(f"\nL{s[0]} {s[1]}")
    print(f"  {s[2][:200]}")
