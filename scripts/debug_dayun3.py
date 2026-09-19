# -*- coding: utf-8 -*-
import io
src=io.open(r'D:\shuntian-ziping-p0\scripts\dayun_align.py',encoding='utf-8').read()
anchor="        clash=[c['verdict'] for c in transit_clash_verdicts(tp) if z in c['pair']]\n"
# 在 lc 定案后、neutral continue 前打印所有 new_hs 且顺用且 gc==av 的步
dbg=("        if new_hs and any(x in ('ZHUANWANG','LIANGQI','CONG_SHUN') for x in (ye.get('yongshen_paths') or [])) and gc=='av':\n"
     "            print('JU',li+1,''.join(a+b for a,b in fp),gz,'v=',v,'gc=',gc,'zc=',zc,'newhs=',new_hs,'lc=',lc,'ben干=',int(tp0['wuxing_power']['wuxing_power'][GAN_WX[g]].get('ben_n',0)),'blob=',blob[:40].replace(chr(10),' '))\n")
assert src.count(anchor)==1
src=src.replace(anchor,dbg+anchor)
exec(compile(src,'dayun_align_dbg3','exec'),{'__name__':'__main__'})
