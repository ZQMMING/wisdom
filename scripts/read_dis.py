# -*- coding: utf-8 -*-
import io,sys
sys.path.insert(0,r'D:\shuntian-ziping-p0\scripts')
src=io.open(r'D:\shuntian-ziping-p0\scripts\dayun_align.py',encoding='utf-8').read()
g={'__name__':'__probe__'}
exec(compile(src,'dayun_align','exec'),g)
cases=g['cases']
import sys
charts=sys.argv[1:] if len(sys.argv)>1 else ['壬申壬寅壬申辛丑','戊寅丁巳丙寅甲午','壬子辛亥乙亥丙子','癸酉甲子庚辰甲申','乙卯己卯戊辰癸亥','丁巳癸丑丁卯丙午','戊子戊午戊戌戊午','庚申壬午辛酉癸巳']
cmap={''.join(a+b for a,b in fp):(li,txt) for li,fp,dy,txt in cases}
for ch in charts:
    if ch in cmap:
        li,txt=cmap[ch]
        print('='*28,ch,'line',li+1,'='*28)
        print(txt[:1150]); print()
