"""
验证 P2.2 治理修复的正确性
- 检查 Evidence Status Ladder 定义是否完整
- 验证盲派证据状态分布
- 确认 schema 正确扩展
- 检查 Heluo 内容已拆分
"""
import json
from pathlib import Path
from collections import Counter

# 1. 检查 EVIDENCE_STATUS_LADDER.md 定义
print("=" * 60)
print("1. Evidence Status Ladder 定义检查")
print("=" * 60)

ladder_file = Path("EVIDENCE_STATUS_LADDER.md")
if ladder_file.exists():
    content = ladder_file.read_text(encoding='utf-8')
    print(f"✓ {ladder_file} 存在 ({len(content)} 字符)")
    
    # 检查关键定义
    checks = [
        ("Layer 1: Source Verification", "source_verification.status = VERIFIED"),
        ("Layer 2: SEMANTIC_MATCHED", "authority_status = SEMANTIC_MATCHED"),
        ("Layer 3: Production Admittance", "PRODUCTION_ADMITTED"),
        ("禁止规则", "❌ 禁止"),
        ("Human Expert 要求", "Human Expert"),
        ("逐字比对要求", "verbatim_comparison"),
    ]
    
    for name, marker in checks:
        if marker in content:
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name} 未找到: {marker}")
else:
    print(f"✗ {ladder_file} 不存在")

# 2. 检查 schema 扩展
print("\n" + "=" * 60)
print("2. Schema 扩展检查")
print("=" * 60)

schema_file = Path("data/schemas/blind-evidence.schema.json")
if schema_file.exists():
    schema = json.loads(schema_file.read_text(encoding='utf-8'))
    
    # 检查 authority_status 枚举
    if 'authority_status' in schema.get('properties', {}):
        auth_enum = schema['properties']['authority_status'].get('enum', [])
        expected = ['UNVERIFIED', 'SEMANTIC_MATCHED', 'PRODUCTION_ADMITTED', 'REJECTED', 'PENDING_REVIEW', 'CASE_EVIDENCE']
        missing = [e for e in expected if e not in auth_enum]
        if not missing:
            print(f"✓ authority_status 枚举完整: {auth_enum}")
        else:
            print(f"✗ authority_status 缺少: {missing}")
    
    # 检查 source_fidelity 枚举
    if 'source_fidelity' in schema.get('properties', {}):
        fidelity_enum = schema['properties']['source_fidelity'].get('enum', [])
        if 'SEMANTIC_MATCH' in fidelity_enum:
            print(f"✓ source_fidelity 包含 SEMANTIC_MATCH")
        else:
            print(f"✗ source_fidelity 缺少 SEMANTIC_MATCH: {fidelity_enum}")
else:
    print(f"✗ {schema_file} 不存在")

# 3. 检查盲派证据状态分布
print("\n" + "=" * 60)
print("3. 盲派证据状态分布")
print("=" * 60)

blind_dir = Path("data/evidence/blind_seg")
if blind_dir.exists():
    evidence_files = list(blind_dir.glob("E-BLIND-*.json"))
    status_counts = Counter()
    
    for f in evidence_files:
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            status = data.get('authority_status', 'UNKNOWN')
            status_counts[status] += 1
        except:
            status_counts['PARSE_ERROR'] += 1
    
    print(f"总证据数: {len(evidence_files)}")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    
    # 检查 SEMANTIC_MATCHED 比例
    semantic = status_counts.get('SEMANTIC_MATCHED', 0)
    if len(evidence_files) > 0:
        ratio = semantic / len(evidence_files) * 100
        print(f"\n语义匹配率: {ratio:.1f}% ({semantic}/{len(evidence_files)})")
else:
    print(f"✗ {blind_dir} 不存在")

# 4. 检查随机样本的 source_verification 字段
print("\n" + "=" * 60)
print("4. 随机样本验证 (source_verification 字段)")
print("=" * 60)

if blind_dir.exists():
    sample_files = [
        "E-BLIND-A-IDENTITY-001.json",
        "E-BLIND-B-IMAGE-001.json",
        "E-BLIND-C-WORK_METHOD-001.json",
    ]
    
    for sample_name in sample_files:
        sample_path = blind_dir / sample_name
        if sample_path.exists():
            data = json.loads(sample_path.read_text(encoding='utf-8'))
            
            # 检查 source_verification
            sv = data.get('source_verification', {})
            if sv.get('status') == 'VERIFIED':
                print(f"✓ {sample_name}: source_verification.status = VERIFIED")
                print(f"  verification_method = {sv.get('verification_method', 'N/A')}")
            else:
                print(f"⚠ {sample_name}: source_verification.status = {sv.get('status', 'MISSING')}")
                
            # 检查 authority_status
            auth = data.get('authority_status', 'MISSING')
            if auth == 'SEMANTIC_MATCHED':
                print(f"  authority_status = SEMANTIC_MATCHED ✓")
            else:
                print(f"  authority_status = {auth} ⚠")
        else:
            print(f"✗ {sample_name} 不存在")

# 5. 检查 Heluo 内容拆分
print("\n" + "=" * 60)
print("5. Heluo 内容拆分检查")
print("=" * 60)

# 检查 HUELLO_APPENDIX_J_K.md 存在
appendix_file = Path("HUELLO_APPENDIX_J_K.md")
if appendix_file.exists():
    print(f"✓ {appendix_file} 存在")
    content = appendix_file.read_text(encoding='utf-8')
    if 'H1 Yi Core Contract' in content:
        print(f"  ✓ 包含 H1 实现记录")
    if '251 tests passed' in content:
        print(f"  ✓ 包含测试统计")
else:
    print(f"✗ {appendix_file} 不存在")

# 检查 HeluoRuleEvidenceMatrix_Final.md 是否还包含实现记录
matrix_file = Path("HeluoRuleEvidenceMatrix_Final.md")
if matrix_file.exists():
    content = matrix_file.read_text(encoding='utf-8')
    if 'HUELLO_APPENDIX_J_K' in content or '附录J' in content:
        print(f"⚠ {matrix_file} 可能仍包含附录内容")
    else:
        print(f"✓ {matrix_file} 已清理附录内容")

# 6. 总结
print("\n" + "=" * 60)
print("6. 治理修复验证总结")
print("=" * 60)

all_passed = True

# 检查关键条件
if ladder_file.exists():
    content = ladder_file.read_text(encoding='utf-8')
    if 'PRODUCTION_ADMITTED' in content and 'VERIFIED ≠ Production Authority':
        print("✓ Evidence Status Ladder 正确定义")
    else:
        print("✗ Evidence Status Ladder 定义不完整")
        all_passed = False

if schema_file.exists():
    schema = json.loads(schema_file.read_text(encoding='utf-8'))
    if 'SEMANTIC_MATCHED' in schema.get('properties', {}).get('authority_status', {}).get('enum', []):
        print("✓ Schema 已扩展 SEMANTIC_MATCHED")
    else:
        print("✗ Schema 未扩展 SEMANTIC_MATCHED")
        all_passed = False

if blind_dir.exists():
    files = list(blind_dir.glob("E-BLIND-*.json"))
    semantic_count = sum(1 for f in files if json.loads(f.read_text(encoding='utf-8')).get('authority_status') == 'SEMANTIC_MATCHED')
    if semantic_count > 0:
        print(f"✓ {semantic_count}/{len(files)} 证据处于 SEMANTIC_MATCHED 状态")
    else:
        print("✗ 无证据处于 SEMANTIC_MATCHED 状态")
        all_passed = False

if appendix_file.exists():
    print("✓ Heluo 附录已拆分到独立文件")
else:
    print("✗ Heluo 附录文件不存在")
    all_passed = False

print("\n" + "=" * 60)
if all_passed:
    print("🟢 治理修复验证通过")
else:
    print("🔴 治理修复验证失败，存在未解决问题")
print("=" * 60)
