# -*- coding: utf-8 -*-
import io
src=io.open(r'D:\shuntian-ziping-p0\scripts\dayun_align.py',encoding='utf-8').read()
anchor="        clash=[c['verdict'] for c in transit_clash_verdicts(tp) if z in c['pair']]\n"
dbg=("        if ''.join(a+b for a,b in fp) in ('壬辰壬子壬子癸卯','戊子戊午戊戌戊午','壬子辛亥乙亥丙子','乙亥辛巳丁巳庚戌','庚寅壬午戊午丁巳','壬申辛亥辛酉庚寅','辛丑丙申癸巳庚申'):\n"
     "            _dmw=WUXING[dm]; _SM={v:k for k,v in SHENG.items()}\n"
     "            _P=max('木火土金水', key=lambda x: element_power_tier(tp0,x)['tier'])\n"
     "            _wg=GAN_WX[g]; _wz=BRANCH_WX[z]\n"
     "            print('XU',li+1,''.join(a+b for a,b in fp)[:8],gz,'v=',v,'spec=',ye.get('spectrum_tier'),'P=',_P,'tP=',element_power_tier(tp0,_P)['tier'],'Pin生扶=',_P in (_dmw,_SM.get(_dmw)),'g=',_wg,'tg=',element_power_tier(tp,_wg)['tier'],'gc=',gc,'z=',_wz,'tz=',element_power_tier(tp,_wz)['tier'],'zc=',zc,'newhs=',new_hs,'lc=',lc)\n")
assert src.count(anchor)==1
src=src.replace(anchor,dbg+anchor)
exec(compile(src,'dbg4','exec'),{'__name__':'__main__'})
