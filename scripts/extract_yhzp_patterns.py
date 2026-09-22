# -*- coding: utf-8 -*-
"""从《渊海子平》提取专旺/化气相关章节"""
import sys
import io
import json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 相关章节
RELEVANT_CHAPTERS = [
    "外十八格",
    "化氣十段錦（其一）",
    "論運化氣",
    "丙十八格",
]

found = {}

with open(r'D:\shuntian-ziping-p0\registries\source\sources.yhzp.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if not line.strip(): continue
        rec = json.loads(line)
        chapter = rec.get('chapter', '')
        if chapter not in RELEVANT_CHAPTERS:
            continue
        if chapter not in found:
            found[chapter] = []
        found[chapter].append(rec)

for ch in RELEVANT_CHAPTERS:
    if ch not in found:
        print(f"=== {ch}: 未找到 ===\n")
        continue
    
    cases = found[ch]
    print(f"=== {ch}（{len(cases)}条） ===")
    for rec in cases[:5]:  # 每章只显示前5条
        sid = rec.get('source_id')
        layer = rec.get('text_layer')
        grade = rec.get('evidence_grade')
        text = rec.get('source_text', '')[:120] + '...' if len(rec.get('source_text', '')) > 120 else rec.get('source_text', '')
        print(f"  [{grade}] {sid} ({layer})")
        print(f"    {text}")
    if len(cases) > 5:
        print(f"  ... 还有{len(cases)-5}条")
    print()
