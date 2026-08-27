"""V-Validation V1.2 — Validation State Machine.

Contract:
  NOT_IMPLEMENTED ≠ FAIL, NOT_EVALUABLE ≠ FAIL, BLOCKED ≠ FAIL
  NOT_IMPLEMENTED / NOT_EVALUABLE are EXCLUDED from denominator
  BLOCKED is INCLUDED in denominator but marked BLOCKED

Micro-F1 = primary metric (MANDATORY). Macro-F1 = auxiliary only.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class ValidationStatus(enum.Enum):
    """Dimension diagnostic status.

    These five non-PASS statuses are mutually exclusive and must NOT be
    conflated with FAIL.

    - NOT_IMPLEMENTED : component not yet built; excluded from denominator
    - NOT_EVALUABLE   : data insufficient for assessment
    - BLOCKED         : depends on upstream schema not yet available
    - PARTIAL         : partial coverage; no failures recorded
    - PASS / FAIL     : definitive diagnostic result
    """

    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    NOT_EVALUABLE = "NOT_EVALUABLE"
    BLOCKED = "BLOCKED"
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"

    @property
    def is_diagnostic(self) -> bool:
        """True for statuses that contribute to diagnostic denominator."""
        return self in (
            ValidationStatus.PASS,
            ValidationStatus.FAIL,
            ValidationStatus.PARTIAL,
        )

    @property
    def is_final(self) -> bool:
        """True for definitive terminal states."""
        return self in (ValidationStatus.PASS, ValidationStatus.FAIL)

    @property
    def is_skippable(self) -> bool:
        """True if this status should be excluded from denominator."""
        return self in (
            ValidationStatus.NOT_IMPLEMENTED,
            ValidationStatus.NOT_EVALUABLE,
        )


class F1AggregationMethod(enum.Enum):
    """V1.2 mandates Micro-F1 for Overall F1. Macro-F1 is auxiliary only."""

    MICRO = "MICRO"
    MACRO = "MACRO"


@dataclass(frozen=True)
class DimensionStatus:
    """Diagnostic state of a single Validation Dimension."""

    dimension_id: str
    status: ValidationStatus
    score: Optional[float] = None
    failures: List[str] = field(default_factory=list)
    coverage_ratio: Optional[float] = None
    blocked_by: Optional[str] = None

    def to_dict(self) -> dict:
        d: Dict = {
            "dimension_id": self.dimension_id,
            "status": self.status.value,
        }
        if self.score is not None:
            d["score"] = self.score
        if self.failures:
            d["failures"] = self.failures
        if self.coverage_ratio is not None:
            d["coverage_ratio"] = self.coverage_ratio
        if self.blocked_by is not None:
            d["blocked_by"] = self.blocked_by
        return d


@dataclass
class ValidationStatusReport:
    """Schema 1 output: whole-validation diagnostic summary."""

    report_id: str
    generated_at: str
    v1_2_version: str
    dataset_version: str

    dimensions: Dict[str, DimensionStatus] = field(default_factory=dict)

    f1_aggregation_method: F1AggregationMethod = F1AggregationMethod.MICRO
    overall_f1: Optional[float] = None
    overall_precision: Optional[float] = None
    overall_recall: Optional[float] = None

    # Auxiliary metrics (must NOT be confused with overall_f1)
    jaccard_match_rate: Optional[float] = None
    macro_f1: Optional[float] = None

    total_events: int = 0
    total_dimensions_evaluated: int = 0
    total_failures: int = 0

    def to_dict(self) -> Dict[str, object]:
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at,
            "v1_2_version": self.v1_2_version,
            "dataset_version": self.dataset_version,
            "f1_aggregation_method": self.f1_aggregation_method.value,
            "overall_f1": self.overall_f1,
            "overall_precision": self.overall_precision,
            "overall_recall": self.overall_recall,
            "jaccard_match_rate": self.jaccard_match_rate,
            "macro_f1": self.macro_f1,
            "dimensions": {k: v.to_dict() for k, v in self.dimensions.items()},
            "total_events": self.total_events,
            "total_dimensions_evaluated": self.total_dimensions_evaluated,
            "total_failures": self.total_failures,
        }


# ─── V1.2-defined 9 Dimension IDs (strict order) ──────────────────────────────

VALIDATION_DIMENSIONS: List[str] = [
    "CALCULATION",
    "SIGNAL",
    "ONTOLOGY",
    "TEMPORAL",
    "SEVERITY",
    "EVIDENCE",
    "INTERPRETATION",
    "CROSS_ENGINE_AGREE",
    "DIRECTIONALITY",
]

assert len(VALIDATION_DIMENSIONS) == 9, \
    f"V1.2 mandates exactly 9 Dimensions, got {len(VALIDATION_DIMENSIONS)}"
