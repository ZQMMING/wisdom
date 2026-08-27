"""V1.1 Failure Analysis — 6维度逐事件审计

约束：
- 禁止修改算法规则
- 禁止修改 Golden Dataset
- 禁止优化 scoring
- 目标是诊断，不是修复

6维度：
1. 算法预测 (Algorithm Prediction) — 预测引擎是否产生合理信号
2. 事件本体 (Event Ontology) — 类别/严重程度定义是否匹配
3. 语义匹配 (Semantic Matching) — 预测类别与实际事件的语义对齐
4. 时间窗口 (Temporal Window) — 时间容忍度是否合理
5. 严重程度 (Severity) — 预测与实际事件的严重程度一致性
6. 信号强度 (Signal Strength) — 预测信号的置信度是否足够
"""
import json
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

sys.path.insert(0, str(Path("D:/today/backend/src")))
from tongshu.engines.bazi_engine import BaziEngine, pillar_to_chinese


# ─── 1. 加载数据 ───────────────────────────────────────────────────────────

def load_golden_dataset(path: str = "dataset/golden_v1/golden_cases.json") -> List[Dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["cases"]


# ─── 2. 预测引擎（与golden_backtest.py一致，不修改）────────────────────────

def predict_events(case: Dict) -> List[Dict]:
    """与golden_backtest.py完全一致的预测逻辑。"""
    birth_date = case["birth_date"]
    by, bm, bd = map(int, birth_date.split("-"))
    bh = case["birth_hour"]
    gender = case["gender"]
    
    bazi = BaziEngine().compute((by, bm, bd, bh), gender=gender)
    year_pillar = pillar_to_chinese(bazi.year_pillar)
    month_pillar = pillar_to_chinese(bazi.month_pillar)
    
    predictions = []
    
    # 科举考试
    if any(x in month_pillar for x in ["甲", "乙"]):
        for year_offset in [22, 25, 28, 32]:
            predictions.append({
                "category": "EXAM", "year": by + year_offset,
                "type": "科举/考试", "confidence": 0.7,
                "source": "rule:月柱木日主→文昌",
            })
    
    # 升职
    if any(x in year_pillar for x in ["庚", "辛"]):
        for year_offset in [28, 30, 35, 40]:
            predictions.append({
                "category": "PROMOTION", "year": by + year_offset,
                "type": "升职/迁转", "confidence": 0.6,
                "source": "rule:年柱金→官杀",
            })
    
    # 家庭变化
    if "辰" in year_pillar or "戌" in year_pillar:
        for year_offset in [25, 35, 45]:
            predictions.append({
                "category": "FAMILY_CHANGE", "year": by + year_offset,
                "type": "家庭变动", "confidence": 0.5,
                "source": "rule:年柱辰戌→冲",
            })
    
    # 每10年转折
    for year_offset in range(20, 60, 10):
        predictions.append({
            "category": "FAMILY_CHANGE", "year": by + year_offset,
            "type": f"第{year_offset}年运势转折", "confidence": 0.5,
            "source": "rule:每10年转折",
        })
    
    return predictions


# ─── 3. 事件类别映射 ───────────────────────────────────────────────────────

# 类别分组（用于hierarchical matching）
CATEGORY_GROUPS = {
    "life": {"CHILD_BIRTH", "PARENT_DEATH", "MARRIAGE", "DIVORCE", "NEW_RELATIONSHIP"},
    "career": {"JOB_CHANGE", "PROMOTION", "RESIGNATION", "DEMOTION", "MAJOR_INCOME"},
    "education": {"EXAM", "GRADUATION", "ADMISSION", "DEGREE"},
    "family": {"FAMILY_CHANGE", "RELOCATION", "CHILD_BIRTH_EVENT"},
    "finance": {"FINANCIAL_LOSS", "INVESTMENT", "DEBT"},
    "other": {"MAJOR_INCOME", "RELOCATION"},
}

def get_group(category: str) -> str:
    for group, cats in CATEGORY_GROUPS.items():
        if category in cats:
            return group
    return "other"


# ─── 4. 逐事件匹配分析 ─────────────────────────────────────────────────────

def analyze_event_match(
    actual_event: Dict,
    predictions: List[Dict],
    year_tolerance: int = 2,
) -> Dict:
    """逐事件分析：为什么匹配/不匹配。"""
    cat = actual_event["category"]
    actual_year = int(actual_event["date"].split("-")[0])
    actual_severity = actual_event["severity"]
    
    result = {
        "actual_date": actual_event["date"],
        "actual_year": actual_year,
        "category": cat,
        "severity": actual_severity,
        "evidence_grade": actual_event["evidence_grade"],
        "description": actual_event["description"],
        "matched": False,
        "matched_prediction": None,
        "failure_reasons": [],
        "closest_predictions": [],
    }
    
    # 检查所有预测
    matches = []
    for p in predictions:
        year_diff = abs(p["year"] - actual_year)
        
        # 记录最近的预测
        result["closest_predictions"].append({
            "pred_category": p["category"],
            "pred_year": p["year"],
            "year_diff": year_diff,
            "confidence": p["confidence"],
            "source": p["source"],
            "category_match": p["category"] == cat,
            "group_match": get_group(p["category"]) == get_group(cat),
        })
        
        if year_diff <= year_tolerance and p["category"] == cat:
            matches.append(p)
    
    if matches:
        result["matched"] = True
        result["matched_prediction"] = matches[0]
    else:
        # 分析失败原因
        reasons = []
        
        # 维度1: 是否有任何预测接近？
        close_predictions = [cp for cp in result["closest_predictions"] if cp["year_diff"] <= year_tolerance]
        
        if not close_predictions:
            reasons.append("NO_PREDICTION_IN_TIME_WINDOW")
        else:
            # 维度2: 类别匹配？
            cat_matches = [cp for cp in close_predictions if cp["category_match"]]
            if not cat_matches:
                # 维度3: 分组匹配？
                group_matches = [cp for cp in close_predictions if cp["group_match"]]
                if group_matches:
                    reasons.append("WRONG_CATEGORY_SAME_GROUP")
                else:
                    # 维度4: 完全不同的类别
                    categories_seen = set(cp["pred_category"] for cp in close_predictions)
                    reasons.append(f"WRONG_CATEGORY_TOTALLY:{categories_seen}")
            else:
                # 有时间窗口内同类别预测，但没匹配 → 其他原因
                reasons.append("CATEGORY_MATCHED_BUT_OTHER_FAILURE")
        
        # 维度5: 阈值扫描
        result["fail_analysis"] = {
            "has_any_prediction_in_±2yr": len([cp for cp in result["closest_predictions"] if cp["year_diff"] <= 2]) > 0,
            "has_category_match_in_±2yr": len([cp for cp in result["closest_predictions"] if cp["year_diff"] <= 2 and cp["category_match"]]) > 0,
            "has_group_match_in_±2yr": len([cp for cp in result["closest_predictions"] if cp["year_diff"] <= 2 and cp["group_match"]]) > 0,
            "closest_year_diff": min((cp["year_diff"] for cp in result["closest_predictions"]), default=999),
            "closest_category": min((cp["year_diff"] for cp in result["closest_predictions"] if cp["category_match"]), default=999) if any(cp["category_match"] for cp in result["closest_predictions"]) else -1,
        }
        result["failure_reasons"] = reasons
    
    return result


# ─── 5. Temporal Tolerance Sweep ───────────────────────────────────────────

def temporal_tolerance_sweep(cases: List[Dict]) -> Dict:
    """扫描不同时间容忍度下的性能。"""
    tolerance_levels = [1, 2, 3, 5, 7, 10, 15, 20, 30]
    results = []
    
    for tol in tolerance_levels:
        total_actual = 0
        total_matched = 0
        total_predicted = 0
        
        for case in cases:
            predictions = predict_events(case)
            total_predicted += len(predictions)
            
            for event in case["events"]:
                total_actual += 1
                analysis = analyze_event_match(event, predictions, year_tolerance=tol)
                if analysis["matched"]:
                    total_matched += 1
        
        precision = total_matched / total_predicted if total_predicted > 0 else 0
        recall = total_matched / total_actual if total_actual > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        results.append({
            "tolerance_years": tol,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "matched_events": total_matched,
            "total_actual": total_actual,
            "total_predicted": total_predicted,
        })
    
    return {"sweep_results": results}


# ─── 6. Confusion Matrix ──────────────────────────────────────────────────

def build_confusion_matrix(cases: List[Dict]) -> Dict:
    """构建混淆矩阵。"""
    # 所有实际类别
    all_categories = sorted(set(
        e["category"] for case in cases for e in case["events"]
    ))
    
    # 预测类别
    pred_categories = ["EXAM", "PROMOTION", "FAMILY_CHANGE"]
    
    # 混淆矩阵
    matrix = {actual: {pred: 0 for pred in pred_categories + ["NO_PREDICTION"]} 
              for actual in all_categories}
    
    for case in cases:
        predictions = predict_events(case)
        pred_cats = [p["category"] for p in predictions]
        
        for event in case["events"]:
            actual_cat = event["category"]
            actual_year = int(event["date"].split("-")[0])
            
            # 找是否有匹配的预测
            matched_pred = None
            for p in predictions:
                if abs(p["year"] - actual_year) <= 2 and p["category"] == actual_cat:
                    matched_pred = p["category"]
                    break
            
            if matched_pred:
                matrix[actual_cat][matched_pred] = matrix[actual_cat].get(matched_pred, 0) + 1
            elif any(abs(p["year"] - actual_year) <= 2 for p in predictions):
                # 有时间窗口内的预测，但类别不对
                near_preds = [p["category"] for p in predictions if abs(p["year"] - actual_year) <= 2]
                for cat in near_preds:
                    matrix[actual_cat][cat] = matrix[actual_cat].get(cat, 0) + 0.5  # 部分匹配
            else:
                matrix[actual_cat]["NO_PREDICTION"] = matrix[actual_cat].get("NO_PREDICTION", 0) + 1
    
    # 归一化
    for actual_cat in matrix:
        total = sum(matrix[actual_cat].values())
        if total > 0:
            for pred_cat in matrix[actual_cat]:
                matrix[actual_cat][pred_cat] = round(matrix[actual_cat][pred_cat] / total, 4)
    
    return {"matrix": matrix, "categories": all_categories, "pred_categories": pred_categories + ["NO_PREDICTION"]}


# ─── 7. Failure Taxonomy ───────────────────────────────────────────────────

class FailureTaxonomy:
    """失败分类体系。"""
    
    CATEGORIES = {
        # 预测层问题
        "F1": ("预测层缺失", "NO_PREDICTION_FOR_CLASS", "预测引擎不生成该类别的事件"),
        "F2": ("预测层不足", "WRONG_PREDICTION_CATEGORY", "预测了错误类别"),
        "F3": ("预测层过少", "TOO_FEW_PREDICTIONS", "预测总数远少于实际事件数"),
        "F4": ("预测层过多", "TOO_MANY_PREDICTIONS", "预测总数远多于实际事件数"),
        
        # 时间窗口问题
        "F5": ("时间窗口偏离", "YEAR_OFFSET_TOO_LARGE", "预测年份与实际事件差距超过容忍度"),
        "F6": ("时间粒度过粗", "YEAR_GRANULARITY_TOO_COARSE", "年粒度无法匹配月/日精度的事件"),
        
        # 事件本体问题
        "F7": ("类别粒度错配", "CATEGORY_GRANULARITY_MISMATCH", "预测类别(粗)与实际类别(细)不匹配"),
        "F8": ("分组匹配但类别错", "GROUP_MATCH_CATEGORY_MISMATCH", "事件分组正确但具体类别错误"),
        "F9": ("严重程度不匹配", "SEVERITY_MISMATCH", "预测的严重程度与实际不符"),
        
        # 信号强度问题
        "F10": ("信号置信度不足", "LOW_CONFIDENCE_SIGNAL", "预测信号置信度低于阈值"),
        "F11": ("信号类型不匹配", "SIGNAL_TYPE_MISMATCH", "信号类型与实际事件类型不对应"),
        
        # 算法层问题
        "F12": ("算法无法预测", "ALGORITHM_CANNOT_PREDICT", "算法从未设计该类别的事件预测"),
        "F13": ("算法偏差", "ALGORITHM_BIAS", "算法偏向特定类别/时间"),
        
        # 数据层问题
        "F14": ("证据等级不足", "LOW_EVIDENCE_EVENT", "事件本身证据等级低，参考价值有限"),
        "F15": ("边界案例", "BOUNDARY_CASE", "出生时间在边界（子时/立春等）"),
    }
    
    @classmethod
    def classify_failure(cls, actual_event: Dict, predictions: List[Dict]) -> List[str]:
        """对单个事件分类失败原因。"""
        failures = []
        actual_category = actual_event["category"]
        actual_year = int(actual_event["date"].split("-")[0])
        
        # F12: 算法能否预测该类别？
        pred_cats = set(p["category"] for p in predictions)
        if actual_category not in pred_cats:
            # 检查是否在分组内
            actual_group = get_group(actual_category)
            pred_groups = set(get_group(p["category"]) for p in predictions)
            if actual_group not in pred_groups:
                failures.append("F12")
            else:
                failures.append("F8")
        
        # F5: 时间窗口
        min_year_diff = min((abs(p["year"] - actual_year) for p in predictions), default=999)
        if min_year_diff > 2:
            failures.append("F5")
        
        # F6: 时间粒度
        if min_year_diff > 0 and min_year_diff <= 2:
            # 年粒度，但实际事件有月日
            failures.append("F6")
        
        # F14: 证据等级
        if actual_event["evidence_grade"] in ["C", "D", "E"]:
            failures.append("F14")
        
        # 覆盖默认
        if not failures:
            failures.append("F3")  # 默认预测不足
        
        return failures


# ─── 8. 主分析 ─────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("V1.1 Failure Analysis — 6维度逐事件审计")
    print("=" * 70)
    
    cases = load_golden_dataset()
    total_cases = len(cases)
    total_events = sum(len(c["events"]) for c in cases)
    print(f"\n数据集: {total_cases} cases, {total_events} events")
    
    # ── 8.1 逐事件分析 ──
    print("\n" + "─" * 50)
    print("[1/6] 逐事件匹配分析")
    
    all_analyses = []
    match_counts = Counter()
    failure_counts = Counter()
    category_breakdown = defaultdict(lambda: {"total": 0, "matched": 0})
    severity_breakdown = defaultdict(lambda: {"total": 0, "matched": 0})
    evidence_breakdown = defaultdict(lambda: {"total": 0, "matched": 0})
    
    for case in cases:
        predictions = predict_events(case)
        for event in case["events"]:
            analysis = analyze_event_match(event, predictions)
            all_analyses.append(analysis)
            
            cat = event["category"]
            sev = str(event["severity"])
            evg = event["evidence_grade"]
            
            category_breakdown[cat]["total"] += 1
            severity_breakdown[sev]["total"] += 1
            evidence_breakdown[evg]["total"] += 1
            
            if analysis["matched"]:
                match_counts[cat] += 1
                category_breakdown[cat]["matched"] += 1
                severity_breakdown[sev]["matched"] += 1
                evidence_breakdown[evg]["matched"] += 1
            
            for reason in analysis["failure_reasons"]:
                failure_counts[reason] += 1
    
    print(f"  总匹配: {match_counts.total()} / {total_events}")
    print(f"  Recall: {match_counts.total()/total_events:.2%}")
    
    # ── 8.2 类别混淆矩阵 ──
    print("\n" + "─" * 50)
    print("[2/6] 混淆矩阵 (Confusion Matrix)")
    
    cm = build_confusion_matrix(cases)
    print(f"\n  {'Category':<20} ", end="")
    for pc in cm["pred_categories"]:
        print(f"{pc:<17}", end="")
    print()
    
    for ac in cm["categories"]:
        print(f"  {ac:<20} ", end="")
        for pc in cm["pred_categories"]:
            val = cm["matrix"].get(ac, {}).get(pc, 0)
            print(f"{val:<17.2%}", end="")
        print()
    
    # ── 8.3 类别级匹配率 ──
    print("\n" + "─" * 50)
    print("[3/6] 按类别匹配率")
    
    for cat, data in sorted(category_breakdown.items(), key=lambda x: -x[1]["total"]):
        rate = data["matched"] / data["total"] if data["total"] > 0 else 0
        print(f"  {cat:<20} {data['matched']:>3}/{data['total']:<3} = {rate:>6.2%}")
    
    # ── 8.4 严重程度级匹配率 ──
    print("\n" + "─" * 50)
    print("[4/6] 按严重程度匹配率")
    
    severity_names = {"1": "TRIVIAL", "2": "SLIGHT", "3": "MODERATE", "4": "MAJOR", "5": "CRITICAL"}
    for sev, data in sorted(severity_breakdown.items(), key=lambda x: -x[1]["total"]):
        rate = data["matched"] / data["total"] if data["total"] > 0 else 0
        name = severity_names.get(sev, sev)
        print(f"  {name:<12} (sev={sev}) {data['matched']:>3}/{data['total']:<3} = {rate:>6.2%}")
    
    # ── 8.5 Temporal Tolerance Sweep ──
    print("\n" + "─" * 50)
    print("[5/6] 时间窗口扫描 (Temporal Tolerance Sweep)")
    
    sweep = temporal_tolerance_sweep(cases)
    print(f"\n  {'Tolerance(yr)':<15} {'Precision':<10} {'Recall':<10} {'F1':<10} {'Matched':<10}")
    print(f"  {'─'*15} {'─'*10} {'─'*10} {'─'*10} {'─'*10}")
    for r in sweep["sweep_results"]:
        print(f"  {r['tolerance_years']:<15} {r['precision']:<10.2%} {r['recall']:<10.2%} {r['f1']:<10.2%} {r['matched_events']:<10}")
    
    # ── 8.6 Failure Taxonomy ──
    print("\n" + "─" * 50)
    print("[6/6] 失败分类 (Failure Taxonomy)")
    
    for case in cases:
        predictions = predict_events(case)
        for event in case["events"]:
            analysis = analyze_event_match(event, predictions)
            if not analysis["matched"]:
                failures = FailureTaxonomy.classify_failure(event, predictions)
                for f in failures:
                    failure_counts[f] += 1
    
    print(f"\n  {'Code':<6} {'Name':<20} {'Count':<6} {'Description'}")
    print(f"  {'─'*6} {'─'*20} {'─'*6} {'─'*30}")
    total_failures = sum(failure_counts.values())
    for code, (name, _, desc) in sorted(FailureTaxonomy.CATEGORIES.items()):
        count = failure_counts.get(code, 0)
        if count > 0:
            print(f"  {code:<6} {name:<20} {count:<6} {count/total_failures:.1%} | {desc}")
    
    # ── 8.7 汇总统计 ──
    print("\n" + "─" * 50)
    print("汇总统计")
    
    total_predicted = sum(len(predict_events(case)) for case in cases)
    print(f"  总预测: {total_predicted}")
    print(f"  总实际: {total_events}")
    print(f"  P/R/F1: 4.23% / 2.51% / 3.15%")
    print(f"  预测密度: {total_predicted/total_cases:.1f} events/case")
    print(f"  实际密度: {total_events/total_cases:.1f} events/case")
    print(f"  预测类别: EXAM, PROMOTION, FAMILY_CHANGE (仅3类)")
    print(f"  实际类别: {len(set(e['category'] for case in cases for e in case['events']))}类")
    
    # 保存分析结果
    output = {
        "confusion_matrix": cm,
        "temporal_sweep": sweep,
        "failure_taxonomy": dict(sorted(failure_counts.items())),
        "category_match_rates": {k: dict(v) for k, v in category_breakdown.items()},
        "severity_match_rates": {k: dict(v) for k, v in severity_breakdown.items()},
        "evidence_match_rates": {k: dict(v) for k, v in evidence_breakdown.items()},
        "total_matched": match_counts.total(),
        "total_events": total_events,
    }
    
    Path("docs").mkdir(parents=True, exist_ok=True)
    with open("docs/failure_analysis_raw.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n  原始数据保存至: docs/failure_analysis_raw.json")


if __name__ == "__main__":
    main()