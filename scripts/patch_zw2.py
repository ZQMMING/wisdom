# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()

old1=("            if cai_zai:\n"
      "                P(gw,'WANG_KE','曲直春木，阳杀(庚)得财星本气之载，力足以修旺木，用杀')\n"
      "            elif not guan_rooted and stem(gw)>=1 and stem(sw)>=1:\n")
new1=("            if cai_zai:\n"
      "                P(gw,'WANG_KE','曲直春木，阳杀(庚)得财星本气之载，力足以修旺木，用杀')\n"
      "            elif stem(gw)>=1 and (ben(cw)>=1 or cs(cw)):\n"
      "                P(gw,'WANG_KE','曲直木旺成方，官杀透而得财星本气之生(财滋弱官)，运至官杀得地则贵，逆用官杀'); S(cw,'财生官杀')\n"
      "            elif not guan_rooted and stem(gw)>=1 and stem(sw)>=1:\n")
assert s.count(old1)==1,('quzhi',s.count(old1)); s=s.replace(old1,new1)

old2=("            else:\n"
      "                A(gw); S(cw,'食伤生财/身旺任财')\n")
new2=("            else:\n"
      "                A(gw)\n"
      "                if stem(sw)>=2 or cs(sw) or ben(cw)>=1 or cs(cw):\n"
      "                    S(cw,'食伤成势/财有根，食伤生财、身旺任财')\n"
      "                # 食伤仅虚透、财命局无本气根: 孤财难任不默认喜, 运至孤财犯旺之凶留应期层判\n")
assert s.count(old2)==1,('shuncai',s.count(old2)); s=s.replace(old2,new2)

old3=("        if '从财' in cong:\n"
      "            if t['cai']=='水' and (mz in ('亥','子','丑','辰') or cold):\n")
new3=("        if '从财' in cong:\n"
      "            A(t['guan'],'从财格官杀克从日主、泄财气，逆局忌之')\n"
      "            if t['cai']=='水' and (mz in ('亥','子','丑','辰') or cold):\n")
assert s.count(old3)==1,('congcai',s.count(old3)); s=s.replace(old3,new3)

old4=("            P(t['guan'],'CONG_SHUN','从官杀顺官杀'); S(t['cai'],'财生官杀')\n")
new4=("            P(t['guan'],'CONG_SHUN','从官杀顺官杀'); S(t['cai'],'财生官杀'); A(t['shi'],'从官杀格食伤制杀逆局忌之')\n")
assert s.count(old4)==1,('congguan',s.count(old4)); s=s.replace(old4,new4)

io.open(p,'w',encoding='utf-8',newline='').write(s)
print('曲直逆用财滋官+顺用财收窄+从格忌神 done')
