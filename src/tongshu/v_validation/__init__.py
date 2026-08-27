"""V-Validation Layer — 命理系统实证验证框架

完整链路：历史回测 → 盲测 → 交叉验证 → 消融实验 → 前瞻测试
"""
from __future__ import annotations

__version__ = "1.0.0"
__build_date__ = "2026-08-22"

from .schema.case import Case, Event, EvidenceGrade, EventSeverity, EventCategory
from .schema.prediction import Prediction, Signal, ScoreCard, PredictionLevel
from .backtest.engine import BacktestEngine, BacktestResult
from .blind.protocol import BlindProtocol, BlindRun
from .scoring.matrix import ScoringMatrix
from .ablation.runner import AblationRunner, AblationVariant, AblationResult
from .baseline.system import BaselineSystem, BaselineResult
from .reports.generator import ValidationReport

__all__ = [
    # Version
    "__version__", "__build_date__",
    # Schema
    "Case", "Event", "EvidenceGrade", "EventSeverity", "EventCategory",
    "Prediction", "Signal", "ScoreCard", "PredictionLevel",
    # Engine
    "BacktestEngine", "BacktestResult",
    "BlindProtocol", "BlindRun",
    "ScoringMatrix",
    "AblationRunner", "AblationVariant", "AblationResult",
    "BaselineSystem", "BaselineResult",
    "ValidationReport",
]
