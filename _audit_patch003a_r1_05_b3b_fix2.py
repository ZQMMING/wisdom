# -*- coding: utf-8 -*-
"""SMTH 干支组合/强弱 相关原文检索（修正 030-002 引用）"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

KEYS = ['地支', '至切', '為強', '为强', '生旺休', '強弱', '强弱', '日主強', '日主强']
seen = set()
for l in io.open(r'D:\shuntian-ziping-p0\registries\source\sources.smth.jsonl', encoding='utf-8'):
    if not l.strip():
        continue
    s = json.loads(l)
    t = s.get('source_text', '')
    hit = sum(1 for k in KEYS if k in t)
    if hit >= 2 and s['source_id'] not in seen:
        seen.add(s['source_id'])
        print(f"{s['source_id']} [{s.get('chapter')}] {s.get('text_layer')}/{s.get('evidence_grade')} 命中{hit}: {t[:90]}")
