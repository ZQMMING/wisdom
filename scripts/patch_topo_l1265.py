# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\scripts\gen_topo.py'
s=io.open(p,encoding='utf-8').read()
old=("    elif (S>=3 and guan_hua and dm_has_lu and yin_ben>=1 and yin_stem>=1\n"
     "          and fin_rooted_eff<=1 and ratio>=0.20):\n"
     "        spec='旺'   # 财当令而财->官->印->身流通, 禄刃+本气印双透: 日元临旺逢生官印双清(乙卯丁亥戊午丙辰)\n")
new=("    elif (S>=3 and guan_hua and dm_has_lu and yin_ben>=1 and yin_stem>=1\n"
     "          and fin_rooted_eff<=1 and ratio>=0.20\n"
     "          and not (L==0 and month_wx==cai_wx and gs_ben>=1 and gs_stem>=1)):\n"
     "        spec='旺'   # 财当令而财->官->印->身流通, 禄刃+本气印双透: 日元临旺逢生官印双清(乙卯丁亥戊午丙辰);\n"
     "        # PCT-MARK 例外: 日主囚死月令(L=0)+财当令+官杀本气根且透干=财官连环成党压失令之身(春金虽弱/杀重身轻, L1265甲午丙寅辛酉己丑), 不落流通判旺, 交后line204太衰身弱喜印比\n")
assert s.count(old)==1,('g',s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('gen_topo line177 财官连环失令例外 added')
