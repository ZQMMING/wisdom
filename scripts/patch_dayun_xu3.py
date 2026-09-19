# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(p,encoding='utf-8').read()
old=("        if _spec in ('太旺','旺极'):\n"
     "            _SHENG_ME={v:k for k,v in SHENG.items()}; _dmw=WUXING[dm]\n"
     "            _P=max('木火土金水', key=lambda x: element_power_tier(tp0['wuxing_power'],x)['tier'])\n"
     "            if _P in (_dmw, _SHENG_ME.get(_dmw)) and element_power_tier(tp0['wuxing_power'],_P)['tier']>=2:\n"
     "                def _xufan(w):\n"
     "                    return bool(w) and (KE.get(_P)==w or KE.get(w)==_P) and element_power_tier(tp['wuxing_power'],w)['tier']<=1\n"
     "                if gc=='fav' and _xufan(GAN_WX[g]): gc='av'\n"
     "                if zc=='fav' and not new_hs and _xufan(BRANCH_WX[z]): zc='av'\n")
new=("        if _spec in ('太旺','旺极'):\n"
     "            _SHENG_ME={v:k for k,v in SHENG.items()}; _dmw=WUXING[dm]\n"
     "            _KE_ME={v:k for k,v in KE.items()}\n"
     "            _P=max('木火土金水', key=lambda x: element_power_tier(tp0['wuxing_power'],x)['tier'])\n"
     "            _ke_set={KE.get(_dmw), _KE_ME.get(_dmw)}  # 仅财(我克)+官杀(克我)为逆神; 食伤顺泄秀、印比不犯旺\n"
     "            if _P in (_dmw, _SHENG_ME.get(_dmw)) and element_power_tier(tp0['wuxing_power'],_P)['tier']>=2:\n"
     "                def _xufan(w):\n"
     "                    # 完全无本气根的虚透(tier0衰)方为微神犯旺; 有一根(含运柱得禄/通根,tier>=1)即能立, 不犯。根被冲拔/合化折减另见合化刀\n"
     "                    return bool(w) and w in _ke_set and element_power_tier(tp['wuxing_power'],w)['tier']==0\n"
     "                if gc=='fav' and _xufan(GAN_WX[g]): gc='av'\n"
     "                if zc=='fav' and not new_hs and _xufan(BRANCH_WX[z]): zc='av'\n")
assert s.count(old)==1,('xu3',s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('虚喜犯旺收紧(财官+tier0) done')
