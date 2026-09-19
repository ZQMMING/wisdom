# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(p,encoding='utf-8').read()
reps=[
 ("_P=max('木火土金水', key=lambda x: element_power_tier(tp0,x)['tier'])",
  "_P=max('木火土金水', key=lambda x: element_power_tier(tp0['wuxing_power'],x)['tier'])"),
 ("if _P in (_dmw, _SHENG_ME.get(_dmw)) and element_power_tier(tp0,_P)['tier']>=2:",
  "if _P in (_dmw, _SHENG_ME.get(_dmw)) and element_power_tier(tp0['wuxing_power'],_P)['tier']>=2:"),
 ("return bool(w) and (KE.get(_P)==w or KE.get(w)==_P) and element_power_tier(tp,w)['tier']<=1",
  "return bool(w) and (KE.get(_P)==w or KE.get(w)==_P) and element_power_tier(tp['wuxing_power'],w)['tier']<=1"),
]
for old,new in reps:
    assert s.count(old)==1,(old[:30],s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('虚喜犯旺 tier入参修正 done')
