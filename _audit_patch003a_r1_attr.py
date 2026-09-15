# -*- coding: utf-8 -*-
"""R1-01：DTS ANNOTATION 全部 124 条特征扫描（判定 attribution 依据）"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

lines = open(r'D:\shuntian-ziping-p0\registries\source\sources.dts.jsonl', encoding='utf-8').read().splitlines()
books = [json.loads(l) for l in lines if l.strip()]

ann = [s for s in books if s.get('text_layer') == 'ANNOTATION']
print(f"ANNOTATION 共 {len(ann)} 条\n")

# 特征1：是否含 任氏/任铁樵/曰 标记
import re
marks = {'任氏': [], '任铁樵': [], '任曰': [], '原注': [], '補曰': [], '註曰': [], '釋曰': []}
for s in ann:
    t = s.get('source_text', '')
    for k in marks:
        if k in t:
            marks[k].append(s['source_id'])
for k, v in marks.items():
    print(f"含「{k}」: {len(v)} 条 {v[:10]}")

# 特征2：长度分布（长注倾向任氏展开）
lens = [(len(s.get('source_text', '')), s['source_id']) for s in ann]
lens.sort(reverse=True)
print("\n最长 15 条注（>300 字倾向任氏展开）:")
for l, sid in lens[:15]:
    print(f"  {sid}: {l}字")

# 特征3：短注（<80 字，倾向原注）
short = [(len(s.get('source_text', '')), s['source_id']) for s in ann if len(s.get('source_text', '')) < 80]
print(f"\n短注（<80字，倾向原注/简注）: {len(short)} 条")
for l, sid in short[:20]:
    print(f"  {sid}: {l}字")

# 特征4：每章注的格式统一性（是否都带 > 注： 前缀）
prefix = {}
for s in ann:
    t = s.get('source_text', '')
    p = t[:6]
    prefix.setdefault(p, 0)
    prefix[p] += 1
print("\n注前缀格式分布:")
for p, c in sorted(prefix.items(), key=lambda x: -x[1])[:5]:
    print(f"  {p!r}: {c} 条")
