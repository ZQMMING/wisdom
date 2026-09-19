# -*- coding: utf-8 -*-
import csv
with open(r'D:\shuntian-ziping-p0\scripts\dts_513_output.csv', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

# 检查用神过旺反忌条件触发情况
trigger_count = 0
for row in rows:
    chart = row['chart']
    dayun_str = row.get('dayun', '')
    if not dayun_str:
        continue
    dayun_list = dayun_str.split('|')
    
    # 检查每个大运的标签
    for item in row.get('dayun_xiji', '').split('|'):
        if ':' in item:
            parts = item.split(':')
            gz = parts[0]
            label = parts[1] if len(parts) > 1 else ''
            # 检查是否有SUPPRESS_USE_GOD标签(可能是用神过旺反忌触发的)
            if 'SUPPRESS' in label:
                trigger_count += 1

print(f'SUPPRESS_USE_GOD标签总数: {trigger_count}')
print(f'总命例数: {len(rows)}')
