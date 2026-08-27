"""V-Validation V1.2 — Public API."""
from __future__ import annotations

from .state_machine import (
    ValidationStatus,
    F1AggregationMethod,
    DimensionStatus,
    ValidationStatusReport,
    VALIDATION_DIMENSIONS,
)
from .failure_taxonomy import (
    FailureType,
    FailureRecord,
    DimensionFailureAnalysis,
    FailureAnalysisReport,
)
from .micro_f1 import (
    micro_f1,
    micro_precision,
    micro_recall,
    macro_f1,
    jaccard_match_rate,
    compute_all_metrics,
)
from .agreement_evidence import (
    AgreementLevel,
    SignalEvidence,
    AgreementResult,
    AgreementEvidenceEngine,
)
from .dimensions import (
    DimensionRequirement,
    ValidationDimension,
    VALIDATION_DIMENSION_DEFS,
    DIMENSION_BY_ID,
    REQUIRED_DIMENSIONS,
    OPTIONAL_DIMENSIONS,
)
from .read_only import (
    ReadOnlyViolationError,
    enforce_read_only,
    ImmutableInputChecker,
)
from .report_generator import ValidationReportGenerator

__version__ = "1.2.0"
__all__ = [
    # State Machine
    "ValidationStatus",
    "F1AggregationMethod",
    "DimensionStatus",
    "ValidationStatusReport",
    "VALIDATION_DIMENSIONS",
    # Failure Taxonomy
    "FailureType",
    "FailureRecord",
    "DimensionFailureAnalysis",
    "FailureAnalysisReport",
    # Micro-F1
    "micro_f1",
    "micro_precision",
    "micro_recall",
    "macro_f1",
    "jaccard_match_rate",
    "compute_all_metrics",
    # Agreement Evidence
    "AgreementLevel",
    "SignalEvidence",
    "AgreementResult",
    "AgreementEvidenceEngine",
    # Dimensions
    "DimensionRequirement",
    "ValidationDimension",
    "VALIDATION_DIMENSION_DEFS",
    "DIMENSION_BY_ID",
    "REQUIRED_DIMENSIONS",
    "OPTIONAL_DIMENSIONS",
    # Read-Only
    "ReadOnlyViolationError",
    "enforce_read_only",
    "ImmutableInputChecker",
    # Report
    "ValidationReportGenerator",
]
