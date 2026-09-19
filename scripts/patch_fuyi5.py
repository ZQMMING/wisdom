# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()

# B6身旺块开头插入枭神夺食判据
old1=("        if primary is None and tier in WANG_TIER:\n"
      "            if stem(t['guan'])>=2 and stem(t['shi'])>=1: P(t['shi'],'BINGYAO','身旺官杀众透，食伤制杀兼泄秀')\n")
new1=("        if primary is None and tier in WANG_TIER:\n"
      "            _gy=dm in '甲丙戊庚壬'; _yg='甲丙戊庚壬' if _gy else '乙丁己辛癸'\n"
      "            _py_tou=any(_ganwx.get(g)==t['yin'] for g in other_gan if g in _yg)  # 偏印(生我同阴阳)透干\n"
      "            _xiao_duo_shi=_py_tou and stem(t['shi'])>=1 and ben(t['shi'])==0  # 偏印透、食伤透无本气根=枭神夺食, 食伤被夺不可用\n"
      "            if stem(t['guan'])>=2 and stem(t['shi'])>=1: P(t['shi'],'BINGYAO','身旺官杀众透，食伤制杀兼泄秀')\n")
assert s.count(old1)==1, ('b6head',s.count(old1))
s=s.replace(old1,new1)

# 印重食伤泄秀分支排除枭神夺食
old2=("            elif (cs(t['yin']) or ben(t['yin'])>=2) and ben(t['guan'])==0 and not cs(t['guan']) \\\n"
      "                    and stem(t['shi'])>=1 and qi(t['shi']):\n")
new2=("            elif (cs(t['yin']) or ben(t['yin'])>=2) and ben(t['guan'])==0 and not cs(t['guan']) \\\n"
      "                    and stem(t['shi'])>=1 and qi(t['shi']) and not _xiao_duo_shi:\n")
assert s.count(old2)==1, ('b6fenzhi',s.count(old2))
s=s.replace(old2,new2)

io.open(p,'w',encoding='utf-8',newline='').write(s)
print('枭神夺食判据 done')
