# -*- coding: utf-8 -*-
import json, io, sys
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\shuntian\data\heluo\canping\canping_jingyi_full.json'
d = json.load(open(p, encoding='utf-8'))
items = d if isinstance(d, list) else d.get('items') or d.get('data')
from collections import defaultdict
grp = defaultdict(list)
for it in items:
    part = it.get('part'); h = it.get('header')
    if part in ('water','fire','wood'):
        grp[(part,h)].append(str(it.get('no')))
amb = {k:v for k,v in grp.items() if len(v)>1}
print('水火木 total items:', sum(len(v) for v in grp.values()))
print('unique keys:', len(grp))
print('ambiguous groups:', len(amb))
for k,v in sorted(amb.items()):
    print('  AMBIG', k, v)
# 残缺header（非两字地支）
import re
bad=[]
for it in items:
    if it.get('part') in ('water','fire','wood'):
        h=it.get('header','')
        if not re.fullmatch(r'[子丑寅卯辰巳午未申酉戌亥]{2}', h or ''):
            bad.append((it.get('part'),it.get('no'),h))
print('bad/non-standard header:', bad)
