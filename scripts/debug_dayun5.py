# -*- coding: utf-8 -*-
import io
src=io.open(r'D:\shuntian-ziping-p0\scripts\dayun_align.py',encoding='utf-8').read()
anchor="        clash=[c['verdict'] for c in transit_clash_verdicts(tp) if z in c['pair']]\n"
dbg=("        if blob and ('【原注】' in blob or ('日主喜' in blob and '则' in blob)):\n"
     "            print('YZ',li+1,''.join(a+b for a,b in fp)[:8],gz,'v=',v,'lc=',lc,'|',blob[:60].replace(chr(10),' '))\n")
src=src.replace(anchor,dbg+anchor)
g={'__name__':'__main__'}; exec(compile(src,'d','exec'),g)
