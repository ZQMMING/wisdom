#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3C: Mapping Integrity Verification
验证Feature/Signal Mapping修复后的完整性
"""

import json
from pathlib import Path
from collections import defaultdict, Counter

def main():
    evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')
    canonical_dir = Path('C:/Users/wisdom/wisdom/data/canonical')
    
    print("=" * 70)
    print("Phase 3C: Mapping Integrity Verification")
    print("=" * 70)
    print()
    
    errors = []
    
    # 1. 验证Signal分布
    signal_counts = Counter()
    classic_signal_matrix = defaultdict(lambda: Counter())
    total = 0
    
    for f in evidence_dir.rglob('E-*.json'):
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            
            total += 1
            signal = data.get('signal_type', 'GENERAL')
            classic = data.get('authority_type', 'UNKNOWN')
            
            signal_counts[signal] += 1
            classic_signal_matrix[classic][signal] += 1
        except:
            pass
    
    print("📊 Evidence Signal分布:")
    for sig, count in sorted(signal_counts.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        print(f"   {sig}: {count} ({pct:.1f}%)")
    print()
    
    # 验证：GENERAL应该<10%
    general_count = signal_counts.get('GENERAL', 0)
    if general_count / total > 0.1:
        errors.append(f"GENERAL比例过高: {general_count}/{total} ({general_count/total*100:.1f}%)")
    else:
        print(f"✅ GENERAL比例正常: {general_count}/{total} ({general_count/total*100:.1f}%)")
    
    # 2. 验证Classic×Signal矩阵合理性
    print()
    print("📈 Classic×Signal矩阵:")
    for classic in sorted(classic_signal_matrix.keys()):
        signals = classic_signal_matrix[classic]
        total_classic = sum(signals.values())
        
        # 验证QTBJ应该主要是CLIMATE和PATTERN
        if classic == 'CLIMATE_SEASONAL':
            climate_pattern = signals.get('CLIMATE', 0) + signals.get('PATTERN', 0)
            if climate_pattern / total_classic < 0.5:
                errors.append(f"QTBJ的CLIMATE+PATTERN比例过低: {climate_pattern}/{total_classic}")
            else:
                print(f"   {classic}: {total_classic} (CLIMATE+PATTERN={climate_pattern} ✓)")
        
        # 验证PZZQ应该主要是PATTERN
        elif classic == 'PATTERN_OPERATIONAL':
            pattern_count = signals.get('PATTERN', 0)
            if pattern_count / total_classic < 0.5:
                errors.append(f"PZZQ的PATTERN比例过低: {pattern_count}/{total_classic}")
            else:
                print(f"   {classic}: {total_classic} (PATTERN={pattern_count} ✓)")
        
        # 验证DTS应该主要是STRENGTH
        elif classic == 'PRINCIPLE_CONSTRAINT':
            strength_count = signals.get('STRENGTH', 0)
            if strength_count / total_classic < 0.1:
                errors.append(f"DTS的STRENGTH比例过低: {strength_count}/{total_classic}")
            else:
                print(f"   {classic}: {total_classic} (STRENGTH={strength_count} ✓)")
    
    print()
    
    # 3. 验证TEN_GOD是Canonical Derived
    mapping_path = evidence_dir.parent / 'feature_signal_mapping.json'
    with open(mapping_path, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    
    ten_god_feature = mapping.get('signal_features', {}).get('TEN_GOD', {})
    if ten_god_feature.get('status') == 'CANONICAL_DERIVED':
        print("✅ TEN_GOD已降级为Canonical Derived Signal")
    else:
        errors.append("TEN_GOD未正确标记为CANONICAL_DERIVED")
    
    # 4. 验证STRENGTH是Canonical + Semantic
    strength_feature = mapping.get('signal_features', {}).get('STRENGTH', {})
    if strength_feature.get('status') == 'CANONICAL_WITH_SEMANTIC':
        print("✅ STRENGTH已正确设置为Canonical + Semantic")
    else:
        errors.append("STRENGTH未正确标记为CANONICAL_WITH_SEMANTIC")
    
    # 5. 验证Alias Mapping
    alias_path = canonical_dir / 'alias_mapping.json'
    with open(alias_path, 'r', encoding='utf-8') as f:
        alias_map = json.load(f)
    
    expected_aliases = {'QTB': 'QTBJ', 'ZIPI': 'PZZQ', 'SAN_': 'SMTH'}
    for src, expected in expected_aliases.items():
        if src in alias_map['mappings']:
            actual = alias_map['mappings'][src].get('maps_to', '')
            if actual == expected:
                print(f"✅ Alias {src} → {expected} 正确")
            else:
                errors.append(f"Alias {src} 映射错误: 期望{expected}, 实际{actual}")
        else:
            errors.append(f"缺少Alias: {src}")
    
    print()
    
    # 最终结论
    if errors:
        print("❌ 验证失败:")
        for e in errors:
            print(f"   - {e}")
        return False
    else:
        print("✅ Phase 3C 验证通过")
        print()
        print("总结:")
        print(f"  - 总证据数: {total}")
        print(f"  - GENERAL比例: {general_count}/{total} ({general_count/total*100:.1f}%)")
        print(f"  - TEN_GOD: Canonical Derived ✓")
        print(f"  - STRENGTH: Canonical + Semantic ✓")
        print(f"  - Alias Mapping: 3个正确 ✓")
        return True

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)