# -*- coding: utf-8 -*-
"""003B-04 修正1：从原文回填缺失 attribution；修正2：g7/g8 按总纲/断语分层"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\shuntian-ziping-p0\governance\r1_05_verified_scope.json'
data = json.load(io.open(P, encoding='utf-8'))
BOOK_FILE = {'YHZP': 'yhzp', 'PZZQ': 'pzzq', 'DTS': 'dts', 'QTBJ': 'qtbj', 'SMTH': 'smth', 'SFTK': 'sftk'}
src = {}
for b, f in BOOK_FILE.items():
    src[b] = {}
    for l in io.open(rf'D:\shuntian-ziping-p0\registries\source\sources.{f}.jsonl', encoding='utf-8'):
        if not l.strip():
            continue
        s = json.loads(l)
        src[b][s['source_id']] = s

# 1. 回填 attribution
backfilled = 0
for dk, dom in data.items():
    for b, cells in dom.get('books', {}).items():
        for c in cells:
            at = c.get('attribution')
            if at in (None, '', '—', 'UNKNOWN', 'TO_VERIFY'):
                s = src.get(b, {}).get(c.get('source_id') or '')
                if s and s.get('attribution'):
                    c['attribution'] = s['attribution']
                    backfilled += 1
json.dump(data, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'attribution 回填：{backfilled} cell')
