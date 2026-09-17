# -*- coding: utf-8 -*-
"""查HEAVY盘里任氏说无根/根轻/弱的——可能误判."""
import csv, sys, re
sys.path.insert(0, '.')
path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines = open(path, encoding='utf-8').read().splitlines()
rows = list(csv.DictReader(open('scripts/dts_513_output.csv', encoding='utf-8-sig')))

# 对每个HEAVY盘, 读其段(到下一个盘行), 找"无根|根轻|无气|弱|衰|虚"
heavies = [r for r in rows if r['root']=='HEAVY']
suspect = []
for i, r in enumerate(rows):
    if r['root'] != 'HEAVY': continue
    li = int(r['line']) - 1
    # 找下一个盘行
    next_li = len(lines)
    for j in range(i+1, len(rows)):
        next_li = int(rows[j]['line']) - 1
        break
    seg = '\n'.join(lines[li:min(next_li, li+25)])
    # 任氏明确说无根/根轻
    if re.search(r'无根|根轻|无气|虚浮|弱极|衰极', seg):
        suspect.append((r['line'], r['chart'], seg[:200]))

print(f'HEAVY盘中任氏说无根/根轻/虚浮的: {len(suspect)}')
for s in suspect[:15]:
    print(f"\nL{s[0]} {s[1]}")
    print(f"  {s[2][:180]}")
