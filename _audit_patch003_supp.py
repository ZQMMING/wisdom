# -*- coding: utf-8 -*-
"""补扫：QTBJ 寒暖燥湿用词 / PZZQ 相神 / DTS 党众原文"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load(eng):
    lines = open(rf'D:\shuntian-ziping-p0\registries\source\sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
    return [json.loads(l) for l in lines if l.strip()]

print("===== QTBJ 寒暖燥湿用词统计 =====")
qtbj = load('qtbj')
words = ['寒', '暖', '燥', '濕', '湿', '調候', '调候', '餘寒', '余寒', '三伏生寒', '寒木向陽', '旱田', '解寒', '退氣', '退气', '進氣', '进气']
from collections import Counter
c = Counter()
for s in qtbj:
    t = s.get('source_text', '')
    for w in words:
        if w in t:
            c[w] += 1
for w, n in c.most_common():
    print(f'  {w}: {n}')

print("\n===== PZZQ 相神/用神之相 =====")
pzzq = load('pzzq')
for s in pzzq:
    t = s.get('source_text', '')
    if '相神' in t or '相' in t and '用神' in t and len(t) < 300:
        print(f"- {s['source_id']} [{s.get('chapter')}] {t[:120]}")

print("\n===== DTS 党众原文 =====")
dts = load('dts')
for s in dts:
    t = s.get('source_text', '')
    if '黨' in t or '党' in t:
        print(f"- {s['source_id']} [{s.get('chapter')}] {t[:120]}")

print("\n===== QTBJ 调候代表（寒/暖/燥/濕 组合）=====")
seen = 0
for s in qtbj:
    t = s.get('source_text', '')
    if any(w in t for w in ['餘寒', '三伏生寒', '寒木向陽', '旱田', '解寒', '燥', '濕']):
        print(f"- {s['source_id']} [{s.get('chapter')}] {t[:100]}")
        seen += 1
        if seen >= 8:
            break
