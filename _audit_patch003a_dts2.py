# -*- coding: utf-8 -*-
"""查 DTS 月令論/生時論 分层"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

lines = open(r'D:\shuntian-ziping-p0\registries\source\sources.dts.jsonl', encoding='utf-8').read().splitlines()
for l in lines:
    if not l.strip():
        continue
    s = json.loads(l)
    if '月令' in s.get('chapter', '') or '生時' in s.get('chapter', ''):
        print(f"--- {s['source_id']} [{s.get('chapter')}] {s.get('text_layer')}/{s.get('evidence_grade')}")
        print(s.get('source_text', '')[:400])
        print()
