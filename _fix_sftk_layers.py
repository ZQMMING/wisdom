# -*- coding: utf-8 -*-
"""SFTK text_layer 修正：補曰/註/釋 开头的条目 = 注解层（张楠补注），
错标 ORIGINAL/A → ANNOTATION/B。歌/詩 开头登记待批不机械改。"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\shuntian-ziping-p0\registries\source\sources.sftk.jsonl'
lines = open(P, encoding='utf-8').read().splitlines()
out = []
fixed = []
pend = []
for l in lines:
    if not l.strip():
        out.append(l)
        continue
    s = json.loads(l)
    txt = s.get('source_text', '').strip()
    layer = s.get('text_layer')
    grade = s.get('evidence_grade')
    # 注解开头：補曰 / 註 / 釋 / 註釋
    if txt.startswith(('補曰', '註釋', '註', '釋')):
        if layer != 'ANNOTATION' or grade != 'B':
            s['text_layer'] = 'ANNOTATION'
            s['evidence_grade'] = 'B'
            s['notes'] = s.get('notes', '') + '；2026-09-16 修正：注解层（補曰/註/釋 开头=张楠补注），原误标 ORIGINAL/A'
            fixed.append(s['source_id'])
    # 歌/詩 开头：登记待批
    elif txt.startswith(('歌', '詩')):
        pend.append(s['source_id'])
    out.append(json.dumps(s, ensure_ascii=False))

open(P, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(f'修正为 ANNOTATION/B: {len(fixed)} 条')
print(f'歌/詩 开头待批（未改）: {len(pend)} 条')
for x in fixed[:10]:
    print('  FIX', x)
print('  ...')
print('待批样本:', pend[:10])
