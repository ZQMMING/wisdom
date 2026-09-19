# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(p,encoding='utf-8').read()

old1="QUBING=re.compile(r'病药相济|药病相济|有病得药|克去|破其|冲去|制去|合去|去其|拔去|去病')\n"
new1=("QUBING=re.compile(r'病药相济|药病相济|有病得药|克去|破其|冲去|制去|合去|去其|拔去|去病')\n"
      "GUIYIN=re.compile(r'退归|致仕|归田|休官|告老|林下|挂冠|归老|退隐')\n"
      "ANXIANG=re.compile(r'安享|琴书|其乐|自若|安闲|优游|无恙|颐养|安逸|安享余年|乐享')\n")
assert s.count(old1)==1,('d1',s.count(old1)); s=s.replace(old1,new1)

old2=("    if LAO.search(blob) and not re.search(r'家破|破尽|横|刑丧|克妻|克子|贫乏|乞丐',blob):\n"
      "        return 'lao',blob[:70]\n")
new2=("    if LAO.search(blob) and not re.search(r'家破|破尽|横|刑丧|克妻|克子|贫乏|乞丐',blob):\n"
      "        return 'lao',blob[:70]\n"
      "    # 归隐安乐(退归/致仕+安享琴书其乐): 非仕途升迁之吉, 亦非灾亡之凶, 属归隐安乐中性, 不计成败分母(L889甲申乙酉退归安享琴书其乐自如)\n"
      "    if GUIYIN.search(blob) and ANXIANG.search(blob) and not re.search(r'家破|破尽|刑丧|克妻|克子|贫乏|乞丐|不禄|蹭蹬|亡|死',blob):\n"
      "        return 'lao',blob[:70]\n")
assert s.count(old2)==1,('d2',s.count(old2)); s=s.replace(old2,new2)

io.open(p,'w',encoding='utf-8',newline='').write(s)
print('归隐安享中性规则 added')
