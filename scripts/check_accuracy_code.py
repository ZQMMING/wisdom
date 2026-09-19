# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_dayun_xiji_accuracy.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 先查看当前的匹配逻辑结构
import re
# 找到engine_label的位置
print('当前engine_label相关代码:')
for i, line in enumerate(c.split('\n')):
    if 'engine_label' in line or 'dayun_xiji' in line:
        print(f'  {i}: {line.strip()}')
