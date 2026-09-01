#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3C Enhanced Verification: 完整的证据一致性审计
验证所有字段的一致性和完整性
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

def main():
    evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')
    canonical_dir = Path('C:/Users/wisdom/wisdom/data/canonical')
    
    print("=" * 70)
    print("Phase 3C Enhanced Verification")
    print("=" * 70)
    print()
    
    errors = []
    warnings = []
    
    # ===== 1. Signal Distribution =====
    signal_counts = Counter()
    classic_signal_matrix = defaultdict(Counter)
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
        except Exception as e:
            errors.append(f"读取 {f.name} 失败: {e}")
    
    print("📊 Evidence Signal分布:")
    for sig, count in sorted(signal_counts.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        print(f"   {sig}: {count} ({pct:.1f}%)")
    print()
    
    general_count = signal_counts.get('GENERAL', 0)
    if general_count / total > 0.1:
        errors.append(f"GENERAL比例过高: {general_count}/{total} ({general_count/total*100:.1f}%)")
    else:
        print(f"✅ GENERAL比例正常: {general_count}/{total} ({general_count/total*100:.1f}%)")
    
    # ===== 2. Field Consistency Audit =====
    print()
    print("🔍 Field Consistency Audit:")
    
    signal_type_conflicts = 0
    missing_semantic_features = 0
    invalid_signal_types = []
    authority_signal_mismatches = 0
    
    AUTHORITY_SIGNAL_MAP = {
        'CLIMATE_SEASONAL': {'CLIMATE', 'PATTERN', 'FIVE_ELEMENTS', 'STRENGTH', 'GENERAL'},
        'PATTERN_OPERATIONAL': {'PATTERN', 'CLIMATE', 'GENERAL'},
        'DAYMASTER_STRUCTURE': {'STRENGTH', 'PATTERN', 'CLIMATE', 'FIVE_ELEMENTS', 'GENERAL'},
        'PRINCIPLE_CONSTRAINT': {'STRENGTH', 'CLIMATE', 'PATTERN', 'FIVE_ELEMENTS', 'GENERAL'},
        'ELEMENT_IDENTITY': {'FIVE_ELEMENTS', 'CLIMATE', 'PATTERN', 'GENERAL'},
        'COMPLEMENTARY': {'GENERAL', 'PATTERN', 'CLIMATE'},
        'CONTEXTUAL': {'GENERAL'}
    }
    
    for f in evidence_dir.rglob('E-*.json'):
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            
            signal_type = data.get('signal_type', 'GENERAL')
            semantic_features = data.get('semantic_features', {})
            authority = data.get('authority_type', 'UNKNOWN')
            
            # Check 1: signal_type vs semantic_features.signal
            if semantic_features and 'signal' in semantic_features:
                sf_signal = semantic_features['signal']
                if sf_signal != signal_type:
                    signal_type_conflicts += 1
            
            # Check 2: feature_mapped → semantic_features
            if data.get('feature_mapped') and not semantic_features:
                missing_semantic_features += 1
            
            # Check 3: Invalid signal_type
            valid_signals = {'GENERAL', 'STRENGTH', 'CLIMATE', 'PATTERN', 'TEN_GOD', 'FIVE_ELEMENTS', 'YIN_YANG'}
            if signal_type not in valid_signals:
                invalid_signal_types.append((f.name, signal_type))
            
            # Check 4: Authority × Signal
            expected = AUTHORITY_SIGNAL_MAP.get(authority, {'GENERAL'})
            if signal_type not in expected:
                authority_signal_mismatches += 1
                
        except Exception as e:
            errors.append(f"验证 {f.name} 失败: {e}")
    
    print(f"   signal_type vs semantic_features.signal 冲突: {signal_type_conflicts}")
    print(f"   feature_mapped 但缺少 semantic_features: {missing_semantic_features}")
    print(f"   无效 signal_type: {len(invalid_signal_types)}")
    print(f"   Authority×Signal 不匹配: {authority_signal_mismatches}")
    
    if signal_type_conflicts > 0:
        errors.append(f"存在 {signal_type_conflicts} 条 signal_type 与 semantic_features.signal 冲突")
    if missing_semantic_features > 0:
        errors.append(f"存在 {missing_semantic_features} 条 feature_mapped 但缺少 semantic_features")
    if invalid_signal_types:
        errors.append(f"存在 {len(invalid_signal_types)} 条无效 signal_type")
    if authority_signal_mismatches > 0:
        errors.append(f"存在 {authority_signal_mismatches} 条 Authority×Signal 不匹配")
    
    if signal_type_conflicts == 0 and missing_semantic_features == 0 and not invalid_signal_types and authority_signal_mismatches == 0:
        print("✅ 所有字段一致性检查通过")
    print()
    
    # ===== 3. Classic×Signal Matrix =====
    print("📈 Classic×Signal Matrix:")
    
    qtbj = classic_signal_matrix.get('CLIMATE_SEASONAL', {})
    qtbj_total = sum(qtbj.values())
    qtbj_climate_pattern = qtbj.get('CLIMATE', 0) + qtbj.get('PATTERN', 0)
    if qtbj_total > 0 and qtbj_climate_pattern / qtbj_total < 0.5:
        errors.append(f"QTBJ CLIMATE+PATTERN比例过低: {qtbj_climate_pattern}/{qtbj_total}")
    else:
        print(f"   CLIMATE_SEASONAL: {qtbj_total} (CLIMATE+PATTERN={qtbj_climate_pattern} ✓)")
    
    pzzq = classic_signal_matrix.get('PATTERN_OPERATIONAL', {})
    pzzq_total = sum(pzzq.values())
    pzzq_pattern = pzzq.get('PATTERN', 0)
    if pzzq_total > 0 and pzzq_pattern / pzzq_total < 0.5:
        errors.append(f"PZZQ PATTERN比例过低: {pzzq_pattern}/{pzzq_total}")
    else:
        print(f"   PATTERN_OPERATIONAL: {pzzq_total} (PATTERN={pzzq_pattern} ✓)")
    
    dts = classic_signal_matrix.get('PRINCIPLE_CONSTRAINT', {})
    dts_total = sum(dts.values())
    dts_strength = dts.get('STRENGTH', 0)
    if dts_total > 0 and dts_strength / dts_total < 0.1:
        errors.append(f"DTS STRENGTH比例过低: {dts_strength}/{dts_total}")
    else:
        print(f"   PRINCIPLE_CONSTRAINT: {dts_total} (STRENGTH={dts_strength} ✓)")
    print()
    
    # ===== 4. Mapping Schema =====
    print("🔧 Mapping Schema Verification:")
    
    mapping_path = evidence_dir.parent / 'feature_signal_mapping.json'
    with open(mapping_path, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    
    ten_god = mapping.get('signal_features', {}).get('TEN_GOD', {})
    if ten_god.get('status') == 'CANONICAL_DERIVED':
        print("   TEN_GOD: Canonical Derived ✅")
    else:
        errors.append(f"TEN_GOD status错误: {ten_god.get('status')}")
    
    strength = mapping.get('signal_features', {}).get('STRENGTH', {})
    if strength.get('status') == 'CANONICAL_WITH_SEMANTIC':
        print("   STRENGTH: Canonical + Semantic ✅")
    else:
        errors.append(f"STRENGTH status错误: {strength.get('status')}")
    print()
    
    # ===== 5. Alias Mapping =====
    print("🔄 Alias Canonicalization:")
    
    alias_path = canonical_dir / 'alias_mapping.json'
    with open(alias_path, 'r', encoding='utf-8') as f:
        alias_map = json.load(f)
    
    expected_aliases = {'QTB': 'QTBJ', 'ZIPI': 'PZZQ', 'SAN_': 'SMTH'}
    for src, expected in expected_aliases.items():
        actual = alias_map['mappings'].get(src, {}).get('maps_to', '')
        if actual == expected:
            print(f"   {src} → {expected} ✅")
        else:
            errors.append(f"Alias {src}映射错误: 期望{expected}, 实际{actual}")
    print()
    
    # ===== 6. YIN_YANG Primitives =====
    print("📜 YIN_YANG Primitives:")
    
    with open(canonical_dir / 'primitive_registry.json', 'r', encoding='utf-8') as f:
        primitives = json.load(f)
    
    yinyang_prims = [p for p in primitives if any(k in p.get('name', '') for k in ['阴阳', '阳支', '阴支'])]
    active_count = sum(1 for p in yinyang_prims if p.get('registry_status') == 'ACTIVE')
    full_auth = sum(1 for p in yinyang_prims if p.get('production_authorization') == 'FULL')
    
    if len(yinyang_prims) == 7 and active_count == 7 and full_auth == 7:
        print(f"   {len(yinyang_prims)}条全部 ACTIVE + FULL ✅")
    else:
        errors.append(f"YIN_YANG Primitives不完整: {len(yinyang_prims)}条, {active_count} ACTIVE, {full_auth} FULL")
    print()
    
    # ===== 7. Summary =====
    print("=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    print()
    print(f"Total evidence: {total}")
    print(f"GENERAL: {general_count} ({general_count/total*100:.1f}%)")
    print(f"Field consistency errors: {signal_type_conflicts + missing_semantic_features + len(invalid_signal_types) + authority_signal_mismatches}")
    print(f"Validation errors: {len(errors)}")
    print()
    
    if errors:
        print("❌ Verification FAILED:")
        for e in errors:
            print(f"   - {e}")
        return False
    else:
        print("✅ Phase 3C Enhanced Verification PASSED")
        print()
        print("All checks passed:")
        print(f"  - Signal distribution: GENERAL < 10% ✅")
        print(f"  - Field consistency: 0 conflicts ✅")
        print(f"  - Classic×Signal matrix:合理 ✅")
        print(f"  - TEN_GOD: Canonical Derived ✅")
        print(f"  - STRENGTH: Canonical + Semantic ✅")
        print(f"  - Alias mapping: 3/3 correct ✅")
        print(f"  - YIN_YANG primitives: 7/7 ACTIVE+FULL ✅")
        return True

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)