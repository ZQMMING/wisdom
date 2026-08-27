"""Scoring Matrix — 多维度评分矩阵

评分维度（满分100）：
┌─────────────────┬──────┬──────────────────────────────┐
│ 维度            │ 权重 │ 说明                         │
├─────────────────┼──────┼──────────────────────────────┤
│ 事件类别正确     │ 30   │ MARRIAGE/MARRIAGE 匹配        │
│ 时间窗口正确     │ 20   │ 预测年份与实际误差 <= 1年      │
│ 方向正确         │ 15   │ UP/DOWN 与实际一致             │
│ 强度正确         │ 15   │ 严重程度等级匹配               │
│ 描述接近度       │ 10   │ 语义相似度                     │
│ 具体性           │ 10   │ 是否给出具体时间窗口           │
└─────────────────┴──────┴──────────────────────────────┘
"""
from __future__ import annotations
import difflib
from typing import Optional

from ..schema.case import Event, EventSeverity
from ..schema.prediction import Prediction, Signal


class ScoringMatrix:
    """多维度评分矩阵。"""

    WEIGHTS = {
        "category": 30.0,
        "time": 20.0,
        "direction": 15.0,
        "intensity": 15.0,
        "description": 10.0,
        "specificity": 10.0,
    }

    @classmethod
    def score(
        cls,
        prediction: Prediction,
        event: Event,
    ) -> dict:
        """对单个预测-事件对进行评分。

        Returns:
            dict with per-dimension scores and total.
        """
        return {
            "category": cls._score_category(prediction, event),
            "time": cls._score_time(prediction, event),
            "direction": cls._score_direction(prediction, event),
            "intensity": cls._score_intensity(prediction, event),
            "description": cls._score_description(prediction, event),
            "specificity": cls._score_specificity(prediction),
        }

    @classmethod
    def _score_category(cls, prediction: Prediction, event: Event) -> float:
        """事件类别正确性评分（0-30）。"""
        # 简单实现：检查预测信号是否包含事件类别关键词
        event_cat = event.category.value.lower()
        for signal in prediction.signals:
            if event_cat in signal.category.lower() or \
               signal.category.lower() in event_cat:
                return 30.0
        return 0.0

    @classmethod
    def _score_time(cls, prediction: Prediction, event: Event) -> float:
        """时间窗口正确性评分（0-20）。"""
        if prediction.target_year == event.date.year:
            return 20.0
        elif abs(prediction.target_year - event.date.year) == 1:
            return 10.0
        return 0.0

    @classmethod
    def _score_direction(cls, prediction: Prediction, event: Event) -> float:
        """方向正确性评分（0-15）。"""
        # 简化：重大事件默认方向为变化
        if event.severity >= EventSeverity.MAJOR:
            for signal in prediction.signals:
                if signal.direction in ("UP", "CHANGE"):
                    return 15.0
        return 0.0

    @classmethod
    def _score_intensity(cls, prediction: Prediction, event: Event) -> float:
        """强度正确性评分（0-15）。"""
        # 根据事件严重程度匹配信号强度
        expected_intensity = event.severity / 5.0  # 归一化到 0-1
        for signal in prediction.signals:
            if abs(signal.intensity - expected_intensity) < 0.3:
                return 15.0
        return 0.0

    @classmethod
    def _score_description(cls, prediction: Prediction, event: Event) -> float:
        """描述接近度评分（0-10）。"""
        # 使用文本相似度
        pred_text = " ".join(s.description for s in prediction.signals)
        if not pred_text:
            return 0.0
        ratio = difflib.SequenceMatcher(None, pred_text, event.description).ratio()
        return ratio * 10.0

    @classmethod
    def _score_specificity(cls, prediction: Prediction) -> float:
        """具体性评分（0-10）。"""
        # 有明确时间窗口的信号更具体
        has_window = sum(
            1 for s in prediction.signals
            if s.time_window_start and s.time_window_end
        )
        if has_window > 0:
            return 10.0
        return 5.0  # 无具体时间窗口但仍有预测

    @classmethod
    def compute_total(cls, prediction: Prediction, event: Event) -> float:
        """计算总分。"""
        scores = cls.score(prediction, event)
        return sum(scores.values())

    @classmethod
    def benchmark(
        cls,
        predictions: list[Prediction],
        events: list[Event],
    ) -> dict:
        """批量评分，计算整体指标。"""
        total_scores = []
        matched = 0
        for pred in predictions:
            for event in events:
                if pred.target_year == event.date.year:
                    score = cls.compute_total(pred, event)
                    total_scores.append(score)
                    if score >= 60:
                        matched += 1

        return {
            "total_evaluations": len(total_scores),
            "matched_count": matched,
            "match_rate": matched / len(total_scores) if total_scores else 0,
            "mean_score": sum(total_scores) / len(total_scores) if total_scores else 0,
            "median_score": sorted(total_scores)[len(total_scores)//2] if total_scores else 0,
        }
