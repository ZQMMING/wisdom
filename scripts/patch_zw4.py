# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()
old=("            else:\n"
     "                A(gw)\n"
     "                if stem(sw)>=2 or cs(sw) or ben(cw)>=1 or cs(cw):\n"
     "                    S(cw,'食伤成势/财有根，食伤生财、身旺任财')\n"
     "                # 食伤仅虚透、财命局无本气根: 孤财难任不默认喜, 运至孤财犯旺之凶留应期层判\n")
new=("            else:\n"
     "                A(gw); S(cw,'食伤生财/身旺任财')  # 顺用身旺任财; 孤财犯旺(无通关、运财被专旺方众冲)之凶由应期层判\n")
assert s.count(old)==1,('revert',s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('回退顺用财收窄(留应期层) done')
