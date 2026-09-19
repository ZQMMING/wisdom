# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()

# 1) line350 身旺块初始化 _zhuan_shi
old0="        if primary is None and tier in WANG_TIER:\n            _gy=dm in '甲丙戊庚壬'; _yg='甲丙戊庚壬' if _gy else '乙丁己辛癸'\n"
new0="        if primary is None and tier in WANG_TIER:\n            _zhuan_shi=False\n            _gy=dm in '甲丙戊庚壬'; _yg='甲丙戊庚壬' if _gy else '乙丁己辛癸'\n"
assert s.count(old0)==1,('o0',s.count(old0)); s=s.replace(old0,new0)

# 2) line354 细分伤官去官(官杀众透无根+食伤当令)
old1="            if stem(t['guan'])>=2 and stem(t['shi'])>=1: P(t['shi'],'BINGYAO','身旺官杀众透，食伤制杀兼泄秀')\n"
new1=("            if stem(t['guan'])>=2 and stem(t['shi'])>=1 and ben(t['guan'])==0 and ling(t['shi'])=='旺':\n"
      "                # 身旺+食伤当令+官杀众透无根=伤官去官/食伤泄秀(L1080): 比劫生食伤顺泄、食伤生财为喜, 虚官犯旺、印克食伤为忌\n"
      "                _zhuan_shi=True; P(t['shi'],'BINGYAO','身旺食伤当令、官杀众透无根，伤官去官、食伤泄秀生财'); S(t['bi'],'比劫生食伤帮身任泄'); S(t['cai'],'食伤生财'); A(t['guan'],'虚官被去、岁运犯旺凶'); A(t['yin'],'印克食伤、莫作用印')\n"
      "            elif stem(t['guan'])>=2 and stem(t['shi'])>=1: P(t['shi'],'BINGYAO','身旺官杀众透，食伤制杀兼泄秀')\n")
assert s.count(old1)==1,('o1',s.count(old1)); s=s.replace(old1,new1)

# 3) line371 块尾: 去官分支已自定喜忌, 跳过统一 A印比(不忌比劫)
old2="            S(t['cai'] if primary==t['guan'] else t['shi'],''); A(t['yin'],t['bi'])\n"
new2="            if not _zhuan_shi:\n                S(t['cai'] if primary==t['guan'] else t['shi'],''); A(t['yin'],t['bi'])\n"
assert s.count(old2)==1,('o2',s.count(old2)); s=s.replace(old2,new2)

io.open(p,'w',encoding='utf-8',newline='').write(s)
print('身旺块伤官去官细分 done')
