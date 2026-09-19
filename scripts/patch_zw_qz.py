# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()
old=("            elif not guan_rooted and stem(gw)>=1 and stem(sw)>=1:\n"
     "                P(sw,'WANG_KE','曲直官杀虚透临绝(木旺金缺)，食伤火透泄秀兼制虚杀，寒木向阳')\n")
new=("            elif not guan_rooted and ben(cw)==0 and not cs(cw) and (BRANCH_WX.get(mz)==yw or ling(yw)=='旺') and stem(gw)>=1 and stem(sw)>=1:\n"
     "                P(sw,'ZHUANWANG','曲直官杀根绝(临绝、财虚不生官)而印星当令旺，食伤火透寒木向阳顺泄；比劫化印(卯泄水生火)为喜，不忌比劫'); S(t['bi'],'比劫化印')\n"
     "                print('ZW-QZ-DEBUG',''.join(a+b for a,b in pillars.values()))\n"
     "            elif not guan_rooted and stem(gw)>=1 and stem(sw)>=1:\n"
     "                P(sw,'WANG_KE','曲直官杀虚透临绝(木旺金缺)，食伤火透泄秀兼制虚杀，寒木向阳')\n")
assert s.count(old)==1,('qz',s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('曲直印月官绝顺用 done(含debug)')
