#!/usr/bin/env python3
"""盲派 Evidence 最终来源真实性验证"""
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# 使用项目根目录
project_dir = Path('C:/Users/wisdom/wisdom')
evidence_dir = project_dir / 'data/evidence/blind_seg'

print("=" * 80)
print("盲派 Evidence 最终来源真实性验证")
print("=" * 80)

# 1. 读取重分类矩阵
matrix_file = evidence_dir / 'reclassification_matrix.json'
matrix = json.load(open(matrix_file, 'r', encoding='utf-8'))
matrix_data = matrix['matrix']

print(f"\n【Step 1】读取重分类矩阵: {len(matrix_data)}条")

# 2. 按来源验证状态分组
pending = []
claimed_direct = []
verified = []

for item in matrix_data:
    status = item['source_verification_status']
    if status == 'PENDING':
        pending.append(item)
    elif status == 'CLAIMED_DIRECT':
        claimed_direct.append(item)
    elif status == 'VERIFIED':
        verified.append(item)

print(f"\n【来源验证状态】")
print(f"   VERIFIED: {len(verified)}条")
print(f"   PENDING: {len(pending)}条")
print(f"   CLAIMED_DIRECT: {len(claimed_direct)}条")

# 3. 逐条核验CLAIMED_DIRECT
print(f"\n【Step 2】逐条核验CLAIMED_DIRECT ({len(claimed_direct)}条)")

verification_results = []
downgraded = []
retained = []

for item in claimed_direct:
    eid = item['evidence_id']
    filepath = evidence_dir / f"{eid}.json"
    
    if not filepath.exists():
        verification_results.append({
            'id': eid,
            'action': 'FILE_NOT_FOUND',
            'reason': 'Evidence文件不存在'
        })
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 检查必要字段
    original_text = data.get('original_text', '')
    source = data.get('source', '')
    author = data.get('author', '')
    chapter = data.get('chapter', '')
    locator = data.get('locator', '')
    edition = data.get('edition', '')
    theory_layer = data.get('theory_layer', '')
    
    # 核验original_text
    text_issues = []
    if len(original_text) < 10:
        text_issues.append('text_too_short')
    if len(original_text) > 500:
        text_issues.append('text_too_long')
    
    # 核验source
    source_issues = []
    if not source:
        source_issues.append('no_source')
    if not author:
        source_issues.append('no_author')
    
    # 核验chapter/locator
    locator_issues = []
    if not chapter:
        locator_issues.append('no_chapter')
    if not locator:
        locator_issues.append('no_locator')
    
    # 核验theory_layer
    layer_issues = []
    if not theory_layer:
        layer_issues.append('no_theory_layer')
    
    # 判定结果
    all_issues = text_issues + source_issues + locator_issues + layer_issues
    
    if not all_issues:
        action = 'RETAINED_DIRECT'
        status = 'VERIFIED'
        retained.append(eid)
        print(f"   ✅ {eid}: 来源完整")
    else:
        action = 'DOWNGRADED'
        status = 'PENDING_VERIFICATION'
        downgraded.append({
            'id': eid,
            'issues': all_issues,
            'issue_details': {
                'text': text_issues,
                'source': source_issues,
                'locator': locator_issues,
                'layer': layer_issues
            }
        })
        print(f"   ⚠️  {eid}: {all_issues}")
    
    verification_results.append({
        'id': eid,
        'action': action,
        'status': status,
        'issues': all_issues,
        'source': source,
        'author': author,
        'chapter': chapter,
        'locator': locator
    })

print(f"\n【核验结果】")
print(f"   保留DIRECT: {len(retained)}条")
print(f"   降级PENDING: {len(downgraded)}条")

# 4. 更新证据文件
print(f"\n【Step 3】更新证据文件")

for item in downgraded:
    eid = item['id']
    filepath = evidence_dir / f"{eid}.json"
    
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 降级source_fidelity
        data['source_fidelity'] = 'PENDING_VERIFICATION'
        data['certainty'] = 'MEDIUM'
        
        # 添加核验标记
        notes = data.get('notes', '')
        notes += f' | 🔍 来源验证: DOWNGRADED - {item["issues"]}'
        data['notes'] = notes
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

print(f"   已更新 {len(downgraded)} 条证据文件")

# 5. 更新重分类矩阵
print(f"\n【Step 4】更新重分类矩阵")

for result in verification_results:
    if result['id'] in [d['id'] for d in downgraded]:
        # 找到对应的矩阵项
        for item in matrix_data:
            if item['evidence_id'] == result['id']:
                item['source_verification_status'] = 'PENDING'
                item['source_verification_notes'] = f"Downgraded: {result['issues']}"
                break

matrix['generated_at'] = datetime.now().isoformat()
matrix['verification_results'] = verification_results
matrix['summary']['downgraded'] = len(downgraded)
matrix['summary']['retained_direct'] = len(retained)

with open(matrix_file, 'w', encoding='utf-8') as f:
    json.dump(matrix, f, ensure_ascii=False, indent=2)

print(f"   矩阵已更新")

# 6. 统计最终状态
print(f"\n【最终状态】")

# 重新统计
final_pending = sum(1 for i in matrix_data if i['source_verification_status'] == 'PENDING')
final_claimed = sum(1 for i in matrix_data if i['source_verification_status'] == 'CLAIMED_DIRECT')
final_verified = sum(1 for i in matrix_data if i['source_verification_status'] == 'VERIFIED')

print(f"   VERIFIED: {final_verified}条")
print(f"   CLAIMED_DIRECT: {final_claimed}条")
print(f"   PENDING: {final_pending}条")
print(f"   总计: {len(matrix_data)}条")

# 7. 生成核验报告
report_file = evidence_dir / 'source_verification_final_report.json'
report = {
    'verification_date': datetime.now().isoformat(),
    'total_evidence': len(matrix_data),
    'verification_summary': {
        'retained_direct': len(retained),
        'downgraded_to_pending': len(downgraded),
        'verified_count': final_verified,
        'claimed_direct_count': final_claimed,
        'pending_count': final_pending
    },
    'downgraded_items': downgraded,
    'verification_results': verification_results
}

with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\n✅ 核验报告已生成: {report_file}")

# 8. 检查结果
print("\n" + "=" * 80)
if final_claimed > 0 or final_pending > 0:
    print(f"⚠️ 仍有 {final_claimed + final_pending} 条证据需要验证")
    print(f"   CLAIMED_DIRECT: {final_claimed}条")
    print(f"   PENDING: {final_pending}条")
else:
    print(f"✅ 所有证据已完成验证")
print("=" * 80)