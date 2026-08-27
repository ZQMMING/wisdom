"""Schema: Prediction & ScoreCard — 预测与评分模型"""
from __future__ import annotations
import enum
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


class PredictionLevel(enum.IntEnum):
    """预测粒度层级。"""
    YEAR = 1      # 年
    QUARTER = 2   # 季度
    MONTH = 3     # 月
    WEEK = 4      # 周
    DAY = 5       # 日


@dataclass
class Signal:
    """单一信号：某个维度的预测输出。"""
    category: str            # 如 "career", "relationship", "wealth"
    direction: str           # "UP" / "DOWN" / "STABLE" / "CHANGE"
    intensity: float         # 0.0 - 1.0
    time_window_start: Optional[date] = None
    time_window_end: Optional[date] = None
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "direction": self.direction,
            "intensity": self.intensity,
            "time_window": f"{self.time_window_start}~{self.time_window_end}"
                if self.time_window_start and self.time_window_end
                else "unspecified",
            "description": self.description,
        }


@dataclass
class Prediction:
    """对某年的完整预测输出。"""
    case_id: str
    target_year: int
    signals: list[Signal] = field(default_factory=list)
    raw_calculation: dict = field(default_factory=dict)  # 原始计算结果（防幻觉）
    confidence: float = 0.0
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "target_year": self.target_year,
            "signals": [s.to_dict() for s in self.signals],
            "raw_calculation": self.raw_calculation,
            "confidence": self.confidence,
            "notes": self.notes,
        }


@dataclass
class ScoreCard:
    """单事件评分卡。

    评分维度（满分100）：
    - 事件类别正确: 30分
    - 时间窗口正确: 20分
    - 方向正确: 15分
    - 强度正确: 15分
    - 描述接近度: 10分
    - 具体性: 10分
    """
    prediction: Prediction
    ground_truth: Optional[dict] = None  # {"date": ..., "category": ..., ...}

    # 各维度得分
    category_score: float = 0.0
    time_score: float = 0.0
    direction_score: float = 0.0
    intensity_score: float = 0.0
    description_score: float = 0.0
    specificity_score: float = 0.0

    @property
    def total_score(self) -> float:
        return (
            self.category_score +
            self.time_score +
            self.direction_score +
            self.intensity_score +
            self.description_score +
            self.specificity_score
        )

    @property
    def matched(self) -> bool:
        return self.total_score >= 60  # 60分及格

    def to_dict(self) -> dict:
        return {
            "prediction": self.prediction.to_dict(),
            "ground_truth": self.ground_truth,
            "scores": {
                "category": self.category_score,
                "time": self.time_score,
                "direction": self.direction_score,
                "intensity": self.intensity_score,
                "description": self.description_score,
                "specificity": self.specificity_score,
            },
            "total": self.total_score,
            "matched": self.matched,
        }
