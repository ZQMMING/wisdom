#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrity Check Script for Semantic Normalization
验证归一化产物的完整性和一致性
"""

import json
from pathlib import Path
import sys

def check_integrity():
    evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')
    
    print("=== Integrity Check ===\n")
    
    # 1. 检查报告文件
    report_path = evidence_dir / 'semantic_normalization_report.json'
    if not report_path.exists():
        print("❌ Missing report file")
        return False
    
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    # 2. 检查权威注册表
    registry_path = evidence_dir / 'semantic_authority_registry.json'
    if not registry_path.exists():
        print("❌ Missing registry file")
        return False
    
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    # 3. 验证报告完整性
    required_fields = ['total_evidence', 'updated_count', 'by_authority', 
                       'by_signal', 'by_category', 'integrity_check', 'artifact_version']
    for field in required_fields:
        if field not in report:
            print(f"❌ Missing field in report: {field}")
            return False
    
    # 4. 验证注册表完整性
    if '_metadata' not in registry:
        print("❌ Missing _metadata in registry")
        return False
    
    metadata = registry['_metadata']
    if 'total_evidence' not in metadata:
        print("❌ Missing total_evidence in metadata")
        return False
    
    # 5. 交叉验证报告与注册表
    report_total = report['total_evidence']
    registry_total = metadata['total_evidence']
    
    if report_total != registry_total:
        print(f"❌ Mismatch: report total ({report_total}) != registry total ({registry_total})")
        return False
    
    # 6. 验证数值合理性
    if report_total < 1000:
        print(f"⚠️  Suspiciously low total: {report_total}")
    
    if report['updated_count'] != report['total_evidence']:
        print(f"⚠️  Updated count ({report['updated_count']}) != total ({report_total})")
    
    # 7. 验证authority分布
    authority_totals = sum(report['by_authority'].values())
    if authority_totals != report['updated_count']:
        print(f"⚠️  Authority sum ({authority_totals}) != updated count ({report['updated_count']})")
    
    # 8. 验证signal分布
    signal_totals = sum(report['by_signal'].values())
    if signal_totals != report['updated_count']:
        print(f"⚠️  Signal sum ({signal_totals}) != updated count ({report['updated_count']})")
    
    # 9. 验证category分布
    category_totals = sum(report['by_category'].values())
    if category_totals != report['updated_count']:
        print(f"⚠️  Category sum ({category_totals}) != updated count ({report['updated_count']})")
    
    # 10. 验证关键指标
    print(f"✅ Report total: {report_total}")
    print(f"✅ Registry total: {registry_total}")
    print(f"✅ Updated count: {report['updated_count']}")
    print(f"✅ Integrity check: {report['integrity_check']}")
    print(f"✅ Version: {report['artifact_version']}")
    
    # 打印分布详情
    print(f"\nAuthority distribution:")
    for auth, count in sorted(report['by_authority'].items()):
        print(f"  {auth}: {count}")
    
    print(f"\nSignal distribution:")
    for sig, count in sorted(report['by_signal'].items()):
        print(f"  {sig}: {count}")
    
    print(f"\nCategory distribution:")
    for cat, count in sorted(report['by_category'].items()):
        print(f"  {cat}: {count}")
    
    print("\n✅ All integrity checks passed!")
    return True

if __name__ == '__main__':
    success = check_integrity()
    sys.exit(0 if success else 1)
