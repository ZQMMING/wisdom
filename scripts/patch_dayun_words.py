# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(p,encoding='utf-8').read()
old_ji="'无恙']"; new_ji="'升迁','举于乡','县宰','无恙']"
assert s.count(old_ji)==1,('ji',s.count(old_ji)); s=s.replace(old_ji,new_ji)
old_x="'艰难']"; new_x="'一败而尽','一败涂地','艰难']"
assert s.count(old_x)==1,('x',s.count(old_x)); s=s.replace(old_x,new_x)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('纯词表补充 done')
