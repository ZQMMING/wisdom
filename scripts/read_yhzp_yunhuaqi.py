# -*- coding: utf-8 -*-
"""读取《渊海子平·論運化氣》完整原文"""
import sys
import io
import json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

target_chapter = "論運化氣"
cases = []

with open(r'D:\shuntian-ziping-p0\registries\source\sources.yhzp.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if not line.strip(): continue
        rec = json.loads(line)
        if rec.get('chapter') == target_chapter:
            cases.append(rec)

print(f"=== 《渊海子平·論運化氣》完整原文（{len(cases)}条） ===\n")

for rec in cases:
    sid = rec.get('source_id')
    layer = rec.get('text_layer')
    grade = rec.get('evidence_grade')
    text = rec.get('source_text', '')
    variants = rec.get('text_variants', [])
    
    print(f"--- {sid} [{grade}] {layer} ---")
    print(text)
    if variants:
        print(f"  异文数: {len(variants)}")
        for v in variants:
            print(f"    - {v.get('loc', '')}: {v.get('project_base_text', '')} vs {v.get('variant', '')}")
            print(f"      {v.get('note', '')[:80]}...")
    print()
