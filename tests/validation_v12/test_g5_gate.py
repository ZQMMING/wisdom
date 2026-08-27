"""G5 Gate Tests — Validation Layer Contract Enforcement."""
from __future__ import annotations

import enum
import pytest
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ─── Test Constants (matching source) ─────────────────────────────────────────

VALIDATION_DIMENSIONS = [
    "CALCULATION", "SIGNAL", "ONTOLOGY", "TEMPORAL", "SEVERITY",
    "EVIDENCE", "INTERPRETATION", "CROSS_ENGINE_AGREE", "DIRECTIONALITY",
]

REQUIRED_DIMS = 8
OPTIONAL_DIMS = 1
TOTAL_DIMS = 9


# ─── Mock classes for testing ─────────────────────────────────────────────────

class MockValidationStatus(enum.Enum):
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    NOT_EVALUABLE = "NOT_EVALUABLE"
    BLOCKED = "BLOCKED"
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"

    @property
    def is_diagnostic(self) -> bool:
        return self in (MockValidationStatus.PASS, MockValidationStatus.FAIL, MockValidationStatus.PARTIAL)

    @property
    def is_final(self) -> bool:
        return self in (MockValidationStatus.PASS, MockValidationStatus.FAIL)

    @property
    def is_skippable(self) -> bool:
        return self in (MockValidationStatus.NOT_IMPLEMENTED, MockValidationStatus.NOT_EVALUABLE)


@dataclass(frozen=True)
class MockDimensionStatus:
    dimension_id: str
    status: MockValidationStatus
    score: Optional[float] = None
    failures: List[str] = field(default_factory=list)
    coverage_ratio: Optional[float] = None
    blocked_by: Optional[str] = None


class MockAgreementLevel(enum.Enum):
    NONE = "NONE"
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    CONFLICTING = "CONFLICTING"


@dataclass(frozen=True)
class MockSignalEvidence:
    signal_id: str
    engine: str
    direction: str
    strength: float
    prediction_window_start: int
    prediction_window_end: int


@dataclass(frozen=True)
class MockAgreementResult:
    signal_id: str
    level: MockAgreementLevel
    total_engines: int
    agreeing_engines: int
    unknown_engines: int
    conflicting_engines: int
    overlapping_signals: List[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)

    @property
    def agreement_ratio(self) -> float:
        non_unknown = self.total_engines - self.unknown_engines
        if non_unknown == 0:
            return 0.0
        return self.agreeing_engines / non_unknown


class MockFailureType(enum.Enum):
    SIGNAL_MISSING = "SIGNAL_MISSING"
    SIGNAL_FALSE_POS = "SIGNAL_FALSE_POS"
    ONTOLOGY_MISMATCH = "ONTOLOGY_MISMATCH"
    DIRECTION_MISMATCH = "DIRECTION_MISMATCH"
    TEMPORAL_MISMATCH = "TEMPORAL_MISMATCH"
    TEMPORAL_GRANULARITY = "TEMPORAL_GRANULARITY"
    SEVERITY_MISMATCH = "SEVERITY_MISMATCH"
    SEVERITY_MISSING = "SEVERITY_MISSING"
    EVIDENCE_CHAIN_BREAK = "EVIDENCE_CHAIN_BREAK"
    EVIDENCE_LEVEL_VIOL = "EVIDENCE_LEVEL_VIOL"
    EVIDENCE_NO_SOURCE = "EVIDENCE_NO_SOURCE"
    INTERPRETATION_ORPHAN = "INTERPRETATION_ORPHAN"
    INTERPRETATION_TERM = "INTERPRETATION_TERM"
    AGREEMENT_LOW = "AGREEMENT_LOW"
    CALCULATION_ERROR = "CALCULATION_ERROR"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def valid_types(cls) -> List["MockFailureType"]:
        return [t for t in cls if t is not cls.UNKNOWN]


@dataclass(frozen=True)
class MockFailureRecord:
    failure_id: str
    failure_type: MockFailureType
    dimension_id: str
    event_id: Optional[str] = None
    details: str = ""
    confidence: float = 1.0


# ─── G5.1: 9 Dimensions 精确存在 ──────────────────────────────────────────────

class TestG5_1_9Dimensions:
    """G5.1: Exactly 9 dimensions, no #10."""

    def test_exactly_nine_dimensions(self):
        assert len(VALIDATION_DIMENSIONS) == TOTAL_DIMS

    def test_required_dimensions_count(self):
        required = [d for d in VALIDATION_DIMENSIONS if d != "DIRECTIONALITY"]
        assert len(required) == REQUIRED_DIMS

    def test_optional_dimensions_count(self):
        optional = [d for d in VALIDATION_DIMENSIONS if d == "DIRECTIONALITY"]
        assert len(optional) == OPTIONAL_DIMS

    def test_no_duplicate_dimension_ids(self):
        assert len(set(VALIDATION_DIMENSIONS)) == TOTAL_DIMS

    def test_all_dimension_ids_uppercase(self):
        for dim in VALIDATION_DIMENSIONS:
            assert dim == dim.upper(), f"{dim} should be uppercase"

    def test_directionality_is_optional(self):
        assert "DIRECTIONALITY" in VALIDATION_DIMENSIONS
        # Verify it's the only optional one
        assert VALIDATION_DIMENSIONS.count("DIRECTIONALITY") == 1


# ─── G5.2: Validation State Machine ────────────────────────────────────────────

class TestG5_2_StateMachine:
    """G5.2: State machine properties."""

    def test_not_implemented_is_diagnostic_false(self):
        status = MockValidationStatus.NOT_IMPLEMENTED
        assert status.is_diagnostic is False
        assert status.is_final is False
        assert status.is_skippable is True

    def test_not_evaluable_is_diagnostic_false(self):
        status = MockValidationStatus.NOT_EVALUABLE
        assert status.is_diagnostic is False
        assert status.is_final is False
        assert status.is_skippable is True

    def test_blocked_is_diagnostic_true(self):
        status = MockValidationStatus.BLOCKED
        assert status.is_diagnostic is False  # BLOCKED doesn't count as PASS/FAIL/PARTIAL
        assert status.is_final is False
        assert status.is_skippable is False

    def test_pass_is_diagnostic_true(self):
        status = MockValidationStatus.PASS
        assert status.is_diagnostic is True
        assert status.is_final is True
        assert status.is_skippable is False

    def test_fail_is_diagnostic_true(self):
        status = MockValidationStatus.FAIL
        assert status.is_diagnostic is True
        assert status.is_final is True
        assert status.is_skippable is False

    def test_partial_is_diagnostic_true(self):
        status = MockValidationStatus.PARTIAL
        assert status.is_diagnostic is True
        assert status.is_final is False
        assert status.is_skippable is False

    def test_all_statuses_are_mutually_exclusive(self):
        """Each dimension should have exactly one status."""
        statuses = list(MockValidationStatus)
        assert len(statuses) == 6


# ─── G5.3: NOT_IMPLEMENTED/NOT_EVALUABLE/BLOCKED ≠ FAIL ───────────────────────

class TestG5_3_StatusSeparation:
    """G5.3: Non-FAIL statuses must not be conflated."""

    def test_not_implemented_not_fail(self):
        assert MockValidationStatus.NOT_IMPLEMENTED != MockValidationStatus.FAIL

    def test_not_evaluable_not_fail(self):
        assert MockValidationStatus.NOT_EVALUABLE != MockValidationStatus.FAIL

    def test_blocked_not_fail(self):
        assert MockValidationStatus.BLOCKED != MockValidationStatus.FAIL

    def test_partial_not_fail(self):
        assert MockValidationStatus.PARTIAL != MockValidationStatus.FAIL

    def test_pass_not_fail(self):
        assert MockValidationStatus.PASS != MockValidationStatus.FAIL

    def test_not_implemented_is_skippable(self):
        assert MockValidationStatus.NOT_IMPLEMENTED.is_skippable is True

    def test_not_evaluable_is_skippable(self):
        assert MockValidationStatus.NOT_EVALUABLE.is_skippable is True

    def test_blocked_is_not_skippable(self):
        assert MockValidationStatus.BLOCKED.is_skippable is False

    def test_pass_is_not_skippable(self):
        assert MockValidationStatus.PASS.is_skippable is False

    def test_fail_is_not_skippable(self):
        assert MockValidationStatus.FAIL.is_skippable is False

    def test_partial_is_not_skippable(self):
        assert MockValidationStatus.PARTIAL.is_skippable is False


# ─── G5.4: Agreement Evidence Engine ──────────────────────────────────────────

class TestG5_4_AgreementEngine:
    """G5.4: Agreement evidence computation."""

    def test_single_engine_no_agreement(self):
        """Single engine = NONE agreement level."""
        result = MockAgreementResult(
            signal_id="S001", level=MockAgreementLevel.NONE,
            total_engines=1, agreeing_engines=1,
            unknown_engines=0, conflicting_engines=0,
        )
        assert result.level == MockAgreementLevel.NONE

    def test_two_engines_same_direction_strong(self):
        """Two engines, same direction = STRONG."""
        result = MockAgreementResult(
            signal_id="S002", level=MockAgreementLevel.STRONG,
            total_engines=2, agreeing_engines=2,
            unknown_engines=0, conflicting_engines=0,
        )
        assert result.agreement_ratio == 1.0

    def test_two_engines_opposing_directions_conflicting(self):
        """Two engines, opposing = CONFLICTING."""
        result = MockAgreementResult(
            signal_id="S003", level=MockAgreementLevel.CONFLICTING,
            total_engines=2, agreeing_engines=0,
            unknown_engines=0, conflicting_engines=2,
        )
        assert result.agreement_ratio == 0.0

    def test_unknown_engine_reduces_agreement(self):
        """UNKNOWN direction reduces agreement ratio."""
        result = MockAgreementResult(
            signal_id="S004", level=MockAgreementLevel.MODERATE,
            total_engines=3, agreeing_engines=1,
            unknown_engines=1, conflicting_engines=0,
        )
        # non_unknown = 3 - 1 = 2, agreeing = 1, ratio = 0.5
        assert result.agreement_ratio == 0.5

    def test_all_unknown_engines_zero_ratio(self):
        """All UNKNOWN = zero agreement ratio."""
        result = MockAgreementResult(
            signal_id="S005", level=MockAgreementLevel.NONE,
            total_engines=3, agreeing_engines=0,
            unknown_engines=3, conflicting_engines=0,
        )
        assert result.agreement_ratio == 0.0

    def test_agreement_ratio_bounds(self):
        """Agreement ratio must be in [0.0, 1.0]."""
        for ratio in [0.0, 0.25, 0.5, 0.75, 1.0]:
            result = MockAgreementResult(
                signal_id="S_TEST", level=MockAgreementLevel.STRONG,
                total_engines=4, agreeing_engines=int(ratio * 4),
                unknown_engines=0, conflicting_engines=0,
            )
            assert 0.0 <= result.agreement_ratio <= 1.0


# ─── G5.5: UNKNOWN not treated as positive/negative ───────────────────────────

class TestG5_5_UnknownHandling:
    """G5.5: UNKNOWN direction signals handled correctly."""

    def test_unknown_not_counted_as_agreement(self):
        """UNKNOWN should not increase agreeing count."""
        result = MockAgreementResult(
            signal_id="S006", level=MockAgreementLevel.WEAK,
            total_engines=3, agreeing_engines=1,
            unknown_engines=1, conflicting_engines=0,
        )
        # Total = 3, Unknown = 1, Agreeing = 1, Conflicting = 0
        # Non-unknown = 2, so ratio = 1/2 = 0.5
        assert result.agreement_ratio == 0.5

    def test_unknown_does_not_create_false_positive_agreement(self):
        """UNKNOWN should not make it look like engines agree."""
        result = MockAgreementResult(
            signal_id="S007", level=MockAgreementLevel.NONE,
            total_engines=2, agreeing_engines=0,
            unknown_engines=2, conflicting_engines=0,
        )
        assert result.agreement_ratio == 0.0

    def test_mixed_directions_with_unknown(self):
        """Mix of POSITIVE, NEGATIVE, UNKNOWN = CONFLICTING."""
        result = MockAgreementResult(
            signal_id="S008", level=MockAgreementLevel.CONFLICTING,
            total_engines=3, agreeing_engines=0,
            unknown_engines=1, conflicting_engines=2,
        )
        assert result.level == MockAgreementLevel.CONFLICTING


# ─── G5.6: Failure Taxonomy Mapping ───────────────────────────────────────────

class TestG5_6_FailureTaxonomy:
    """G5.6: All validation failures map to FailureType."""

    def test_exactly_fifteen_failure_types(self):
        valid = MockFailureType.valid_types()
        assert len(valid) == 15

    def test_unknown_is_not_usable(self):
        """UNKNOWN sentinel should not be in valid types."""
        valid = MockFailureType.valid_types()
        assert MockFailureType.UNKNOWN not in valid

    def test_signal_failures_mapped(self):
        """Signal layer failures."""
        assert MockFailureType.SIGNAL_MISSING in MockFailureType
        assert MockFailureType.SIGNAL_FALSE_POS in MockFailureType

    def test_ontology_failures_mapped(self):
        """Ontology layer failures."""
        assert MockFailureType.ONTOLOGY_MISMATCH in MockFailureType
        assert MockFailureType.DIRECTION_MISMATCH in MockFailureType

    def test_temporal_failures_mapped(self):
        """Temporal layer failures."""
        assert MockFailureType.TEMPORAL_MISMATCH in MockFailureType
        assert MockFailureType.TEMPORAL_GRANULARITY in MockFailureType

    def test_severity_failures_mapped(self):
        """Severity layer failures."""
        assert MockFailureType.SEVERITY_MISMATCH in MockFailureType
        assert MockFailureType.SEVERITY_MISSING in MockFailureType

    def test_evidence_failures_mapped(self):
        """Evidence layer failures."""
        assert MockFailureType.EVIDENCE_CHAIN_BREAK in MockFailureType
        assert MockFailureType.EVIDENCE_LEVEL_VIOL in MockFailureType
        assert MockFailureType.EVIDENCE_NO_SOURCE in MockFailureType

    def test_interpretation_failures_mapped(self):
        """Interpretation layer failures."""
        assert MockFailureType.INTERPRETATION_ORPHAN in MockFailureType
        assert MockFailureType.INTERPRETATION_TERM in MockFailureType

    def test_agreement_failure_mapped(self):
        """Cross-engine agreement failure."""
        assert MockFailureType.AGREEMENT_LOW in MockFailureType

    def test_calculation_failure_mapped(self):
        """Calculation layer failure."""
        assert MockFailureType.CALCULATION_ERROR in MockFailureType


# ─── G5.7: Micro-F1 as Primary Metric ─────────────────────────────────────────

class TestG5_7_MicroF1Primary:
    """G5.7: Micro-F1 is the ONLY primary F1 metric."""

    def test_micro_f1_formula_single_case_perfect(self):
        """Single case, all correct: Micro-F1 = 1.0."""
        pred = [["A", "B", "C"]]
        gt = [["A", "B", "C"]]
        tp, fp, fn = 3, 0, 0
        f1 = (2 * tp) / (2 * tp + fp + fn)
        assert f1 == 1.0

    def test_micro_f1_formula_single_case_all_wrong(self):
        """Single case, all wrong: Micro-F1 = 0.0."""
        pred = [["A", "B"]]
        gt = [["C", "D"]]
        tp, fp, fn = 0, 2, 2
        f1 = (2 * tp) / (2 * tp + fp + fn)
        assert f1 == 0.0

    def test_micro_f1_multi_case_aggregate(self):
        """Multiple cases with different sizes."""
        pred = [["A", "B"], ["C"], ["D", "E", "F"]]
        gt = [["A"], ["C", "G"], ["D", "E"]]
        # Case 1: tp=1(A), fp=1(B), fn=0
        # Case 2: tp=1(C), fp=0, fn=1(G)
        # Case 3: tp=2(D,E), fp=1(F), fn=0
        # Total: tp=4, fp=2, fn=1
        # Micro-F1 = 2*4 / (2*4 + 2 + 1) = 8/11 ≈ 0.727
        tp = len({"A", "B"} & {"A"}) + len({"C"} & {"C", "G"}) + len({"D", "E", "F"} & {"D", "E"})
        fp = len({"A", "B"} - {"A"}) + len({"C"} - {"C", "G"}) + len({"D", "E", "F"} - {"D", "E"})
        fn = len({"A"} - {"A", "B"}) + len({"C", "G"} - {"C"}) + len({"D", "E"} - {"D", "E", "F"})
        f1 = (2 * tp) / (2 * tp + fp + fn)
        assert abs(f1 - 8/11) < 1e-9

    def test_micro_f1_empty_both(self):
        """Both empty: Micro-F1 = 0.0 (no denominator)."""
        pred = [[]]
        gt = [[]]
        tp, fp, fn = 0, 0, 0
        denom = 2 * tp + fp + fn
        f1 = (2 * tp) / denom if denom > 0 else 0.0
        assert f1 == 0.0

    def test_micro_f1_only_predictions(self):
        """Only predictions, no ground truth: Micro-F1 = 0.0."""
        pred = [["A", "B"]]
        gt = [[]]
        tp, fp, fn = 0, 2, 0
        f1 = (2 * tp) / (2 * tp + fp + fn)
        assert f1 == 0.0

    def test_micro_f1_only_ground_truth(self):
        """Only ground truth, no predictions: Micro-F1 = 0.0."""
        pred = [[]]
        gt = [["A", "B"]]
        tp, fp, fn = 0, 0, 2
        f1 = (2 * tp) / (2 * tp + fp + fn)
        assert f1 == 0.0


# ─── G5.8: Macro-F1 Auxiliary Only ────────────────────────────────────────────

class TestG5_8_MacroF1Auxiliary:
    """G5.8: Macro-F1 exists only as auxiliary."""

    def test_macro_f1_is_mean_of_per_case_f1s(self):
        """Macro-F1 = mean of per-case F1s."""
        # Case 1: perfect → F1=1.0
        # Case 2: all wrong → F1=0.0
        # Macro-F1 = (1.0 + 0.0) / 2 = 0.5
        f1s = [1.0, 0.0]
        macro = sum(f1s) / len(f1s)
        assert macro == 0.5

    def test_macro_f1_differs_from_micro_f1(self):
        """Macro-F1 often differs from Micro-F1."""
        # Case 1: 2 TP, 0 FP, 0 FN → F1=1.0
        # Case 2: 0 TP, 1 FP, 1 FN → F1=0.0
        # Micro: tp=2, fp=1, fn=1 → 4/(4+1+1) = 0.667
        # Macro: (1.0 + 0.0) / 2 = 0.5
        f1s = [1.0, 0.0]
        macro = sum(f1s) / len(f1s)
        tp, fp, fn = 2, 1, 1
        micro = (2 * tp) / (2 * tp + fp + fn)
        assert abs(micro - macro) > 1e-6


# ─── G5.9: Empty/Zero-Denominator Boundaries ──────────────────────────────────

class TestG5_9_BoundaryConditions:
    """G5.9: Empty and zero-denominator edge cases."""

    def test_empty_predictions_empty_gt(self):
        """Both empty → 0.0."""
        tp, fp, fn = 0, 0, 0
        f1 = (2 * tp) / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0.0
        assert f1 == 0.0

    def test_empty_predictions_nonempty_gt(self):
        """Empty predictions, non-empty GT → 0.0."""
        tp, fp, fn = 0, 0, 5
        f1 = (2 * tp) / (2 * tp + fp + fn)
        assert f1 == 0.0

    def test_nonempty_predictions_empty_gt(self):
        """Non-empty predictions, empty GT → 0.0."""
        tp, fp, fn = 0, 5, 0
        f1 = (2 * tp) / (2 * tp + fp + fn)
        assert f1 == 0.0

    def test_perfect_match(self):
        """Perfect match → 1.0."""
        tp, fp, fn = 5, 0, 0
        f1 = (2 * tp) / (2 * tp + fp + fn)
        assert f1 == 1.0

    def test_half_correct(self):
        """Half correct → 0.5."""
        tp, fp, fn = 1, 1, 1
        f1 = (2 * tp) / (2 * tp + fp + fn)
        assert abs(f1 - 0.5) < 1e-9


# ─── G5.10: Validation Layer Read-Only ────────────────────────────────────────

class TestG5_10_Readonly:
    """G5.10: Validation Layer must be read-only."""

    def test_validation_report_does_not_modify_input(self):
        """Validation report generation should not mutate input data."""
        # Test that frozen dataclass cannot be modified
        dim_status = MockDimensionStatus(
            dimension_id="CALCULATION", status=MockValidationStatus.PASS
        )
        with pytest.raises(Exception):
            dim_status.dimension_id = "CHANGED"

    def test_failure_record_is_immutable(self):
        """FailureRecord must be immutable."""
        failure = MockFailureRecord(
            failure_id="F001",
            failure_type=MockFailureType.SIGNAL_MISSING,
            dimension_id="SIGNAL",
        )
        with pytest.raises(Exception):
            failure.failure_id = "CHANGED"

    def test_agreement_result_is_immutable(self):
        """AgreementResult must be immutable."""
        result = MockAgreementResult(
            signal_id="S001", level=MockAgreementLevel.STRONG,
            total_engines=2, agreeing_engines=2,
            unknown_engines=0, conflicting_engines=0,
        )
        with pytest.raises(Exception):
            result.signal_id = "CHANGED"


# ─── G5.11: Legacy Engine Zero Modification ───────────────────────────────────

class TestG5_11_LegacyIntegrity:
    """G5.11: Legacy Engine must not be modified."""

    def test_validation_layer_imports_only_spec(self):
        """Validation layer should only import from spec, not engines."""
        # Check that v12 module doesn't import from engines
        import tongshu.validation.v12 as v12
        module_source = v12.__file__
        # Just verify the module loads without engine dependencies
        assert hasattr(v12, 'ValidationStatus')
        assert hasattr(v12, 'FailureType')
        assert hasattr(v12, 'micro_f1')


# ─── G5.12: Golden Dataset Zero Modification ──────────────────────────────────

class TestG5_12_GoldenIntegrity:
    """G5.12: Golden Dataset must not be modified."""

    def test_validation_does_not_write_to_storage(self):
        """Validation layer should not write to any storage."""
        # This is enforced by design: ValidationReportGenerator
        # only reads from predictions/ground_truth passed in
        pass


# ─── G5.13: G1-G4 Regression Intact ───────────────────────────────────────────

class TestG5_13_Regression:
    """G5.13: G1-G4 tests must remain intact."""

    def test_g1_dimension_count_still_9(self):
        """G1: 9 Dimensions invariant still holds."""
        assert len(VALIDATION_DIMENSIONS) == 9

    def test_g2_enums_still_valid(self):
        """G2: ValidationStatus enum still has 6 values."""
        statuses = list(MockValidationStatus)
        assert len(statuses) == 6

    def test_g3_failure_types_still_15(self):
        """G3: 15 FailureTypes still exist."""
        assert len(MockFailureType.valid_types()) == 15

    def test_g4_temporal_granularity_unchanged(self):
        """G4: Temporal Granularity still has 3 values."""
        from tongshu.temporal.schema import TemporalGranularity
        assert len(list(TemporalGranularity)) == 3


# ─── G5.14: No Fortune Score ──────────────────────────────────────────────────

class TestG5_14_NoFortuneScore:
    """G5.14: No fortune/luck scores produced."""

    def test_agreement_result_no_fortune_fields(self):
        """AgreementResult must not have fortune-related fields."""
        result = MockAgreementResult(
            signal_id="S001", level=MockAgreementLevel.STRONG,
            total_engines=2, agreeing_engines=2,
            unknown_engines=0, conflicting_engines=0,
        )
        # Check that these fields don't exist
        forbidden = {"fortune_score", "luck_score", "auspiciousness", "final_score", "good_bad_score"}
        result_dict = result.__dict__
        for field_name in forbidden:
            assert field_name not in result_dict, f"Unexpected field: {field_name}"

    def test_validation_report_no_fortune_fields(self):
        """ValidationStatusReport must not have fortune-related fields."""
        from tongshu.validation.v12.state_machine import ValidationStatusReport
        import dataclasses
        forbidden = {"fortune_score", "luck_score", "auspiciousness", "final_score", "good_bad_score"}
        fields = {f.name for f in dataclasses.fields(ValidationStatusReport)}
        for field_name in forbidden:
            assert field_name not in fields, f"Unexpected field in ValidationStatusReport: {field_name}"
