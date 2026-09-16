# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BAK = r'D:\shuntian\data\heluo\canping\canping_jingyi_full.json.bak_46fix'
CUR = r'D:\shuntian\data\heluo\canping\canping_jingyi_full.json'
a = {x['no']: x for x in json.load(open(BAK, encoding='utf-8'))['items']}
b = {x['no']: x for x in json.load(open(CUR, encoding='utf-8'))['items']}
print('bak items', len(a), 'cur items', len(b))
PROT=['source_text','jingyi','modern_explanation','semantic_tags','evidence_basis']
hdr_changes=[]; content_changes=[]
for no in b:
    if no not in a:
        print('NEW no in cur:', no); continue
    ha=a[no].get('header'); hb=b[no].get('header')
    if ha!=hb:
        hdr_changes.append((no, a[no].get('part'), ha, hb))
    for k in PROT:
        if a[no].get(k)!=b[no].get(k):
            content_changes.append((no,k))
for no in a:
    if no not in b: print('MISSING in cur:', no)
print('=== header 字段改动 (%d) ==='%len(hdr_changes))
for no,part,ha,hb in hdr_changes:
    print(f'  {part:6} {no:10} {ha!r:8} -> {hb!r}')
print('=== 受保护内容字段改动 (%d) ==='%len(content_changes))
for no,k in content_changes[:50]:
    print('  ', no, k)
