# -*- coding: utf-8 -*-
"""PATCH-003 语境聚合：书×章节 命中分布 + text_layer 统计 + 代表原文"""
import json, io, sys
from collections import OrderedDict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'D:\shuntian-ziping-p0\registries\source'
KEYS = ['身旺', '身強', '身弱', '身衰']
ENGINES = ['yhzp', 'pzzq', 'dts', 'qtbj', 'smth', 'sftk']
ENG_NAME = {'yhzp': '渊海子平', 'pzzq': '子平真诠', 'dts': '滴天髓',
            'qtbj': '穷通宝鉴', 'smth': '三命通会', 'sftk': '神峰通考'}

for eng in ENGINES:
    lines = open(f'{ROOT}/sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
    chapters = OrderedDict()
    for l in lines:
        if not l.strip():
            continue
        s = json.loads(l)
        txt = s.get('source_text', '')
        if any(k in txt for k in KEYS):
            ch = s.get('chapter', '?')
            c = chapters.setdefault(ch, {'n': 0, 'layers': {}, 'sample': None})
            c['n'] += 1
            c['layers'][s.get('text_layer')] = c['layers'].get(s.get('text_layer'), 0) + 1
            if c['sample'] is None and s.get('text_layer') == 'ORIGINAL':
                c['sample'] = (s['source_id'], txt[:60])
    print(f"===== {ENG_NAME[eng]}（{eng}）=====")
    for ch, c in chapters.items():
        print(f"  {ch} | {c['n']}条 | {dict(c['layers'])}")
        if c['sample']:
            print(f"    代表: {c['sample'][0]} {c['sample'][1]}")
    print()
