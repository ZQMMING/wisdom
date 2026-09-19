# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(p,encoding='utf-8').read()

# 1. 吉词补
old_ji="'无恙']"
new_ji="'升迁','举于乡','县宰','无恙']"
assert s.count(old_ji)==1,('ji',s.count(old_ji)); s=s.replace(old_ji,new_ji)

# 2. 凶词补(一败而尽被QUBING"冲去"误判去病吉)
old_x="'艰难']"
new_x="'一败而尽','一败涂地','艰难']"
assert s.count(old_x)==1,('x',s.count(old_x)); s=s.replace(old_x,new_x)

# 3. 运/年指称切段函数(插 luck_verdict 前)
anchor="def luck_verdict(txt,g,z):\n"
segfn=("_DTOK=re.compile(r'(?P<gz>[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])(?P<k>运|年)?|(?P<gan>[甲乙丙丁戊己庚辛壬癸])(?P<kg>运|年)|(?P<zhi>[子丑寅卯辰巳午未申酉戌亥])(?P<kz>运|年)')\n"
       "def period_segments(st,g,z,dy):\n"
       "    '''按大运/流年指称切段, 只返回当前大运(g/z)统辖且非流年(Y年)的段; 裸两字干支仅当在该造大运列表中才视为运指称(避免会局寅卯辰误切)。'''\n"
       "    dyc=set(dy); toks=[]\n"
       "    for m in _DTOK.finditer(st):\n"
       "        gz=m.group('gz')\n"
       "        if gz:\n"
       "            lab=gz; kd=m.group('k') or ('运' if gz in dyc else '')\n"
       "        elif m.group('gan'):\n"
       "            lab=m.group('gan'); kd=m.group('kg')\n"
       "        else:\n"
       "            lab=m.group('zhi'); kd=m.group('kz')\n"
       "        if kd: toks.append((m.start(),m.end(),lab,kd))\n"
       "    keep=[]\n"
       "    for i,(a,b,lab,kd) in enumerate(toks):\n"
       "        if kd=='年': continue\n"
       "        e=toks[i+1][0] if i+1<len(toks) else len(st)\n"
       "        if lab==g+z or lab==g or lab==z: keep.append(st[b:e])\n"
       "    return keep\n"
       "def luck_verdict(txt,g,z,dy):\n")
assert s.count(anchor)==1,('anchor',s.count(anchor)); s=s.replace(anchor,segfn)

# 4. luck_verdict 内用切段替换整blob
old_b="    b=blob\n"
new_b=("    kept=[]\n"
       "    for st in hits:\n"
       "        _sg=period_segments(st,g,z,dy)\n"
       "        if _sg: kept.extend(_sg)\n"
       "    b=' '.join(kept) if kept else blob\n")
assert s.count(old_b)==1,('b',s.count(old_b)); s=s.replace(old_b,new_b)

# 5. 调用处传dy
old_call="        v,blob=luck_verdict(txt,g,z)\n"
new_call="        v,blob=luck_verdict(txt,g,z,dy)\n"
assert s.count(old_call)==1,('call',s.count(old_call)); s=s.replace(old_call,new_call)

io.open(p,'w',encoding='utf-8',newline='').write(s)
print('dayun 指称切段+词表 done')
