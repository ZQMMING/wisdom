# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\scripts\gen_topo.py'
s=io.open(p,encoding='utf-8').read()
old="and not (L==0 and month_wx==cai_wx and gs_ben>=1 and gs_stem>=1)):"
new="and not (L==0 and month_wx==cai_wx and gs_ben>=1 and gs is not None and int(gs.get('stem_n',0))>=1)):"
assert s.count(old)==1,('gs',s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('gs_stem -> int(gs.get stem) 修正')
