# -*- coding: utf-8 -*-
import csv
rows=list(csv.DictReader(open('scripts/dts_513_output.csv',encoding='utf-8-sig')))
for r in rows:
    if '癸巳癸亥甲寅壬申' in r.get('chart',''):
        print(f'日主: {r["daymaster"]}')
        print(f'根: {r["root"]}')
        print(f'根详情: {r["root_detail"]}')
        print(f'季节: {r["season"]}')
        print(f'queries: {r["queries"]}')
        break
