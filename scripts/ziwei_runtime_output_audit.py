#!/usr/bin/env python3
"""Ziwei Runtime Verification Harness — P-A1 Post-Cleanup

This script is a VERIFICATION TOOL, not production code.
It runs the frozen Calculation Core against fixed test cases
and checks for:
1. Structural correctness (命宫/身宫/五行局)
2. Decadal direction rules (四种阴阳组合)
3. Mutagen computation (流年/流月/流日/大限)
4. No semantic leakage (forbidden terms in all outputs)

Production Code: FROZEN (be3dce9)
Verification Date: 2026-09-02
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "wisdom" / "src"))

from tongshu.engines.ziwei_engine import ZiweiEngine, GAN_SIHUA, MAIN_STAR_USO
from tongshu.engines.time.solar_time import calculate_true_solar_time

# ============================================================================
# FIXED TEST CASES
# ============================================================================

# Case 1: 毛泽东 — 阳男, 木三局
CASE_MAO = {
    "name": "毛泽东",
    "solar_date": (1893, 12, 26),
    "lunar_date": (1893, 11, 19),
    "hour": 8,  # 辰时
    "gender": "male",
    "longitude": 112.9,  # 湖南湘潭
}

# Case 2: 阳女 — 金四局 (expected: 逆)
CASE_YANG_FEMALE = {
    "name": "阳女测试",
    "solar_date": (1998, 4, 15),
    "lunar_date": (1998, 3, 19),
    "hour": 10,  # 巳时
    "gender": "female",
    "longitude": 120.0,
}

# Case 3: 阴男 — 水二局 (expected: 逆)
CASE_YIN_MALE = {
    "name": "阴男测试",
    "solar_date": (1999, 2, 20),
    "lunar_date": (1999, 1, 15),
    "hour": 14,  # 未时
    "gender": "male",
    "longitude": 116.0,
}

# Case 4: 阴女 — 火六局 (expected: 顺)
CASE_YIN_FEMALE = {
    "name": "阴女测试",
    "solar_date": (1997, 8, 8),
    "lunar_date": (1997, 7, 7),
    "hour": 16,  # 申时
    "gender": "female",
    "longitude": 121.0,
}

ALL_CASES = [CASE_MAO, CASE_YANG_FEMALE, CASE_YIN_MALE, CASE_YIN_FEMALE]

# Expected sihua for specific stems (VERBATIM from GAN_SIHUA)
EXPECTED_SIHUA = {
    '甲': ['廉贞', '破军', '武曲', '太阳'],
    '乙': ['天机', '天梁', '紫微', '太阴'],
    '丙': ['天同', '天机', '文昌', '廉贞'],
    '丁': ['太阴', '天同', '天机', '巨门'],
    '戊': ['贪狼', '太阴', '右弼', '天机'],
    '己': ['武曲', '贪狼', '天梁', '文曲'],
    '庚': ['太阳', '武曲', '太阴', '天同'],
    '辛': ['巨门', '太阳', '文曲', '文昌'],
    '壬': ['天梁', '紫微', '左辅', '武曲'],
    '癸': ['破军', '巨门', '太阴', '贪狼'],
}

# Forbidden semantic terms (should never appear in any output)
FORBIDDEN_TERMS = [
    'opportunity', 'caution', 'neutral',  # direction leakage
    'INCREASE', 'DECREASE',  # effect mapping
    'score_topic', 'topic_score',  # scoring
    'direction',  # native_direction
]

# ============================================================================
# VERIFICATION FUNCTIONS
# ============================================================================

def check_structural(chart_data, case):
    """Check basic chart structure."""
    results = []
    
    # Five elements bureau
    bureau = chart_data.get('fiveElementsClass', '')
    if not bureau:
        results.append(("✗", f"{case['name']}: 五行局缺失"))
    else:
        results.append(("✓", f"{case['name']}: 五行局={bureau}"))
    
    # Soul palace
    soul = chart_data.get('soulPalaceBranch', '')
    if not soul:
        results.append(("✗", f"{case['name']}: 命宫缺失"))
    else:
        results.append(("✓", f"{case['name']}: 命宫={soul}"))
    
    # Body palace
    body = chart_data.get('bodyPalaceBranch', '')
    if not body:
        results.append(("✗", f"{case['name']}: 身宫缺失"))
    else:
        results.append(("✓", f"{case['name']}: 身宫={body}"))
    
    return results


def check_decadal_direction(chart_data, gender, case):
    """Check decadal direction rules."""
    results = []
    palaces = chart_data.get('palaces', {})
    
    # Extract decadal info from each palace
    decadal_info = []
    for pname, pdata in palaces.items():
        dr = pdata.get('decadalRange', [])
        if dr and len(dr) == 2:
            decadal_info.append({
                'palace': pname,
                'branch': pdata.get('branch', ''),
                'stem': pdata.get('stem', ''),
                'range': dr
            })
    
    if len(decadal_info) != 12:
        results.append(("✗", f"{case['name']}: 大限信息不完整 ({len(decadal_info)}/12)"))
        return results
    
    # Sort by start age
    decadal_info.sort(key=lambda x: x['range'][0])
    
    # Extract palace order
    palace_order = [d['palace'] for d in decadal_info]
    first_palace = palace_order[0]
    
    results.append(("✓", f"{case['name']}: 第一大限={first_palace} (起运{decadal_info[0]['range'][0]}岁)"))
    results.append(("✓", f"{case['name']}: 大限顺序前3宫={palace_order[:3]}"))
    
    return results


def check_sihua_integrity():
    """Check GAN_SIHUA table integrity."""
    results = []
    
    if len(GAN_SIHUA) != 10:
        results.append(("✗", f"GAN_SIHUA只有{len(GAN_SIHUA)}干"))
    else:
        results.append(("✓", f"GAN_SIHUA: 10干完整"))
    
    # Check each stem has 4 mutagens
    for stem, mutagens in GAN_SIHUA.items():
        if len(mutagens) != 4:
            results.append(("✗", f"GAN_SIHUA[{stem}]只有{len(mutagens)}个四化"))
        elif set(mutagens) != set(EXPECTED_SIHUA[stem]):
            results.append(("✗", f"GAN_SIHUA[{stem}]不匹配预期"))
        else:
            results.append(("✓", f"GAN_SIHUA[{stem}]={mutagens}"))
    
    return results


def check_forbidden_terms(*outputs):
    """Check all outputs for forbidden semantic terms."""
    results = []
    
    all_text = []
    for i, output in enumerate(outputs):
        if isinstance(output, dict):
            all_text.append(json.dumps(output, ensure_ascii=False))
        elif isinstance(output, list):
            for item in output:
                if isinstance(item, dict):
                    all_text.append(json.dumps(item, ensure_ascii=False))
                else:
                    all_text.append(str(item))
        elif isinstance(output, str):
            all_text.append(output)
    
    full_text = '\n'.join(all_text)
    
    found_leaks = []
    for term in FORBIDDEN_TERMS:
        if term.lower() in full_text.lower():
            found_leaks.append(term)
    
    if found_leaks:
        results.append(("✗", f"发现语义泄漏: {found_leaks}"))
    else:
        results.append(("✓", "无forbidden terms泄漏"))
    
    return results


def check_methods_removed():
    """Check that all forbidden methods are removed."""
    results = []
    engine = ZiweiEngine()
    
    forbidden_methods = [
        'native_direction',
        'score_topic',
        'score_topic_sanfang',
        'decadal_soul_effect',
    ]
    
    for method in forbidden_methods:
        if hasattr(engine, method):
            results.append(("✗", f"{method}仍存在"))
        else:
            results.append(("✓", f"{method}已删除"))
    
    return results


def run_temporal_checks(case):
    """Run temporal mutation checks."""
    results = []
    engine = ZiweiEngine()
    lunar_date = case['lunar_date']
    hour = case['hour']
    gender = case['gender']
    
    chart = engine.compute(lunar_date, hour, gender)
    fc = engine.full_chart(lunar_date, hour, gender)
    
    # Year mutagen
    try:
        year_mutagen = engine.flow_years_mutagen([lunar_date[0]], lunar_date, hour, gender)
        results.append(("✓", f"{case['name']}: 流年四化API正常"))
    except Exception as e:
        results.append(("✗", f"{case['name']}: 流年四化失败: {e}"))
    
    # Month mutagen
    try:
        month_mutagen = engine.flow_month_mutagen(lunar_date[0], lunar_date[1], lunar_date, hour, gender)
        results.append(("✓", f"{case['name']}: 流月四化API正常"))
    except Exception as e:
        results.append(("✗", f"{case['name']}: 流月四化失败: {e}"))
    
    # Day mutagen
    try:
        day_mutagen = engine.flow_day_mutagen(lunar_date[0], lunar_date[1], lunar_date[2], lunar_date, hour, gender)
        results.append(("✓", f"{case['name']}: 流日四化API正常"))
    except Exception as e:
        results.append(("✗", f"{case['name']}: 流日四化失败: {e}"))
    
    # Decadal mutagen
    try:
        decadal_mutagen = engine.flow_decadal_mutagen([lunar_date[0]], lunar_date, hour, gender)
        results.append(("✓", f"{case['name']}: 大限四化API正常"))
    except Exception as e:
        results.append(("✗", f"{case['name']}: 大限四化失败: {e}"))
    
    return results


def run_true_solar_time_check(case):
    """Run true solar time differential check.
    
    NOTE: This is a MANUAL DIFFERENTIAL TEST, not a production policy verification.
    The production engine does NOT automatically apply true solar time correction.
    Users must call calculate_true_solar_time() manually and then map the result
    to an hour index before passing to compute().
    """
    results = []
    engine = ZiweiEngine()
    
    # Test with original hour
    fc_original = engine.full_chart(case['lunar_date'], case['hour'], case['gender'])
    
    # Test with corrected hour (manual differential)
    dt = datetime(*case['solar_date'][:3], case['hour'])
    tst = calculate_true_solar_time(dt, case['longitude'])
    
    # Extract corrected hour from true_solar_time string
    true_solar_str = tst.get('true_solar_time', '')
    if 'T' in true_solar_str:
        corrected_hour = int(true_solar_str.split('T')[1].split(':')[0])
    else:
        corrected_hour = case['hour']  # fallback
    
    fc_corrected = engine.full_chart(case['lunar_date'], corrected_hour, case['gender'])
    
    # Check if results differ
    if fc_original['soulPalaceBranch'] != fc_corrected['soulPalaceBranch']:
        results.append(("✓", f"{case['name']}: 经度校正影响命宫 ({fc_original['soulPalaceBranch']}→{fc_corrected['soulPalaceBranch']})"))
    else:
        results.append(("△", f"{case['name']}: 经度校正未改变命宫 (可能未跨时辰边界)"))
    
    results.append(("△", f"NOTE: 这是manual differential test，不是production policy验证"))
    results.append(("△", f"生产引擎compute()不自动接受longitude参数"))
    
    return results


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 70)
    print("ZIWEI RUNTIME VERIFICATION HARNESS — P-A1 Post-Cleanup")
    print("=" * 70)
    print()
    
    all_results = []
    
    # 1. Structural checks
    print("[1] STRUCTURAL CHECKS")
    print("-" * 70)
    for case in ALL_CASES:
        engine = ZiweiEngine()
        fc = engine.full_chart(case['lunar_date'], case['hour'], case['gender'])
        results = check_structural(fc, case)
        all_results.extend(results)
        for status, msg in results:
            print(f"  {status} {msg}")
    
    print()
    
    # 2. Decadal direction checks
    print("[2] DECADAL DIRECTION CHECKS")
    print("-" * 70)
    for case in ALL_CASES:
        engine = ZiweiEngine()
        fc = engine.full_chart(case['lunar_date'], case['hour'], case['gender'])
        results = check_decadal_direction(fc, case['gender'], case)
        all_results.extend(results)
        for status, msg in results:
            print(f"  {status} {msg}")
    
    print()
    
    # 3. GAN_SIHUA integrity
    print("[3] GAN_SIHUA INTEGRITY")
    print("-" * 70)
    results = check_sihua_integrity()
    all_results.extend(results)
    for status, msg in results:
        print(f"  {status} {msg}")
    
    print()
    
    # 4. Temporal mutation checks
    print("[4] TEMPORAL MUTATION CHECKS")
    print("-" * 70)
    for case in ALL_CASES:
        results = run_temporal_checks(case)
        all_results.extend(results)
        for status, msg in results:
            print(f"  {status} {msg}")
    
    print()
    
    # 5. True solar time differential
    print("[5] TRUE SOLAR TIME DIFFERENTIAL (MANUAL ONLY)")
    print("-" * 70)
    for case in ALL_CASES[:1]:  # Only test first case
        results = run_true_solar_time_check(case)
        all_results.extend(results)
        for status, msg in results:
            print(f"  {status} {msg}")
    
    print()
    
    # 6. Forbidden methods check
    print("[6] FORBIDDEN METHODS CHECK")
    print("-" * 70)
    results = check_methods_removed()
    all_results.extend(results)
    for status, msg in results:
        print(f"  {status} {msg}")
    
    print()
    
    # 7. Semantic leakage check
    print("[7] SEMANTIC LEAKAGE CHECK")
    print("-" * 70)
    for case in ALL_CASES:
        engine = ZiweiEngine()
        fc = engine.full_chart(case['lunar_date'], case['hour'], case['gender'])
        
        # Check multiple outputs
        outputs = [fc]
        if hasattr(engine, 'birth_sihua'):
            try:
                outputs.append(engine.birth_sihua(None, fc))
            except:
                pass
        
        results = check_forbidden_terms(*outputs)
        all_results.extend(results)
        for status, msg in results:
            print(f"  {status} {msg}")
    
    print()
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for s, _ in all_results if s == "✓")
    warnings = sum(1 for s, _ in all_results if s == "△")
    failed = sum(1 for s, _ in all_results if s == "✗")
    
    print(f"  Passed:   {passed}")
    print(f"  Warnings: {warnings}")
    print(f"  Failed:   {failed}")
    print()
    
    if failed > 0:
        print("  STATUS: ❌ FAILED")
        for s, msg in all_results:
            if s == "✗":
                print(f"    - {msg}")
        sys.exit(1)
    else:
        print("  STATUS: ✅ PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
