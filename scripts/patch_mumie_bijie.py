# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()
old="            elif stem(t['guan'])>=1: P(t['guan'],'FUYI','身旺官杀透干，用官杀克身成权(待根)')\n"
new=("            elif ben(t['yin'])>=3 and ben(t['bi'])<=1 and ben(t['cai'])==0 and stem(t['cai'])==0 \\\n"
     "                    and stem(t['shi'])==0 and ben(t['guan'])==0:\n"
     "                # 母多灭子(土多金埋类): 印本气极重埋身、日主本气根弱, 财破印/食伤泄皆不可得、官杀无根(生印反埋);\n"
     "                # 正治取比劫分印之壅、帮身出土(任注 L1763 辛酉比劫拱保辰丑出仕), 忌印、官杀生印。# PCT-MARK 印/日本气党众\n"
     "                P(t['bi'],'BINGYAO','母多灭子印重埋身，财破印与食伤泄俱不可得，比劫分印之壅、帮身出土'); S(t['shi'],'食伤待运泄秀'); S(t['cai'],'财待运破印'); A(t['yin'],'印重埋身'); A(t['guan'],'官杀生印助埋')\n"
     "            elif stem(t['guan'])>=1: P(t['guan'],'FUYI','身旺官杀透干，用官杀克身成权(待根)')\n")
assert s.count(old)==1,('mm',s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('母多灭子比劫分印分支 done')
