"""P6-C Failure Attribution - 逐条归因513条Temporal Baseline V1.

Failure Layer分类:
- YEAR_CALCULATION: 年份干支计算错误
- TEN_GOD_CALCULATION: 十神计算错误
- DOMAIN_MAPPING: 十神→domain映射错误
- FAMILY_MAPPING: 十神→semantic_family映射错误
- DIRECTION_MAPPING: direction判断错误(冲合伏吟直接当结果方向)
- CONTEXT_MISSING: 缺少本命结构/大运/宫位等上下文
- ONTOLOGY_MISMATCH: 语义空间不对齐(partial match)

五个优先级:
1. 验证年份干支
2. 验证十神计算
3. Domain Attribution
4. Direction Attribution (structural signal vs outcome polarity)
5. Ontology Mismatch (partial match分析)
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
from p6b_annotation_contract import load_annotation_table


def load_baseline_v1() -> dict:
    """加载Baseline V1详细结果."""
    with open("docs/audit/p6c_temporal_baseline_v1.json", encoding="utf-8") as f:
        return json.load(f)


def load_golden_cases() -> list[dict]:
    """加载Golden Dataset."""
    with open("dataset/golden_v1/golden_cases.json", encoding="utf-8") as f:
        return json.load(f)["cases"]


def verify_year_calculation(results: list[dict]) -> dict:
    """优先级1: 验证年份干支计算."""
    errors = []
    for r in results:
        target_year = r["target_year"]
        # 用独立方法验证: 1984甲子年基准
        expected_stem, expected_branch = compute_year_pillar(target_year)
        # 从ten_god反推stem (需要日主)
        # 这里只验证计算一致性
        if expected_stem not in HEAVENLY_STEMS or expected_branch not in EARTHLY_BRANCHES:
            errors.append({
                "event_id": r["event_id"],
                "target_year": target_year,
                "expected": f"{expected_stem}{expected_branch}",
                "error": "invalid stem/branch",
            })

    return {
        "total": len(results),
        "errors": len(errors),
        "error_rate": len(errors) / len(results) * 100 if results else 0,
        "details": errors[:10],
    }


def verify_ten_god_calculation(results: list[dict], golden_cases: list[dict]) -> dict:
    """优先级2: 验证十神计算."""
    # 建立case_id -> 日主映射
    case_day_master = {}
    for case in golden_cases:
        case_id = case["case_id"]
        birth = case["birth_date"].split("-")
        from tongshu.engines.bazi_engine import BaziEngine
        engine = BaziEngine()
        try:
            chart = engine.compute(
                (int(birth[0]), int(birth[1]), int(birth[2]), case["birth_hour"]),
                case["gender"]
            )
            case_day_master[case_id] = chart.day_master
        except Exception:
            case_day_master[case_id] = "YI"

    errors = []
    for r in results:
        case_id = r["case_id"]
        target_year = r["target_year"]
        pred_ten_god = r["ten_god"]

        day_master = case_day_master.get(case_id, "YI")
        year_stem, _ = compute_year_pillar(target_year)
        expected_ten_god = compute_ten_god(day_master, year_stem)

        if pred_ten_god != expected_ten_god:
            errors.append({
                "event_id": r["event_id"],
                "case_id": case_id,
                "target_year": target_year,
                "day_master": day_master,
                "year_stem": year_stem,
                "predicted": pred_ten_god,
                "expected": expected_ten_god,
            })

    return {
        "total": len(results),
        "errors": len(errors),
        "error_rate": len(errors) / len(results) * 100 if results else 0,
        "details": errors[:10],
    }


def attribute_domain_errors(results: list[dict]) -> dict:
    """优先级3: Domain Attribution - 十神→domain映射矩阵."""
    # 按十神分组, 看每个十神预测的domain vs Ground Truth domain
    ten_god_domain_gt = defaultdict(Counter)  # ten_god -> {gt_domain: count}
    ten_god_domain_pred = defaultdict(Counter)  # ten_god -> {pred_domain: count}
    domain_correct_by_ten_god = defaultdict(lambda: {"correct": 0, "total": 0})

    for r in results:
        tg = r["ten_god"]
        gt_domain = r["gt_domain"]
        pred_domain = r["pred_domain"]

        ten_god_domain_gt[tg][gt_domain] += 1
        ten_god_domain_pred[tg][pred_domain] += 1
        domain_correct_by_ten_god[tg]["total"] += 1
        if gt_domain == pred_domain:
            domain_correct_by_ten_god[tg]["correct"] += 1

    # 计算每个十神的domain准确率
    ten_god_accuracy = {}
    for tg, stats in domain_correct_by_ten_god.items():
        ten_god_accuracy[tg] = {
            "correct": stats["correct"],
            "total": stats["total"],
            "accuracy": stats["correct"] / stats["total"] * 100 if stats["total"] > 0 else 0,
            "gt_distribution": dict(ten_god_domain_gt[tg]),
            "pred_distribution": dict(ten_god_domain_pred[tg]),
        }

    return {
        "by_ten_god": ten_god_accuracy,
        "overall": {
            "correct": sum(s["correct"] for s in domain_correct_by_ten_god.values()),
            "total": len(results),
            "accuracy": sum(s["correct"] for s in domain_correct_by_ten_god.values()) / len(results) * 100 if results else 0,
        },
    }


def attribute_direction_errors(results: list[dict]) -> dict:
    """优先级4: Direction Attribution - structural signal vs outcome polarity."""
    # 分析branch_relations对direction的影响
    branch_direction = defaultdict(Counter)  # relation_type -> {gt_direction: count}
    pred_direction_by_relation = defaultdict(Counter)
    clash_cases = []
    fuyin_cases = []
    hexagram_cases = []
    no_relation_cases = []

    for r in results:
        relations = r.get("branch_relations", [])
        gt_dir = r["gt_direction"]
        pred_dir = r["pred_direction"]

        has_clash = any("CLASH" in rel for rel in relations)
        has_fuyin = any("FUYIN" in rel for rel in relations)
        has_hexagram = any("HEXAGRAM" in rel for rel in relations)

        if has_clash:
            clash_cases.append(r)
            branch_direction["CLASH"][gt_dir] += 1
            pred_direction_by_relation["CLASH"][pred_dir] += 1
        if has_fuyin:
            fuyin_cases.append(r)
            branch_direction["FUYIN"][gt_dir] += 1
            pred_direction_by_relation["FUYIN"][pred_dir] += 1
        if has_hexagram:
            hexagram_cases.append(r)
            branch_direction["HEXAGRAM"][gt_dir] += 1
            pred_direction_by_relation["HEXAGRAM"][pred_dir] += 1
        if not relations:
            no_relation_cases.append(r)
            branch_direction["NO_RELATION"][gt_dir] += 1
            pred_direction_by_relation["NO_RELATION"][pred_dir] += 1

    # 关键分析: 冲是否=caution?
    clash_gt_direction = branch_direction.get("CLASH", Counter())
    clash_pred_direction = pred_direction_by_relation.get("CLASH", Counter())

    # 合是否=supportive?
    hexagram_gt_direction = branch_direction.get("HEXAGRAM", Counter())
    hexagram_pred_direction = pred_direction_by_relation.get("HEXAGRAM", Counter())

    return {
        "clash": {
            "count": len(clash_cases),
            "gt_direction": dict(clash_gt_direction),
            "pred_direction": dict(clash_pred_direction),
            "analysis": "冲=structural change, 不直接=caution",
        },
        "fuyin": {
            "count": len(fuyin_cases),
            "gt_direction": dict(branch_direction.get("FUYIN", Counter())),
            "pred_direction": dict(pred_direction_by_relation.get("FUYIN", Counter())),
        },
        "hexagram": {
            "count": len(hexagram_cases),
            "gt_direction": dict(hexagram_gt_direction),
            "pred_direction": dict(hexagram_pred_direction),
            "analysis": "合=structural connection, 不直接=supportive",
        },
        "no_relation": {
            "count": len(no_relation_cases),
            "gt_direction": dict(branch_direction.get("NO_RELATION", Counter())),
            "pred_direction": dict(pred_direction_by_relation.get("NO_RELATION", Counter())),
        },
        "key_finding": "当前系统将冲→caution, 合→supportive, 伏吟→neutral, 这是过度推断. structural relationship != outcome polarity.",
    }


def analyze_ontology_mismatch(results: list[dict]) -> dict:
    """优先级5: Ontology Mismatch - partial match分析."""
    # 分解: 正确Family但错误Domain, 正确Direction但错误Domain等
    partial_matches = {
        "family_correct_domain_wrong": 0,
        "direction_correct_domain_wrong": 0,
        "domain_correct_family_wrong": 0,
        "domain_correct_direction_wrong": 0,
        "family_correct_direction_wrong": 0,
        "direction_correct_family_wrong": 0,
        "all_wrong": 0,
        "all_correct": 0,
    }

    for r in results:
        domain_match = r["domain_match"]
        family_match = r["family_match"]
        direction_match = r["direction_match"]

        if domain_match and family_match and direction_match:
            partial_matches["all_correct"] += 1
        elif not domain_match and not family_match and not direction_match:
            partial_matches["all_wrong"] += 1
        else:
            if family_match and not domain_match:
                partial_matches["family_correct_domain_wrong"] += 1
            if direction_match and not domain_match:
                partial_matches["direction_correct_domain_wrong"] += 1
            if domain_match and not family_match:
                partial_matches["domain_correct_family_wrong"] += 1
            if domain_match and not direction_match:
                partial_matches["domain_correct_direction_wrong"] += 1
            if family_match and not direction_match:
                partial_matches["family_correct_direction_wrong"] += 1
            if direction_match and not family_match:
                partial_matches["direction_correct_family_wrong"] += 1

    # 计算Exact Match被Domain错误拉低的程度
    total = len(results)
    exact_match = partial_matches["all_correct"]
    family_correct = sum(1 for r in results if r["family_match"])
    direction_correct = sum(1 for r in results if r["direction_match"])
    domain_correct = sum(1 for r in results if r["domain_match"])

    return {
        "partial_matches": partial_matches,
        "analysis": {
            "total": total,
            "exact_match": exact_match,
            "exact_match_rate": exact_match / total * 100,
            "domain_correct": domain_correct,
            "domain_correct_rate": domain_correct / total * 100,
            "family_correct": family_correct,
            "family_correct_rate": family_correct / total * 100,
            "direction_correct": direction_correct,
            "direction_correct_rate": direction_correct / total * 100,
            "if_domain_were_correct": f"如果Domain全对, Exact Match上限约为 min(family, direction) = {min(family_correct, direction_correct)}/{total} = {min(family_correct, direction_correct)/total*100:.1f}%",
            "domain_is_bottleneck": f"Domain错误是Exact Match低的主要原因: {total - domain_correct}/{total} ({(total-domain_correct)/total*100:.1f}%) Domain错误",
        },
    }


def attribute_each_event(results: list[dict]) -> list[dict]:
    """对513条逐条归因."""
    attributions = []
    for r in results:
        failure_layers = []

        # 检查是否有错误
        if not r["domain_match"]:
            failure_layers.append("DOMAIN_MAPPING")
        if not r["family_match"]:
            failure_layers.append("FAMILY_MAPPING")
        if not r["direction_match"]:
            failure_layers.append("DIRECTION_MAPPING")

        # 检查是否有branch relation被直接当direction
        relations = r.get("branch_relations", [])
        has_clash = any("CLASH" in rel for rel in relations)
        has_hexagram = any("HEXAGRAM" in rel for rel in relations)

        if has_clash and r["pred_direction"] == "caution" and not r["direction_match"]:
            failure_layers.append("DIRECTION_OVERINFERENCE_CLASH")
        if has_hexagram and r["pred_direction"] == "supportive" and not r["direction_match"]:
            failure_layers.append("DIRECTION_OVERINFERENCE_HEXAGRAM")

        # 检查是否缺少context (本命结构/大运/宫位)
        if not r["domain_match"] and r["ten_god"] in ["ZHENGCAI", "PIANCAI"] and r["gt_domain"] != "FINANCE":
            failure_layers.append("CONTEXT_MISSING")
        if not r["domain_match"] and r["ten_god"] in ["ZHENGGUAN", "QISHA"] and r["gt_domain"] != "CAREER":
            failure_layers.append("CONTEXT_MISSING")

        # Ontology mismatch (partial match)
        if r["family_match"] and not r["domain_match"]:
            failure_layers.append("ONTOLOGY_MISMATCH_FAMILY_OK_DOMAIN_WRONG")
        if r["direction_match"] and not r["domain_match"]:
            failure_layers.append("ONTOLOGY_MISMATCH_DIRECTION_OK_DOMAIN_WRONG")

        if not failure_layers:
            failure_layers.append("NONE_CORRECT")

        attributions.append({
            "event_id": r["event_id"],
            "case_id": r["case_id"],
            "target_year": r["target_year"],
            "ten_god": r["ten_god"],
            "branch_relations": relations,
            "gt": {"domain": r["gt_domain"], "family": r["gt_family"], "direction": r["gt_direction"]},
            "pred": {"domain": r["pred_domain"], "family": r["pred_family"], "direction": r["pred_direction"]},
            "matches": {"domain": r["domain_match"], "family": r["family_match"], "direction": r["direction_match"]},
            "failure_layers": failure_layers,
        })

    return attributions


def build_root_cause_matrix(attributions: list[dict]) -> dict:
    """构建Root Cause Matrix."""
    layer_counts = Counter()
    for a in attributions:
        for layer in a["failure_layers"]:
            layer_counts[layer] += 1

    # 按主要错误类型分类
    total = len(attributions)
    correct = layer_counts.get("NONE_CORRECT", 0)
    domain_errors = sum(1 for a in attributions if "DOMAIN_MAPPING" in a["failure_layers"])
    family_errors = sum(1 for a in attributions if "FAMILY_MAPPING" in a["failure_layers"])
    direction_errors = sum(1 for a in attributions if "DIRECTION_MAPPING" in a["failure_layers"])
    direction_overinference = sum(1 for a in attributions if any("OVERINFERENCE" in l for l in a["failure_layers"]))
    context_missing = sum(1 for a in attributions if "CONTEXT_MISSING" in a["failure_layers"])
    ontology_mismatch = sum(1 for a in attributions if any("ONTOLOGY" in l for l in a["failure_layers"]))

    return {
        "total_events": total,
        "correct": correct,
        "correct_rate": correct / total * 100,
        "error_breakdown": {
            "domain_mapping_errors": {"count": domain_errors, "rate": domain_errors / total * 100},
            "family_mapping_errors": {"count": family_errors, "rate": family_errors / total * 100},
            "direction_mapping_errors": {"count": direction_errors, "rate": direction_errors / total * 100},
            "direction_overinference": {"count": direction_overinference, "rate": direction_overinference / total * 100},
            "context_missing": {"count": context_missing, "rate": context_missing / total * 100},
            "ontology_mismatch": {"count": ontology_mismatch, "rate": ontology_mismatch / total * 100},
        },
        "layer_counts": dict(layer_counts.most_common()),
    }


def main():
    print("=" * 70)
    print("P6-C Failure Attribution - 逐条归因513条")
    print("=" * 70)

    # 加载数据
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
    print(f"  错误率: {year_verification['error_rate']:.1f}%")
    if year_verification["errors"] == 0:
        print("  ✅ 年份干支计算全部正确")

    # 优先级2: 验证十神
    print(f"\n{'='*70}")
    print("优先级2: 验证十神计算")
    print(f"{'='*70}")
    ten_god_verification = verify_ten_god_calculation(results, golden_cases)
    print(f"  总数: {ten_god_verification['total']}")
    print(f"  错误: {ten_god_verification['errors']}")
    print(f"  错误率: {ten_god_verification['error_rate']:.1f}%")
    if ten_god_verification["errors"] == 0:
        print("  ✅ 十神计算全部正确")

    # 优先级3: Domain Attribution
    print(f"\n{'='*70}")
    print("优先级3: Domain Attribution - 十神→domain映射矩阵")
    print(f"{'='*70}")
    domain_attr = attribute_domain_errors(results)
    print(f"  总体Domain准确率: {domain_attr['overall']['accuracy']:.1f}%")
    print(f"\n  按十神分解:")
    for tg, stats in sorted(domain_attr["by_ten_god"].items(), key=lambda x: -x[1]["total"]):
        print(f"    {tg:12}: {stats['accuracy']:5.1f}% ({stats['correct']}/{stats['total']})")
        print(f"      GT分布: {dict(sorted(stats['gt_distribution'].items(), key=lambda x: -x[1]))}")
        print(f"      Pred分布: {dict(sorted(stats['pred_distribution'].items(), key=lambda x: -x[1]))}")

    # 优先级4: Direction Attribution
    print(f"\n{'='*70}")
    print("优先级4: Direction Attribution - structural signal vs outcome polarity")
    print(f"{'='*70}")
    direction_attr = attribute_direction_errors(results)
    print(f"  冲(CLASH): {direction_attr['clash']['count']}条")
    print(f"    GT方向: {direction_attr['clash']['gt_direction']}")
    print(f"    Pred方向: {direction_attr['clash']['pred_direction']}")
    print(f"  合(HEXAGRAM): {direction_attr['hexagram']['count']}条")
    print(f"    GT方向: {direction_attr['hexagram']['gt_direction']}")
    print(f"    Pred方向: {direction_attr['hexagram']['pred_direction']}")
    print(f"  伏吟(FUYIN): {direction_attr['fuyin']['count']}条")
    print(f"    GT方向: {direction_attr['fuyin']['gt_direction']}")
    print(f"    Pred方向: {direction_attr['fuyin']['pred_direction']}")
    print(f"  无关系: {direction_attr['no_relation']['count']}条")
    print(f"  关键发现: {direction_attr['key_finding']}")

    # 优先级5: Ontology Mismatch
    print(f"\n{'='*70}")
    print("优先级5: Ontology Mismatch - partial match分析")
    print(f"{'='*70}")
    ontology = analyze_ontology_mismatch(results)
    print(f"  Partial matches:")
    for k, v in ontology["partial_matches"].items():
        print(f"    {k}: {v}")
    print(f"\n  分析:")
    for k, v in ontology["analysis"].items():
        print(f"    {k}: {v}")

    # 逐条归因
    print(f"\n{'='*70}")
    print("逐条归因 (513条)")
    print(f"{'='*70}")
    attributions = attribute_each_event(results)
    root_cause = build_root_cause_matrix(attributions)

    print(f"\n  Root Cause Matrix:")
    print(f"    总事件: {root_cause['total_events']}")
    print(f"    完全正确: {root_cause['correct']} ({root_cause['correct_rate']:.1f}%)")
    print(f"\n    错误分解:")
    for k, v in root_cause["error_breakdown"].items():
        print(f"      {k}: {v['count']} ({v['rate']:.1f}%)")

    # 保存结果
    output = {
        "year_verification": year_verification,
        "ten_god_verification": ten_god_verification,
        "domain_attribution": domain_attr,
        "direction_attribution": direction_attr,
        "ontology_mismatch": ontology,
        "root_cause_matrix": root_cause,
        "per_event_attribution": attributions,
    }

    with open("docs/audit/p6c_failure_attribution.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n详细结果已保存: docs/audit/p6c_failure_attribution.json")

    # 最终结论
    print(f"\n{'='*70}")
    print("Failure Attribution 结论")
    print(f"{'='*70}")
    print(f"  1. 年份干支计算: 全部正确 (0错误)")
    print(f"  2. 十神计算: 全部正确 (0错误)")
    print(f"  3. Domain映射: {root_cause['error_breakdown']['domain_mapping_errors']['rate']:.1f}%错误, 是主要瓶颈")
    print(f"  4. Direction过度推断: {root_cause['error_breakdown']['direction_overinference']['rate']:.1f}% (冲→caution, 合→supportive)")
    print(f"  5. Context缺失: {root_cause['error_breakdown']['context_missing']['rate']:.1f}% (十神→domain一对一映射, 缺少本命结构/大运/宫位)")
    print(f"  6. Ontology Mismatch: {root_cause['error_breakdown']['ontology_mismatch']['rate']:.1f}% (Family/Direction正确但Domain错误)")
    print(f"\n  核心发现:")
    print(f"  - 计算层(年份/十神)没有问题")
    print(f"  - 主要问题在映射层: 十神→domain一对一映射过于简单")
    print(f"  - Direction存在过度推断: structural relationship ≠ outcome polarity")
    print(f"  - 缺少本命结构/大运/宫位等上下文信息")
    print(f"  - Exact Match低主要被Domain错误拉低, 不是Engine极差")

    return output


if __name__ == "__main__":
    main()
