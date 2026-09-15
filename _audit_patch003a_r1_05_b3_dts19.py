# -*- coding: utf-8 -*-
"""读 DTS-019 通关论全文（正文+注）"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

lines = open(r'D:\shuntian-ziping-p0\registries\source\sources.dts.jsonl', encoding='utf-8').read().splitlines()
for l in lines:
    if not l.strip():
        continue
    s = json.loads(l)
    if s['source_id'] in ('DTS-019-001', 'DTS-019-002'):
        print(f"=== {s['source_id']} [{s.get('chapter')}] {s.get('text_layer')}/{s.get('evidence_grade')} attr={s.get('attribution','?')} ===")
        print(s.get('source_text', '')[:600])
        print()
