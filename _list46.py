# -*- coding: utf-8 -*-
import json, io, sys
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

lib = json.load(open(r'D:\shuntian\data\heluo\canping\canping_jingyi_full.json', encoding='utf-8'))
items = lib['items']

groups = defaultdict(list)
for x in items:
    h = x.get('header')
    if h:
        groups[(x.get('part'), h)].append(x)

amb = {k: v for k, v in groups.items() if len(v) > 1}
print(f'共 {len(amb)} 组 / {sum(len(v) for v in amb.values())} 条待补 header\n')
for (part, h), lst in sorted(amb.items()):
    print(f'### part={part} header="{h}"  ({len(lst)}列)')
    for x in lst:
        # no = p{page}-c{col}
        pc = x['no']
        s0 = x['source_text'][0]
        s1 = x['source_text'][1] if len(x['source_text'])>1 else ''
        s2 = x['source_text'][2] if len(x['source_text'])>2 else ''
        print(f'  {pc}  mark={x.get("mark","")!r:8}  首句={s0} | {s1} | {s2}')
    print()
