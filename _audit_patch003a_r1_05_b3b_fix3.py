# -*- coding: utf-8 -*-
"""SMTH 干支组合域可核实原文检索"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

KEYS = ['黨', '党', '地支', '支神', '四柱', '干支', '相配', '配合']
for l in io.open(r'D:\shuntian-ziping-p0\registries\source\sources.smth.jsonl', encoding='utf-8'):
    if not l.strip():
        continue
    s = json.loads(l)
    t = s.get('source_text', '')
    hits = [k for k in ['黨', '党'] if k in t]
    if hits:
        print(f"{s['source_id']} [{s.get('chapter')}] {s.get('text_layer')}/{s.get('evidence_grade')}: {t[:110]}")
