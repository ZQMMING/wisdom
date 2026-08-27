"""
Contract Tests: Schema 9 — Validation Dimensions
G1.13: Exactly 9 Dimensions, VALIDATION_STATUS is summary not #10
G1.10: Validation read-only contract
"""
from __future__ import annotations

import pytest
from tongshu.spec.validation_dimensions import (
    DimensionRequirement,
    ValidationDimension,
    VALIDATION_DIMENSION_DEFS,
    DIMENSION_BY_ID,
    ValidationDimensionResult,
    enforce_read_only,
)


# ─── Exactly 9 Dimensions (G1.13) ────────────────────────────────────────────


def test_nine_dimensions():
    assert len(VALIDATION_DIMENSION_DEFS) == 9


def test_dimension_ids_match_spec():
    expected_ids = [
        "CALCULATION", "SIGNAL", "ONTOLOGY", "TEMPORAL", "SEVERITY",
        "EVIDENCE", "INTERPRETATION", "CROSS_ENGINE_AGREE", "DIRECTIONALITY",
    ]
    actual_ids = [d.dimension_id for d in VALIDATION_DIMENSION_DEFS]
    assert actual_ids == expected_ids


def test_no_validation_status_as_dimension():
    """G1.13: VALIDATION_STATUS must NOT be Dimension #10."""
    ids = {d.dimension_id for d in VALIDATION_DIMENSION_DEFS}
    assert "VALIDATION_STATUS" not in ids


def test_all_required_dims():
    """CALCULATION through CROSS_ENGINE_AGREE are REQUIRED."""
    required_ids = {"CALCULATION", "SIGNAL", "ONTOLOGY", "TEMPORAL", "SEVERITY",
                    "EVIDENCE", "INTERPRETATION", "CROSS_ENGINE_AGREE"}
    actual = {d.dimension_id for d in VALIDATION_DIMENSION_DEFS if d.requirement == DimensionRequirement.REQUIRED}
    assert actual == required_ids


def test_directionality_optional():
    """DIRECTIONALITY is OPTIONAL."""
    dir_dim = DIMENSION_BY_ID["DIRECTIONALITY"]
    assert dir_dim.requirement == DimensionRequirement.OPTIONAL


# ─── Dimension definitions ───────────────────────────────────────────────────


def test_calculation_phase_1():
    dim = DIMENSION_BY_ID["CALCULATION"]
    assert dim.phase == 1
    assert dim.target_status == "PASS"


def test_signal_phase_3():
    dim = DIMENSION_BY_ID["SIGNAL"]
    assert dim.phase == 3


def test_evidence_phase_2():
    dim = DIMENSION_BY_ID["EVIDENCE"]
    assert dim.phase == 2


def test_interpretation_phase_6():
    dim = DIMENSION_BY_ID["INTERPRETATION"]
    assert dim.phase == 6
    assert dim.target_status == "NOT_IMPLEMENTED"


# ─── O(1) lookup ─────────────────────────────────────────────────────────────


def test_dim_by_id_contains_all():
    for d in VALIDATION_DIMENSION_DEFS:
        assert DIMENSION_BY_ID[d.dimension_id] is d


def test_dim_by_id_exact_size():
    assert len(DIMENSION_BY_ID) == 9


# ─── ValidationDimensionResult ───────────────────────────────────────────────


def test_dimension_result_defaults():
    r = ValidationDimensionResult(dimension_id="CALCULATION", status="PASS")
    assert r.score is None
    assert r.failures == []
    assert r.details == {}


def test_dimension_result_to_dict():
    r = ValidationDimensionResult(
        dimension_id="ONTOLOGY",
        status="FAIL",
        score=0.72,
        failures=["ONTOLOGY_MISMATCH", "DIRECTION_MISMATCH"],
        details={"mismatches": 3},
    )
    d = r.to_dict()
    assert d["dimension_id"] == "ONTOLOGY"
    assert d["status"] == "FAIL"
    assert d["score"] == 0.72
    assert d["failures"] == ["ONTOLOGY_MISMATCH", "DIRECTION_MISMATCH"]
    assert d["details"] == {"mismatches": 3}


# ─── Read-only contract (G1.10) ──────────────────────────────────────────────


def test_enforce_read_only_exists():
    """The read-only contract function must exist."""
    enforce_read_only("test_contract")  # should not raise


def test_validation_dimension_no_write_to_calculation():
    """Validation Dimensions must not write to Calculation engine data."""
    # This is a structural invariant: ValidationDimension.reads_from
    # should only reference L0/L1 schema IDs, never L3 (interpretation) write targets.
    for dim in VALIDATION_DIMENSION_DEFS:
        for ref in dim.reads_from:
            assert not ref.startswith("write_"), \
                f"Dimension {dim.dimension_id} references write target {ref}"
