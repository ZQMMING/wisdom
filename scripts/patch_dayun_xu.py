# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(p,encoding='utf-8').read()

old_imp1="from engines.common.wuxing_power import build_wuxing_power, build_spectrum_topology, BRANCH_WX\n"
new_imp1="from engines.common.wuxing_power import build_wuxing_power, build_spectrum_topology, BRANCH_WX, SHENG, KE\n"
assert s.count(old_imp1)==1,('i1',s.count(old_imp1)); s=s.replace(old_imp1,new_imp1)
old_imp2="from engines.common.transit_power import build_transit_power, transit_clash_verdicts\n"
new_imp2="from engines.common.transit_power import build_transit_power, transit_clash_verdicts, element_power_tier\n"
assert s.count(old_imp2)==1,('i2',s.count(old_imp2)); s=s.replace(old_imp2,new_imp2)

old=("        new_hs=new_huashen(tp0,tp)\n"
     "        if new_hs:\n")
new=("        new_hs=new_huashen(tp0,tp)\n"
     "        # 虚喜犯旺(微神入旺乡): 命局太旺/旺极、生扶方P(比劫或印)成势tier>=2, 运上与P相克(财/官, 非顺泄秀神)的喜神复合仍虚tier<=1,\n"
     "        # 则微财微官无力为用、反激旺神/被旺神所灭, 降判忌; 喜神得根成党tier>=2为真用神不犯。有序枚举+比重, # PCT-MARK\n"
     "        _spec=ye.get('spectrum_tier') or ''\n"
     "        if _spec in ('太旺','旺极'):\n"
     "            _SHENG_ME={v:k for k,v in SHENG.items()}; _dmw=WUXING[dm]\n"
     "            _P=max('木火土金水', key=lambda x: element_power_tier(tp0,x)['tier'])\n"
     "            if _P in (_dmw, _SHENG_ME.get(_dmw)) and element_power_tier(tp0,_P)['tier']>=2:\n"
     "                def _xufan(w):\n"
     "                    return bool(w) and (KE.get(_P)==w or KE.get(w)==_P) and element_power_tier(tp,w)['tier']<=1\n"
     "                if gc=='fav' and _xufan(GAN_WX[g]): gc='av'\n"
     "                if zc=='fav' and not new_hs and _xufan(BRANCH_WX[z]): zc='av'\n"
     "        if new_hs:\n")
assert s.count(old)==1,('xu',s.count(old)); s=s.replace(old,new)

io.open(p,'w',encoding='utf-8',newline='').write(s)
print('虚喜犯旺 done')
