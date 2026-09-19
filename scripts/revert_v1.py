# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\dts_export_csv.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

c = c.replace('from engines.common.dayun_xiji_v2 import build_dayun_xiji', 'from engines.common.dayun_xiji import build_dayun_xiji')
c = c.replace('dx = build_dayun_xiji(p, ye, dy, f)', 'dx = build_dayun_xiji(p, ye, dy)')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('回退到V1完成')
