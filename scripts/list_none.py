# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0, '.')
rows = list(csv.DictReader(open('scripts/dts_513_output.csv', encoding='utf-8-sig')))
none = [r for r in rows if r['root']=='NONE']
heavy = [r for r in rows if r['root']=='HEAVY']
print(f'NONE {len(none)} 个, HEAVY {len(heavy)} 个')
print('\n=== NONE 列表 ===')
for r in none:
    print(f"  L{r['line']} {r['chart']}")
