# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(p,encoding='utf-8').read()
old=("            if ha and not hf: lc='av'\n"
     "            elif hf and not ha: lc='fav'\n"
     "            else: lc='mix'\n")
new=("            _shun=any(x in ('ZHUANWANG','LIANGQI','CONG_SHUN') for x in (ye.get('yongshen_paths') or []))\n"
     "            if ha and not hf: lc='av'\n"
     "            elif hf and not ha:\n"
     "                # 顺用格会顺神方局(化神喜)而运干为逆神: 运支入会局被化, 干逆神在原局无本气根=虚透犯旺主凶(任注: 虚神犯旺/激其冲奔); 有本气根则相争混。正格身弱会印局(杀印相生)paths非顺用, 不触发\n"
     "                if _shun and gc=='av' and int(tp0['wuxing_power']['wuxing_power'][GAN_WX[g]].get('ben_n',0))==0:\n"
     "                    lc='av'\n"
     "                elif _shun and gc=='av':\n"
     "                    lc='mix'\n"
     "                else:\n"
     "                    lc='fav'\n"
     "            else: lc='mix'\n")
assert s.count(old)==1,('ju',s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('化神不救虚干犯旺 done')
