"""
Phase 4 — Temporal Objects Schema

Contract (V1.2 strict separation):
  - PredictionWindow: set by system BEFORE evaluation, never modified by Validation
  - EvaluationToleranceWindow: around actual_event for matching against prediction
  - These are TWO DIFFERENT types — never interchangeable
  - TemporalSignal: single-engine time evidence, NO convergence info
  - TemporalConvergence: multi-engine aggregation, composed of TemporalSignals
  - Phase 4 MUST NOT produce Fortune Score or final fortune/auspiciousness score
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ─── TemporalGranularity ──────────────────────────────────────────────────────

class TemporalGranularity(str, enum.Enum):
    """Time granularity levels for temporal alignment."""
    YEARLY = "YEARLY"
    MONTHLY = "MONTHLY"
    DAILY = "DAILY"


# ─── PredictionWindow (strictly separate from EvaluationToleranceWindow) ─────

@dataclass(frozen=True)
class PredictionWindow:
    """
    Window used by the Calculation Engine to produce a prediction.

    Set by the system BEFORE evaluation. Never modified by Validation.
    This is the ENGINE'S claim about WHEN an event may occur.
    """
    start_year: int
    end_year: int
    start_month: Optional[int] = None
    end_month: Optional[int] = None
    start_day: Optional[int] = None
    end_day: Optional[int] = None
    granularity: TemporalGranularity = TemporalGranularity.YEARLY

    def to_dict(self) -> dict:
        return {
            "start_year": self.start_year,
            "end_year": self.end_year,
            "start_month": self.start_month,
            "end_month": self.end_month,
            "start_day": self.start_day,
            "end_day": self.end_day,
            "granularity": self.granularity.value,
        }

    def validate(self) -> List[str]:
        """Validate prediction window constraints."""
        errors = []
        if self.end_year < self.start_year:
            errors.append("end_year < start_year in PredictionWindow")
        if self.start_month is not None and self.end_month is not None:
            if self.end_month < self.start_month:
                errors.append("end_month < start_month in PredictionWindow")
        if self.start_day is not None and self.end_day is not None:
            if self.end_day < self.start_day:
                errors.append("end_day < start_day in PredictionWindow")
        return errors


# ─── EvaluationToleranceWindow (strictly separate from PredictionWindow) ─────

@dataclass(frozen=True)
class EvaluationToleranceWindow:
    """
    Tolerance window around an actual_event for matching against prediction.

    Width depends on severity_class (see V1.2 Schema 6).
    This is the VALIDATION ENGINE'S tolerance for when an observed event
    can be considered "matched" to a prior prediction.
    """
    severity_class: str  # LOW | MODERATE | HIGH | CRITICAL
    tolerance_days: int  # e.g. LOW=365, CRITICAL=7
    reference_date: Optional[str] = None  # ISO8601 date string

    # Strictly separated from PredictionWindow — different semantics
    _window_type: str = field(default="EVALUATION_TOLERANCE", init=False, repr=False)

    def to_dict(self) -> dict:
        return {
            "severity_class": self.severity_class,
            "tolerance_days": self.tolerance_days,
            "reference_date": self.reference_date,
        }

    def validate(self) -> List[str]:
        errors = []
        valid_severities = {"LOW", "MODERATE", "HIGH", "CRITICAL"}
        if self.severity_class not in valid_severities:
            errors.append(f"Invalid severity_class: {self.severity_class}")
        if self.tolerance_days < 0:
            errors.append(f"Negative tolerance_days: {self.tolerance_days}")
        return errors

    @classmethod
    def from_severity(cls, severity: str, tolerance_days: int,
                      reference_date: Optional[str] = None) -> 'EvaluationToleranceWindow':
        """Factory method enforcing severity→tolerance mapping."""
        standard_tolerances = {
            "LOW": 365,
            "MODERATE": 180,
            "HIGH": 30,
            "CRITICAL": 7,
        }
        if severity not in standard_tolerances:
            raise ValueError(f"Unknown severity: {severity}")
        # Use provided tolerance_days only; do not auto-override
        return cls(
            severity_class=severity,
            tolerance_days=tolerance_days,
            reference_date=reference_date,
        )


# ─── TemporalSignal (single-engine time evidence) ─────────────────────────────

@dataclass(frozen=True)
class TemporalSignal:
    """
    Single-engine temporal signal. Contains NO convergence info.

    Links a CanonicalSignal to a temporal scope for alignment.
    """
    signal_id: str                    # FK → CanonicalSignal.signal_id
    engine: str                       # e.g. "Bazi", "Heluo", …
    prediction_window: PredictionWindow
    direction: str                    # POSITIVE|NEGATIVE|CHANGE|NEUTRAL|UNKNOWN
    strength: float                   # 0.0–1.0
    provenance: str = ""              # human-readable source

    def to_dict(self) -> dict:
        return {
            "signal_id": self.signal_id,
            "engine": self.engine,
            "prediction_window": self.prediction_window.to_dict(),
            "direction": self.direction,
            "strength": self.strength,
            "provenance": self.provenance,
        }

    def validate(self) -> List[str]:
        errors = list(self.prediction_window.validate())
        if self.strength < 0.0 or self.strength > 1.0:
            errors.append(f"TemporalSignal strength out of range: {self.strength}")
        valid_directions = {"POSITIVE", "NEGATIVE", "CHANGE", "NEUTRAL", "UNKNOWN"}
        if self.direction not in valid_directions:
            errors.append(f"Invalid direction: {self.direction}")
        return errors


# ─── TemporalEvidence (traceable temporal record) ─────────────────────────────

@dataclass(frozen=True)
class TemporalEvidence:
    """
    Immutable temporal evidence record.
    """
    evidence_id: str
    signal_id: str
    engine: str
    temporal_signal: TemporalSignal
    created_at: str = ""              # ISO8601 timestamp
    verified: bool = False            # Whether validation has been applied

    def to_dict(self) -> dict:
        return {
            "evidence_id": self.evidence_id,
            "signal_id": self.signal_id,
            "engine": self.engine,
            "temporal_signal": self.temporal_signal.to_dict(),
            "created_at": self.created_at,
            "verified": self.verified,
        }


# ─── TemporalConvergence (multi-engine aggregation) ────────────────────────────

@dataclass
class TemporalConvergence:
    """
    Multi-engine temporal convergence evidence.

    Composed of individual TemporalSignals; NOT a TemporalSignal itself.
    Contains overlap_ratio, convergence_score, temporal_agreement.
    """
    convergence_id: str
    target_year: int
    target_month: Optional[int] = None

    # Per-engine signal mappings
    signal_ids_by_engine: Dict[str, List[str]] = field(default_factory=dict)

    # Computed metrics
    overlap_ratio: float = 0.0       # 0.0–1.0
    convergence_score: float = 0.0   # 0.0–1.0
    temporal_agreement: str = "NONE" # NONE|PARTIAL|STRONG|COMPLETE

    total_engines: int = 0
    agreeing_engines: int = 0        # engines with matching time signal
    unknown_engines: int = 0         # engines with UNKNOWN direction

    def to_dict(self) -> dict:
        return {
            "convergence_id": self.convergence_id,
            "target_year": self.target_year,
            "overlap_ratio": self.overlap_ratio,
            "convergence_score": self.convergence_score,
            "temporal_agreement": self.temporal_agreement,
            "signal_ids_by_engine": self.signal_ids_by_engine,
            "total_engines": self.total_engines,
            "agreeing_engines": self.agreeing_engines,
            "unknown_engines": self.unknown_engines,
        }

    def validate(self) -> List[str]:
        errors = []
        if not (0.0 <= self.overlap_ratio <= 1.0):
            errors.append(f"overlap_ratio out of range: {self.overlap_ratio}")
        if not (0.0 <= self.convergence_score <= 1.0):
            errors.append(f"convergence_score out of range: {self.convergence_score}")
        valid_agreements = {"NONE", "PARTIAL", "STRONG", "COMPLETE"}
        if self.temporal_agreement not in valid_agreements:
            errors.append(f"Invalid temporal_agreement: {self.temporal_agreement}")
        return errors
