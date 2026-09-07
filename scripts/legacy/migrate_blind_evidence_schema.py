#!/usr/bin/env python3
"""盲派Evidence Schema v2.0迁移脚本
迁移规则：
1. original_text → normalized_summary
2. 新增 source_excerpt 字段（初始为空）
3. 移除 original_text 字段
"""
import json
from pathlib import Path
import sys

evidence_dir = Path(__file__).parent.parent / 'data' / 'evidence' / 'blind_seg'

print("=" * 70)
print("盲派Evidence Schema v2.0 迁移")
print("=" * 70)

total = 0
migrated = 0
errors = []

for f in sorted(evidence_dir.glob('E-BLIND-*.json')):
    if 'fix-record' in f.name or 'verification' in f.name or 'manifest' in f.name:
        continue
    
    total += 1
    try:
        data = json.loads(f.read_text(encoding='utf-8'))
        
        # 检查是否已迁移
        if 'normalized_summary' in data and 'source_excerpt' in data and 'original_text' not in data:
            migrated += 1
            continue
        
        # 执行迁移
        if 'original_text' in data:
            # 保存原文到normalized_summary
            data['normalized_summary'] = data.pop('original_text')
        
        # 添加source_excerpt（空）
        if 'source_excerpt' not in data:
            data['source_excerpt'] = ''
        
        # 写回文件
        f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        migrated += 1
        
    except Exception as e:
        errors.append(f"{f.name}: {e}")

print(f"\n总Evidence: {total}")
print(f"已迁移: {migrated}")
print(f"错误: {len(errors)}")

if errors:
    print("\n错误详情:")
    for e in errors[:10]:
        print(f"  - {e}")

# 状态统计
print("\n状态统计:")
verified = pending = rejected = 0
for f in sorted(evidence_dir.glob('E-BLIND-*.json')):
    if 'fix-record' in f.name or 'verification' in f.name or 'manifest' in f.name:
        continue
    data = json.loads(f.read_text(encoding='utf-8'))
    sv = data.get('source_verification', {})
    status = sv.get('status', 'PENDING')
    if status == 'VERIFIED':
        verified += 1
    elif status == 'REJECTED':
        rejected += 1
    else:
        pending += 1

print(f"  VERIFIED: {verified}")
print(f"  PENDING: {pending}")
print(f"  REJECTED: {rejected}")

print("\n" + "=" * 70)
if errors:
    print("FAILED")
    sys.exit(1)
else:
    print("PASSED: Schema v2.0 迁移完成")
