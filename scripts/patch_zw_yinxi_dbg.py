# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()
old="            if ben(yw)>=1 and BRANCH_WX.get(mz)!=yw and ben(yw)<ben(t['bi']):\n                S(yw,'专旺顺用，印生本方而不过')\n"
new="            if ben(yw)>=1 and BRANCH_WX.get(mz)!=yw and ben(yw)<ben(t['bi']):\n                print('YINXI',''.join(a+b for a,b in pillars.values()),'印%s ben%d < 比劫 ben%d'%(yw,ben(yw),ben(t['bi'])))\n                S(yw,'专旺顺用，印生本方而不过')\n"
assert s.count(old)==1,('yx',s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('yinxi debug done')
