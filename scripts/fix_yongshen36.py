# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

old = "ben(t['guan'])==0 and d(t['guan'])['zhong_n']==0 and d(t['guan'])['yu_n']>=1"
new = "ben(t['guan'])==0 and (d(t['guan'])['zhong_n']>=1 or d(t['guan'])['yu_n']>=1)"

count = c.count(old)
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print(f'替换完成, 替换次数: {count}')
