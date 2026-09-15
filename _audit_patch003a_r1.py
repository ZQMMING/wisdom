# -*- coding: utf-8 -*-
"""PATCH-003A-R1：DTS Evidence Layer 全量盘点
输出：text_layer 分布 + 五簇相关章节逐条（衰旺/精神/真假/順逆/寒溫濕燥/官煞/清濁/從象/化象等）"""
import json, io, sys
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

lines = open(r'D:\shuntian-ziping-p0\registries\source\sources.dts.jsonl', encoding='utf-8').read().splitlines()
books = [json.loads(l) for l in lines if l.strip()]

print("===== DTS 全部 text_layer 分布 =====")
c = Counter(s.get('text_layer') for s in books)
print(dict(c))
c2 = Counter(s.get('evidence_grade') for s in books)
print('grades:', dict(c2))
print(f'总数: {len(books)}')

print("\n===== DTS 章节清单（layer/grade/条数）=====")
chs = {}
for s in books:
    ch = s.get('chapter', '?')
    chs.setdefault(ch, []).append(s)
for ch in chs:
    layers = Counter(x.get('text_layer') for x in chs[ch])
    print(f"  {ch}: {len(chs[ch])}条 {dict(layers)}")

print("\n===== 五簇相关章节（衰旺/精神/真假/順逆/寒溫濕燥）逐条 =====")
FOCUS = ['衰旺', '精神', '真假', '順逆', '寒溫濕燥', '官煞', '清濁', '從象', '化象', '假象', '假化', '順局', '反局', '戰局', '合局', '體用']
for s in books:
    ch = s.get('chapter', '')
    if any(k in ch for k in FOCUS):
        print(f"  {s['source_id']} [{ch}] {s.get('text_layer')}/{s.get('evidence_grade')}")
        print(f"    {s.get('source_text', '')[:100]}")
