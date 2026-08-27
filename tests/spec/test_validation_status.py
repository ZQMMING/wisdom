"""
Contract Tests: Schema 1 — Validation Status
G1.1–G1.2, G1.11-13
"""
from __future__ import annotations

import pytest
from tongshu.spec.validation_status import (
    ValidationStatus,
    F1AggregationMethod,
    DimensionStatus,
    ValidationStatusReport,
    VALIDATION_DIMENSIONS,
)


# ─── Enum completeness ────────────────────────────────────────────────────────


def test_validation_status_enum_values():
    """All 5 non-PASS statuses must exist."""
    statuses = {s.value for s in ValidationStatus}
    assert statuses == {
        "NOT_IMPLEMENTED",
        "NOT_EVALUABLE",
        "BLOCKED",
        "PASS",
        "FAIL",
        "PARTIAL",
    }


def test_status_invariants():
    """NOT_IMPLEMENTED ≠ FAIL, BLOCKED ≠ FAIL, NOT_EVALUABLE ≠ FAIL."""
    assert ValidationStatus.NOT_IMPLEMENTED != ValidationStatus.FAIL
    assert ValidationStatus.BLOCKED != ValidationStatus.FAIL
    assert ValidationStatus.NOT_EVALUABLE != ValidationStatus.FAIL
    assert ValidationStatus.PARTIAL != ValidationStatus.FAIL
    assert ValidationStatus.PASS != ValidationStatus.FAIL


def test_is_diagnostic():
    """Only PASS/FAIL/PARTIAL are diagnostic."""
    for s in [ValidationStatus.NOT_IMPLEMENTED, ValidationStatus.NOT_EVALUABLE]:
        assert not s.is_diagnostic
    for s in [ValidationStatus.PASS, ValidationStatus.FAIL, ValidationStatus.PARTIAL]:
        assert s.is_diagnostic


def test_is_final():
    """Only PASS and FAIL are final."""
    assert ValidationStatus.PASS.is_final
    assert ValidationStatus.FAIL.is_final
    for s in [ValidationStatus.NOT_IMPLEMENTED, ValidationStatus.NOT_EVALUABLE,
              ValidationStatus.BLOCKED, ValidationStatus.PARTIAL]:
        assert not s.is_final


def test_is_skippable():
    """NOT_IMPLEMENTED and NOT_EVALUABLE are skippable."""
    assert ValidationStatus.NOT_IMPLEMENTED.is_skippable
    assert ValidationStatus.NOT_EVALUABLE.is_skippable
    assert not ValidationStatus.FAIL.is_skippable


def test_f1_aggregation_enum():
    assert F1AggregationMethod.MICRO.value == "MICRO"
    assert F1AggregationMethod.MACRO.value == "MACRO"


# ─── DimensionStatus ─────────────────────────────────────────────────────────


def test_dimension_status_defaults():
    ds = DimensionStatus(dimension_id="CALCULATION", status=ValidationStatus.PASS)
    assert ds.score is None
    assert ds.failures == []
    assert ds.coverage_ratio is None
    assert ds.blocked_by is None


def test_dimension_status_to_dict():
    ds = DimensionStatus(
        dimension_id="SIGNAL",
        status=ValidationStatus.PARTIAL,
        score=0.65,
        coverage_ratio=0.40,
        blocked_by=None,
    )
    d = ds.to_dict()
    assert d["dimension_id"] == "SIGNAL"
    assert d["status"] == "PARTIAL"
    assert d["score"] == 0.65
    assert d["coverage_ratio"] == 0.40


def test_dimension_status_blocked():
    ds = DimensionStatus(
        dimension_id="INTERPRETATION",
        status=ValidationStatus.BLOCKED,
        blocked_by="schema_8",
    )
    assert ds.blocked_by == "schema_8"
    assert ds.to_dict()["blocked_by"] == "schema_8"


# ─── VALIDATION_STATUS_REPORT ────────────────────────────────────────────────


def test_validation_dimensions_count():
    assert len(VALIDATION_DIMENSIONS) == 9


def test_validation_dimensions_order():
    expected = [
        "CALCULATION", "SIGNAL", "ONTOLOGY", "TEMPORAL", "SEVERITY",
        "EVIDENCE", "INTERPRETATION", "CROSS_ENGINE_AGREE", "DIRECTIONALITY",
    ]
    assert VALIDATION_DIMENSIONS == expected


def test_report_minimal():
    r = ValidationStatusReport(
        report_id="test-001",
        generated_at="2026-08-22T00:00:00Z",
        v1_2_version="V1.2",
        dataset_version="v1",
    )
    d = r.to_dict()
    assert d["report_id"] == "test-001"
    assert d["f1_aggregation_method"] == "MICRO"
    assert d["overall_f1"] is None
    assert d["dimensions"] == {}


def test_report_with_dimension():
    r = ValidationStatusReport(
        report_id="r1",
        generated_at="2026-08-22T00:00:00Z",
        v1_2_version="V1.2",
        dataset_version="v2",
        dimensions={"CALCULATION": DimensionStatus(
            dimension_id="CALCULATION",
            status=ValidationStatus.PASS,
            score=0.95,
        )},
        overall_f1=0.88,
        overall_precision=0.90,
        overall_recall=0.86,
        jaccard_match_rate=0.85,
        macro_f1=0.87,
        total_events=100,
        total_dimensions_evaluated=9,
        total_failures=3,
    )
    d = r.to_dict()
    assert d["overall_f1"] == 0.88
    assert d["dimensions"]["CALCULATION"]["status"] == "PASS"
    assert d["total_events"] == 100


def test_micro_f1_is_default():
    r = ValidationStatusReport(
        report_id="r2",
        generated_at="2026-08-22T00:00:00Z",
        v1_2_version="V1.2",
        dataset_version="v1",
    )
    assert r.f1_aggregation_method == F1AggregationMethod.MICRO
