#!/usr/bin/env python3
"""盲派Evidence Schema v2.0 Validator
验证标准：
1. 所有Evidence必须有 source_excerpt 和 normalized_summary 字段
2. original_text 字段不得存在
3. VERIFIED状态必须有非空 source_excerpt
4. PENDING状态必须有空 source_excerpt
"""
import json
from pathlib import Path
import sys

evidence_dir = Path(__file__).parent.parent / 'data' / 'evidence' / 'blind_seg'
schema_path = Path(__file__).parent.parent / 'data' / 'schemas' / 'blind-evidence.schema.json'

def validate_evidence(data: dict, file_path: Path) -> list[str]:
    """验证单条Evidence"""
    errors = []
    ev_id = data.get('evidence_id', file_path.name)
    
    # 1. 必须有 source_excerpt 字段
    if 'source_excerpt' not in data:
        errors.append(f"{ev_id}: 缺少 source_excerpt 字段")
    
    # 2. 必须有 normalized_summary 字段
    if 'normalized_summary' not in data:
        errors.append(f"{ev_id}: 缺少 normalized_summary 字段")
    
    # 3. 不得有 original_text 字段（已迁移到normalized_summary）
    if 'original_text' in data:
        errors.append(f"{ev_id}: 仍保留 original_text 字段，应已迁移到 normalized_summary")
    
    # 4. VERIFIED状态必须有非空 source_excerpt
    sv = data.get('source_verification', {})
    status = sv.get('status', 'PENDING')
    
    if status == 'VERIFIED':
        excerpt = data.get('source_excerpt', '')
        if not excerpt or excerpt.strip() == '':
            errors.append(f"{ev_id}: VERIFIED状态但 source_excerpt 为空")
        # VERIFIED还需要 locator
        if not sv.get('locator'):
            errors.append(f"{ev_id}: VERIFIED状态但缺少 locator")
    
    elif status == 'PENDING':
        # PENDING状态 source_excerpt 应为空
        excerpt = data.get('source_excerpt', '')
        if excerpt and excerpt.strip():
            errors.append(f"{ev_id}: PENDING状态但 source_excerpt 非空（不应有原文摘录）")
    
    elif status == 'REJECTED':
        # REJECTED状态可以有或没有 source_excerpt
        pass
    
    return errors

def main():
    print("=" * 70)
    print("盲派Evidence Schema v2.0 验证器")
    print("=" * 70)
    
    # 检查Schema文件
    print("\n1. 检查Schema文件...")
    if not schema_path.exists():
        print("   ❌ Schema文件不存在")
        sys.exit(1)
    schema = json.loads(schema_path.read_text(encoding='utf-8'))
    print(f"   ✓ Schema文件存在: {schema_path}")
    
    # 检查必填字段
    required = schema.get('required', [])
    if 'source_excerpt' not in required:
        print("   ⚠️  source_excerpt 不是必填字段")
    if 'normalized_summary' not in required:
        print("   ⚠️  normalized_summary 不是必填字段")
    
    # 验证所有Evidence
    print("\n2. 验证Evidence文件...")
    total = 0
    valid = 0
    all_errors = []
    
    for f in sorted(evidence_dir.glob('E-BLIND-*.json')):
        if 'fix-record' in f.name or 'verification' in f.name or 'manifest' in f.name:
            continue
        
        total += 1
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            errors = validate_evidence(data, f)
            if errors:
                all_errors.extend(errors)
            else:
                valid += 1
        except Exception as e:
            all_errors.append(f"{f.name}: 读取失败 - {e}")
    
    print(f"   总Evidence: {total}")
    print(f"   有效: {valid}")
    print(f"   错误: {len(all_errors)}")
    
    # 显示错误详情
    if all_errors:
        print("\n3. 错误详情:")
        for err in all_errors[:20]:  # 只显示前20条
            print(f"   - {err}")
        if len(all_errors) > 20:
            print(f"   ... 还有 {len(all_errors) - 20} 条错误")
    
    # 统计状态
    print("\n4. 状态统计:")
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
    
    print(f"   VERIFIED: {verified}")
    print(f"   PENDING: {pending}")
    print(f"   REJECTED: {rejected}")
    
    # 最终结果
    print("\n" + "=" * 70)
    if all_errors:
        print(f"FAILED: 发现 {len(all_errors)} 个错误")
        sys.exit(1)
    else:
        print("PASSED: 所有Evidence符合Schema v2.0")
        print(f"  - {total}条Evidence全部通过验证")
        print(f"  - VERIFIED={verified}, PENDING={pending}, REJECTED={rejected}")

if __name__ == '__main__':
    main()
