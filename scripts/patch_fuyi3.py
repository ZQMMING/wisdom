# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()
old="                zhi_ok=stem(t['shi'])>=1 and qi(t['shi']) and (tier in WANG_TIER or _dm_root_ok)  # 食伤制杀: 身旺可任; 身弱须日主有不被冲拔本气根(根拔/虚透不任制强杀)\n"
new=("                # 食伤制杀(身弱杀重)成立两路: ①食伤自有本气根/成势(儿能救母, 如丙坐午临旺制坚金);\n"
     "                # ②日主有不被冲拔本气根、食伤透有气(身能任制); 两者俱无(食伤虚、日主根拔)则取印化杀\n"
     "                zhi_ok=stem(t['shi'])>=1 and qi(t['shi']) and (tier in WANG_TIER or ben(t['shi'])>=1 or cs(t['shi']) or _dm_root_ok)\n")
assert s.count(old)==1, ('zhi_ok3',s.count(old))
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('zhi_ok 双路(食伤自旺/日主根稳) done')
