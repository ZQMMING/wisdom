# -*- coding: utf-8 -*-
"""核实L1核心集5条候选的原始记录"""
import sys
import io
import json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 5条候选的source_id
target_ids = [
    "DTS-041-001",  # 化象原文
    "DTS-041-002",  # 化象原注
    "DTS-040-001",  # 从象原文
    "DTS-040-002",  # 从象原注
    "DTS-043-001",  # 假化原文
    "DTS-043-002",  # 假化原注
    "DTS-042-001",  # 假象原文
    "DTS-042-002",  # 假象原注
    "DTS-011-001",  # 形象論獨象原文
    "DTS-011-002",  # 形象論原注
]

found = {}
with open(r'D:\shuntian-ziping-p0\registries\source\sources.dts.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if not line.strip(): continue
        rec = json.loads(line)
        sid = rec.get('source_id', '')
        if sid in target_ids:
            found[sid] = rec

print("=== L1核心集5条候选核实 ===\n")

for sid in target_ids:
    if sid not in found:
        print(f"⚠️ {sid}: 未找到")
        continue
    
    rec = found[sid]
    print(f"--- {sid} ---")
    print(f"  chapter: {rec.get('chapter')}")
    print(f"  text_layer: {rec.get('text_layer')}")
    print(f"  evidence_grade: {rec.get('evidence_grade')}")
    print(f"  attribution: {rec.get('attribution')}")
    print(f"  evidence_use_policy: {rec.get('evidence_use_policy')}")
    print(f"  source_text: {rec.get('source_text', '')[:150]}...")
    print()

# 统计
print("=== 合规性检查 ===")
l1_compliant = 0
for sid in target_ids:
    if sid not in found:
        print(f"  ❌ {sid}: 未找到")
        continue
    rec = found[sid]
    attr = rec.get('attribution', '')
    grade = rec.get('evidence_grade', '')
    if attr in ('ORIGINAL_AUTHOR', 'ORIGINAL_ANNOTATION') and grade in ('A', 'B'):
        print(f"  ✅ {sid}: {attr}/{grade} 合规")
        l1_compliant += 1
    else:
        print(f"  ❌ {sid}: {attr}/{grade} 不合规")

print(f"\n合规条数: {l1_compliant}/{len(target_ids)}")
