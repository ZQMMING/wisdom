# -*- coding: utf-8 -*-
import io
src=io.open(r'D:\shuntian-ziping-p0\scripts\dayun_align.py',encoding='utf-8').read()
anchor=("        if blob and blob.lstrip().startswith('【原注】'):\n"
        "            v=None\n")
dbg=anchor+("        if blob and blob.lstrip().startswith('【原注】'):\n"
     "            print('YZ',li+1,''.join(a+b for a,b in fp)[:8],gz,'v=',luck_verdict(txt,g,z)[0],'|',repr(blob[:50]))\n")
assert src.count(anchor)==1
src=src.replace(anchor,dbg)
g={'__name__':'__main__'}; exec(compile(src,'d','exec'),g)
