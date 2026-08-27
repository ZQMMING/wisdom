"""Agreement Evidence Engine — multi-engine signal consistency.

Contract:
  Agreement Evidence answers: do independent evidence sources agree on the
  same Canonical Signal (direction, time, semantics)?
  It does NOT produce a "fortune score" or weighted sum.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


class AgreementLevel(enum.Enum):
    """Agreement level between engine signals."""
    NONE = "NONE"               # no overlapping signals
    WEAK = "WEAK"               # only temporal overlap, no direction agreement
    MODERATE = "MODERATE"       # partial direction agreement
    STRONG = "STRONG"           # full direction agreement among all engines
    CONFLICTING = "CONFLICTING" # active disagreement


@dataclass(frozen=True)
class SignalEvidence:
    """A single engine's signal contribution to agreement analysis."""

    signal_id: str
    engine: str
    direction: str          # "POSITIVE" | "NEGATIVE" | "UNKNOWN"
    strength: float         # 0.0–1.0
    prediction_window_start: int
    prediction_window_end: int

    def to_dict(self) -> dict:
        return {
            "signal_id": self.signal_id,
            "engine": self.engine,
            "direction": self.direction,
            "strength": self.strength,
            "prediction_window": f"{self.prediction_window_start}–{self.prediction_window_end}",
        }


@dataclass(frozen=True)
class AgreementResult:
    """Result of agreement evidence computation."""

    signal_id: str
    level: AgreementLevel
    total_engines: int
    agreeing_engines: int
    unknown_engines: int
    conflicting_engines: int
    overlapping_signals: List[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)

    @property
    def agreement_ratio(self) -> float:
        """Ratio of agreeing engines to total (excluding UNKNOWN)."""
        non_unknown = self.total_engines - self.unknown_engines
        if non_unknown == 0:
            return 0.0
        return self.agreeing_engines / non_unknown

    def to_dict(self) -> dict:
        return {
            "signal_id": self.signal_id,
            "level": self.level.value,
            "total_engines": self.total_engines,
            "agreeing_engines": self.agreeing_engines,
            "unknown_engines": self.unknown_engines,
            "conflicting_engines": self.conflicting_engines,
            "agreement_ratio": self.agreement_ratio,
            "overlapping_signals": self.overlapping_signals,
            "details": self.details,
        }


class AgreementEvidenceEngine:
    """Multi-engine agreement evidence computation.

    Read-only: does NOT modify any input signals.
    Does NOT produce fortune/luck/good_bad scores.
    """

    def __init__(self) -> None:
        self._signals: Dict[str, List[SignalEvidence]] = {}

    def add_signal(self, sig: SignalEvidence) -> None:
        """Add a signal evidence for agreement analysis."""
        self._signals.setdefault(sig.signal_id, []).append(sig)

    def compute_agreement(self, signal_id: str) -> AgreementResult:
        """Compute agreement for a single signal across engines."""
        sigs = self._signals.get(signal_id, [])
        if len(sigs) <= 1:
            return AgreementResult(
                signal_id=signal_id,
                level=AgreementLevel.NONE,
                total_engines=len(sigs),
                agreeing_engines=len(sigs),
                unknown_engines=sum(1 for s in sigs if s.direction == "UNKNOWN"),
                conflicting_engines=0,
            )

        # Group by direction
        directions: Dict[str, List[SignalEvidence]] = {}
        for s in sigs:
            directions.setdefault(s.direction, []).append(s)

        pos_count = len(directions.get("POSITIVE", []))
        neg_count = len(directions.get("NEGATIVE", []))
        unk_count = len(directions.get("UNKNOWN", []))

        total = len(sigs)
        non_unknown = total - unk_count

        # Determine agreement level
        if pos_count == 0 and neg_count == 0:
            level = AgreementLevel.NONE
            agreeing = 0
            conflicting = 0
        if pos_count > 0 and neg_count > 0:
            level = AgreementLevel.CONFLICTING
            agreeing = 0
            conflicting = pos_count + neg_count
        elif pos_count > 0 or neg_count > 0:
            # All non-unknown agree on same direction
            level = AgreementLevel.STRONG if non_unknown == (pos_count + neg_count) else AgreementLevel.MODERATE
            agreeing = pos_count + neg_count
            conflicting = 0
        else:
            level = AgreementLevel.NONE
            agreeing = 0
            conflicting = 0

        overlapping = [s.signal_id for s in sigs]

        return AgreementResult(
            signal_id=signal_id,
            level=level,
            total_engines=total,
            agreeing_engines=agreeing,
            unknown_engines=unk_count,
            conflicting_engines=conflicting,
            overlapping_signals=overlapping,
            details={
                "POSITIVE": pos_count,
                "NEGATIVE": neg_count,
                "UNKNOWN": unk_count,
            },
        )

    def compute_all(self) -> Dict[str, AgreementResult]:
        """Compute agreement for all registered signals."""
        return {sid: self.compute_agreement(sid) for sid in self._signals}

    def get_agreement_by_level(self, level: AgreementLevel) -> List[str]:
        """Get signal IDs with a specific agreement level."""
        return [
            sid for sid, result in self.compute_all().items()
            if result.level == level
        ]
