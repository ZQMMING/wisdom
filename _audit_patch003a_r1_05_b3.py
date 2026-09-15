# -*- coding: utf-8 -*-
"""R1-05 第三批：生扶克泄耗 / 气势 / 调候 / 通关 六部扫描"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

groups = {
    '生扶克泄耗': ['生扶', '扶身', '幫身', '泄', '洩', '耗', '尅洩', '克泄', '洩氣', '泄氣', '生我', '我生', '尅我', '我尅'],
    '气势': ['氣勢', '氣勢', '氣', '勢', '精神', '貫', '流通', '沖奔', '氣象'],
    '调候': ['調候', '調停', '寒', '暖', '燥', '濕', '溫', '冷', '凍', '解凍', '調和', '寒暖'],
    '通关': ['通關', '引通', '通', '引化', '化煞', '引通', '關'],
}

for gname, KEYS in groups.items():
    print(f'\n{"="*60}\n## {gname}')
    for eng in ['yhzp', 'pzzq', 'dts', 'qtbj', 'smth', 'sftk']:
        lines = open(rf'D:\shuntian-ziping-p0\registries\source\sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
        books = [json.loads(l) for l in lines if l.strip()]
        hits = [s for s in books if any(k in s.get('source_text', '') for k in KEYS)]
        scored = sorted(hits, key=lambda s: sum(1 for k in KEYS if k in s.get('source_text', '')), reverse=True)
        print(f'\n--- {eng}（{len(hits)} 条） ---')
        for s in scored[:4]:
            t = s.get('source_text', '')
            print(f'  {s["source_id"]} [{s.get("chapter")}] {s.get("text_layer")}/{s.get("evidence_grade")} 命中{sum(1 for k in KEYS if k in t)}: {t[:100]}')
