# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(p,encoding='utf-8').read()
q="                print('XUGUAN',li+1,''.join(a+b for a,b in fp)[:8],gz,'|',blob[:38].replace(chr(10),' '))\n"
assert s.count(q)==1,('dbg',s.count(q))
io.open(p,'w',encoding='utf-8',newline='').write(s.replace(q,''))
print('XUGUAN debug removed')
