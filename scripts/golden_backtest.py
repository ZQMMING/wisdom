"""Golden Dataset Backtest — 简化版回测

直接计算八字→提取信号→匹配事件
"""
import json
import sys
from datetime import date
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path("D:/today/backend/src")))

from tongshu.v_validation.schema.case import Case, Event, EventCategory, EventSeverity, EvidenceGrade
from tongshu.v_validation.ontology import EventMatcher, SeverityScoring
from tongshu.engines.bazi_engine import BaziEngine, pillar_to_chinese


def load_golden_dataset(path: str = "dataset/golden_v1/golden_cases.json") -> List[Case]:
    """加载Golden Dataset。"""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    
    cases = []
    for case_data in data.get("cases", []):
        birth_date = case_data["birth_date"]
        by, bm, bd = map(int, birth_date.split("-"))
        
        case = Case(
            case_id=case_data["case_id"],
            gender=case_data["gender"],
            birth_year=by,
            birth_month=bm,
            birth_day=bd,
            birth_hour=case_data["birth_hour"],
            source_type=case_data.get("source_type", "manual"),
        )
        
        for event_data in case_data.get("events", []):
            event = Event(
                date=date.fromisoformat(event_data["date"]),
                category=EventCategory[event_data["category"]],
                severity=EventSeverity(event_data["severity"]),
                description=event_data["description"],
                evidence_grade=EvidenceGrade(event_data["evidence_grade"]),
            )
            case.events.append(event)
        
        cases.append(case)
    
    return cases


def predict_events_for_case(case: Case) -> List[Dict]:
    """根据命盘预测该案例的重要事件。"""
    # 计算八字
    bazi = BaziEngine().compute(
        (case.birth_year, case.birth_month, case.birth_day, case.birth_hour),
        gender=case.gender
    )
    
    # 获取中文干支
    year_pillar = pillar_to_chinese(bazi.year_pillar)
    month_pillar = pillar_to_chinese(bazi.month_pillar)
    day_pillar = pillar_to_chinese(bazi.day_pillar)
    hour_pillar = pillar_to_chinese(bazi.hour_pillar)
    
    # 基于命盘特征推断事件类型和时间
    predictions = []
    
    # 日主属性（用于判断五行特性）
    day_stem = bazi.day_pillar.heavenly_stem  # 英文如 JIA
    
    # 科举考试（如果有印星或官杀，推测中年考试运）
    if any(x in month_pillar for x in ["甲", "乙"]):  # 木日主，有文昌
        for year_offset in [22, 25, 28, 32]:
            pred_year = case.birth_year + year_offset
            predictions.append({
                "category": EventCategory.EXAM.value,
                "year": pred_year,
                "type": "科举/考试",
                "confidence": 0.7,
            })
    
    # 升职（如果有财星或官星）
    if any(x in year_pillar for x in ["庚", "辛"]):  # 金柱，有官杀
        for year_offset in [28, 30, 35, 40]:
            pred_year = case.birth_year + year_offset
            predictions.append({
                "category": EventCategory.PROMOTION.value,
                "year": pred_year,
                "type": "升职/迁转",
                "confidence": 0.6,
            })
    
    # 家庭变化（如果有冲克）
    if "辰" in year_pillar or "戌" in year_pillar:  # 辰戌冲
        for year_offset in [25, 35, 45]:
            pred_year = case.birth_year + year_offset
            predictions.append({
                "category": EventCategory.FAMILY_CHANGE.value,
                "year": pred_year,
                "type": "家庭变动",
                "confidence": 0.5,
            })
    
    # 重大转折点（每10年）
    for year_offset in range(20, 60, 10):
        pred_year = case.birth_year + year_offset
        predictions.append({
            "category": EventCategory.FAMILY_CHANGE.value,
            "year": pred_year,
            "type": f"第{year_offset}年运势转折",
            "confidence": 0.5,
        })
    
    return predictions


def run_backtest(cases: List[Case]) -> Dict[str, Any]:
    """运行完整回测。"""
    results = []
    
    for case in cases:
        if not case.events:
            continue
        
        # 预测事件
        predictions = predict_events_for_case(case)
        
        # 实际事件
        actual_events = case.events
        
        # 匹配预测与实际
        matched = []
        for pred in predictions:
            pred_date = date(pred["year"], 6, 1)  # 年中
            for actual in actual_events:
                # 检查时间窗口（±2年）
                if abs(pred["year"] - actual.date.year) <= 2:
                    # 检查类别匹配
                    if pred["category"] == actual.category.value:
                        matched.append({
                            "predicted": pred,
                            "actual": actual.to_dict(),
                        })
                        break
        
        # 计算指标
        total_actual = len(actual_events)
        total_predicted = len(predictions)
        total_matched = len(matched)
        
        precision = total_matched / total_predicted if total_predicted > 0 else 0
        recall = total_matched / total_actual if total_actual > 0 else 0
        f1 = (2 * precision * recall / (precision + recall) 
              if (precision + recall) > 0 else 0)
        
        results.append({
            "case_id": case.case_id,
            "actual_events": total_actual,
            "predicted_events": total_predicted,
            "matched_events": total_matched,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        })
    
    # 汇总统计
    total_actual = sum(r["actual_events"] for r in results)
    total_matched = sum(r["matched_events"] for r in results)
    total_predicted = sum(r["predicted_events"] for r in results)
    
    overall_precision = total_matched / total_predicted if total_predicted > 0 else 0
    overall_recall = total_matched / total_actual if total_actual > 0 else 0
    overall_f1 = (2 * overall_precision * overall_recall / 
                  (overall_precision + overall_recall) 
                  if (overall_precision + overall_recall) > 0 else 0)
    
    summary = {
        "total_cases": len(cases),
        "total_actual_events": total_actual,
        "total_predicted_events": total_predicted,
        "total_matched_events": total_matched,
        "overall_precision": round(overall_precision, 4),
        "overall_recall": round(overall_recall, 4),
        "overall_f1": round(overall_f1, 4),
    }
    
    return {"summary": summary, "results": results}


def main():
    """主函数。"""
    print("=" * 60)
    print("Golden Dataset Backtest V1")
    print("=" * 60)
    
    # 加载数据
    print("\n[1/3] Loading Golden Dataset...")
    cases = load_golden_dataset()
    print(f"  Loaded {len(cases)} cases")
    
    # 运行回测
    print("\n[2/3] Running backtest...")
    results = run_backtest(cases)
    
    # 输出结果
    print("\n[3/3] Results:")
    summary = results["summary"]
    print(f"  Total Cases: {summary['total_cases']}")
    print(f"  Actual Events: {summary['total_actual_events']}")
    print(f"  Predicted Events: {summary['total_predicted_events']}")
    print(f"  Matched Events: {summary['total_matched_events']}")
    print(f"  Precision: {summary['overall_precision']:.2%}")
    print(f"  Recall: {summary['overall_recall']:.2%}")
    print(f"  F1: {summary['overall_f1']:.2%}")
    
    # 保存结果
    output_path = "docs/golden_backtest_results.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n  Saved to: {output_path}")
    
    return results


if __name__ == "__main__":
    main()
