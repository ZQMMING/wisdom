# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(p,encoding='utf-8').read()
old=("        if not new_hs:\n"
     "            _gw0={v:k for k,v in KE.items()}.get(WUXING[dm])\n"
     "            if _gw0 and gc=='av' and GAN_WX.get(g)==_gw0 and zc=='fav' and BRANCH_WX.get(z)!=_gw0 \\\n"
     "                    and element_power_tier(tp['wuxing_power'],_gw0)['tier']==0:\n"
     "                print('XUGUAN',li+1,''.join(a+b for a,b in fp)[:8],gz,'|',blob[:38].replace(chr(10),' '))\n"
     "                gc='xian'\n")
new=("        if not new_hs:\n"
     "            _dmw0=WUXING[dm]; _gw0={v:k for k,v in KE.items()}.get(_dmw0); _yw0={v:k for k,v in SHENG.items()}.get(_dmw0)\n"
     "            _yp=ye.get('yongshen_paths') or []\n"
     "            _zw_shun=any('ZHUANWANG' in x for x in _yp) and not any('LIANGQI' in x for x in _yp)  # 仅专旺顺用; 两气/伤官格虚官坐食伤=伤官见官混局仍病(L360庚午降)\n"
     "            if _gw0 and _zw_shun and gc=='av' and GAN_WX.get(g)==_gw0 and zc=='fav' \\\n"
     "                    and BRANCH_WX.get(z) in (_dmw0,_yw0) \\\n"
     "                    and element_power_tier(tp['wuxing_power'],_gw0)['tier']==0:\n"
     "                print('XUGUAN',li+1,''.join(a+b for a,b in fp)[:8],gz,'|',blob[:38].replace(chr(10),' '))\n"
     "                gc='xian'\n")
assert s.count(old)==1,('xg2',s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('虚官不犯收窄(专旺顺用+支比劫/印) done')
