"""
Contract Tests: Schema 2 — Failure Taxonomy
G1.2, G1.13
"""
from __future__ import annotations

import pytest
from tongshu.spec.failure_taxonomy import (
    FailureType,
    FailureRecord,
    DimensionFailureAnalysis,
    FailureAnalysisReport,
)


# ─── FailureType enum completeness ────────────────────────────────────────────


def test_all_failure_types_exist():
    """All 15 V1.2 FailureTypes must be present."""
    expected = {
        "SIGNAL_MISSING",
        "SIGNAL_FALSE_POS",
        "ONTOLOGY_MISMATCH",
        "DIRECTION_MISMATCH",
        "TEMPORAL_MISMATCH",
        "TEMPORAL_GRANULARITY",
        "SEVERITY_MISMATCH",
        "SEVERITY_MISSING",
        "EVIDENCE_CHAIN_BREAK",
        "EVIDENCE_LEVEL_VIOL",
        "EVIDENCE_NO_SOURCE",
        "INTERPRETATION_ORPHAN",
        "INTERPRETATION_TERM",
        "AGREEMENT_LOW",
        "CALCULATION_ERROR",
        "UNKNOWN",
    }
    actual = {ft.value for ft in FailureType}
    assert actual == expected, f"Mismatch: {actual.symmetric_difference(expected)}"


def test_direction_mismatch_is_independent():
    """DIRECTION_MISMATCH must be its own FailureType, not a subtype of ONTOLOGY_MISMATCH."""
    assert FailureType.DIRECTION_MISMATCH != FailureType.ONTOLOGY_MISMATCH
    assert FailureType.DIRECTION_MISMATCH.value == "DIRECTION_MISMATCH"


def test_failure_type_count():
    assert len(list(FailureType)) == 16  # 15 + UNKNOWN sentinel


# ─── FailureRecord ────────────────────────────────────────────────────────────


def test_failure_record_defaults():
    fr = FailureRecord(
        failure_id="f-001",
        failure_type=FailureType.SIGNAL_MISSING,
        dimension_id="SIGNAL",
    )
    assert fr.event_id is None
    assert fr.details == ""
    assert fr.confidence == 1.0


def test_failure_record_with_event():
    fr = FailureRecord(
        failure_id="f-002",
        failure_type=FailureType.ONTOLOGY_MISMATCH,
        dimension_id="ONTOLOGY",
        event_id="case-042",
        details="Predicted CAREER:JOB_CHANGE but actual was EDUCATION:EXAM",
        confidence=0.85,
    )
    assert fr.event_id == "case-042"
    assert fr.confidence == 0.85


# ─── FailureAnalysisReport ───────────────────────────────────────────────────


def test_empty_report():
    r = FailureAnalysisReport(
        report_id="fa-001",
        analysis_time="2026-08-22T00:00:00Z",
        total_events=10,
        dimensions_analyzed=3,
    )
    assert r.total_failure_count == 0
    assert r.dominant_failure_type is None


def test_dominant_failure_type():
    r = FailureAnalysisReport(
        report_id="fa-002",
        analysis_time="2026-08-22T00:00:00Z",
        total_events=10,
        dimensions_analyzed=3,
        failures=[
            FailureRecord("f1", FailureType.SIGNAL_MISSING, "SIGNAL"),
            FailureRecord("f2", FailureType.SIGNAL_MISSING, "SIGNAL"),
            FailureRecord("f3", FailureType.ONTOLOGY_MISMATCH, "ONTOLOGY"),
        ],
    )
    assert r.dominant_failure_type == FailureType.SIGNAL_MISSING
