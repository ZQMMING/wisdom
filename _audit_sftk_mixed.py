# -*- coding: utf-8 -*-
"""多重混排识别：含 2+ 处 釋 标记的条目（正文断语夹在釋之间）"""
import json, io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for l in open(r'D:\shuntian-ziping-p0\registries\source\sources.sftk.jsonl', encoding='utf-8').read().splitlines():
    if not l.strip():
        continue
    s = json.loads(l)
    txt = s.get('source_text', '')
    hits = re.findall(r'(歌釋|詩釋|歇釋|歌曰|詩曰)', txt)
    if len(hits) >= 2:
        print(f"{s['source_id']} | {s.get('chapter')} | {s.get('text_layer')} | {s.get('evidence_grade')} | 釋数={len(hits)}")
        print(f"    {txt[:120]}")
