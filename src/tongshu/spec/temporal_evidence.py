"""
V-Validation V1.2 — Temporal Evidence Schema (Schema 5)

Contract:
  PredictionWindow and EvaluationToleranceWindow are TWO DIFFERENT types.
  TemporalSignal does NOT contain convergence — that lives in TemporalConvergence.
  Phase 1: schema only. No convergence algorithm.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ─── TemporalSignal (single-engine time evidence) ────────────────────────────


@dataclass
class TemporalSignal:
    """Single-engine time signal. Contains NO convergence info."""

    signal_id: str            # FK → CanonicalSignal.signal_id
    engine: str               # e.g. "Bazi", "Heluo", …
    year: int
    month: Optional[int] = None
    day: Optional[int] = None
    granularity: str = "YEARLY"

    def to_dict(self) -> dict:
        return {
            "signal_id": self.signal_id,
            "engine": self.engine,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "granularity": self.granularity,
        }


# ─── TemporalConvergence (multi-engine aggregation) ──────────────────────────


@dataclass
class TemporalConvergence:
    """Multi-engine temporal convergence evidence.

    Composed of individual TemporalSignals; NOT a TemporalSignal itself.
    """

    convergence_id: str
    target_year: int
    target_month: Optional[int] = None

    signal_ids_by_engine: Dict[str, List[str]] = field(default_factory=dict)

    overlap_ratio: float = 0.0       # 0.0–1.0
    convergence_score: float = 0.0   # 0.0–1.0

    total_engines: int = 0
    agreeing_engines: int = 0        # engines with matching time signal

    def to_dict(self) -> dict:
        return {
            "convergence_id": self.convergence_id,
            "target_year": self.target_year,
            "overlap_ratio": self.overlap_ratio,
            "convergence_score": self.convergence_score,
            "signal_ids_by_engine": self.signal_ids_by_engine,
            "total_engines": self.total_engines,
            "agreeing_engines": self.agreeing_engines,
        }


# ─── PredictionWindow (strictly separate from EvaluationToleranceWindow) ─────


@dataclass
class PredictionWindow:
    """Window used by the Calculation Engine to produce a prediction.

    Set by the system BEFORE evaluation. Never modified by Validation.
    """

    start_year: int
    end_year: int
    start_month: Optional[int] = None
    end_month: Optional[int] = None


# ─── EvaluationToleranceWindow (strictly separate from PredictionWindow) ─────


@dataclass
class EvaluationToleranceWindow:
    """Tolerance window around an actual_event for matching against prediction.

    Width depends on severity_class (see V1.2 Schema 6).
    """

    severity_class: str   # LOW|MODERATE|HIGH|CRITICAL
    tolerance_days: int   # e.g. LOW=365, CRITICAL=7


from typing import Union
