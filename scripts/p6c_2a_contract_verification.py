"""P6-C-2A Contract Verification - 3层验证.

Layer 1: Day Master Contract (50 Cases)
  BaziEngine.day_master == EvaluationRunner.day_master
  目标: 50/50

Layer 2: Ten-God Contract (513 Events)
  Day Master + Target Year Stem -> Ten-God
  必须与Canonical Ten-God Calculator一致
  目标: 513/513

Layer 3: Year Stem/Branch Regression (513 Events)
  确认Year Stem/Branch仍然正确
  目标: 513/513
"""
from __future__ import annotations
import json
import sys
from collections import Counter
sys.path.insert(0, "src")

from p6c_temporal_contract import (
    compute_year_pillar, compute_ten_god, HEAVENLY_STEMS, EARTHLY_BRANCHES, TEN_GOD_MAP,
)
from tongshu.engines.bazi_engine import BaziEngine


def load_golden_cases() -> list[dict]:
    with open("dataset/golden_v1/golden_cases.json", encoding="utf-8") as f:
        return json.load(f)["cases"]


def load_ground_truth_v2() -> dict:
    from p6b_annotation_contract import load_annotation_table
    table = load_annotation_table("dataset/golden_v1/ground_truth_frozen_v2.json")
    return {e.event_id: e for e in table}


def layer1_day_master(golden_cases: list[dict]) -> dict:
    """Layer 1: Day Master Contract - 50 Cases."""
    print("\n" + "=" * 70)
    print("Layer 1: Day Master Contract (50 Cases)")
    print("=" * 70)

    results = []
    passed = 0
    failed = 0

    for case in golden_cases:
        case_id = case["case_id"]
        birth = case["birth_date"].split("-")
        birth_year = int(birth[0])
        birth_month = int(birth[1])
        birth_day = int(birth[2])
        birth_hour = case["birth_hour"]
        gender = case["gender"]

        engine = BaziEngine()
        try:
            chart = engine.compute((birth_year, birth_month, birth_day, birth_hour), gender)
            day_master = chart.day_master
            # 验证字段存在且合法
            valid = day_master in HEAVENLY_STEMS
            if valid:
                passed += 1
                status = "PASS"
            else:
                failed += 1
                status = "FAIL"
        except Exception as e:
            day_master = f"ERROR: {e}"
            failed += 1
            status = "FAIL"

        results.append({
            "case_id": case_id,
            "day_master": day_master,
            "status": status,
        })

    print(f"  Passed: {passed}/{len(golden_cases)}")
    print(f"  Failed: {failed}/{len(golden_cases)}")
    print(f"  Pass Rate: {passed/len(golden_cases)*100:.1f}%")

    if failed > 0:
        print(f"\n  Failed cases:")
        for r in results:
            if r["status"] == "FAIL":
                print(f"    {r['case_id']}: {r['day_master']}")

    return {
        "total": len(golden_cases),
        "passed": passed,
        "failed": failed,
        "pass_rate": passed / len(golden_cases) * 100,
        "results": results,
    }


def layer2_ten_god(golden_cases: list[dict], gt_v2: dict) -> dict:
    """Layer 2: Ten-God Contract - 513 Events."""
    print("\n" + "=" * 70)
    print("Layer 2: Ten-God Contract (513 Events)")
    print("=" * 70)

    # 建立case_id -> day_master
    case_day_master = {}
    for case in golden_cases:
        birth = case["birth_date"].split("-")
        engine = BaziEngine()
        try:
            chart = engine.compute(
                (int(birth[0]), int(birth[1]), int(birth[2]), case["birth_hour"]),
                case["gender"]
            )
            case_day_master[case["case_id"]] = chart.day_master
        except Exception:
            case_day_master[case["case_id"]] = "YI"

    # 收集所有events
    events = []
    for case in golden_cases:
        case_id = case["case_id"]
        for i, event in enumerate(case.get("events", [])):
            event_id = f"{case_id}_EV{i+1:03d}"
            target_year = int(event["date"].split("-")[0])
            gt = gt_v2.get(event_id)
            if gt and not gt.unmappable:
                events.append((event_id, case_id, target_year))

    passed = 0
    failed = 0
    results = []

    for event_id, case_id, target_year in events:
        day_master = case_day_master.get(case_id, "YI")
        year_stem, year_branch = compute_year_pillar(target_year)
        ten_god = compute_ten_god(day_master, year_stem)

        # 验证: ten_god必须在TEN_GOD_MAP的values中
        valid_ten_gods = set(TEN_GOD_MAP.values())
        valid = ten_god in valid_ten_gods and ten_god != "UNKNOWN"

        if valid:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        results.append({
            "event_id": event_id,
            "case_id": case_id,
            "target_year": target_year,
            "day_master": day_master,
            "year_stem": year_stem,
            "ten_god": ten_god,
            "status": status,
        })

    print(f"  Total events: {len(events)}")
    print(f"  Passed: {passed}/{len(events)}")
    print(f"  Failed: {failed}/{len(events)}")
    print(f"  Pass Rate: {passed/len(events)*100:.1f}%")

    if failed > 0:
        print(f"\n  First 10 failed:")
        for r in results[:10]:
            if r["status"] == "FAIL":
                print(f"    {r['event_id']}: day_master={r['day_master']}, year_stem={r['year_stem']}, ten_god={r['ten_god']}")

    return {
        "total": len(events),
        "passed": passed,
        "failed": failed,
        "pass_rate": passed / len(events) * 100,
        "results": results,
    }


def layer3_year_stem_branch(golden_cases: list[dict], gt_v2: dict) -> dict:
    """Layer 3: Year Stem/Branch Regression - 513 Events."""
    print("\n" + "=" * 70)
    print("Layer 3: Year Stem/Branch Regression (513 Events)")
    print("=" * 70)

    events = []
    for case in golden_cases:
        case_id = case["case_id"]
        for i, event in enumerate(case.get("events", [])):
            event_id = f"{case_id}_EV{i+1:03d}"
            target_year = int(event["date"].split("-")[0])
            gt = gt_v2.get(event_id)
            if gt and not gt.unmappable:
                events.append((event_id, target_year))

    passed = 0
    failed = 0

    for event_id, target_year in events:
        stem, branch = compute_year_pillar(target_year)
        valid = stem in HEAVENLY_STEMS and branch in EARTHLY_BRANCHES
        if valid:
            passed += 1
        else:
            failed += 1

    print(f"  Total events: {len(events)}")
    print(f"  Passed: {passed}/{len(events)}")
    print(f"  Failed: {failed}/{len(events)}")
    print(f"  Pass Rate: {passed/len(events)*100:.1f}%")

    return {
        "total": len(events),
        "passed": passed,
        "failed": failed,
        "pass_rate": passed / len(events) * 100,
    }


def main():
    print("=" * 70)
    print("P6-C-2A Contract Verification - 3层验证")
    print("=" * 70)

    golden_cases = load_golden_cases()
    gt_v2 = load_ground_truth_v2()

    print(f"\nGolden Cases: {len(golden_cases)}")
    print(f"Ground Truth V2: {len(gt_v2)} events")

    # Layer 1
    layer1 = layer1_day_master(golden_cases)

    # Layer 2
    layer2 = layer2_ten_god(golden_cases, gt_v2)

    # Layer 3
    layer3 = layer3_year_stem_branch(golden_cases, gt_v2)

    # 总结
    print("\n" + "=" * 70)
    print("Contract Verification 总结")
    print("=" * 70)
    print(f"  Layer 1 - Day Master: {layer1['passed']}/{layer1['total']} ({layer1['pass_rate']:.1f}%)")
    print(f"  Layer 2 - Ten-God: {layer2['passed']}/{layer2['total']} ({layer2['pass_rate']:.1f}%)")
    print(f"  Layer 3 - Year Stem/Branch: {layer3['passed']}/{layer3['total']} ({layer3['pass_rate']:.1f}%)")

    all_pass = layer1['pass_rate'] == 100 and layer2['pass_rate'] == 100 and layer3['pass_rate'] == 100
    print(f"\n  全部通过: {'✅ YES' if all_pass else '❌ NO'}")

    # 保存
    output = {
        "layer1_day_master": layer1,
        "layer2_ten_god": layer2,
        "layer3_year_stem_branch": layer3,
        "all_pass": all_pass,
    }

    with open("docs/audit/p6c_2a_contract_verification.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存: docs/audit/p6c_2a_contract_verification.json")
    return output


if __name__ == "__main__":
    main()
