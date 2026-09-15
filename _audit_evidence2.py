# -*- coding: utf-8 -*-
"""PENDING-EVIDENCE 深入钉查：
1. SMTH-092-007 完整记录（亥卯未印旺 真实出处）
2. SFTK 全部 補曰/註/釋 开头条目 text_layer 统计（疑似注解错标 ORIGINAL）"""
import json, io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'D:\shuntian-ziping-p0\registries\source'

print('===== SMTH-092-007 完整记录 =====')
for l in open(f'{ROOT}/sources.smth.jsonl', encoding='utf-8').read().splitlines():
    if not l.strip():
        continue
    s = json.loads(l)
    if s.get('source_id') == 'SMTH-092-007':
        for k, v in s.items():
            print(f'  {k}: {v}')
        break

print()
print('===== SFTK source 全文「補曰/註/釋」开头统计 =====')
total = 0
annot_head = {'補曰': 0, '註': 0, '釋': 0, '歌': 0, '詩': 0}
mislabel = []  # 注解开头但标 ORIGINAL
for l in open(f'{ROOT}/sources.sftk.jsonl', encoding='utf-8').read().splitlines():
    if not l.strip():
        continue
    s = json.loads(l)
    total += 1
    txt = s.get('source_text', '').strip()
    for kw in annot_head:
        if txt.startswith(kw):
            annot_head[kw] += 1
            if s.get('text_layer') == 'ORIGINAL':
                mislabel.append((s.get('source_id'), kw, s.get('evidence_grade')))
            break
print('SFTK source 总数:', total)
print('注解开头统计:', annot_head)
print('错标 ORIGINAL 的注解条目数:', len(mislabel))
for sid, kw, g in mislabel[:40]:
    print(f'  {sid} [{kw}] grade={g}')
