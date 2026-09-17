# -*- coding: utf-8 -*-
"""校两端: 任氏说"两停/成党/势均力敌" vs ZHONGGUA; 说"从势/偏旺" vs 单端."""
import csv, sys, re
sys.path.insert(0, '.')
path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines = open(path, encoding='utf-8').read().splitlines()
rows = list(csv.DictReader(open('scripts/dts_513_output.csv', encoding='utf-8-sig')))

# 任氏说"从格/从势/从财/从杀/从儿"的, 应单端(无扶)
cong = []
for i, r in enumerate(rows):
    li = int(r['line'])-1
    next_li = len(lines)
    for j in range(i+1, len(rows)):
        next_li = int(rows[j]['line'])-1; break
    seg = '\n'.join(lines[li:min(next_li, li+25)])
    if re.search(r'从财|从杀|从儿|从其势|从弱|从旺|从强|从格|从官|从其旺|顺其势', seg):
        cong.append((r['line'], r['chart'], r['root'], r['queries'][:80]))
print(f'任氏说从格/从势: {len(cong)}')
for c in cong[:15]:
    print(f"  L{c[0]} {c[1]} root={c[2]}")
    print(f"    {c[3]}")
