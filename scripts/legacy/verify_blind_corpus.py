#!/usr/bin/env python3
"""Phase A Verification - Blind Evidence Corpus v1"""
import json
from pathlib import Path

evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence/blind_seg')

# 验证 manifest
with open(evidence_dir / 'manifest.json', 'r', encoding='utf-8') as f:
    manifest = json.load(f)

print("=" * 70)
print("Phase A Verification: Blind Evidence Corpus v1")
print("=" * 70)
print()
print(f"总证据数: {manifest['total_evidence']}")
print(f"状态: {manifest['status']}")
print()
print("分层分布:")
for layer, count in manifest['provenance_distribution'].items():
    print(f"  Layer {layer}: {count}")
print()
print("主题分布:")
for topic, count in manifest['topic_distribution'].items():
    print(f"  {topic}: {count}")
print()

# 验证所有证据文件
errors = []
for f in evidence_dir.glob('E-BLIND-*.json'):
    with open(f, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    
    # 必填字段检查
    required_fields = ['evidence_id', 'system', 'provenance_layer', 'source', 
                       'original_text', 'extraction_topic', 'claim_type', 'certainty']
    for field in required_fields:
        if field not in data:
            errors.append(f"{f.name}: 缺少字段 {field}")
    
    # provenance_layer 检查
    if data.get('provenance_layer') not in ['A', 'B', 'C']:
        errors.append(f"{f.name}: 无效的 provenance_layer {data.get('provenance_layer')}")
    
    # original_text 非空检查
    if not data.get('original_text'):
        errors.append(f"{f.name}: original_text 为空")

if errors:
    print("❌ 验证失败:")
    for e in errors:
        print(f"   - {e}")
else:
    print("✅ 所有证据文件验证通过")
    print()
    print("Phase A 状态: 完成")
    print("下一步: 补充剩余主题 Evidence 或进入 Phase B")
