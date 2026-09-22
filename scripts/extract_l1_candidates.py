# -*- coding: utf-8 -*-
"""T1：从DTS切片中提取L1核心集候选"""
import sys
import io
import json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 相关章节
RELEVANT_CHAPTERS = [
    "六親論·化象",
    "六親論·從象",
    "通天論·形象論",
    "通天論·方局論",
    "六親論·假化",
    "六親論·假象",
    "六親論·順局",
    "六親論·戰局",
    "六親論·反局",
    "六親論·合局",
]

l1_candidates = []

with open(r'D:\shuntian-ziping-p0\registries\source\sources.dts.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if not line.strip(): continue
        rec = json.loads(line)
        
        # 硬门槛：只认京图原文 + 刘基原注
        if rec.get('attribution') not in ('ORIGINAL_AUTHOR', 'ORIGINAL_ANNOTATION'):
            continue
        if rec.get('evidence_grade') not in ('A', 'B'):
            continue
        
        chapter = rec.get('chapter', '')
        if chapter not in RELEVANT_CHAPTERS:
            continue
        
        l1_candidates.append({
            'source_id': rec.get('source_id'),
            'chapter': chapter,
            'text_layer': rec.get('text_layer'),
            'evidence_grade': rec.get('evidence_grade'),
            'attribution': rec.get('attribution'),
            'source_text': rec.get('source_text', '')[:200] + '...' if len(rec.get('source_text', '')) > 200 else rec.get('source_text', ''),
            'full_text_length': len(rec.get('source_text', '')),
        })

print(f"=== L1核心集候选（共{len(l1_candidates)}条） ===\n")

# 按章节分组
by_chapter = {}
for c in l1_candidates:
    ch = c['chapter']
    if ch not in by_chapter:
        by_chapter[ch] = []
    by_chapter[ch].append(c)

for ch, cases in sorted(by_chapter.items()):
    print(f"--- {ch}（{len(cases)}条） ---")
    for c in cases[:3]:  # 每章只显示前3条
        print(f"  [{c['evidence_grade']}] {c['source_id']}")
        print(f"    {c['source_text'][:100]}...")
    if len(cases) > 3:
        print(f"  ... 还有{len(cases)-3}条")
    print()

# 保存候选
output_dir = Path(r'D:\shuntian-ziping-p0\tests\l1_core')
output_dir.mkdir(parents=True, exist_ok=True)

with open(output_dir / 'dts_candidates.json', 'w', encoding='utf-8') as f:
    json.dump(l1_candidates, f, ensure_ascii=False, indent=2)

print(f"候选已保存到: tests/l1_core/dts_candidates.json")
