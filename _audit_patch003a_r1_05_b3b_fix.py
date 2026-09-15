# -*- coding: utf-8 -*-
"""查找 SMTH 黨盛為強 实际 source_id"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for l in io.open(r'D:\shuntian-ziping-p0\registries\source\sources.smth.jsonl', encoding='utf-8'):
    if not l.strip():
        continue
    s = json.loads(l)
    t = s.get('source_text', '')
    if '黨盛' in t or '党盛' in t or ('地支至切' in t):
        print(f"{s['source_id']} [{s.get('chapter')}] {s.get('text_layer')}/{s.get('evidence_grade')}: {t[:80]}")
