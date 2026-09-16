# -*- coding: utf-8 -*-
import json, io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\shuntian\data\heluo\canping\canping_jingyi_full.json'
d = json.load(open(p, encoding='utf-8'))
pages = [27,29,30,31,33,34,35,38,43,46,49,50,55]
for pg in pages:
    print(f'--- p{pg} ---')
    rows=[it for it in d['items'] if str(it.get('no'))==f'p{pg}-c0' or str(it.get('no')).startswith(f'p{pg}-c')]
    for it in sorted(rows, key=lambda x:int(str(x['no']).split('-c')[1])):
        print(f"  {it['no']} [{it.get('part')}] h={it.get('header')!r} 首句={str(it.get('source_text'))[:22]}")
