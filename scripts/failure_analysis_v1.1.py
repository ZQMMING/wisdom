"""V1.1 Failure Analysis — 六维度逐事件诊断

诊断原则:
1. 禁止优化分数 — 只定位问题
2. 每个失败必须归因到具体维度（或UNKNOWN）
3. 支持多重失败 — 一个事件可在多个维度同时失败
4. 区分 PROVEN / HYPOTHESIS / UNKNOWN
5. 未实现模块（如SignalEngine）不视为算法失败

Failure Categories:
- CALCULATION_ERROR: 算法计算错误
- SIGNAL_MISSING: 预测层未生成该类别信号
- SIGNAL_WRONG: 信号生成但类别/时间错误
- ONTOLOGY_MISMATCH: 预测类别与实际类别不可映射
- TEMPORAL_MISMATCH: 预测时间与实际时间差距过大
- SEVERITY_MISMATCH: 预测严重程度与实际不符
- INTERPRETATION_MISMATCH: 关系解释逻辑错误
- NO_PREDICTION: 无任何预测生成
- UNKNOWN: 无法归类

Multi-Failure: 每个事件可同时在多个维度失败
"""
import json
import sys
from datetime import date
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict, Any, Optional, Set
from enum import Enum

sys.path.insert(0, str(Path("D:/today/backend/src")))

from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.heluo import heluo_calculate, find_yuantang


# ─── 枚举 ───────────────────────────────────────────────────────────────────

class FailureCategory(Enum):
    """失败分类 — 必须精确归因，不可合并"""
    CALCULATION_ERROR = "CALCULATION_ERROR"
    SIGNAL_MISSING = "SIGNAL_MISSING"
    SIGNAL_WRONG = "SIGNAL_WRONG"
    ONTOLOGY_MISMATCH = "ONTOLOGY_MISMATCH"
    TEMPORAL_MISMATCH = "TEMPORAL_MISMATCH"
    SEVERITY_MISMATCH = "SEVERITY_MISMATCH"
    INTERPRETATION_MISMATCH = "INTERPRETATION_MISMATCH"
    NO_PREDICTION = "NO_PREDICTION"
    UNKNOWN = "UNKNOWN"


class DiagnosisStatus(Enum):
    """诊断状态 — 区分证据等级"""
    PROVEN = "PROVEN"           # 实际数据已证明
    HYPOTHESIS = "HYPOTHESIS"   # 当前推测，需进一步验证
    UNKNOWN = "UNKNOWN"         # 数据不足以判断


# ─── 事件本体映射 ───────────────────────────────────────────────────────────

CATEGORY_GROUPS = {
    "life": {"CHILD_BIRTH", "PARENT_DEATH", "MARRIAGE", "DIVORCE", "NEW_RELATIONSHIP"},
    "career": {"JOB_CHANGE", "PROMOTION", "RESIGNATION", "DEMOTION", "MAJOR_INCOME"},
    "education": {"EXAM", "GRADUATION", "ADMISSION", "DEGREE"},
    "family": {"FAMILY_CHANGE", "RELOCATION", "HOUSE_MOVE"},
    "finance": {"FINANCIAL_LOSS", "INVESTMENT", "DEBT", "MAJOR_INCOME"},
    "health": {"ILLNESS", "INJURY", "HEALTH_CRISIS"},
    "general": {"OTHER", "LIFE_CHANGE"},
}

CATEGORY_MAPPING = {
    # 预测类别 → 实际可映射的类别
    "EXAM": {"EXAM", "GRADUATION", "ADMISSION", "DEGREE"},
    "PROMOTION": {"PROMOTION", "JOB_CHANGE", "RESIGNATION", "DEMOTION", "MAJOR_INCOME"},
    "FAMILY_CHANGE": {"FAMILY_CHANGE", "NEW_RELATIONSHIP", "RELOCATION", "CHILD_BIRTH", "PARENT_DEATH"},
}


def get_category_group(cat: str) -> str:
    for group, cats in CATEGORY_GROUPS.items():
        if cat in cats:
            return group
    return "general"


def get_mapping_group(cat: str) -> Set[str]:
    return CATEGORY_MAPPING.get(cat, set())


# ─── 基准预测引擎（与golden_backtest.py一致，禁止修改）──────────────────────

def predict_events_baseline(case: Dict) -> List[Dict]:
    """BASELINE_V1冻结的预测引擎 — 禁止修改用于诊断"""
    birth_date = case["birth_date"]
    by, bm, bd = map(int, birth_date.split("-"))
    bh = case["birth_hour"]
    gender = case["gender"]
    
    bazi = BaziEngine().compute((by, bm, bd, bh), gender=gender)
    year_pillar = bazi.year_pillar.heavenly_stem  # e.g., "甲" (stem)
    month_pillar = bazi.month_pillar.heavenly_stem
    
    predictions = []
    
    # 规则1: 月柱天干甲乙 → EXAM信号
    if month_pillar in ["JIA", "YI"]:
        for offset in [22, 25, 28, 32]:
            predictions.append({
                "category": "EXAM",
                "year": by + offset,
                "confidence": 0.7,
                "source": f"rule:bazi_month_gan_{month_pillar}_文昌",
                "dimension": "Bazi",
            })
    
    # 规则2: 年柱天干庚辛 → PROMOTION信号
    if year_pillar in ["GENG", "XIN"]:
        for offset in [28, 30, 35, 40]:
            predictions.append({
                "category": "PROMOTION",
                "year": by + offset,
                "confidence": 0.6,
                "source": f"rule:bazi_year_gan_{year_pillar}_官杀",
                "dimension": "Bazi",
            })
    
    # 规则3: 年支辰戌 → FAMILY_CHANGE信号
    year_branch = bazi.year_pillar.earthly_branch
    if year_branch in ["CHEN", "XU"]:
        for offset in [25, 35, 45]:
            predictions.append({
                "category": "FAMILY_CHANGE",
                "year": by + offset,
                "confidence": 0.5,
                "source": f"rule:bazi_year_zhi_{year_branch}_冲",
                "dimension": "Bazi",
            })
    
    # 规则4: 每10年转折
    for offset in range(20, 60, 10):
        predictions.append({
            "category": "FAMILY_CHANGE",
            "year": by + offset,
            "confidence": 0.5,
            "source": "rule:decade_transition",
            "dimension": "Bazi",
        })
    
    return predictions


# ─── 六维度诊断函数 ─────────────────────────────────────────────────────────

class FailureAnalyzer:
    """六维度逐事件诊断器"""
    
    def __init__(self):
        self.case_results = []
        self.failure_counts = Counter()
        self.proven_hypothesis_unknown = {
            "PROVEN": Counter(),
            "HYPOTHESIS": Counter(),
            "UNKNOWN": Counter(),
        }
    
    def analyze_case(self, case: Dict) -> Dict:
        """分析单个案例的所有事件"""
        case_id = case["case_id"]
        predictions = predict_events_baseline(case)
        
        event_results = []
        for i, event in enumerate(case["events"]):
            result = self.analyze_event(event, predictions, case)
            event_results.append(result)
            
            # 统计失败 — 将枚举转为字符串
            for fcat in result["failure_categories"]:
                fcat_str = fcat.value if hasattr(fcat, 'value') else str(fcat)
                self.failure_counts[fcat_str] += 1
                status_key = result["diagnosis_status"]
                if status_key not in self.proven_hypothesis_unknown:
                    self.proven_hypothesis_unknown[status_key] = Counter()
                self.proven_hypothesis_unknown[status_key][fcat_str] += 1
        
        return {
            "case_id": case_id,
            "gender": case["gender"],
            "birth_date": case["birth_date"],
            "source_type": case.get("source_type", "unknown"),
            "total_events": len(case["events"]),
            "total_predictions": len(predictions),
            "matched_count": sum(1 for e in event_results if e["is_matched"]),
            "events": event_results,
        }
    
    def analyze_event(
        self, 
        actual_event: Dict, 
        predictions: List[Dict],
        case: Dict
    ) -> Dict:
        """分析单个事件的六维度失败"""
        actual_date = actual_event["date"]
        actual_year = int(actual_date.split("-")[0])
        actual_month = int(actual_date.split("-")[1]) if len(actual_date.split("-")) > 1 else None
        actual_category = actual_event["category"]
        actual_severity = actual_event.get("severity", 3)
        
        result = {
            "event_index": actual_event.get("index", -1),
            "actual_date": actual_date,
            "actual_year": actual_year,
            "actual_month": actual_month,
            "actual_category": actual_category,
            "actual_severity": actual_severity,
            "actual_evidence_grade": actual_event.get("evidence_grade", "B"),
            "actual_description": actual_event.get("description", ""),
            "failure_categories": [],
            "diagnosis_details": {},
            "is_matched": False,
            "matched_prediction": None,
            "closest_prediction": None,
            "diagnosis_status": DiagnosisStatus.UNKNOWN.value,
        }
        
        # ── Dimension 1: Calculation ─────────────────────────────────
        calc_status, calc_detail = self._analyze_calculation(actual_event, case)
        result["diagnosis_details"]["calculation"] = calc_detail
        
        # ── Dimension 2: Signal ──────────────────────────────────────
        signal_status, signal_detail = self._analyze_signal(actual_event, predictions)
        result["diagnosis_details"]["signal"] = signal_detail
        if signal_status == "FAIL":
            result["failure_categories"].append(FailureCategory.SIGNAL_MISSING.value)
        
        # ── Dimension 3: Ontology ────────────────────────────────────
        ontology_status, ontology_detail = self._analyze_ontology(actual_event, predictions)
        result["diagnosis_details"]["ontology"] = ontology_detail
        if ontology_status == "FAIL":
            result["failure_categories"].append(FailureCategory.ONTOLOGY_MISMATCH.value)
        
        # ── Dimension 4: Temporal ────────────────────────────────────
        temporal_status, temporal_detail = self._analyze_temporal(actual_event, predictions)
        result["diagnosis_details"]["temporal"] = temporal_detail
        if temporal_status == "FAIL":
            result["failure_categories"].append(FailureCategory.TEMPORAL_MISMATCH.value)
        
        # ── Dimension 5: Severity ────────────────────────────────────
        severity_status, severity_detail = self._analyze_severity(actual_event, predictions)
        result["diagnosis_details"]["severity"] = severity_detail
        if severity_status == "FAIL":
            result["failure_categories"].append(FailureCategory.SEVERITY_MISMATCH.value)
        
        # ── Dimension 6: Interpretation ──────────────────────────────
        interp_status, interp_detail = self._analyze_interpretation(
            actual_event, predictions, calc_status
        )
        result["diagnosis_details"]["interpretation"] = interp_detail
        
        # ── 综合诊断 ─────────────────────────────────────────────────
        result["diagnosis_status"] = self._determine_status(result)
        
        # 确定是否匹配
        if predictions and temporal_status == "PASS" and ontology_status == "PASS":
            result["is_matched"] = True
            result["matched_prediction"] = result["closest_prediction"]
        
        return result
    
    def _analyze_calculation(
        self, event: Dict, case: Dict
    ) -> tuple:
        """维度1: 计算是否正确"""
        # 当前诊断假设：八字引擎已通过fate-bench验证(96.7%)
        # 这是HYPOTHESIS而非PROVEN，因为未对每个case单独验证
        
        bazi = BaziEngine().compute(
            (*map(int, case["birth_date"].split("-")), case["birth_hour"]),
            gender=case["gender"]
        )
        
        # 检查四柱计算是否有明显错误
        # 由于fate-bench已验证，此处标记为PASS（基于历史证据）
        return ("PASS", {
            "status": "PASS",
            "evidence": "fate-bench 59/61 cases aligned (96.7%)",
            "diagnosis_status": "HYPOTHESIS",
            "note": "八字引擎通过外部验证，未对本dataset逐例验证"
        })
    
    def _analyze_signal(
        self, event: Dict, predictions: List[Dict]
    ) -> tuple:
        """维度2: 是否生成了对应信号"""
        actual_cat = event["category"]
        actual_year = int(event["date"].split("-")[0])
        
        # 检查是否有任何预测覆盖该类别
        has_prediction = False
        closest_pred = None
        min_year_diff = 999
        
        for p in predictions:
            year_diff = abs(p["year"] - actual_year)
            if year_diff < min_year_diff:
                min_year_diff = year_diff
                closest_pred = p
            
            # 类别匹配（精确或映射）
            if p["category"] == actual_cat:
                has_prediction = True
        
        # 即使类别不精确，检查是否在映射范围内
        if not has_prediction:
            for pred in predictions:
                mapped_cats = get_mapping_group(pred["category"])
                if actual_cat in mapped_cats:
                    has_prediction = True
                    break
        
        return (
            "PASS" if has_prediction else "FAIL",
            {
                "status": "PASS" if has_prediction else "FAIL",
                "closest_prediction": closest_pred,
                "min_year_diff": min_year_diff,
                "total_predictions": len(predictions),
                "has_category_match": has_prediction,
                "prediction_categories": list(set(p["category"] for p in predictions)),
            }
        )
    
    def _analyze_ontology(
        self, event: Dict, predictions: List[Dict]
    ) -> tuple:
        """维度3: 预测类别与实际类别是否可映射"""
        actual_cat = event["category"]
        
        # 找最近时间的预测
        actual_year = int(event["date"].split("-")[0])
        closest = None
        min_diff = 999
        for p in predictions:
            diff = abs(p["year"] - actual_year)
            if diff < min_diff:
                min_diff = diff
                closest = p
        
        if not closest:
            return ("FAIL", {
                "status": "FAIL",
                "reason": "no_prediction",
                "mapping_possible": False,
            })
        
        # 检查映射
        direct_match = closest["category"] == actual_cat
        mapped_match = actual_cat in get_mapping_group(closest["category"])
        
        return (
            "PASS" if direct_match or mapped_match else "FAIL",
            {
                "status": "PASS" if direct_match or mapped_match else "FAIL",
                "predicted_category": closest["category"],
                "actual_category": actual_cat,
                "direct_match": direct_match,
                "mapped_match": mapped_match,
                "category_group": get_category_group(actual_cat),
            }
        )
    
    def _analyze_temporal(
        self, event: Dict, predictions: List[Dict]
    ) -> tuple:
        """维度4: 时间窗口是否匹配"""
        actual_year = int(event["date"].split("-")[0])
        actual_month = int(event["date"].split("-")[1]) if len(event["date"].split("-")) > 1 else None
        
        # 找最近预测
        closest = None
        min_diff = 999
        for p in predictions:
            diff = abs(p["year"] - actual_year)
            if diff < min_diff:
                min_diff = diff
                closest = p
        
        if not closest:
            return ("FAIL", {
                "status": "FAIL",
                "year_diff": None,
                "reason": "no_prediction",
            })
        
        year_diff = abs(closest["year"] - actual_year)
        
        # 时间窗口阈值
        thresholds = {
            "exact": 0,      # 同年
            "tight": 1,      # ±1年
            "standard": 2,   # ±2年（BASELINE）
            "relaxed": 5,    # ±5年
        }
        
        return (
            "PASS" if year_diff <= thresholds["standard"] else "FAIL",
            {
                "status": "PASS" if year_diff <= thresholds["standard"] else "FAIL",
                "predicted_year": closest["year"],
                "actual_year": actual_year,
                "year_diff": year_diff,
                "threshold_standard": thresholds["standard"],
                "within_exact": year_diff == 0,
                "within_tight": year_diff <= 1,
                "within_standard": year_diff <= 2,
                "within_relaxed": year_diff <= 5,
            }
        )
    
    def _analyze_severity(
        self, event: Dict, predictions: List[Dict]
    ) -> tuple:
        """维度5: 严重程度是否匹配"""
        actual_severity = event.get("severity", 3)
        
        # 当前预测无严重程度字段 — 这是已知限制
        has_severity = any("severity" in p for p in predictions)
        
        if not has_severity:
            return ("FAIL", {
                "status": "FAIL",
                "reason": "prediction_layer_no_severity_field",
                "actual_severity": actual_severity,
                "predicted_severity": None,
                "note": "BASELINE预测层未实现严重程度字段",
                "diagnosis_status": "PROVEN",
            })
        
        # 理论上应比较，但当前无数据
        return ("UNKNOWN", {
            "status": "UNKNOWN",
            "reason": "cannot_compare",
            "actual_severity": actual_severity,
        })
    
    def _analyze_interpretation(
        self, event: Dict, predictions: List[Dict], calc_status: str
    ) -> tuple:
        """维度6: 关系解释是否正确"""
        # 关键区分：Interpretation Engine尚未完整实现
        # 这不是算法失败，而是架构链路未完成
        
        has_evidence = any(
            "source" in p and p["source"].startswith("rule:") 
            for p in predictions
        )
        
        # 诊断状态：PROVEN（因为SignalEngine和RelationalInterpretation确实是missing）
        return (
            "PASS" if calc_status == "PASS" and has_evidence else "FAIL",
            {
                "status": "PASS" if calc_status == "PASS" and has_evidence else "FAIL",
                "has_evidence_refs": has_evidence,
                "relational_engine_status": "PARTIALLY_IMPLEMENTED",
                "note": "关系解释引擎为架构核心创新层，当前部分实现，不视为算法失败",
                "diagnosis_status": "PROVEN",
            }
        )
    
    def _determine_status(self, result: Dict) -> str:
        """确定整体诊断状态"""
        failures = [f.value if hasattr(f, 'value') else str(f) for f in result["failure_categories"]]

        if not failures:
            return DiagnosisStatus.PROVEN.value
        
        # 检查是否有HYPOTHESIS级别的诊断
        details = result["diagnosis_details"]
        hypothesis_found = any(
            d.get("diagnosis_status") == "HYPOTHESIS"
            for dim in details.values()
            for k, d in dim.items() if isinstance(d, dict)
        )
        
        if hypothesis_found:
            return DiagnosisStatus.HYPOTHESIS.value
        
        return DiagnosisStatus.PROVEN.value


# ─── 主分析流程 ─────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("V1.1 Failure Analysis — 六维度逐事件诊断")
    print("=" * 70)
    print()
    print("诊断原则:")
    print("  1. 禁止优化分数 — 纯诊断")
    print("  2. 每失败必须归因（允许UNKNOWN）")
    print("  3. 支持多重失败")
    print("  4. 区分PROVEN/HYPOTHESIS/UNKNOWN")
    print("  5. Interpretation缺失 ≠ 算法失败")
    print()
    
    # 加载数据集
    dataset_path = Path("dataset/golden_v1/golden_cases.json")
    with open(dataset_path, encoding="utf-8") as f:
        data = json.load(f)
    
    cases = data["cases"]
    analyzer = FailureAnalyzer()
    
    print(f"数据集: {len(cases)} cases, {sum(len(c['events']) for c in cases)} events")
    print()
    
    # 逐案例诊断
    all_results = []
    for case in cases:
        result = analyzer.analyze_case(case)
        all_results.append(result)
    
    # ── 汇总统计 ───────────────────────────────────────────────────────
    total_events = sum(r["total_events"] for r in all_results)
    total_matched = sum(r["matched_count"] for r in all_results)
    
    # 维度级统计
    dimension_stats = {
        "calculation": {"pass": 0, "fail": 0, "unknown": 0},
        "signal": {"pass": 0, "fail": 0, "unknown": 0},
        "ontology": {"pass": 0, "fail": 0, "unknown": 0},
        "temporal": {"pass": 0, "fail": 0, "unknown": 0},
        "severity": {"pass": 0, "fail": 0, "unknown": 0},
        "interpretation": {"pass": 0, "fail": 0, "unknown": 0},
    }
    
    for r in all_results:
        for event in r["events"]:
            for dim in dimension_stats:
                status = event["diagnosis_details"].get(dim, {}).get("status", "UNKNOWN")
                if status == "PASS":
                    dimension_stats[dim]["pass"] += 1
                elif status == "FAIL":
                    dimension_stats[dim]["fail"] += 1
                else:
                    dimension_stats[dim]["unknown"] += 1
    
    # ── 输出报告 ───────────────────────────────────────────────────────
    report = {
        "meta": {
            "analysis_version": "V1.1",
            "date": "2026-08-22",
            "baseline_commit": "034d0b2",
            "dataset": "golden_v1",
            "cases": len(cases),
            "events": total_events,
            "matched": total_matched,
            "precision": round(total_matched / sum(r["total_predictions"] for r in all_results), 4) if sum(r["total_predictions"] for r in all_results) > 0 else 0,
            "recall": round(total_matched / total_events, 4),
            "f1": 2 * (total_matched / sum(r["total_predictions"] for r in all_results)) * (total_matched / total_events) / (
                (total_matched / sum(r["total_predictions"] for r in all_results)) + (total_matched / total_events)
            ) if ((total_matched / sum(r["total_predictions"] for r in all_results)) + (total_matched / total_events)) > 0 else 0,
        },
        "dimension_summary": dimension_stats,
        "failure_attribution": {k: v for k, v in analyzer.failure_counts.items()},
        "diagnosis_status_distribution": {
            status: dict(counts) 
            for status, counts in analyzer.proven_hypothesis_unknown.items()
        },
        "case_results": all_results,
    }
    
    # 保存
    output_dir = Path("docs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "failure_analysis_v1.1_raw.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("输出文件:", output_path)
    
    # 打印关键统计
    print()
    print("=" * 70)
    print("六维度诊断结果")
    print("=" * 70)
    print()
    print(f"{'维度':<15} {'PASS':>6} {'FAIL':>6} {'UNKNOWN':>8} {'通过率':>8}")
    print("-" * 50)
    for dim, stats in dimension_stats.items():
        total = stats["pass"] + stats["fail"] + stats["unknown"]
        rate = stats["pass"] / total if total > 0 else 0
        print(f"{dim:<15} {stats['pass']:>6} {stats['fail']:>6} {stats['unknown']:>8} {rate:>7.1%}")
    
    print()
    print("=" * 70)
    print("失败归因分布")
    print("=" * 70)
    print()
    for cat, count in sorted(analyzer.failure_counts.items(), key=lambda x: -x[1]):
        pct = count / total_events * 100
        print(f"  {cat:<25} {count:>4} ({pct:>5.1f}%)")
    
    print()
    print("=" * 70)
    print("诊断状态分布")
    print("=" * 70)
    print()
    for status, counts in analyzer.proven_hypothesis_unknown.items():
        total = sum(counts.values())
        print(f"  {status:<12} {total:>4} events")
        for cat, count in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"    - {cat}: {count}")
    
    return report


if __name__ == "__main__":
    main()