# -*- coding: utf-8 -*-
"""R1-05 第二批：十神 六部原文扫描"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

KEYS = ['正官', '偏官', '七殺', '七杀', '正印', '偏印', '梟', '正財', '偏財', '食神',
        '傷官', '比肩', '劫財', '十神', '官殺', '財官']

for eng in ['yhzp', 'pzzq', 'dts', 'qtbj', 'smth', 'sftk']:
    lines = open(rf'D:\shuntian-ziping-p0\registries\source\sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
    books = [json.loads(l) for l in lines if l.strip()]
    print(f'\n=== {eng} ===')
    hits = [s for s in books if any(k in s.get('source_text', '') for k in KEYS)]
    scored = sorted(hits, key=lambda s: sum(1 for k in KEYS if k in s.get('source_text', '')), reverse=True)
    for s in scored[:6]:
        t = s.get('source_text', '')
        print(f'  {s["source_id"]} [{s.get("chapter")}] {s.get("text_layer")}/{s.get("evidence_grade")} 命中{sum(1 for k in KEYS if k in t)}: {t[:110]}')
    print(f'  ...共 {len(hits)} 条')
