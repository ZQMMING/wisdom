# -*- coding: utf-8 -*-
"""提取 SFTK 91 条 歌/詩 开头条目全文，用于逐条 text_layer 定性"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

lines = open(r'D:\shuntian-ziping-p0\registries\source\sources.sftk.jsonl', encoding='utf-8').read().splitlines()
rows = []
for l in lines:
    if not l.strip():
        continue
    s = json.loads(l)
    txt = s.get('source_text', '').strip()
    if txt.startswith(('歌', '詩')):
        rows.append(s)

print(f'歌/詩 开头总数: {len(rows)}')
# 按开头字细分
from collections import Counter
heads = Counter()
for s in rows:
    heads[s['source_text'][:4]] += 1
for k, v in heads.most_common(30):
    print(f'  {k}: {v}')

print()
print('===== 全量明细 =====')
for s in rows:
    print(f"--- {s['source_id']} | {s.get('chapter')} | layer={s.get('text_layer')} | grade={s.get('evidence_grade')}")
    print(f"    {s.get('source_text', '')}")
