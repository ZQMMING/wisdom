# -*- coding: utf-8 -*-
"""R1-05 第二批：生旺休囚 / 根气 / 党众 六部扫描"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

groups = {
    '生旺休囚': ['生旺休囚', '旺相休囚', '生旺', '死絕', '長生', '沐浴', '冠帶', '臨官', '帝旺', '衰', '病', '死', '墓', '絕', '胎', '養', '十二宮', '五行長生'],
    '根气': ['有根', '無根', '通根', '根氣', '根深', '根淺', '得根', '根重', '根輕', '歸祿', '坐祿'],
    '党众': ['黨', '眾', '衆', '黨眾', '多', '旺黨', '得黨', '党'],
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
