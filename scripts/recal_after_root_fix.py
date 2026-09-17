# -*- coding: utf-8 -*-
"""root修后重新校对JIRUO和root分布."""
import csv, sys
sys.path.insert(0, '.')
rows = list(csv.DictReader(open('scripts/dts_513_output.csv', encoding='utf-8-sig')))

from collections import Counter
rc = Counter(r['root'] for r in rows)
print('root:', dict(rc))
jq = Counter()
for r in rows:
    for q in r['queries'].split('|'):
        if q: jq[q]+=1
print('\nquery:')
for q,c in jq.most_common(): print(f'  {q:22s} {c}')

# 新NONE的盘里JIRUO触发了吗
print('\n=== 新NONE盘(之前LIGHT现在NONE) ===')
n=0
for r in rows:
    if r['root']=='NONE':
        n+=1
        if n<=15: print(f"  L{r['line']} {r['chart']}  queries={r['queries'][:60]}")
