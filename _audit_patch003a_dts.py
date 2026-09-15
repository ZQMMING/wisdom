# -*- coding: utf-8 -*-
"""补扫：DTS 衰旺論/月令論/生時論 原文 + 单字旺用法"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

lines = open(r'D:\shuntian-ziping-p0\registries\source\sources.dts.jsonl', encoding='utf-8').read().splitlines()
books = [json.loads(l) for l in lines if l.strip()]

print("===== DTS 章节含 衰旺/月令/生時/旺 的 ORIGINAL =====")
for s in books:
    t = s.get('source_text', '')
    ch = s.get('chapter', '')
    if any(k in ch for k in ['衰旺', '月令', '生時', '旺衰']) or ('旺' in ch):
        print(f"\n--- {s['source_id']} [{ch}] {s.get('text_layer')}/{s.get('evidence_grade')}")
        print(t[:600])
