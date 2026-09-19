# -*- coding: utf-8 -*-
import io
src=io.open(r'D:\shuntian-ziping-p0\scripts\dayun_align.py',encoding='utf-8').read()
anchor="        clash=[c['verdict'] for c in transit_clash_verdicts(tp) if z in c['pair']]\n"
dbg=("        if ''.join(a+b for a,b in fp) in ('丙午戊戌丙午戊戌','甲申丙子癸亥癸亥','壬辰壬子壬子癸卯','戊子戊午戊戌戊午'):\n"
     "            print('DBG',li+1,''.join(a+b for a,b in fp),gz,'v=',v,'gc=',gc,'zc=',zc,'newhs=',new_hs,'lc=',lc,'ju=',ju,'paths=',ye.get('yongshen_paths'),'fav=',sorted(fav),'av=',sorted(av))\n")
assert src.count(anchor)==1
src=src.replace(anchor,dbg+anchor)
exec(compile(src,'dayun_align_dbg','exec'),{'__name__':'__main__'})
