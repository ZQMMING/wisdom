# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()
old="            elif stem(gw)>=1 and (ben(cw)>=1 or cs(cw)):\n                P(gw,'WANG_KE','曲直木旺成方，官杀透而得财星本气之生(财滋弱官)，运至官杀得地则贵，逆用官杀'); S(cw,'财生官杀')\n"
new="            elif stem(gw)>=1 and stem(cw)>=1 and (ben(cw)>=1 or cs(cw)):\n                P(gw,'WANG_KE','曲直木旺成方，官杀透且财星透干通根以生官(财滋弱官)，运至官杀得地则贵，逆用官杀'); S(cw,'财生官杀')\n"
assert s.count(old)==1,('qz',s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('曲直逆用收紧为财透干通根 done')
