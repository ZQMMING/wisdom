# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\shuntian\data\heluo\canping\canping_jingyi_full.json'
d = json.load(open(p, encoding='utf-8'))
# 看一个水火木 entry 的全部字段
for it in d['items']:
    if str(it.get('no'))=='p24-c1':
        print('=== p24-c1 all fields ===')
        for k,v in it.items():
            print(f'  {k}: {str(v)[:80]}')
        break
# 看一个重复组两个entry的字段差异
from collections import defaultdict
g=defaultdict(list)
for it in d['items']:
    if it.get('part') in ('water','fire','wood'):
        g[(it['part'],it.get('header'))].append(it)
for k,v in g.items():
    if len(v)>1:
        print('===',k,'===')
        for it in v:
            print('  ', it['no'], 'keys=', [x for x in it.keys() if x not in ('source_text','jingyi','modern_explanation','semantic_tags','evidence_basis')])
        break
