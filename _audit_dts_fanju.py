# -*- coding: utf-8 -*-
"""DTS 反局篇 + 何知章 全量条目（含任氏注）"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

lines = open(r'D:\shuntian-ziping-p0\registries\source\sources.dts.jsonl', encoding='utf-8').read().splitlines()
for l in lines:
    if not l.strip():
        continue
    s = json.loads(l)
    ch = s.get('chapter', '')
    if '反局' in ch or '何知' in ch:
        print(f"--- {s['source_id']} | {ch} | {s.get('text_layer')} | {s.get('evidence_grade')}")
        print(f"    {s.get('source_text', '')[:200]}")
