# -*- coding: utf-8 -*-
"""R1-05 补充定位：YHZP-138-001 子平赋 + SMTH 党盛/力势"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for eng, kws in {
    'yhzp': ['子平賦', '無氣', '遇劫', '得時', '四柱無根', '日干無氣'],
    'smth': ['黨', '至切', '力勢', '衝起', '拱起', '刑起', '合起'],
    'dts': ['勢', '順勢', '從勢', '不可遏'],
    'sftk': ['從化', '棄命', '從財', '從殺'],
}.items():
    lines = open(rf'D:\shuntian-ziping-p0\registries\source\sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
    books = [json.loads(l) for l in lines if l.strip()]
    print(f'=== {eng} ===')
    for kw in kws:
        cnt = 0
        for s in books:
            t = s.get('source_text', '')
            if kw in t:
                print(f'  {s["source_id"]} [{s.get("chapter")}] {s.get("text_layer")}/{s.get("evidence_grade")}: ...{t[max(0,t.find(kw)-12):t.find(kw)+32]}...')
                cnt += 1
                if cnt >= 3:
                    break
        if cnt == 0:
            print(f'  [{kw}] 未找到')
