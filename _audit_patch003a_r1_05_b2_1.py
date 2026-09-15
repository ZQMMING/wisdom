# -*- coding: utf-8 -*-
"""R1-05 第二批：基础五行 六部原文扫描（定位 VERIFIED_SCOPE 证据）"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

KEYS = ['相生', '相尅', '相克', '生尅', '生克', '五行', '木生火', '金生水', '水生木',
        '木尅土', '土尅水', '水尅火', '火尅金', '金尅木',
        '木曰曲直', '火曰炎上', '土爰稼穡', '土曰稼穡', '金曰從革', '水曰潤下',
        '曲直', '炎上', '稼穡', '從革', '潤下']

for eng in ['yhzp', 'pzzq', 'dts', 'qtbj', 'smth', 'sftk']:
    lines = open(rf'D:\shuntian-ziping-p0\registries\source\sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
    books = [json.loads(l) for l in lines if l.strip()]
    print(f'\n=== {eng} ===')
    hits = []
    for s in books:
        t = s.get('source_text', '')
        if any(k in t for k in KEYS):
            hits.append(s)
    # 去重：只显示命中关键词最多的前 8 条代表性原文
    scored = sorted(hits, key=lambda s: sum(1 for k in KEYS if k in s.get('source_text','')), reverse=True)
    for s in scored[:8]:
        t = s.get('source_text', '')
        print(f'  {s["source_id"]} [{s.get("chapter")}] {s.get("text_layer")}/{s.get("evidence_grade")} 命中{sum(1 for k in KEYS if k in t)}: {t[:120]}')
    print(f'  ...共 {len(hits)} 条')
