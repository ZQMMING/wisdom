#!/usr/bin/env python3
"""盲派 Evidence 来源真实性核验"""
import json
import re
from pathlib import Path
from datetime import datetime

# 使用相对路径
evidence_dir = Path(__file__).resolve().parents[1] / 'data/evidence/blind_seg'

print("=" * 80)
print("盲派 Evidence 来源真实性核验")
print("=" * 80)

# 读取重分类矩阵
matrix_file = evidence_dir / 'reclassification_matrix.json'
if not matrix_file.exists():
    print("❌ 重分类矩阵不存在，请先运行 blind_reclassification.py")
    exit(1)

matrix_data = json.load(open(matrix_file, 'r', encoding='utf-8'))
matrix = matrix_data['matrix']

# 需要处理的问题
issues = {
    'needs_reclassification': [],
    'pending_verification': [],
    'length_warning': []
}

for item in matrix:
    eid = item['evidence_id']
    filepath = evidence_dir / f"{eid}.json"
    
    if item['reclassification_required']:
        issues['needs_reclassification'].append(eid)
    
    if item['source_verification_status'] == 'PENDING':
        issues['pending_verification'].append(eid)
    
    if item['text_length'] > 150 and item['source_verification_status'] == 'CLAIMED_DIRECT':
        issues['length_warning'].append(eid)

print(f"\n【问题统计】")
print(f"   需要重分类: {len(issues['needs_reclassification'])}条")
print(f"   待核验来源: {len(issues['pending_verification'])}条")
print(f"   长度警告: {len(issues['length_warning'])}条")

# 处理长度警告 - 降级为 PENDING_VERIFICATION
print(f"\n【处理长度警告】")
for eid in issues['length_warning']:
    filepath = evidence_dir / f"{eid}.json"
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查是否已经是 PENDING
        if data.get('source_fidelity') != 'PENDING_VERIFICATION':
            data['source_fidelity'] = 'PENDING_VERIFICATION'
            data['certainty'] = 'MEDIUM'
            data['verification_status'] = 'SOURCE_VERIFICATION_REQUIRED'
            data['notes'] = data.get('notes', '') + ' | ⚠️ 原文长度较长，需最终文献核验'
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"   ✅ {eid}: DIRECT/HIGH → PENDING_VERIFICATION/MEDIUM")

# 生成核验报告
report = {
    'verification_date': datetime.now().isoformat(),
    'total_evidence': len(matrix),
    'issues': {
        'needs_reclassification': issues['needs_reclassification'],
        'pending_verification': issues['pending_verification'],
        'length_warning': issues['length_warning']
    },
    'summary': {
        'needs_action': len(issues['needs_reclassification']),
        'already_pending': len(issues['pending_verification']),
        'just_downgraded': len(issues['length_warning'])
    }
}

report_file = evidence_dir / 'source_verification_report.json'
with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\n✅ 核验报告已保存: {report_file.name}")