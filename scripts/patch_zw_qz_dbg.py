# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()
q="                print('ZW-QZ-DEBUG',''.join(a+b for a,b in pillars.values()))\n"
assert s.count(q)==1,('dbg',s.count(q))
io.open(p,'w',encoding='utf-8',newline='').write(s.replace(q,''))
print('debug removed')
