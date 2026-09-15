# -*- coding: utf-8 -*-
"""1. 9 个混排 source_id 全仓库引用面（rules/其他）
2. 9 条完整 source_text"""
import json, io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MIXED = ['SFTK-018-012', 'SFTK-043-003', 'SFTK-062-038', 'SFTK-124-025',
         'SFTK-124-064', 'SFTK-124-095', 'SFTK-124-107', 'SFTK-125-029', 'SFTK-125-057']

print('===== 引用面搜索 =====')
ROOT = r'D:\shuntian-ziping-p0'
for dirpath, _, files in os.walk(ROOT):
    if '.git' in dirpath:
        continue
    for f in files:
        if not f.endswith(('.jsonl', '.json', '.py', '.md', '.tsv')):
            continue
        p = os.path.join(dirpath, f)
        try:
            content = open(p, encoding='utf-8').read()
        except Exception:
            continue
        for sid in MIXED:
            if sid in content:
                # 只统计引用（非定义行）
                print(f'  {sid} <- {p}')
                break

print()
print('===== 9 条完整内容 =====')
src = {s['source_id']: s for l in open(f'{ROOT}/registries/source/sources.sftk.jsonl', encoding='utf-8').read().splitlines() if l.strip() for s in [json.loads(l)]}
for sid in MIXED:
    s = src.get(sid)
    if s:
        print(f'--- {sid} | {s.get("chapter")} | layer={s.get("text_layer")} | grade={s.get("evidence_grade")}')
        print(s.get('source_text', ''))
        print()
