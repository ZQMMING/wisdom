"""Validation Report Generator — aggregates dimension results into final report.

Read-only: only reads from upstream schemas, writes to output report.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

from .state_machine import (
    ValidationStatusReport,
    DimensionStatus,
    ValidationStatus,
    F1AggregationMethod,
    VALIDATION_DIMENSIONS,
)
from .failure_taxonomy import FailureAnalysisReport, FailureRecord, FailureType
from .micro_f1 import compute_all_metrics
from .agreement_evidence import AgreementResult, AgreementEvidenceEngine
from .dimensions import ValidationDimension, DIMENSION_BY_ID


class ValidationReportGenerator:
    """Generate ValidationStatusReport from dimension results.

    Contract:
      - Micro-F1 is MANDATORY primary metric
      - Macro-F1 is AUXILIARY only
      - NOT_IMPLEMENTED / NOT_EVALUABLE excluded from denominator
      - BLOCKED included in denominator
      - No Fortune Score produced
    """

    def __init__(self, report_id: str, dataset_version: str) -> None:
        self.report_id = report_id
        self.dataset_version = dataset_version
        self._dimensions: Dict[str, DimensionStatus] = {}
        self._failures: List[FailureRecord] = []
        self._predictions: List[List[str]] = []
        self._ground_truths: List[List[str]] = []
        self._agreement_engine = AgreementEvidenceEngine()

    def set_dimension_status(self, dimension_id: str, status: DimensionStatus) -> None:
        """Set the status of a single dimension."""
        if dimension_id not in VALIDATION_DIMENSIONS:
            raise ValueError(f"Unknown dimension: {dimension_id}")
        self._dimensions[dimension_id] = status

    def add_failure(self, failure: FailureRecord) -> None:
        """Add a failure record."""
        self._failures.append(failure)

    def add_prediction_ground_truth(
        self, predictions: List[str], ground_truth: List[str]
    ) -> None:
        """Add prediction/ground-truth pair for Micro-F1 computation."""
        self._predictions.append(predictions)
        self._ground_truths.append(ground_truth)

    def register_agreement(self, engine: AgreementEvidenceEngine) -> None:
        """Register agreement evidence engine for analysis."""
        self._agreement_engine = engine

    def generate(self) -> ValidationStatusReport:
        """Generate the final validation report."""
        # Compute Micro-F1 (primary)
        metrics = compute_all_metrics(self._predictions, self._ground_truths)
        micro_f1 = metrics["micro_f1"]
        macro_f1 = metrics["macro_f1"]

        # Count dimensions evaluated (excluding NOT_IMPLEMENTED / NOT_EVALUABLE)
        evaluated = sum(
            1 for ds in self._dimensions.values()
            if not ds.status.is_skippable and ds.status != ValidationStatus.BLOCKED
        )

        # Build report
        report = ValidationStatusReport(
            report_id=self.report_id,
            generated_at=datetime.now(timezone.utc).isoformat(),
            v1_2_version="V1.2",
            dataset_version=self.dataset_version,
            dimensions=self._dimensions,
            f1_aggregation_method=F1AggregationMethod.MICRO,
            overall_f1=micro_f1,
            overall_precision=metrics["micro_precision"],
            overall_recall=metrics["micro_recall"],
            jaccard_match_rate=metrics["jaccard_match_rate"],
            macro_f1=macro_f1,
            total_events=len(self._predictions),
            total_dimensions_evaluated=evaluated,
            total_failures=len(self._failures),
        )
        return report

    def get_failure_analysis(self) -> FailureAnalysisReport:
        """Generate failure analysis from collected failures."""
        per_dim: Dict[str, FailureAnalysisReport.__dict__] = {}  # type: ignore
        from .failure_taxonomy import DimensionFailureAnalysis
        dim_counts: Dict[str, Dict[FailureType, int]] = {}

        for f in self._failures:
            dim_counts.setdefault(f.dimension_id, {})
            dim_counts[f.dimension_id][f.failure_type] = \
                dim_counts[f.dimension_id].get(f.failure_type, 0) + 1

        for dim_id, type_counts in dim_counts.items():
            total = sum(type_counts.values())
            per_dim[dim_id] = DimensionFailureAnalysis(
                dimension_id=dim_id,
                total_failures=total,
                failures_by_type=dict(type_counts),
                failure_rate=total / len(self._predictions) if self._predictions else 0.0,
            )

        return FailureAnalysisReport(
            report_id=f"{self.report_id}_failure",
            analysis_time=datetime.now(timezone.utc).isoformat(),
            total_events=len(self._predictions),
            dimensions_analyzed=len(per_dim),
            failures=self._failures,
            per_dimension=per_dim,
        )
