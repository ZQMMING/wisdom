# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()
old="                zhi_ok=stem(t['shi'])>=1 and (ben(t['shi'])>=1 or cs(t['shi']))  # 食伤须本气根/成势方任制杀, 中余气虚透不制强杀\n"
new=("                _chong_dui={'子':'午','午':'子','丑':'未','未':'丑','寅':'申','申':'寅','卯':'酉','酉':'卯','辰':'戌','戌':'辰','巳':'亥','亥':'巳'}\n"
     "                _dm_root_b=[brs[_i] for _i,_k in enumerate(_pks)\n"
     "                            if ((facts.get('hidden_stems',{}).get(_k) or []) and _ganwx.get((facts.get('hidden_stems',{}).get(_k) or [None])[0])==dmw)]\n"
     "                _dm_root_ok=any(_chong_dui.get(b) not in brs for b in _dm_root_b)  # 日主至少一原始本气根不被六冲拔\n"
     "                zhi_ok=stem(t['shi'])>=1 and qi(t['shi']) and (tier in WANG_TIER or _dm_root_ok)  # 食伤制杀: 身旺可任; 身弱须日主有不被冲拔本气根(根拔/虚透不任制强杀)\n")
assert s.count(old)==1, ('zhi_ok2',s.count(old))
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('zhi_ok 改为日主根稳判据 done')
