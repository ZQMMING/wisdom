# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(p,encoding='utf-8').read()

old_ji="'无恙']"; new_ji="'升迁','举于乡','县宰','无恙']"
assert s.count(old_ji)==1,('ji',s.count(old_ji)); s=s.replace(old_ji,new_ji)
old_x="'艰难']"; new_x="'一败而尽','一败涂地','艰难']"
assert s.count(old_x)==1,('x',s.count(old_x)); s=s.replace(old_x,new_x)

anchor="def luck_verdict(txt,g,z):\n"
segfn=("_DTOK=re.compile(r'(?P<gz>[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])(?P<k>运|年)?|(?P<gan>[甲乙丙丁戊己庚辛壬癸])(?P<kg>运|年)|(?P<zhi>[子丑寅卯辰巳午未申酉戌亥])(?P<kz>运|年)')\n"
       "def cur_period_text(st,g,z,dy):\n"
       "    '''仅当同句出现多个不同运指称(两步混句)或流年(Y年)指称时, 取当前大运(g/z)统辖段; 普通单运/无指称句整句返回; 裸两字干支须在该造大运列表中才算运指称。'''\n"
       "    dyc=set(dy); toks=[]\n"
       "    for m in _DTOK.finditer(st):\n"
       "        gz=m.group('gz')\n"
       "        if gz: lab=gz; kd=m.group('k') or ('运' if gz in dyc else '')\n"
       "        elif m.group('gan'): lab=m.group('gan'); kd=m.group('kg')\n"
       "        else: lab=m.group('zhi'); kd=m.group('kz')\n"
       "        if kd: toks.append((m.start(),m.end(),lab,kd))\n"
       "    if not toks: return st\n"
       "    iscur=lambda lab: lab==g+z or lab==g or lab==z\n"
       "    cur=[t for t in toks if t[3]=='运' and iscur(t[2])]\n"
       "    oyear=[t for t in toks if t[3]=='年']\n"
       "    oyun=[t for t in toks if t[3]=='运' and not iscur(t[2])]\n"
       "    if not cur: return st\n"
       "    if not oyear and not oyun: return st\n"
       "    segs=[]\n"
       "    for i,(a,b,lab,kd) in enumerate(toks):\n"
       "        if kd=='运' and iscur(lab):\n"
       "            e=toks[i+1][0] if i+1<len(toks) else len(st); segs.append(st[b:e])\n"
       "    return ''.join(segs)\n"
       "def luck_verdict(txt,g,z,dy):\n")
assert s.count(anchor)==1,('anchor',s.count(anchor)); s=s.replace(anchor,segfn)

old_b="    b=blob\n"
new_b=("    _ps=[cur_period_text(st,g,z,dy) for st in hits]\n"
       "    _ps=[x for x in _ps if x is not None]\n"
       "    b=' '.join(_ps) if _ps else blob\n")
assert s.count(old_b)==1,('b',s.count(old_b)); s=s.replace(old_b,new_b)

old_call="        v,blob=luck_verdict(txt,g,z)\n"
new_call="        v,blob=luck_verdict(txt,g,z,dy)\n"
assert s.count(old_call)==1,('call',s.count(old_call)); s=s.replace(old_call,new_call)

io.open(p,'w',encoding='utf-8',newline='').write(s)
print('dayun 保守指称切段 done')
