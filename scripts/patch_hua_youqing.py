# -*- coding: utf-8 -*-
# 假化有情补第三门(与special化气透干通根门对齐): 非CONFIRMED但化神透干+有本气根(透干通根)、
# 日主与印皆无本气根(不从正格) -> 化神有情, 按真化喜忌(P化神/S生神与泄秀/A克化神与返本印)。
# 任注"丙火透而通根,化火斯真,嫌壬水克丙"=真化带病。L1640戊癸化火: 丙透通根巳禄、癸无根无金本气印。
import io
fp=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(fp,encoding='utf-8').read()
old="""        if (BRANCH_WX.get(mz)==hua_hwx) or \\
           (ben(hua_hwx)>=2 and (stem(hua_hwx)>=1 or (_sh and stem(_sh)>=1))):
            hua_youqing=True"""
assert s.count(old)==1, ('old',s.count(old))
new="""        if (BRANCH_WX.get(mz)==hua_hwx) or \\
           (ben(hua_hwx)>=2 and (stem(hua_hwx)>=1 or (_sh and stem(_sh)>=1))) or \\
           (stem(hua_hwx)>=1 and ben(hua_hwx)>=1 and ben(dmw)==0 and ben(t['yin'])==0):
            hua_youqing=True"""
s=s.replace(old,new)
io.open(fp,'w',encoding='utf-8',newline='').write(s)
print('patched hua_youqing tougan-tonggen rootless gate')
