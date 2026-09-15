# -*- coding: utf-8 -*-
"""搜 DTS 令星/人元/宅/用事/月令 相关原文"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

lines = open(r'D:\shuntian-ziping-p0\registries\source\sources.dts.jsonl', encoding='utf-8').read().splitlines()
books = [json.loads(l) for l in lines if l.strip()]

KEYS = ['令星', '人元', '宅', '用事', '月令', '提綱', '提纲', '氣象得令']
for s in books:
    t = s.get('source_text', '')
    if any(k in t for k in KEYS):
        print(f"--- {s['source_id']} [{s.get('chapter')}] {s.get('text_layer')}/{s.get('evidence_grade')}")
        print(t[:350])
        print()
