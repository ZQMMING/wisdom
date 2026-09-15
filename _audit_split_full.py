# -*- coding: utf-8 -*-
"""读 018-012 / 062-038 完整文本（切分用）"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for l in open(r'D:\shuntian-ziping-p0\registries\source\sources.sftk.jsonl', encoding='utf-8').read().splitlines():
    if not l.strip():
        continue
    s = json.loads(l)
    if s['source_id'] in ('SFTK-018-012', 'SFTK-062-038'):
        print(f"===== {s['source_id']} 全文 =====")
        print(s['source_text'])
        print()
