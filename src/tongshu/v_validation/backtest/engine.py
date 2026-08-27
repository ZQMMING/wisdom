"""Backtest Engine — 时间轴回测核心

支持：
- Life Timeline Backtest: 对单案例完整人生时间线回测
- Multi-year Backtest: 对多个年份分别预测
- Precision/Recall/F1 计算
- 负样本测试（检查非事件年是否也有强信号）
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional

from ..schema.case import Case, Event, EventSeverity, EvidenceGrade
from ..schema.prediction import Prediction, Signal

logger = logging.getLogger(__name__)


@dataclass
class BacktestResult:
    """单次回测结果。"""
    case_id: str
    year: int
    predicted: Prediction
    actual_events: list[Event]
    matched_events: list[tuple[Event, Signal]] = field(default_factory=list)
    false_positives: list[Signal] = field(default_factory=list)
    false_negatives: list[Event] = field(default_factory=list)

    @property
    def precision(self) -> float:
        total = len(self.matched_events) + len(self.false_positives)
        return len(self.matched_events) / total if total > 0 else 0.0

    @property
    def recall(self) -> float:
        total = len(self.matched_events) + len(self.false_negatives)
        return len(self.matched_events) / total if total > 0 else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) > 0 else 0.0


class BacktestEngine:
    """时间轴回测引擎。

    使用方式：
        engine = BacktestEngine(pipeline_fn=pipeline.run)
        results = engine.run(case, start_year=2010, end_year=2025)
    """

    def __init__(self, pipeline_fn=None):
        """
        Args:
            pipeline_fn: Callable[[Case, date], dict] — 传入pipeline.run结果
        """
        self._pipeline_fn = pipeline_fn
        self._results: dict[str, list[BacktestResult]] = {}

    def run(self, case: Case, start_year: int, end_year: int) -> list[BacktestResult]:
        """对[start_year, end_year]区间逐年回测。"""
        results = []
        for year in range(start_year, end_year + 1):
            result = self._backtest_year(case, year)
            results.append(result)
            if year % 10 == 0:
                logger.info(f"Progress: {case.case_id} year {year}/{end_year}")
        self._results[case.case_id] = results
        return results

    def _backtest_year(self, case: Case, year: int) -> BacktestResult:
        """对单一年份进行回测。"""
        # 1. 获取该年的预测
        prediction = self._predict_year(case, year)

        # 2. 获取该年的真实事件
        events_in_year = [
            e for e in case.events
            if e.date.year == year
        ]

        # 3. 匹配预测与真实事件
        matched = []
        unmatched_predictions = []
        for signal in prediction.signals:
            for event in events_in_year:
                if self._match_signal_to_event(signal, event):
                    matched.append((event, signal))
                    break
            else:
                unmatched_predictions.append(signal)

        # 4. 计算漏报
        matched_event_ids = {(e.date, e.category) for e, _ in matched}
        false_negatives = [
            e for e in events_in_year
            if (e.date, e.category) not in matched_event_ids
        ]

        return BacktestResult(
            case_id=case.case_id,
            year=year,
            predicted=prediction,
            actual_events=events_in_year,
            matched_events=matched,
            false_positives=unmatched_predictions,
            false_negatives=false_negatives,
        )

    def _predict_year(self, case: Case, year: int) -> Prediction:
        """调用pipeline预测某年。"""
        if self._pipeline_fn is None:
            # 模拟预测（用于无pipeline时的单元测试）
            return Prediction(
                case_id=case.case_id,
                target_year=year,
                signals=[],
                raw_calculation={"simulated": True},
            )
        # 实际调用pipeline
        analysis_date = date(year, 6, 1)  # 年中分析
        result = self._pipeline_fn(case, analysis_date)
        return Prediction(
            case_id=case.case_id,
            target_year=year,
            signals=result.get("signals", []),
            raw_calculation=result.get("raw", {}),
            confidence=result.get("confidence", 0.0),
        )

    def _match_signal_to_event(self, signal: Signal, event: Event) -> bool:
        """判断信号是否与事件匹配。"""
        # 时间窗口匹配
        if signal.time_window_start and signal.time_window_end:
            if not (signal.time_window_start <= event.date <= signal.time_window_end):
                return False
        elif signal.time_window_start:
            if abs((event.date - signal.time_window_start).days) > 30:
                return False

        # 类别匹配（简单字符串包含）
        signal_cat = signal.category.lower()
        event_cat = event.category.value.lower()
        return signal_cat in event_cat or event_cat in signal_cat

    def aggregate_stats(self) -> dict:
        """聚合所有回测结果的统计指标。"""
        all_precisions = []
        all_recalls = []
        all_f1s = []
        major_event_recall = []

        for case_id, results in self._results.items():
            for r in results:
                all_precisions.append(r.precision)
                all_recalls.append(r.recall)
                all_f1s.append(r.f1)

                # 重大事件召回率
                if r.actual_events:
                    major = [e for e in r.actual_events if e.severity >= EventSeverity.MAJOR]
                    if major:
                        matched_major = [e for e, _ in r.matched_events if e.severity >= EventSeverity.MAJOR]
                        major_event_recall.append(len(matched_major) / len(major))

        return {
            "cases_tested": len(self._results),
            "total_years": sum(len(r) for r in self._results.values()),
            "mean_precision": sum(all_precisions) / len(all_precisions) if all_precisions else 0,
            "mean_recall": sum(all_recalls) / len(all_recalls) if all_recalls else 0,
            "mean_f1": sum(all_f1s) / len(all_f1s) if all_f1s else 0,
            "major_event_recall": sum(major_event_recall) / len(major_event_recall) if major_event_recall else 0,
        }
