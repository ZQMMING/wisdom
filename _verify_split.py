# -*- coding: utf-8 -*-
"""抽查拆条结果"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CHK = ['SFTK-018-012-01', 'SFTK-018-012-04', 'SFTK-018-012-06',
       'SFTK-043-003-02', 'SFTK-043-003-03', 'SFTK-043-003-06',
       'SFTK-062-038-01', 'SFTK-062-038-06',
       'SFTK-124-025-01', 'SFTK-124-025-02',
       'SFTK-125-029-01', 'SFTK-125-029-02', 'SFTK-125-029-15',
       'SFTK-125-057-01', 'SFTK-125-057-02']
for l in open(r'D:\shuntian-ziping-p0\registries\source\sources.sftk.jsonl', encoding='utf-8').read().splitlines():
    if not l.strip():
        continue
    s = json.loads(l)
    if s['source_id'] in CHK:
        extra = ''
        if 'annotation_type' in s:
            extra = f" | ann={s['annotation_type']}/{s.get('attribution')}"
        if 'quoted_origin' in s:
            extra = f" | origin={s['quoted_origin']} | verif={s.get('origin_verification')}"
        print(f"--- {s['source_id']} | {s['text_layer']} | {s['evidence_grade']}{extra}")
        print(f"    {s['source_text'][:100]}")
        print()
