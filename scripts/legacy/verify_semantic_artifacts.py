#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Artifact Integrity Verification for Semantic Normalization
Verifies that registry, report, and evidence files are consistent.
"""

import json
from pathlib import Path
from collections import Counter

def verify():
    evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')
    
    # 1. Load registry
    registry_path = evidence_dir / 'semantic_authority_registry.json'
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    # 2. Load report
    report_path = evidence_dir / 'semantic_normalization_report.json'
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    # 3. Count evidence files
    total_files = 0
    classified_files = 0
    by_authority = Counter()
    
    for f in evidence_dir.rglob('E-*.json'):
        total_files += 1
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            if data.get('authority_type'):
                classified_files += 1
                by_authority[data['authority_type']] += 1
        except:
            pass
    
    # 4. Verify consistency
    errors = []
    
    # Check registry total
    if registry['_metadata']['total_evidence'] != total_files:
        errors.append(f"Registry total mismatch: {registry['_metadata']['total_evidence']} vs {total_files}")
    
    # Check report total
    if report['total_evidence'] != total_files:
        errors.append(f"Report total mismatch: {report['total_evidence']} vs {total_files}")
    
    # Check classified count
    if classified_files != total_files:
        errors.append(f"Not all files classified: {classified_files}/{total_files}")
    
    # Check expected classic counts
    expected = {'DTS': 50, 'QTBJ': 1234, 'PZZQ': 10, 'YHZP': 121, 'SMTH': 12}
    for classic, expected_count in expected.items():
        actual = registry['authorities'].get(classic, {}).get('actual_count', 0)
        if actual != expected_count:
            errors.append(f"{classic} count mismatch: registry={actual}, expected={expected_count}")
    
    # 5. Print results
    print("=" * 60)
    print("Artifact Integrity Verification")
    print("=" * 60)
    print(f"Total evidence files: {total_files}")
    print(f"Classified files: {classified_files}")
    print(f"Coverage: {classified_files/total_files*100:.1f}%")
    print()
    print("Registry authorities:")
    for prefix, info in registry['authorities'].items():
        print(f"  {prefix}: {info.get('actual_count', 0)} ({info.get('authority', 'N/A')})")
    print()
    print("Evidence by authority:")
    for auth, count in sorted(by_authority.items()):
        print(f"  {auth}: {count}")
    print()
    
    if errors:
        print("❌ VERIFICATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print("✅ VERIFICATION PASSED - Artifact Integrity OK")
        return True

if __name__ == '__main__':
    success = verify()
    exit(0 if success else 1)