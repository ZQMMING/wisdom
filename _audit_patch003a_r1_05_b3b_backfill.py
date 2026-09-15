# -*- coding: utf-8 -*-
"""003B：第一批 TO_VERIFY cell 从原文回填 text_layer/evidence_grade/attribution"""
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

filled = 0
still_tv = 0
for dk, dom in data.items():
    for b, cells in dom.get('books', {}).items():
        for c in cells:
            if c.get('text_layer') != 'TO_VERIFY':
                continue
            sid = c.get('source_id')
            s = src.get(b, {}).get(sid)
            if not s:
                c['text_layer'] = 'NOT_FOUND'
                c['evidence_grade'] = None
                c['attribution'] = None
                c['chapter_id'] = 'NOT_FOUND'
                still_tv += 1
                continue
            # 从原文回填
            c['text_layer'] = s.get('text_layer') or '—'
            c['evidence_grade'] = s.get('evidence_grade') or '—'
            c['attribution'] = s.get('attribution') or 'UNKNOWN'
            if c.get('chapter_id') == 'TO_VERIFY':
                c['chapter_id'] = s.get('chapter') or '—'
            if c.get('object_type') == 'TO_VERIFY':
                c['object_type'] = 'FOUR_PILLARS' if b in ('YHZP', 'SMTH', 'SFTK') else 'DAY_STEM'
            if c.get('semantic_role') == 'TO_VERIFY':
                c['semantic_role'] = 'DEFINITION'
            filled += 1

json.dump(data, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'第一批回填：{filled} cell；仍 TO_VERIFY/NOT_FOUND：{still_tv}')
