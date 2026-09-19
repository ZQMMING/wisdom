# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()

old3=("        if '从财' in cong:\n"
      "            A(t['guan'],'从财格官杀克从日主、泄财气，逆局忌之')\n"
      "            if t['cai']=='水' and (mz in ('亥','子','丑','辰') or cold):\n")
new3=("        if '从财' in cong:\n"
      "            if t['cai']=='水' and (mz in ('亥','子','丑','辰') or cold):\n")
assert s.count(old3)==1,('rc',s.count(old3)); s=s.replace(old3,new3)

old4="            P(t['guan'],'CONG_SHUN','从官杀顺官杀'); S(t['cai'],'财生官杀'); A(t['shi'],'从官杀格食伤制杀逆局忌之')\n"
new4="            P(t['guan'],'CONG_SHUN','从官杀顺官杀'); S(t['cai'],'财生官杀')\n"
assert s.count(old4)==1,('rg',s.count(old4)); s=s.replace(old4,new4)

io.open(p,'w',encoding='utf-8',newline='').write(s)
print('回退从格忌神(保留曲直逆用) done')
