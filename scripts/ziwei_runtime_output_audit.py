#!/usr/bin/env python3
"""Ziwei Runtime Verification Harness — P-A1 Post-Cleanup (v2)

This script is a VERIFICATION TOOL, not production code.
It runs the frozen Calculation Core against fixed test cases
and checks for:
1. Structural correctness (命宫/身宫/五行局)
2. Decadal direction rules (四种阴阳组合) WITH EXPECTED ASSERTIONS
3. Temporal mutagen computation WITH EXPECTED VALUES
4. No semantic leakage in ALL API outputs

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
# FIXED TEST CASES WITH EXPECTED VALUES
# ============================================================================
# Expected values are OBSERVED from the current engine output.
# These serve as regression baselines — any change will be flagged.

# Case 1: 毛泽东 — 阴男, 木三局
CASE_MAO = {
    "name": "毛泽东",
    "solar_date": (1893, 12, 26),
    "lunar_date": (1893, 11, 19),
    "hour": 8,  # 辰时
    "gender": "male",
    "longitude": 112.9,  # 湖南湘潭
    "expected": {
        "soul_palace": "申",
        "body_palace": "辰",
        "five_elements": "木三局",
        "decadal_order": ['命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄', '迁移', '仆役', '官禄', '田宅', '福德', '父母'],
        "year_mutagen": {1893: ['破军', '巨门', '太阴', '贪狼']},
        "month_mutagen": ['破军', '巨门', '太阴', '贪狼'],
        "day_mutagen": ['太阳', '武曲', '太阴', '天同'],
        "decadal_mutagen": {1893: ['太阳', '武曲', '太阴', '天同']},
    }
}

# Case 2: 阳女 — 阳女, 水二局
CASE_YANG_FEMALE = {
    "name": "阳女测试",
    "solar_date": (1998, 4, 15),
    "lunar_date": (1998, 3, 19),
    "hour": 10,  # 巳时
    "gender": "female",
    "longitude": 120.0,
    "expected": {
        "soul_palace": "亥",
        "body_palace": "酉",
        "five_elements": "水二局",
        "decadal_order": ['命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄', '迁移', '仆役', '官禄', '田宅', '福德', '父母'],
        "year_mutagen": {1998: ['贪狼', '太阴', '右弼', '天机']},
        "month_mutagen": ['天机', '天梁', '紫微', '太阴'],
        "day_mutagen": ['天机', '天梁', '紫微', '太阴'],
        "decadal_mutagen": {1998: ['破军', '巨门', '太阴', '贪狼']},
    }
}

# Case 3: 阴男 — 阴男, 土五局
CASE_YIN_MALE = {
    "name": "阴男测试",
    "solar_date": (1999, 2, 20),
    "lunar_date": (1999, 1, 15),
    "hour": 14,  # 未时
    "gender": "male",
    "longitude": 116.0,
    "expected": {
        "soul_palace": "未",
        "body_palace": "酉",
        "five_elements": "土五局",
        "decadal_order": ['命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄', '迁移', '仆役', '官禄', '田宅', '福德', '父母'],
        "year_mutagen": {1999: ['武曲', '贪狼', '天梁', '文曲']},
        "month_mutagen": ['廉贞', '破军', '武曲', '太阳'],
        "day_mutagen": ['太阴', '天同', '天机', '巨门'],
        "decadal_mutagen": {1999: ['巨门', '太阳', '文曲', '文昌']},
    }
}

# Case 4: 阴女 — 阴女, 木三局
CASE_YIN_FEMALE = {
    "name": "阴女测试",
    "solar_date": (1997, 8, 8),
    "lunar_date": (1997, 7, 7),
    "hour": 16,  # 申时
    "gender": "female",
    "longitude": 121.0,
    "expected": {
        "soul_palace": "子",
        "body_palace": "辰",
        "five_elements": "木三局",
        "decadal_order": ['命宫', '父母', '福德', '田宅', '官禄', '仆役', '迁移', '疾厄', '财帛', '子女', '夫妻', '兄弟'],
        "year_mutagen": {1997: ['太阴', '天同', '天机', '巨门']},
        "month_mutagen": ['太阴', '天同', '天机', '巨门'],
        "day_mutagen": ['太阳', '武曲', '太阴', '天同'],
        "decadal_mutagen": {1997: ['天梁', '紫微', '左辅', '武曲']},
    }
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
    """Check basic chart structure with expected values."""
    results = []
    exp = case.get('expected', {})
    
    # Five elements bureau
    bureau = chart_data.get('fiveElementsClass', '')
    if not bureau:
        results.append(("✗", f"{case['name']}: 五行局缺失"))
    elif bureau != exp.get('five_elements', bureau):
        results.append(("✗", f"{case['name']}: 五行局期望={exp.get('five_elements')}, 实际={bureau}"))
    else:
        results.append(("✓", f"{case['name']}: 五行局={bureau}"))
    
    # Soul palace
    soul = chart_data.get('soulPalaceBranch', '')
    if not soul:
        results.append(("✗", f"{case['name']}: 命宫缺失"))
    elif soul != exp.get('soul_palace', soul):
        results.append(("✗", f"{case['name']}: 命宫期望={exp.get('soul_palace')}, 实际={soul}"))
    else:
        results.append(("✓", f"{case['name']}: 命宫={soul}"))
    
    # Body palace
    body = chart_data.get('bodyPalaceBranch', '')
    if not body:
        results.append(("✗", f"{case['name']}: 身宫缺失"))
    elif body != exp.get('body_palace', body):
        results.append(("✗", f"{case['name']}: 身宫期望={exp.get('body_palace')}, 实际={body}"))
    else:
        results.append(("✓", f"{case['name']}: 身宫={body}"))
    
    return results


def check_decadal_direction(chart_data, case):
    """Check decadal direction with EXPECTED order assertion."""
    results = []
    palaces = chart_data.get('palaces', {})
    exp = case.get('expected', {})
    
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
    first_range = decadal_info[0]['range']
    
    # ASSERT: Check first palace matches expected
    expected_first = exp.get('decadal_order', [first_palace])
    if expected_first[0] != first_palace:
        results.append(("✗", f"{case['name']}: 第一大限期望={expected_first[0]}, 实际={first_palace}"))
    else:
        results.append(("✓", f"{case['name']}: 第一大限={first_palace} 起运{first_range[0]}岁"))
    
    # ASSERT: Check full order matches expected
    if palace_order != expected_first:
        results.append(("✗", f"{case['name']}: 大限顺序不匹配"))
        results.append(("△", f"  期望: {expected_first}"))
        results.append(("△", f"  实际: {palace_order}"))
    else:
        results.append(("✓", f"{case['name']}: 大限顺序完整匹配"))
    
    return results


def check_sihua_integrity():
    """Check GAN_SIHUA table integrity."""
    results = []
    
    if len(GAN_SIHUA) != 10:
        results.append(("✗", f"GAN_SIHUA只有{len(GAN_SIHUA)}干"))
    else:
        results.append(("✓", f"GAN_SIHUA: 10干完整"))
    
    # Check each stem has 4 mutagens matching expected
    for stem, expected in EXPECTED_SIHUA.items():
        actual = GAN_SIHUA.get(stem, ())
        if actual != tuple(expected):
            results.append(("✗", f"GAN_SIHUA[{stem}]不匹配: 期望={expected}, 实际={actual}"))
        else:
            results.append(("✓", f"GAN_SIHUA[{stem}]={list(actual)}"))
    
    return results


def check_forbidden_terms(*outputs):
    """Check all outputs for forbidden semantic terms."""
    results = []
    
    all_text = []
    for i, output in enumerate(outputs):
        if output is None:
            continue
        if isinstance(output, dict):
            all_text.append(json.dumps(output, ensure_ascii=False))
        elif isinstance(output, list):
            for item in output:
                if isinstance(item, dict):
                    all_text.append(json.dumps(item, ensure_ascii=False))
                elif isinstance(item, list):
                    all_text.append(json.dumps(item, ensure_ascii=False))
                else:
                    all_text.append(str(item))
        elif isinstance(output, str):
            all_text.append(output)
        elif isinstance(output, tuple):
            all_text.append(str(output))
    
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
    """Run temporal mutation checks WITH EXPECTED VALUES."""
    results = []
    engine = ZiweiEngine()
    lunar_date = case['lunar_date']
    hour = case['hour']
    gender = case['gender']
    exp = case.get('expected', {})
    
    chart = engine.compute(lunar_date, hour, gender)
    fc = engine.full_chart(lunar_date, hour, gender)
    
    # Collect all outputs for forbidden term checking
    all_temporal_outputs = [fc]
    
    # Year mutagen — ASSERT expected value
    try:
        year_mutagen = engine.flow_years_mutagen([lunar_date[0]], lunar_date, hour, gender)
        all_temporal_outputs.append(year_mutagen)
        expected_ym = exp.get('year_mutagen', {})
        if year_mutagen != expected_ym:
            results.append(("✗", f"{case['name']}: 流年四化不匹配"))
            results.append(("△", f"  期望: {expected_ym}"))
            results.append(("△", f"  实际: {year_mutagen}"))
        else:
            results.append(("✓", f"{case['name']}: 流年四化={year_mutagen.get(lunar_date[0], 'N/A')}"))
    except Exception as e:
        results.append(("✗", f"{case['name']}: 流年四化失败: {e}"))
    
    # Month mutagen — ASSERT expected value
    try:
        month_mutagen = engine.flow_month_mutagen(lunar_date[0], lunar_date[1], lunar_date, hour, gender)
        all_temporal_outputs.append(month_mutagen)
        expected_mm = exp.get('month_mutagen', [])
        if month_mutagen != expected_mm:
            results.append(("✗", f"{case['name']}: 流月四化不匹配"))
            results.append(("△", f"  期望: {expected_mm}"))
            results.append(("△", f"  实际: {month_mutagen}"))
        else:
            results.append(("✓", f"{case['name']}: 流月四化={month_mutagen}"))
    except Exception as e:
        results.append(("✗", f"{case['name']}: 流月四化失败: {e}"))
    
    # Day mutagen — ASSERT expected value
    try:
        day_mutagen = engine.flow_day_mutagen(lunar_date[0], lunar_date[1], lunar_date[2], lunar_date, hour, gender)
        all_temporal_outputs.append(day_mutagen)
        expected_dm = exp.get('day_mutagen', [])
        if day_mutagen != expected_dm:
            results.append(("✗", f"{case['name']}: 流日四化不匹配"))
            results.append(("△", f"  期望: {expected_dm}"))
            results.append(("△", f"  实际: {day_mutagen}"))
        else:
            results.append(("✓", f"{case['name']}: 流日四化={day_mutagen}"))
    except Exception as e:
        results.append(("✗", f"{case['name']}: 流日四化失败: {e}"))
    
    # Decadal mutagen — ASSERT expected value
    try:
        decadal_mutagen = engine.flow_decadal_mutagen([lunar_date[0]], lunar_date, hour, gender)
        all_temporal_outputs.append(decadal_mutagen)
        expected_dcm = exp.get('decadal_mutagen', {})
        if decadal_mutagen != expected_dcm:
            results.append(("✗", f"{case['name']}: 大限四化不匹配"))
            results.append(("△", f"  期望: {expected_dcm}"))
            results.append(("△", f"  实际: {decadal_mutagen}"))
        else:
            results.append(("✓", f"{case['name']}: 大限四化={decadal_mutagen.get(lunar_date[0], 'N/A')}"))
    except Exception as e:
        results.append(("✗", f"{case['name']}: 大限四化失败: {e}"))
    
    # Store temporal outputs for forbidden term check (done in main)
    case['_temporal_outputs'] = all_temporal_outputs
    
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
    
    # ASSERT: Check if correction was applied
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
    print("ZIWEI RUNTIME VERIFICATION HARNESS — P-A1 Post-Cleanup (v2)")
    print("=" * 70)
    print()
    
    all_results = []
    all_temporal_outputs = []  # Collect all temporal outputs for leakage check
    
    # 1. Structural checks
    print("[1] STRUCTURAL CHECKS (with expected values)")
    print("-" * 70)
    for case in ALL_CASES:
        engine = ZiweiEngine()
        fc = engine.full_chart(case['lunar_date'], case['hour'], case['gender'])
        results = check_structural(fc, case)
        all_results.extend(results)
        for status, msg in results:
            print(f"  {status} {msg}")
    
    print()
    
    # 2. Decadal direction checks (WITH EXPECTED ASSERTIONS)
    print("[2] DECADAL DIRECTION CHECKS (expected order assertion)")
    print("-" * 70)
    for case in ALL_CASES:
        engine = ZiweiEngine()
        fc = engine.full_chart(case['lunar_date'], case['hour'], case['gender'])
        results = check_decadal_direction(fc, case)
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
    
    # 4. Temporal mutation checks (WITH EXPECTED VALUES)
    print("[4] TEMPORAL MUTATION CHECKS (expected value assertion)")
    print("-" * 70)
    for case in ALL_CASES:
        results = run_temporal_checks(case)
        all_results.extend(results)
        # Collect temporal outputs for leakage check
        if '_temporal_outputs' in case:
            all_temporal_outputs.extend(case['_temporal_outputs'])
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
    
    # 7. Semantic leakage check (ALL API outputs)
    print("[7] SEMANTIC LEAKAGE CHECK (all API outputs)")
    print("-" * 70)
    
    # Collect all outputs: full_chart + all temporal outputs
    all_outputs = []
    for case in ALL_CASES:
        engine = ZiweiEngine()
        fc = engine.full_chart(case['lunar_date'], case['hour'], case['gender'])
        all_outputs.append(fc)
        if '_temporal_outputs' in case:
            all_outputs.extend(case['_temporal_outputs'])
    
    results = check_forbidden_terms(*all_outputs)
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
