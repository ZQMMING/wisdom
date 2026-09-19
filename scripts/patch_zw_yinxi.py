# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()
old="            S(t['bi'],'顺性喜比劫')\n"
new=("            S(t['bi'],'顺性喜比劫')\n"
     "            # 专旺顺用印喜: 印不当令、印本气党少于比劫(印生本方而不壅、非母灭)则印为喜(曲直喜水/润下喜金/炎上喜木, 任注: 支逢生旺/木运名利);\n"
     "            # 印当令旺或印党>=比劫(母旺需比劫化泄、土多金埋)不再喜印。# PCT-MARK 印/比劫本气党众比较\n"
     "            if ben(yw)>=1 and BRANCH_WX.get(mz)!=yw and ben(yw)<ben(t['bi']):\n"
     "                S(yw,'专旺顺用，印生本方而不过')\n")
assert s.count(old)==1,('yinxi',s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('专旺顺用印喜(不过则喜) done')
