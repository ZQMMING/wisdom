# -*- coding: utf-8 -*-
"""定位：DTS 有病方为贵 / PZZQ 杂而不杂 具体 source"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print('=== DTS「有病」语境 ===')
for l in io.open(r'D:\shuntian-ziping-p0\registries\source\sources.dts.jsonl', encoding='utf-8'):
    if not l.strip():
        continue
    s = json.loads(l)
    t = s.get('source_text', '')
    if '有病' in t or '病方' in t:
        print(f"{s['source_id']} [{s.get('chapter')}] {s.get('text_layer')}/{s.get('evidence_grade')} attr={s.get('attribution')}: {t[:120]}")

print('\n=== PZZQ「雜而不雜」语境 ===')
for l in io.open(r'D:\shuntian-ziping-p0\registries\source\sources.pzzq.jsonl', encoding='utf-8'):
    if not l.strip():
        continue
    s = json.loads(l)
    t = s.get('source_text', '')
    if '雜而不雜' in t or ('雜氣' in t and '清' in t):
        print(f"{s['source_id']} [{s.get('chapter')}] {s.get('text_layer')}/{s.get('evidence_grade')}: {t[:130]}")
