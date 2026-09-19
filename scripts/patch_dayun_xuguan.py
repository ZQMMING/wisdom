# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(p,encoding='utf-8').read()
old="        if new_hs:\n            hf=[w for w in new_hs if w in fav]; ha=[w for w in new_hs if w in av]\n"
new=("        # 虚官不犯(虚忌不凶, 对称虚喜犯旺): 专旺顺用、运干官杀复合tier0无根、运支非官杀根而为喜(比劫当令官绝/印化官)、非新会局化神,\n"
     "        # 则虚官坐本方被化/绝不能克旺反不犯(任注: 金不通根、支逢生旺), 干降闲以支喜主导; 会局化神虚干无依直冲(如寅午戌)仍由化神块判凶\n"
     "        if not new_hs:\n"
     "            _gw0={v:k for k,v in KE.items()}.get(WUXING[dm])\n"
     "            if _gw0 and gc=='av' and GAN_WX.get(g)==_gw0 and zc=='fav' and BRANCH_WX.get(z)!=_gw0 \\\n"
     "                    and element_power_tier(tp['wuxing_power'],_gw0)['tier']==0:\n"
     "                print('XUGUAN',li+1,''.join(a+b for a,b in fp)[:8],gz,'|',blob[:38].replace(chr(10),' '))\n"
     "                gc='xian'\n"
     "        if new_hs:\n"
     "            hf=[w for w in new_hs if w in fav]; ha=[w for w in new_hs if w in av]\n")
assert s.count(old)==1,('xg',s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('虚官不犯 done(含debug)')
