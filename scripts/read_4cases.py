# -*- coding: utf-8 -*-
import io,sys
sys.path.insert(0,r'D:\shuntian-ziping-p0\scripts')
src=io.open(r'D:\shuntian-ziping-p0\scripts\dayun_align.py',encoding='utf-8').read()
g={'__name__':'__probe__'}
exec(compile(src,'dayun_align','exec'),g)
cases=g['cases']
targets={'庚午己卯壬申己酉':'L889','戊午壬戌丁卯癸卯':'L1080','甲午丙寅辛酉己丑':'L1265','甲申丙寅甲申庚午':'L1744'}
for li,fp,dy,txt in cases:
    ch=''.join(a+b for a,b in fp)
    if ch in targets:
        print('='*30,targets[ch],ch,'line',li+1,'='*30)
        print(txt[:1400])
        print()
