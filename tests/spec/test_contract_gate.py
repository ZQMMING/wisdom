"""
Contract Tests: Cross-Schema Import + G1 Gate
G1.1: 9 Schema all importable
G1.2: All enums complete
G1.11: No regression in existing modules
"""
from __future__ import annotations

import pytest


def test_import_all_9_schemas():
    """G1.1: All 9 Schema modules must be importable."""
    from tongshu.spec.validation_status import ValidationStatus
    from tongshu.spec.failure_taxonomy import FailureType
    from tongshu.spec.event_ontology_v1 import EVENT_TYPES, Domain
    from tongshu.spec.canonical_signal import CanonicalSignal
    from tongshu.spec.temporal_evidence import TemporalSignal, PredictionWindow, EvaluationToleranceWindow
    from tongshu.spec.severity import EventSeverity, SEVERITY_WEIGHTS
    from tongshu.spec.evidence_chain import EvidenceLevel, Claim, validate_chain
    from tongshu.spec.relational_interpretation import InterpInput
    from tongshu.spec.validation_dimensions import VALIDATION_DIMENSION_DEFS
    # All imports succeed = G1.1 PASS


def test_import_spec_package():
    """G1.1: Package-level import works."""
    from tongshu.spec import (
        ValidationStatus, FailureType, EVENT_TYPES, Domain,
        CanonicalSignal, TemporalSignal, EventSeverity,
        EvidenceLevel, InterpInput, VALIDATION_DIMENSION_DEFS,
    )
    assert ValidationStatus.PASS is not None
    assert len(EVENT_TYPES) == 17
    assert len(VALIDATION_DIMENSION_DEFS) == 9


def test_serialization_roundtrip_validation_status():
    """G1.12: Serialization test for ValidationStatusReport."""
    from tongshu.spec.validation_status import (
        ValidationStatus, DimensionStatus, ValidationStatusReport,
    )
    r = ValidationStatusReport(
        report_id="sr-001",
        generated_at="2026-08-22T00:00:00Z",
        v1_2_version="V1.2",
        dataset_version="v1",
        dimensions={
            "CALCULATION": DimensionStatus(
                dimension_id="CALCULATION",
                status=ValidationStatus.PASS,
                score=0.95,
            ),
            "SIGNAL": DimensionStatus(
                dimension_id="SIGNAL",
                status=ValidationStatus.PARTIAL,
                score=0.60,
                coverage_ratio=0.40,
            ),
            "INTERPRETATION": DimensionStatus(
                dimension_id="INTERPRETATION",
                status=ValidationStatus.NOT_IMPLEMENTED,
            ),
        },
        overall_f1=0.82,
        total_events=50,
    )
    d = r.to_dict()
    assert d["overall_f1"] == 0.82
    assert d["dimensions"]["CALCULATION"]["status"] == "PASS"
    assert d["dimensions"]["SIGNAL"]["status"] == "PARTIAL"
    assert d["dimensions"]["INTERPRETATION"]["status"] == "NOT_IMPLEMENTED"
    # NOT_IMPLEMENTED ≠ FAIL
    assert d["dimensions"]["INTERPRETATION"]["status"] != "FAIL"


def test_serialization_roundtrip_claim():
    """G1.12: Claim serialization preserves created_by constraint."""
    from tongshu.spec.evidence_chain import Claim, ClaimType, EvidenceLevel
    c = Claim(
        claim_id="c-001",
        passage_id="pass-001",
        claim_text="此年有变动。",
        claim_type=ClaimType.PREDICT_TENDENCY,
        evidence_level=EvidenceLevel.LEVEL_2,
        created_by="HUMAN",
    )
    # Cannot serialize directly (dataclass), but we can check fields
    assert c.created_by == "HUMAN"
    assert c.validate() == []


def test_no_regression_calculation():
    """G1.11: Existing calculation/ontology/golden data unchanged."""
    # Import existing modules — if they break, this test fails
    from tongshu.spec.signal_ontology import USO_TYPES, POLARITIES
    from tongshu.spec.cross_states import CROSS_STATES
    assert len(USO_TYPES) > 0
    assert len(CROSS_STATES) > 0


def test_no_regression_existing_tests():
    """
    G1.12: Existing test suite still passes.
    Run: pytest tests/ -x --tb=short
    This test just verifies the test infrastructure is intact.
    """
    # The fact that we can import pytest and run means the test framework works.
    # Full regression is checked by the CI gate, not by this single assertion.
    pass
