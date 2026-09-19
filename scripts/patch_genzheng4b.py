# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()
old=("    _yin_bi_xu = stem(t['yin'])>=1 and stem(t['bi'])>=1 and ben(t['yin'])==0 \\\n"
     "        and zhong(t['yin'])+yu(t['yin'])==0 and ben(t['bi'])==0 and zhong(t['bi'])+yu(t['bi'])==0 \\\n"
     "        and (ben(t['cai'])>=3 or cs(t['cai']))\n")
new=("    _yin_bi_xu = stem(t['yin'])>=1 and stem(t['bi'])>=1 and ben(t['yin'])==0 \\\n"
     "        and d(t['yin'])['zhong_n']+d(t['yin'])['yu_n']==0 and ben(t['bi'])==0 \\\n"
     "        and d(t['bi'])['zhong_n']+d(t['bi'])['yu_n']==0 and (ben(t['cai'])>=3 or cs(t['cai']))\n")
assert s.count(old)==1,('fix',s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('zhong/yu -> d[] 修正 done')
