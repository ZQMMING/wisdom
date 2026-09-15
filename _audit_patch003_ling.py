# -*- coding: utf-8 -*-
"""PATCH-003 第二批：得令/失令/得時/得地/得勢/得垣/持勢/無根/有根/無氣/得劫 六部出处扫描
得势单独统计（不与其他词合并）。"""
import json, io, sys
from collections import OrderedDict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'D:\shuntian-ziping-p0\registries\source'
KEYS = ['得令', '失令', '得時', '失時', '得地', '得勢', '失勢', '得垣', '歸垣',
        '持勢', '無根', '有根', '無氣', '得劫', '得禄', '得祿']
ENGINES = ['yhzp', 'pzzq', 'dts', 'qtbj', 'smth', 'sftk']
ENG_NAME = {'yhzp': '渊海子平', 'pzzq': '子平真诠', 'dts': '滴天髓',
            'qtbj': '穷通宝鉴', 'smth': '三命通会', 'sftk': '神峰通考'}

print("===== 关键词 × 书 命中分布 =====")
key_hits = {k: Counter() for k in KEYS}
chapter_hits = OrderedDict()

for eng in ENGINES:
    lines = open(f'{ROOT}/sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
    for l in lines:
        if not l.strip():
            continue
        s = json.loads(l)
        txt = s.get('source_text', '')
        for k in KEYS:
            if k in txt:
                key_hits[k][eng] += 1

for k in KEYS:
    tot = sum(key_hits[k].values())
    if tot:
        print(f"  {k}: {tot} 条 | " + " ".join(f"{e}={n}" for e, n in key_hits[k].items()))
print()

print("===== 书×章节 聚合（含命中词明细）=====")
for eng in ENGINES:
    lines = open(f'{ROOT}/sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
    chapters = OrderedDict()
    for l in lines:
        if not l.strip():
            continue
        s = json.loads(l)
        txt = s.get('source_text', '')
        hit_keys = [k for k in KEYS if k in txt]
        if hit_keys:
            ch = s.get('chapter', '?')
            c = chapters.setdefault(ch, {'n': 0, 'keys': Counter(), 'sample': None})
            c['n'] += 1
            for k in hit_keys:
                c['keys'][k] += 1
            if c['sample'] is None and s.get('text_layer') == 'ORIGINAL':
                c['sample'] = (s['source_id'], txt[:70])
    if not chapters:
        continue
    print(f"\n----- {ENG_NAME[eng]}（{eng}）-----")
    for ch, c in chapters.items():
        ks = dict(c['keys'])
        print(f"  {ch} | {c['n']}条 | {ks}")
        if c['sample']:
            print(f"    代表: {c['sample'][0]} {c['sample'][1]}")
