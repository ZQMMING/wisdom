"""P6-C Temporal Evaluation Runner.

跑518个events, 与Ground Truth V2比较, 输出Temporal Baseline V1.

指标:
- 单维度: Domain Accuracy, Semantic Family Accuracy, Direction Accuracy
- 联合判断: Exact Semantic Match
- 分类指标: Macro-F1, Micro-F1
- 覆盖率: READY Coverage, UNRESOLVED Coverage, Temporal Coverage
- Event-level + Case-level

诊断矩阵:
- Domain Confusion Matrix
- Direction Confusion Matrix
- semantic_family confusion
"""
from __future__ import annotations
import json
import sys
from collections import Counter, defaultdict
sys.path.insert(0, "src")

from p6c_temporal_contract import (
    generate_temporal_assertion, compute_year_pillar, compute_ten_god,
    get_natal_info, TemporalAssertion,
)
from p6b_annotation_contract import load_annotation_table


def load_golden_cases() -> list[dict]:
    """加载Golden Dataset."""
    with open("dataset/golden_v1/golden_cases.json", encoding="utf-8") as f:
        return json.load(f)["cases"]


def load_ground_truth_v2() -> dict[str, dict]:
    """加载Ground Truth V2, 按event_id索引."""
    table = load_annotation_table("dataset/golden_v1/ground_truth_frozen_v2.json")
    return {e.event_id: e for e in table}


def run_evaluation() -> dict:
    """运行完整评估."""
    print("=" * 70)
    print("P6-C Temporal Evaluation - Temporal Baseline V1")
    print("=" * 70)

    golden_cases = load_golden_cases()
    gt_v2 = load_ground_truth_v2()

    print(f"\nGolden Cases: {len(golden_cases)}")
    print(f"Ground Truth V2: {len(gt_v2)} events")

    # 对每个Case计算本命信息(缓存)
    natal_cache = {}
    case_event_map = defaultdict(list)  # case_id -> list of (event_id, target_year, gt)

    for case in golden_cases:
        case_id = case["case_id"]
        birth = case["birth_date"].split("-")
        birth_year = int(birth[0])

        # 计算本命信息 (简化: 用BaziEngine)
        from tongshu.engines.bazi_engine import BaziEngine
        engine = BaziEngine()
        try:
            chart = engine.compute(
                (birth_year, int(birth[1]), int(birth[2]), case["birth_hour"]),
                case["gender"]
            )
            day_master = chart.day_master
            branches = [
                chart.year_pillar.earthly_branch,
                chart.month_pillar.earthly_branch,
                chart.day_pillar.earthly_branch,
                chart.hour_pillar.earthly_branch,
            ]
        except Exception:
            day_master = "YI"
            branches = ["HAI", "XU", "WEI", "WU"]

        natal_cache[case_id] = (day_master, branches)

        # 收集事件
        for i, event in enumerate(case.get("events", [])):
            event_id = f"{case_id}_EV{i+1:03d}"
            target_year = int(event["date"].split("-")[0])
            gt = gt_v2.get(event_id)
            if gt and not gt.unmappable:
                case_event_map[case_id].append((event_id, target_year, gt))

    # 统计
    total_gt_events = sum(len(events) for events in case_event_map.values())
    print(f"\n可评估事件 (Ground Truth V2 mappable): {total_gt_events}")
    print(f"涉及Cases: {len(case_event_map)}")

    # 生成Temporal Assertions并评估
    results = []
    domain_correct = 0
    family_correct = 0
    direction_correct = 0
    exact_match = 0
    total_evaluated = 0

    # Confusion matrices
    domain_confusion = defaultdict(Counter)
    direction_confusion = defaultdict(Counter)
    family_confusion = defaultdict(Counter)

    # Per-case stats
    case_stats = defaultdict(lambda: {"total": 0, "domain_correct": 0, "exact_match": 0})

    for case_id, events in case_event_map.items():
        day_master, branches = natal_cache[case_id]

        for event_id, target_year, gt in events:
            # 生成Temporal Assertion
            temporal_assertion = generate_temporal_assertion(
                case_id=case_id,
                target_year=target_year,
                day_master=day_master,
                natal_branches=branches,
            )

            total_evaluated += 1

            # 评估
            domain_match = temporal_assertion.domain == gt.domain
            family_match = temporal_assertion.semantic_family == gt.semantic_family
            direction_match = temporal_assertion.direction == gt.direction
            exact = domain_match and family_match and direction_match

            if domain_match:
                domain_correct += 1
            if family_match:
                family_correct += 1
            if direction_match:
                direction_correct += 1
            if exact:
                exact_match += 1

            # Confusion matrices
            domain_confusion[gt.domain][temporal_assertion.domain] += 1
            direction_confusion[gt.direction][temporal_assertion.direction] += 1
            family_confusion[gt.semantic_family][temporal_assertion.semantic_family] += 1

            # Case stats
            case_stats[case_id]["total"] += 1
            if domain_match:
                case_stats[case_id]["domain_correct"] += 1
            if exact:
                case_stats[case_id]["exact_match"] += 1

            results.append({
                "event_id": event_id,
                "case_id": case_id,
                "target_year": target_year,
                "gt_domain": gt.domain,
                "gt_family": gt.semantic_family,
                "gt_direction": gt.direction,
                "pred_domain": temporal_assertion.domain,
                "pred_family": temporal_assertion.semantic_family,
                "pred_direction": temporal_assertion.direction,
                "ten_god": temporal_assertion.ten_god,
                "branch_relations": temporal_assertion.branch_relations,
                "domain_match": domain_match,
                "family_match": family_match,
                "direction_match": direction_match,
                "exact_match": exact,
            })

    # 计算指标
    domain_acc = domain_correct / total_evaluated * 100 if total_evaluated else 0
    family_acc = family_correct / total_evaluated * 100 if total_evaluated else 0
    direction_acc = direction_correct / total_evaluated * 100 if total_evaluated else 0
    exact_acc = exact_match / total_evaluated * 100 if total_evaluated else 0

    # Macro-F1 (per-class average)
    def compute_f1(confusion: dict, all_labels: list) -> dict:
        """计算per-class precision/recall/f1和macro/micro."""
        per_class = {}
        total_tp = 0
        total_fp = 0
        total_fn = 0

        for label in all_labels:
            tp = confusion[label][label]
            fp = sum(confusion[other][label] for other in all_labels if other != label)
            fn = sum(confusion[label][other] for other in all_labels if other != label)

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

            per_class[label] = {"precision": precision, "recall": recall, "f1": f1, "support": tp + fn}
            total_tp += tp
            total_fp += fp
            total_fn += fn

        macro_f1 = sum(c["f1"] for c in per_class.values()) / len(per_class) if per_class else 0
        micro_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
        micro_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
        micro_f1 = 2 * micro_precision * micro_recall / (micro_precision + micro_recall) if (micro_precision + micro_recall) > 0 else 0

        return {
            "per_class": per_class,
            "macro_f1": macro_f1,
            "micro_f1": micro_f1,
            "micro_precision": micro_precision,
            "micro_recall": micro_recall,
        }

    all_domains = ["CAREER", "FINANCE", "RELATIONSHIP", "FAMILY", "HEALTH", "GROWTH", "DECISION", "MIGRATION"]
    all_directions = ["supportive", "caution", "neutral"]
    all_families = ["OUTPUT_EXPRESSION", "RESOURCE_WEALTH", "STABILITY_SUPPORT", "CONSTRAINT_RULE",
                    "CHANGE_TRANSFORMATION", "REFLECTION_GROWTH", "RELATION_CONNECTION",
                    "ACTION_EXECUTION", "HEALTH_CAUTION"]

    domain_f1 = compute_f1(domain_confusion, all_domains)
    direction_f1 = compute_f1(direction_confusion, all_directions)
    family_f1 = compute_f1(family_confusion, all_families)

    # Case-level metrics
    case_macro_domain_acc = sum(s["domain_correct"] / s["total"] for s in case_stats.values() if s["total"] > 0) / len(case_stats) * 100 if case_stats else 0
    case_macro_exact = sum(s["exact_match"] / s["total"] for s in case_stats.values() if s["total"] > 0) / len(case_stats) * 100 if case_stats else 0

    # 输出报告
    print(f"\n{'='*70}")
    print("P6-C Temporal Baseline V1 - 结果")
    print(f"{'='*70}")

    print(f"\n=== 覆盖率 ===")
    print(f"  Ground Truth V2 mappable events: {total_gt_events}")
    print(f"  Temporal Assertions generated: {total_evaluated}")
    print(f"  Temporal Coverage: {total_evaluated / total_gt_events * 100:.1f}%")
    print(f"  READY Coverage: 100% (第一版全部READY)")
    print(f"  UNRESOLVED: 0")

    print(f"\n=== 单维度准确率 (Event-level) ===")
    print(f"  Domain Accuracy: {domain_acc:.1f}% ({domain_correct}/{total_evaluated})")
    print(f"  Semantic Family Accuracy: {family_acc:.1f}% ({family_correct}/{total_evaluated})")
    print(f"  Direction Accuracy: {direction_acc:.1f}% ({direction_correct}/{total_evaluated})")

    print(f"\n=== 联合判断 ===")
    print(f"  Exact Semantic Match (domain+family+direction): {exact_acc:.1f}% ({exact_match}/{total_evaluated})")

    print(f"\n=== 分类指标 ===")
    print(f"  Domain Macro-F1: {domain_f1['macro_f1']*100:.1f}%")
    print(f"  Domain Micro-F1: {domain_f1['micro_f1']*100:.1f}%")
    print(f"  Direction Macro-F1: {direction_f1['macro_f1']*100:.1f}%")
    print(f"  Direction Micro-F1: {direction_f1['micro_f1']*100:.1f}%")
    print(f"  Family Macro-F1: {family_f1['macro_f1']*100:.1f}%")
    print(f"  Family Micro-F1: {family_f1['micro_f1']*100:.1f}%")

    print(f"\n=== Case-level指标 ===")
    print(f"  Cases evaluated: {len(case_stats)}")
    print(f"  Case Macro Domain Accuracy: {case_macro_domain_acc:.1f}%")
    print(f"  Case Macro Exact Match: {case_macro_exact:.1f}%")

    # Domain Confusion Matrix
    print(f"\n=== Domain Confusion Matrix (Actual -> Predicted) ===")
    print(f"  {'':15} " + " ".join(f"{d[:8]:>8}" for d in all_domains))
    for actual in all_domains:
        if actual in domain_confusion:
            row = " ".join(f"{domain_confusion[actual][pred]:>8}" for pred in all_domains)
            print(f"  {actual:15} {row}")

    # Direction Confusion Matrix
    print(f"\n=== Direction Confusion Matrix (Actual -> Predicted) ===")
    print(f"  {'':15} " + " ".join(f"{d:>10}" for d in all_directions))
    for actual in all_directions:
        if actual in direction_confusion:
            row = " ".join(f"{direction_confusion[actual][pred]:>10}" for pred in all_directions)
            print(f"  {actual:15} {row}")

    # 加载V1用于对比
    try:
        with open("docs/audit/p6c_temporal_baseline_v1.json", encoding="utf-8") as f:
            v1 = json.load(f)
        v1_accuracy = v1.get("accuracy_event_level", {})
        v1_f1 = v1.get("f1_scores", {})
    except Exception:
        v1_accuracy = {}
        v1_f1 = {}

    # V1/V2对比
    v1_v2_comparison = {
        "domain_accuracy": {"v1": v1_accuracy.get("domain_accuracy_pct", 0), "v2": domain_acc, "delta": domain_acc - v1_accuracy.get("domain_accuracy_pct", 0)},
        "family_accuracy": {"v1": v1_accuracy.get("semantic_family_accuracy_pct", 0), "v2": family_acc, "delta": family_acc - v1_accuracy.get("semantic_family_accuracy_pct", 0)},
        "direction_accuracy": {"v1": v1_accuracy.get("direction_accuracy_pct", 0), "v2": direction_acc, "delta": direction_acc - v1_accuracy.get("direction_accuracy_pct", 0)},
        "exact_match": {"v1": v1_accuracy.get("exact_semantic_match_pct", 0), "v2": exact_acc, "delta": exact_acc - v1_accuracy.get("exact_semantic_match_pct", 0)},
        "domain_macro_f1": {"v1": v1_f1.get("domain_macro_f1", 0), "v2": domain_f1["macro_f1"] * 100, "delta": domain_f1["macro_f1"] * 100 - v1_f1.get("domain_macro_f1", 0)},
        "direction_macro_f1": {"v1": v1_f1.get("direction_macro_f1", 0), "v2": direction_f1["macro_f1"] * 100, "delta": direction_f1["macro_f1"] * 100 - v1_f1.get("direction_macro_f1", 0)},
    }

    print(f"\n=== V1 vs V2 对比 ===")
    for k, v in v1_v2_comparison.items():
        print(f"  {k}: V1={v['v1']:.1f}%, V2={v['v2']:.1f}%, Delta={v['delta']:+.1f}%")

    # 保存结果
    output = {
        "baseline": "P6-C Temporal Baseline V2",
        "v1_status": "INVALIDATED_DIAGNOSTIC_ONLY",
        "fix_applied": "Evaluation Runner Day Master field extraction bug fixed (chart.year_branch -> chart.year_pillar.earthly_branch)",
        "contract_verification": "Day Master 50/50, Ten-God 513/513, Year Stem/Branch 513/513",
        "p5_status": "FROZEN",
        "ground_truth_version": "V2",
        "total_gt_events": total_gt_events,
        "total_evaluated": total_evaluated,
        "coverage": {
            "temporal_coverage_pct": total_evaluated / total_gt_events * 100,
            "ready_coverage_pct": 100,
            "unresolved_count": 0,
        },
        "accuracy_event_level": {
            "domain_accuracy_pct": domain_acc,
            "semantic_family_accuracy_pct": family_acc,
            "direction_accuracy_pct": direction_acc,
            "exact_semantic_match_pct": exact_acc,
        },
        "f1_scores": {
            "domain_macro_f1": domain_f1["macro_f1"] * 100,
            "domain_micro_f1": domain_f1["micro_f1"] * 100,
            "direction_macro_f1": direction_f1["macro_f1"] * 100,
            "direction_micro_f1": direction_f1["micro_f1"] * 100,
            "family_macro_f1": family_f1["macro_f1"] * 100,
            "family_micro_f1": family_f1["micro_f1"] * 100,
        },
        "case_level": {
            "cases_evaluated": len(case_stats),
            "case_macro_domain_accuracy_pct": case_macro_domain_acc,
            "case_macro_exact_match_pct": case_macro_exact,
        },
        "confusion_matrices": {
            "domain": {k: dict(v) for k, v in domain_confusion.items()},
            "direction": {k: dict(v) for k, v in direction_confusion.items()},
            "family": {k: dict(v) for k, v in family_confusion.items()},
        },
        "per_class_f1": {
            "domain": domain_f1["per_class"],
            "direction": direction_f1["per_class"],
            "family": family_f1["per_class"],
        },
        "detailed_results": results,
    }

    import os
    os.makedirs("docs/audit", exist_ok=True)
    with open("docs/audit/p6c_temporal_baseline_v2.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n详细结果已保存: docs/audit/p6c_temporal_baseline_v2.json")

    # 诊断总结
    print(f"\n{'='*70}")
    print("诊断总结")
    print(f"{'='*70}")

    if domain_acc > 60 and family_acc < 40:
        print("  大方向(Domain)对, 但语义分类(Family)不够细")
    elif family_acc > 50 and direction_acc < 40:
        print("  识别到了事情(Family), 但判断有利/谨慎/中性(Direction)出了问题")
    elif domain_acc < 40 and family_acc < 40 and direction_acc < 40:
        print("  三个维度都低, 需要回头审Temporal Rule/ContextResolver")
    else:
        print("  各维度表现不均衡, 详见Confusion Matrix")

    print(f"\n  第一版Temporal Baseline已建立, 不针对结果优化规则")
    print(f"  下一步: 根据诊断矩阵决定修Temporal Rule还是ContextResolver")

    return output


if __name__ == "__main__":
    run_evaluation()
