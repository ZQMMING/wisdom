# -*- coding: utf-8 -*-
"""校SHI-GUI-LU: 时柱有根比例57%, 抽查是否真有根."""
import csv, sys
sys.path.insert(0, '.')
rows = list(csv.DictReader(open('scripts/dts_513_output.csv', encoding='utf-8-sig')))
gui = [r for r in rows if 'SHI-GUI-LU' in r['queries']]
print(f'SHI-GUI-LU {len(gui)}个')
# 抽查10个
for r in gui[:10]:
    print(f"  L{r['line']} {r['chart']} root={r['root']}")
# 反查: 时柱无根但SHI-GUI-LU触发的
print('\n=== 时柱无根但SHI-GUI-LU触发(可能误判) ===')
import re
for r in rows:
    if 'SHI-GUI-LU' not in r['queries']: continue
    # 时柱是chart后两个字
    hz = r['chart'][-2:]
    print(f"  L{r['line']} {r['chart']} 时支={hz[1]}")
