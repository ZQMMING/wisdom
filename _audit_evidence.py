# -*- coding: utf-8 -*-
"""PENDING-EVIDENCE 本地 source 钉查：SFTK-022-010 / SMTH-072-009 完整记录 + 各印旺条 text_layer"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'D:\shuntian-ziping-p0\registries\source'

def dump(eng, sid_filter):
    lines = open(f'{ROOT}/sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
    for l in lines:
        if not l.strip():
            continue
        s = json.loads(l)
        if s.get('source_id') in sid_filter:
            print('---', s.get('source_id'))
            for k in ('book', 'chapter', 'text_layer', 'resource_id', 'text_id',
                      'logical_uri', 'relative_path', 'version', 'status',
                      'evidence_grade', 'text_variants'):
                if k in s:
                    print(f'  {k}: {s[k]}')
            print(f'  source_text: {s.get("source_text", "")[:300]}')
            print()

print('===== SFTK 印旺相关 =====')
dump('sftk', {'SFTK-022-010', 'SFTK-022-027', 'SFTK-025-043', 'SFTK-121-001', 'SFTK-125-023'})

print('===== SMTH 印旺相关 =====')
dump('smth', {'SMTH-072-009', 'SMTH-043-004', 'SMTH-052-002', 'SMTH-117-001'})
