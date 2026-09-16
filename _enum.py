# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\shuntian\data\heluo\canping\canping_jingyi_full.json'
d = json.load(open(p, encoding='utf-8'))
items = d if isinstance(d, list) else d.get('items') or d.get('data')
print('total', len(items))
print('sample keys:', list(items[0].keys()))
# 找水火木 item 看 no/header 样例
for it in items:
    if str(it.get('no','')).startswith('p') and it.get('part') in ('water','fire','wood','水','火','木'):
        print(it.get('part'), repr(it.get('no')), repr(it.get('header')), str(it.get('source_text'))[:30])
        break
# 列出所有待改 no 的现状
targets = [(52,0),(52,4),(40,4),(44,4),(39,2),(51,2),(41,1),(48,1),(52,2),(40,2),(49,2),(44,1),(50,4),(39,1),(47,0),(47,1),(45,1),(50,0),
           (28,4),(36,0),(26,0),(28,0),(37,0),(24,4),(28,3),(35,4),(22,1),(32,4),(26,3),(37,4),(24,2),(24,3),(24,0),(28,1),(37,1),(26,1),(28,2),(32,0),(37,2),(32,2),(36,3),(26,2),(32,1),(37,3),
           (55,1),(56,2)]
print('--- target current ---')
found=0
for pg,cl in targets:
    key=f'p{pg}-c{cl}'
    for it in items:
        if str(it.get('no',''))==key:
            print(key, it.get('part'), repr(it.get('header')), str(it.get('source_text'))[:24])
            found+=1
            break
    else:
        print(key, 'NOT FOUND')
print('found',found)
