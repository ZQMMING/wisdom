# -*- coding: utf-8 -*-
"""R1-05 第五批：干支组合 / 六亲 / 神煞 / 命例验证 六部扫描"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

groups = {
    '干支组合': ['干支', '天干地支', '干上', '支上', '坐', '帶', '逢', '配', '合', '沖', '刑', '破', '害', '拱', '夾', '暗合', '天干地支相'],
    '六亲': ['六親', '父母', '兄弟', '妻', '子', '夫', '祖', '祖上', '妻財', '子女', '六親'],
    '神煞': ['神煞', '吉神', '凶煞', '貴人', '天德', '月德', '桃花', '咸池', '驛馬', '華蓋', '亡神', '劫煞', '羊刃', '空亡', '孤辰', '寡宿', '文昌', '將星', '魁罡', '天乙'],
    '命例验证': ['命例', '之命', '之造', '之命也', '丞相', '尚書', '狀元', '探花', '榜眼', '進士', '翰林', '侍郎', '知府', '員外', '富翁', '乞丐', '僧道'],
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
            print(f'  {s["source_id"]} [{s.get("chapter")}] {s.get("text_layer")}/{s.get("evidence_grade")} 命中{sum(1 for k in KEYS if k in t)}: {t[:95]}')
