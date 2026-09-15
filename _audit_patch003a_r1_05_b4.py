# -*- coding: utf-8 -*-
"""R1-05 第四批：格局成败 / 相神 / 顺逆 六部扫描"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

groups = {
    '格局成败': ['成格', '敗格', '格成', '格敗', '成也', '敗也', '有成', '有敗', '成敗', '不成', '破格', '成格者', '敗格者'],
    '相神': ['相神', '相之', '為相', '輔用', '相我', '輔助用神', '相神者', '相神之用'],
    '顺逆': ['順用', '逆用', '順而', '逆而', '當順而順', '當逆而逆', '順逆', '順之', '逆之'],
}

for gname, KEYS in groups.items():
    print(f'\n{"="*60}\n## {gname}')
    for eng in ['yhzp', 'pzzq', 'dts', 'qtbj', 'smth', 'sftk']:
        lines = open(rf'D:\shuntian-ziping-p0\registries\source\sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
        books = [json.loads(l) for l in lines if l.strip()]
        hits = [s for s in books if any(k in s.get('source_text', '') for k in KEYS)]
        scored = sorted(hits, key=lambda s: sum(1 for k in KEYS if k in s.get('source_text', '')), reverse=True)
        print(f'\n--- {eng}（{len(hits)} 条） ---')
        for s in scored[:5]:
            t = s.get('source_text', '')
            print(f'  {s["source_id"]} [{s.get("chapter")}] {s.get("text_layer")}/{s.get("evidence_grade")} 命中{sum(1 for k in KEYS if k in t)}: {t[:110]}')
