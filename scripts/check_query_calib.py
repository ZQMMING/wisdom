# -*- coding: utf-8 -*-
"""校对query触发: 查SUPPORTED query里明显不对的."""
import csv, sys
sys.path.insert(0, '.')
rows = list(csv.DictReader(open('scripts/dts_513_output.csv', encoding='utf-8-sig')))

# 各query触发率
from collections import Counter
q_all = Counter()
for r in rows:
    for q in r['queries'].split('|'):
        if q: q_all[q] += 1
print('query触发率:')
for q, c in q_all.most_common():
    print(f'  {q:22s} {c:4d}  ({c/len(rows)*100:.0f}%)')

# 找JIRUO=极弱无根但root不是NONE的
print('\n=== JIRUO触发但root!=NONE ===')
for r in rows:
    if 'JIRUO-WUGEN' in r['queries'] and r['root'] != 'NONE':
        print(f"  L{r['line']} {r['chart']} root={r['root']}")

# 找TENGLUO=藤萝系甲但日主不是乙的
print('\n=== TENGLUO触发 ===')
for r in rows:
    if 'TENGLUO-XIJIA' in r['queries']:
        print(f"  L{r['line']} {r['chart']} root={r['root']}")
