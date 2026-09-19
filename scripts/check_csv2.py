# -*- coding: utf-8 -*-
import csv
with open(r'D:\shuntian-ziping-p0\scripts\dts_513_output.csv', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i < 3:
            dx = row.get('dayun_xiji', '')
            print(f'行{i}: dayun_xiji长度={len(dx)}, 前100字={dx[:100]}')
        else:
            break
