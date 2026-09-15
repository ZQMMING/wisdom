# -*- coding: utf-8 -*-
"""R1-01/R1-02：DTS attribution + evidence_use_policy 写入 sources.dts.jsonl
判定依据：
1. 本地 124 条注与维基文库《滴天髓阐微》〈原註〉逐字同源（抽样：天道/天干丁辛壬癸/地支/月令/生时/衰旺/真假）
2. 本地注层无任氏命例特征（此造/余曰/命書/某造/運行命例 0 命中）→ 无 REN_TIEQIAO
3. 滴天髓序 = LATER_COMMENTARY；何知章 UNVERIFIED = UNKNOWN
"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = r'D:\shuntian-ziping-p0\registries\source\sources.dts.jsonl'
lines = open(PATH, encoding='utf-8').read().splitlines()
books = [json.loads(l) for l in lines if l.strip()]

LAYER_MAP = {
    'ORIGINAL': ('ORIGINAL_AUTHOR', ['CORE_RULE_ELIGIBLE']),
    'ANNOTATION': ('ORIGINAL_ANNOTATION', ['SUPPORTING_RULE_ONLY', 'CANDIDATE_RULE', 'NO_ORIGINAL_UPGRADE']),
    'LATER_COMMENTARY': ('LATER_COMMENTARY', ['SUPPORTING_ONLY']),
    'UNVERIFIED': ('UNKNOWN', ['FAIL_CLOSED']),
}

updated = []
for s in books:
    layer = s.get('text_layer', '')
    attr, use = LAYER_MAP.get(layer, ('UNKNOWN', ['FAIL_CLOSED']))
    s['attribution'] = attr
    s['evidence_use_policy'] = use
    s['attribution_basis'] = 'WIKI_CHANWEI_YUANZHU_CROSSCHECK_2026-09-16' if attr == 'ORIGINAL_ANNOTATION' else (
        'WIKI_CHANWEI_CROSSCHECK_2026-09-16' if attr == 'ORIGINAL_AUTHOR' else 'TRANSCRIPTION_2026-09-16')
    updated.append(s)

with open(PATH, 'w', encoding='utf-8') as f:
    for s in updated:
        f.write(json.dumps(s, ensure_ascii=False) + '\n')

from collections import Counter
print('attribution 分布:', dict(Counter(s['attribution'] for s in updated)))
print('总条数:', len(updated))
print('写入完成')
