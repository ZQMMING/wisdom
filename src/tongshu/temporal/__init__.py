"""
Phase 4 — Temporal Module

Exports:
  - TemporalGranularity
  - PredictionWindow, EvaluationToleranceWindow
  - TemporalSignal, TemporalEvidence
  - TemporalConvergence
  - TemporalAlignmentEngine
  - TemporalConvergenceEngine
"""
from __future__ import annotations

from tongshu.temporal.schema import (
    PredictionWindow,
    EvaluationToleranceWindow,
    TemporalGranularity,
    TemporalSignal,
    TemporalEvidence,
    TemporalConvergence,
)
from tongshu.temporal.alignment import TemporalAlignmentEngine, TemporalAlignmentResult
from tongshu.temporal.convergence import TemporalConvergenceEngine

__all__ = [
    "PredictionWindow",
    "EvaluationToleranceWindow",
    "TemporalGranularity",
    "TemporalSignal",
    "TemporalEvidence",
    "TemporalConvergence",
    "TemporalAlignmentEngine",
    "TemporalAlignmentResult",
    "TemporalConvergenceEngine",
]
