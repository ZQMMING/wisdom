# -*- coding: utf-8 -*-
"""确认「通關」是否为后世术语：六部直接命中检查"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for kw in ['通關', '通关', '引通', '引化', '通氣', '通气']:
    print(f'\n=== 「{kw}」 ===')
    for eng in ['yhzp', 'pzzq', 'dts', 'qtbj', 'smth', 'sftk']:
        lines = open(rf'D:\shuntian-ziping-p0\registries\source\sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
        books = [json.loads(l) for l in lines if l.strip()]
        hits = [s for s in books if kw in s.get('source_text', '')]
        if hits:
            for s in hits[:3]:
                t = s.get('source_text', '')
                print(f'  {eng} {s["source_id"]} [{s.get("chapter")}] {s.get("text_layer")}/{s.get("evidence_grade")}: ...{t[max(0,t.find(kw)-10):t.find(kw)+25]}...')
        else:
            print(f'  {eng}: 0 命中')
