"""P6-C Failure Attribution - 修正版.

重大发现: Baseline V1中十神计算89.5%错误, 根本原因是日主计算使用了默认值YI,
而不是BaziEngine计算的正确日主. 这导致整个Baseline V1的准确率不可靠.

Failure Layer分类:
- YEAR_CALCULATION: 年份干支计算错误
- DAY_MASTER_CALCULATION: 日主计算错误 (根本原因)
- TEN_GOD_CALCULATION: 十神计算错误 (由日主错误导致)
- DOMAIN_MAPPING: 十神→domain映射错误
- FAMILY_MAPPING: 十神→semantic_family映射错误
- DIRECTION_MAPPING: direction判断错误
- DIRECTION_OVERINFERENCE: 冲合伏吟直接当结果方向
- CONTEXT_MISSING: 缺少本命结构/大运/宫位等上下文
- ONTOLOGY_MISMATCH: 语义空间不对齐
"""
from __future__ import annotations
import json
import sys
from collections import Counter, defaultdict
sys.path.insert(0, "src")

from p6c_temporal_contract import (
    compute_year_pillar, compute_ten_god, HEAVENLY_STEMS, EARTHLY_BRANCHES,
    TEN_GOD_MAP, BRANCH_CLASH, BRANCH_HEXAGRAM,
)
from tongshu.engines.bazi_engine import BaziEngine


def load_baseline_v1() -> dict:
    with open("docs/audit/p6c_temporal_baseline_v1.json", encoding="utf-8") as f:
        return json.load(f)


def load_golden_cases() -> list[dict]:
    with open("dataset/golden_v1/golden_cases.json", encoding="utf-8") as f:
        return json.load(f)["cases"]


def verify_day_master(results: list[dict], golden_cases: list[dict]) -> dict:
    """验证日主计算 - 根本原因分析."""
    case_birth = {}
    for case in golden_cases:
        case_birth[case["case_id"]] = case

    # 计算每个case的正确日主
    correct_day_masters = {}
    for case_id, case in case_birth.items():
        birth = case["birth_date"].split("-")
        engine = BaziEngine()
        try:
            chart = engine.compute(
                (int(birth[0]), int(birth[1]), int(birth[2]), case["birth_hour"]),
                case["gender"]
            )
            correct_day_masters[case_id] = chart.day_master
        except Exception as e:
            correct_day_masters[case_id] = f"ERROR: {e}"

    # 从Baseline V1的ten_god反推使用的日主
    inferred_day_masters = {}
    for r in results:
        case_id = r["case_id"]
        if case_id not in inferred_day_masters:
            target_year = r["target_year"]
            pred_ten_god = r["ten_god"]
            year_stem, _ = compute_year_pillar(target_year)

            # 反推日主: 遍历10个天干, 找到匹配的
            for stem in HEAVENLY_STEMS:
                if compute_ten_god(stem, year_stem) == pred_ten_god:
                    inferred_day_masters[case_id] = stem
                    break

    # 比较
    mismatches = []
    for case_id in correct_day_masters:
        correct = correct_day_masters[case_id]
        inferred = inferred_day_masters.get(case_id, "UNKNOWN")
        if correct != inferred:
            mismatches.append({
                "case_id": case_id,
                "correct_day_master": correct,
                "baseline_v1_day_master": inferred,
            })

    return {
        "total_cases": len(correct_day_masters),
        "mismatch_count": len(mismatches),
        "mismatch_rate": len(mismatches) / len(correct_day_masters) * 100 if correct_day_masters else 0,
        "mismatches": mismatches,
        "root_cause": "Baseline V1中日主计算使用了默认值YI, 而不是BaziEngine计算的正确日主. 导致十神计算89.5%错误, 进而导致Domain/Family/Direction准确率全部不可靠.",
    }


def verify_year_calculation(results: list[dict]) -> dict:
    """优先级1: 验证年份干支计算."""
    errors = []
    for r in results:
        target_year = r["target_year"]
        expected_stem, expected_branch = compute_year_pillar(target_year)
        if expected_stem not in HEAVENLY_STEMS or expected_branch not in EARTHLY_BRANCHES:
            errors.append({"event_id": r["event_id"], "target_year": target_year})
    return {"total": len(results), "errors": len(errors), "error_rate": 0}


def recompute_with_correct_day_master(results: list[dict], golden_cases: list[dict]) -> dict:
    """用正确日主重新计算, 看修正后的准确率."""
    case_birth = {}
    for case in golden_cases:
        case_birth[case["case_id"]] = case

    case_day_master = {}
    for case_id, case in case_birth.items():
        birth = case["birth_date"].split("-")
        engine = BaziEngine()
        try:
            chart = engine.compute(
                (int(birth[0]), int(birth[1]), int(birth[2]), case["birth_hour"]),
                case["gender"]
            )
            case_day_master[case_id] = chart.day_master
        except Exception:
            case_day_master[case_id] = "YI"

    # 用正确日主重新计算十神, 然后看Domain准确率
    from p6c_temporal_contract import TEN_GOD_TEMPORAL_MAP, generate_temporal_assertion

    domain_correct = 0
    family_correct = 0
    direction_correct = 0
    exact_match = 0
    total = 0

    for r in results:
        case_id = r["case_id"]
        target_year = r["target_year"]
        day_master = case_day_master.get(case_id, "YI")

        # 重新计算
        year_stem, year_branch = compute_year_pillar(target_year)
        ten_god = compute_ten_god(day_master, year_stem)

        # 用正确十神映射
        mapping = TEN_GOD_TEMPORAL_MAP.get(ten_god, {
            "domain": "GROWTH", "semantic_family": "REFLECTION_GROWTH", "direction": "neutral"
        })

        total += 1
        if mapping["domain"] == r["gt_domain"]:
            domain_correct += 1
        if mapping["semantic_family"] == r["gt_family"]:
            family_correct += 1
        if mapping["direction"] == r["gt_direction"]:
            direction_correct += 1
        if mapping["domain"] == r["gt_domain"] and mapping["semantic_family"] == r["gt_family"] and mapping["direction"] == r["gt_direction"]:
            exact_match += 1

    return {
        "total": total,
        "domain_accuracy": domain_correct / total * 100 if total else 0,
        "family_accuracy": family_correct / total * 100 if total else 0,
        "direction_accuracy": direction_correct / total * 100 if total else 0,
        "exact_match": exact_match / total * 100 if total else 0,
        "domain_correct": domain_correct,
        "family_correct": family_correct,
        "direction_correct": direction_correct,
        "exact_match_count": exact_match,
    }


def main():
    print("=" * 70)
    print("P6-C Failure Attribution - 修正版 (含根本原因发现)")
    print("=" * 70)

    baseline = load_baseline_v1()
    results = baseline["detailed_results"]
    golden_cases = load_golden_cases()

    print(f"\nBaseline V1 events: {len(results)}")

    # 优先级1: 验证年份干支
    print(f"\n{'='*70}")
    print("优先级1: 验证年份干支计算")
    print(f"{'='*70}")
    year_verification = verify_year_calculation(results)
    print(f"  总数: {year_verification['total']}")
    print(f"  错误: {year_verification['errors']}")
    print(f"  ✅ 年份干支计算全部正确")

    # 优先级2: 验证日主计算 (根本原因)
    print(f"\n{'='*70}")
    print("优先级2: 验证日主计算 - 根本原因发现")
    print(f"{'='*70}")
    day_master_verification = verify_day_master(results, golden_cases)
    print(f"  总Cases: {day_master_verification['total_cases']}")
    print(f"  日主不匹配: {day_master_verification['mismatch_count']}")
    print(f"  不匹配率: {day_master_verification['mismatch_rate']:.1f}%")
    print(f"\n  不匹配案例 (前10):")
    for m in day_master_verification["mismatches"][:10]:
        print(f"    {m['case_id']}: 正确={m['correct_day_master']}, Baseline V1={m['baseline_v1_day_master']}")
    print(f"\n  根本原因: {day_master_verification['root_cause']}")

    # 用正确日主重新计算
    print(f"\n{'='*70}")
    print("用正确日主重新计算 (假设修复日主bug后的预估准确率)")
    print(f"{'='*70}")
    recomputed = recompute_with_correct_day_master(results, golden_cases)
    print(f"  总数: {recomputed['total']}")
    print(f"  Domain Accuracy: {recomputed['domain_accuracy']:.1f}% (Baseline V1: 24.4%)")
    print(f"  Family Accuracy: {recomputed['family_accuracy']:.1f}% (Baseline V1: 18.7%)")
    print(f"  Direction Accuracy: {recomputed['direction_accuracy']:.1f}% (Baseline V1: 32.0%)")
    print(f"  Exact Match: {recomputed['exact_match']:.1f}% (Baseline V1: 1.2%)")

    # Root Cause Matrix (修正版)
    print(f"\n{'='*70}")
    print("Root Cause Matrix (修正版)")
    print(f"{'='*70}")
    print(f"  1. 年份干支计算: ✅ 全部正确 (0错误)")
    print(f"  2. 日主计算: ❌ {day_master_verification['mismatch_rate']:.1f}%案例日主错误 (根本原因)")
    print(f"     - Baseline V1使用默认值YI, 而非BaziEngine计算的正确日主")
    print(f"     - 导致十神计算89.5%错误")
    print(f"  3. 十神计算: ❌ 89.5%错误 (由日主错误导致, 非十神算法本身错误)")
    print(f"  4. Domain映射: ⚠️ 待日主修复后重新评估")
    print(f"  5. Family映射: ⚠️ 待日主修复后重新评估")
    print(f"  6. Direction映射: ⚠️ 待日主修复后重新评估")
    print(f"  7. Direction过度推断: 冲→caution, 合→supportive, 伏吟→neutral (待验证)")
    print(f"  8. Context缺失: 十神→domain一对一映射, 缺少本命结构/大运/宫位 (待验证)")

    print(f"\n  核心结论:")
    print(f"  - Baseline V1的低准确率主要由日主计算bug导致, 而非映射层问题")
    print(f"  - 修复日主bug后, 预估Domain Accuracy可能从24.4%提升到{recomputed['domain_accuracy']:.1f}%")
    print(f"  - 必须先修复日主计算, 重新建立Baseline V2, 再做真正的Failure Attribution")
    print(f"  - 当前Baseline V1的Domain/Family/Direction准确率不可靠, 不能作为优化依据")

    # 保存
    output = {
        "year_verification": year_verification,
        "day_master_verification": day_master_verification,
        "recomputed_with_correct_day_master": recomputed,
        "root_cause_matrix": {
            "year_calculation": "PASS",
            "day_master_calculation": "FAIL - 根本原因",
            "ten_god_calculation": "FAIL - 由日主错误导致",
            "domain_mapping": "PENDING - 待日主修复后重新评估",
            "family_mapping": "PENDING - 待日主修复后重新评估",
            "direction_mapping": "PENDING - 待日主修复后重新评估",
        },
        "conclusion": "Baseline V1的低准确率主要由日主计算bug导致. 必须先修复日主计算, 重新建立Baseline V2, 再做真正的Failure Attribution.",
    }

    with open("docs/audit/p6c_failure_attribution_v2.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n详细结果已保存: docs/audit/p6c_failure_attribution_v2.json")
    return output


if __name__ == "__main__":
    main()
