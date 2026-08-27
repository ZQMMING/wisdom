"""Failure Taxonomy — 15 FailureTypes per V1.2 Contract."""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import List, Optional


class FailureType(enum.Enum):
    """V1.2 Failure Taxonomy — 15 types, frozen."""

    # Signal layer
    SIGNAL_MISSING = "SIGNAL_MISSING"
    SIGNAL_FALSE_POS = "SIGNAL_FALSE_POS"

    # Ontology layer
    ONTOLOGY_MISMATCH = "ONTOLOGY_MISMATCH"
    DIRECTION_MISMATCH = "DIRECTION_MISMATCH"

    # Temporal layer
    TEMPORAL_MISMATCH = "TEMPORAL_MISMATCH"
    TEMPORAL_GRANULARITY = "TEMPORAL_GRANULARITY"

    # Severity layer
    SEVERITY_MISMATCH = "SEVERITY_MISMATCH"
    SEVERITY_MISSING = "SEVERITY_MISSING"

    # Evidence layer
    EVIDENCE_CHAIN_BREAK = "EVIDENCE_CHAIN_BREAK"
    EVIDENCE_LEVEL_VIOL = "EVIDENCE_LEVEL_VIOL"
    EVIDENCE_NO_SOURCE = "EVIDENCE_NO_SOURCE"

    # Interpretation layer
    INTERPRETATION_ORPHAN = "INTERPRETATION_ORPHAN"
    INTERPRETATION_TERM = "INTERPRETATION_TERM"

    # Cross-engine layer
    AGREEMENT_LOW = "AGREEMENT_LOW"

    # Calculation layer (theoretical no-fail)
    CALCULATION_ERROR = "CALCULATION_ERROR"

    # Sentinel — do NOT use for actual records
    UNKNOWN = "UNKNOWN"

    @classmethod
    def valid_types(cls) -> List["FailureType"]:
        return [t for t in cls if t is not cls.UNKNOWN]


@dataclass(frozen=True)
class FailureRecord:
    """Single diagnostic failure record."""

    failure_id: str
    failure_type: FailureType
    dimension_id: str
    event_id: Optional[str] = None
    details: str = ""
    confidence: float = 1.0

    def to_dict(self) -> dict:
        return {
            "failure_id": self.failure_id,
            "failure_type": self.failure_type.value,
            "dimension_id": self.dimension_id,
            "event_id": self.event_id,
            "details": self.details,
            "confidence": self.confidence,
        }


@dataclass
class DimensionFailureAnalysis:
    """Per-Dimension failure summary."""

    dimension_id: str
    total_failures: int = 0
    failures_by_type: dict = field(default_factory=dict)
    failure_rate: float = 0.0

    def to_dict(self) -> dict:
        return {
            "dimension_id": self.dimension_id,
            "total_failures": self.total_failures,
            "failures_by_type": {k.value: v for k, v in self.failures_by_type.items()},
            "failure_rate": self.failure_rate,
        }


@dataclass
class FailureAnalysisReport:
    """Complete failure analysis report."""

    report_id: str
    analysis_time: str
    total_events: int
    dimensions_analyzed: int
    failures: List[FailureRecord] = field(default_factory=list)
    per_dimension: Dict[str, DimensionFailureAnalysis] = field(default_factory=dict)

    @property
    def total_failure_count(self) -> int:
        return len(self.failures)

    @property
    def dominant_failure_type(self) -> Optional[FailureType]:
        if not self.failures:
            return None
        counts: dict[FailureType, int] = {}
        for f in self.failures:
            counts[f.failure_type] = counts.get(f.failure_type, 0) + 1
        return max(counts, key=counts.get) if counts else None


from typing import Dict  # noqa: E402 (already imported above, kept for compatibility)
