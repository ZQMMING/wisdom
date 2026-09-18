# -*- coding: utf-8 -*-
import csv
rows=list(csv.DictReader(open('scripts/dts_513_output.csv',encoding='utf-8')))
print(f'总案例: {len(rows)}')
print(f'列名: {list(rows[0].keys())}')
print()
for i,r in enumerate(rows[:3]):
    print(f'--- 案例{i+1} ---')
    for k in ['daymaster','root_detail','queries','text']:
        v = r.get(k,'')
        if k=='queries':
            cnt = len([q for q in v.split('|') if q.strip()])
            print(f'  {k}: {cnt}个query')
        else:
            print(f'  {k}: {v[:60]}')
    print()
