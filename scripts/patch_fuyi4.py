# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()

# 1. B6身旺: 印重成势+官杀虚透无根只生印, 不任官, 食伤泄秀生财破印(插在 line339 P官 前)
old1=("            elif stem(t['guan'])>=1: P(t['guan'],'FUYI','身旺官杀透干，用官杀克身成权(待根)')\n")
new1=("            elif (cs(t['yin']) or ben(t['yin'])>=2) and ben(t['guan'])==0 and not cs(t['guan']) \\\n"
      "                    and stem(t['shi'])>=1 and qi(t['shi']):\n"
      "                P(t['shi'],'FUYI','身旺印重成势、官杀虚透无根只生印不制身，食伤泄秀生财破印'); S(t['cai'],'财破印'); A(t['guan'],'官杀生印助壅')\n"
      "            elif stem(t['guan'])>=1: P(t['guan'],'FUYI','身旺官杀透干，用官杀克身成权(待根)')\n")
assert s.count(old1)==1, ('b6yin',s.count(old1))
s=s.replace(old1,new1)

# 2. B6身旺收敛: 印重成势则官杀生印助壅亦忌(官有根成势的官印相生已在B2先取用, 不受影响)
old2="            S(t['cai'] if primary==t['guan'] else t['shi'],''); A(t['yin'],t['bi'])\n"
new2=("            S(t['cai'] if primary==t['guan'] else t['shi'],''); A(t['yin'],t['bi'])\n"
      "            if cs(t['yin']) or ben(t['yin'])>=2: A(t['guan'],'身旺印重，官杀生印助壅(印重不劳官生)')\n")
assert s.count(old2)==1, ('b6aguan',s.count(old2))
s=s.replace(old2,new2)

io.open(p,'w',encoding='utf-8',newline='').write(s)
print('身旺印重官杀生印 修正 done')
