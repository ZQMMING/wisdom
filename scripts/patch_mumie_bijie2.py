# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()
old=("            elif ben(t['yin'])>=3 and ben(t['bi'])<=1 and ben(t['cai'])==0 and stem(t['cai'])==0 \\\n"
     "                    and stem(t['shi'])==0 and ben(t['guan'])==0:\n")
new=("            elif ben(t['yin'])>=3 and ben(t['bi'])<=1 and ben(t['cai'])==0 and stem(t['cai'])==0 \\\n"
     "                    and stem(t['shi'])==0 and ben(t['shi'])==0 and ben(t['guan'])==0:\n")
assert s.count(old)==1,('mm2',s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('母灭分支收窄(食伤亦无本气根, 排官印相生流通用官) done')
