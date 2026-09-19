# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在三合判断前增加original_branches定义
old = """        # V1.2: 三合判断 (大运地支与原局两个地支形成三合局)
        for sanhe in SAN_HE:"""
new = """        # V1.2: 三合判断 (大运地支与原局两个地支形成三合局)
        original_branches = [pillars[k][1] for k in ['year', 'month', 'day', 'hour']]
        for sanhe in SAN_HE:"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('修复original_branches未定义bug')
