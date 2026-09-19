# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()
old=("            else:\n"
     "                P(gw,'WANG_KE','从革金旺喜火炼，取官杀火'); S(cw)\n")
new=("            elif stem(gw)==0 and stem(sw)>=1:\n"
     "                P(sw,'ZHUANWANG','从革金成局而官杀火不透无根，顺食伤水泄秀(金白水清)，虚火犯旺待运透根'); S(cw,'食伤生财')\n"
     "            elif stem(gw)==0:\n"
     "                P(t['bi'],'ZHUANWANG','从革金成局、火不透不逆炼，顺金'); S(sw,'食伤泄秀')\n"
     "            else:\n"
     "                P(gw,'WANG_KE','从革金旺、官杀火透，火炼秋金'); S(cw)\n")
assert s.count(old)==1, ('conge',s.count(old))
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('从革 else 顺逆收窄 done')
