# -*- coding: utf-8 -*-
import io
p=r'scripts/gen_topo.py'
s=io.open(p,encoding='utf-8').read()
old="        lu_chong = bool(_chong_ben) and (L<2 or (cai_ben+gs_ben > dm_ben))"
new=("        # 当令根被单冲属衰神冲旺旺神发(不伤); 唯财官本气党众悬殊(>=身根+2, 两卯+寅+午)方拔\n"
     "        lu_chong = bool(_chong_ben) and (L<2 or (cai_ben+gs_ben >= dm_ben+2))")
assert s.count(old)==1, s.count(old)
io.open(p,'w',encoding='utf-8',newline='').write(s.replace(old,new))
# B 规则阈值同步
oldb="    elif lu_chong and ratio<0.62 and (L<2 or (cai_ben+gs_ben > dm_ben)):"
newb="    elif lu_chong and ratio<0.62 and (L<2 or (cai_ben+gs_ben >= dm_ben+2)):"
assert s.count(oldb)==1, ('b',s.count(oldb))
s=io.open(p,encoding='utf-8').read().replace(old,new)
s=s.replace(oldb,newb)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('众冲寡阈值收紧为 财官本气>=身根+2')
