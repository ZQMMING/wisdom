# -*- coding: utf-8 -*-
"""PATCH-003 关键原文精读：得勢/得垣/歸垣/持勢/子機賦/真假論"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'D:\shuntian-ziping-p0\registries\source'
TARGETS = [
    ('smth', ['得勢', '失勢']),
    ('sftk', ['得垣', '歸垣', '持勢']),
    ('yhzp', ['子機賦']),
    ('dts', ['真假論']),
    ('yhzp', ['無氣遇劫', '得時為旺']),
]
for eng, keys in TARGETS:
    lines = open(f'{ROOT}/sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
    print(f"\n########## {eng} 关键词 {keys} ##########")
    for l in lines:
        if not l.strip():
            continue
        s = json.loads(l)
        txt = s.get('source_text', '')
        ch = s.get('chapter', '?')
        if any(k in ch for k in keys) or any(k in txt for k in keys):
            print(f"--- {s['source_id']} | {ch} | {s.get('text_layer')}/{s.get('evidence_grade')}")
            print(txt[:500])
            print()
