"""Blind Protocol — 盲测协议

核心原则：
- 测试系统只拿到：出生信息 + 目标时间 + 允许使用的知识库
- 不能看到真实事件标签
- 预测完成后才揭晓答案

使用方式：
    blind = BlindProtocol(cases, hidden_events=True)
    predictions = blind.run(start_year=2010, end_year=2025)
    # 然后对比 predictions 与 hidden ground truth
"""
from __future__ import annotations
import logging
from dataclasses import dataclass
from datetime import date
from typing import Optional

from ..schema.case import Case, Event
from ..schema.prediction import Prediction

logger = logging.getLogger(__name__)


@dataclass
class BlindRun:
    """一次盲测运行结果。"""
    case_id: str
    start_year: int
    end_year: int
    predictions: dict[int, Prediction]  # year -> Prediction
    revealed_results: Optional[list] = None  # 揭晓后的对比结果

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "start_year": self.start_year,
            "end_year": self.end_year,
            "prediction_count": len(self.predictions),
            "revealed": self.revealed_results is not None,
        }


class BlindProtocol:
    """盲测协议执行器。

    工作流程：
    1. 初始化时传入 cases，但不暴露 events
    2. 执行预测（系统只看到出生信息）
    3. 揭晓答案，计算准确率
    """

    def __init__(self, cases: list[Case]):
        self._cases = cases
        self._runs: list[BlindRun] = []

    def run(
        self,
        case: Case,
        start_year: int,
        end_year: int,
        predictor=None,
    ) -> BlindRun:
        """执行盲测。

        Args:
            case: 命例（events 字段应被隐藏或清空）
            start_year/end_year: 预测年份范围
            predictor: Callable[[Case, int], Prediction] — 预测函数

        Returns:
            BlindRun: 盲测结果
        """
        # 隐藏事件信息
        hidden_case = self._hide_events(case)

        # 执行预测
        predictions = {}
        for year in range(start_year, end_year + 1):
            if predictor:
                predictions[year] = predictor(hidden_case, year)
            else:
                # 模拟预测
                predictions[year] = Prediction(
                    case_id=case.case_id,
                    target_year=year,
                    signals=[],
                    raw_calculation={},
                )

        run = BlindRun(
            case_id=case.case_id,
            start_year=start_year,
            end_year=end_year,
            predictions=predictions,
        )
        self._runs.append(run)
        return run

    def reveal_and_score(
        self,
        run: BlindRun,
        scoring_fn=None,
    ) -> list:
        """揭晓答案并评分。

        Args:
            run: 盲测结果
            scoring_fn: Callable[[Prediction, Event], float] — 评分函数

        Returns:
            list: 每个事件-预测匹配的评分
        """
        case = next((c for c in self._cases if c.case_id == run.case_id), None)
        if case is None:
            raise ValueError(f"Case {run.case_id} not found")

        scores = []
        for year, prediction in run.predictions.items():
            events_in_year = [e for e in case.events if e.date.year == year]
            for event in events_in_year:
                if scoring_fn:
                    score = scoring_fn(prediction, event)
                    scores.append({
                        "year": year,
                        "event": event.to_dict(),
                        "score": score,
                        "matched": score >= 0.6,
                    })

        # 更新 run
        run.revealed_results = scores
        return scores

    def _hide_events(self, case: Case) -> Case:
        """隐藏事件信息，创建只读副本。"""
        from copy import deepcopy
        hidden = deepcopy(case)
        hidden.events = []  # 清空事件，只保留出生信息
        hidden._hidden_events = case.events  # 保留原始引用供后续揭晓用
        return hidden

    def generate_report(self) -> dict:
        """生成盲测报告。"""
        total_runs = len(self._runs)
        revealed_runs = sum(1 for r in self._runs if r.revealed_results is not None)
        return {
            "total_runs": total_runs,
            "revealed_runs": revealed_runs,
            "runs": [r.to_dict() for r in self._runs],
        }
