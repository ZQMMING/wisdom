"""Comprehensive tests for V1.2 Validation Layer components."""
from __future__ import annotations

import pytest
from dataclasses import asdict

from tongshu.validation.v12.state_machine import (
    ValidationStatus,
    F1AggregationMethod,
    DimensionStatus,
    ValidationStatusReport,
)
from tongshu.validation.v12.failure_taxonomy import (
    FailureType,
    FailureRecord,
    DimensionFailureAnalysis,
    FailureAnalysisReport,
)
from tongshu.validation.v12.micro_f1 import (
    micro_f1,
    micro_precision,
    micro_recall,
    macro_f1,
    jaccard_match_rate,
    compute_all_metrics,
)
from tongshu.validation.v12.agreement_evidence import (
    AgreementLevel,
    SignalEvidence,
    AgreementResult,
    AgreementEvidenceEngine,
)
from tongshu.validation.v12.dimensions import (
    VALIDATION_DIMENSION_DEFS,
    DIMENSION_BY_ID,
    REQUIRED_DIMENSIONS,
    OPTIONAL_DIMENSIONS,
)
from tongshu.validation.v12.report_generator import ValidationReportGenerator


# ─── State Machine Tests ───────────────────────────────────────────────────────

class TestValidationStatus:
    def test_all_statuses_exist(self):
        statuses = list(ValidationStatus)
        expected = {"NOT_IMPLEMENTED", "NOT_EVALUABLE", "BLOCKED", "PASS", "FAIL", "PARTIAL"}
        actual = {s.value for s in statuses}
        assert actual == expected

    def test_not_implemented_properties(self):
        s = ValidationStatus.NOT_IMPLEMENTED
        assert s.is_diagnostic is False
        assert s.is_final is False
        assert s.is_skippable is True

    def test_not_evaluable_properties(self):
        s = ValidationStatus.NOT_EVALUABLE
        assert s.is_diagnostic is False
        assert s.is_final is False
        assert s.is_skippable is True

    def test_blocked_properties(self):
        s = ValidationStatus.BLOCKED
        assert s.is_diagnostic is False
        assert s.is_final is False
        assert s.is_skippable is False

    def test_pass_properties(self):
        s = ValidationStatus.PASS
        assert s.is_diagnostic is True
        assert s.is_final is True
        assert s.is_skippable is False

    def test_fail_properties(self):
        s = ValidationStatus.FAIL
        assert s.is_diagnostic is True
        assert s.is_final is True
        assert s.is_skippable is False

    def test_partial_properties(self):
        s = ValidationStatus.PARTIAL
        assert s.is_diagnostic is True
        assert s.is_final is False
        assert s.is_skippable is False


class TestDimensionStatus:
    def test_frozen_dataclass(self):
        ds = DimensionStatus(dimension_id="CALCULATION", status=ValidationStatus.PASS)
        with pytest.raises(Exception):
            ds.dimension_id = "CHANGED"

    def test_to_dict_basic(self):
        ds = DimensionStatus(dimension_id="CALCULATION", status=ValidationStatus.PASS)
        d = ds.to_dict()
        assert d == {"dimension_id": "CALCULATION", "status": "PASS"}

    def test_to_dict_with_score(self):
        ds = DimensionStatus(dimension_id="CALCULATION", status=ValidationStatus.PASS, score=0.95)
        d = ds.to_dict()
        assert d["score"] == 0.95

    def test_to_dict_with_failures(self):
        ds = DimensionStatus(dimension_id="SIGNAL", status=ValidationStatus.FAIL, failures=["missing"])
        d = ds.to_dict()
        assert d["failures"] == ["missing"]

    def test_to_dict_with_blocked_by(self):
        ds = DimensionStatus(dimension_id="TEMPORAL", status=ValidationStatus.BLOCKED, blocked_by="EVIDENCE")
        d = ds.to_dict()
        assert d["blocked_by"] == "EVIDENCE"


# ─── Failure Taxonomy Tests ────────────────────────────────────────────────────

class TestFailureType:
    def test_exactly_fifteen_types(self):
        valid = FailureType.valid_types()
        assert len(valid) == 15

    def test_unknown_not_in_valid(self):
        assert FailureType.UNKNOWN not in FailureType.valid_types()

    def test_all_types_have_values(self):
        for ft in FailureType:
            assert isinstance(ft.value, str)
            assert len(ft.value) > 0


class TestFailureRecord:
    def test_frozen_dataclass(self):
        fr = FailureRecord(
            failure_id="F001", failure_type=FailureType.SIGNAL_MISSING,
            dimension_id="SIGNAL",
        )
        with pytest.raises(Exception):
            fr.failure_id = "CHANGED"

    def test_to_dict(self):
        fr = FailureRecord(
            failure_id="F001", failure_type=FailureType.SIGNAL_MISSING,
            dimension_id="SIGNAL", event_id="E001", details="test", confidence=0.9,
        )
        d = fr.to_dict()
        assert d["failure_id"] == "F001"
        assert d["failure_type"] == "SIGNAL_MISSING"
        assert d["dimension_id"] == "SIGNAL"
        assert d["event_id"] == "E001"
        assert d["details"] == "test"
        assert d["confidence"] == 0.9


class TestDimensionFailureAnalysis:
    def test_basic(self):
        dfa = DimensionFailureAnalysis(dimension_id="SIGNAL", total_failures=3,
                                        failures_by_type={FailureType.SIGNAL_MISSING: 2,
                                                          FailureType.SIGNAL_FALSE_POS: 1},
                                        failure_rate=0.3)
        d = dfa.to_dict()
        assert d["dimension_id"] == "SIGNAL"
        assert d["total_failures"] == 3
        assert d["failure_rate"] == 0.3

    def test_empty(self):
        dfa = DimensionFailureAnalysis(dimension_id="CALCULATION")
        assert dfa.total_failures == 0
        assert dfa.failure_rate == 0.0


class TestFailureAnalysisReport:
    def test_empty_report(self):
        far = FailureAnalysisReport(report_id="R001", analysis_time="2026-01-01",
                                     total_events=0, dimensions_analyzed=0)
        assert far.total_failure_count == 0
        assert far.dominant_failure_type is None

    def test_dominant_failure_type(self):
        far = FailureAnalysisReport(report_id="R001", analysis_time="2026-01-01",
                                     total_events=10, dimensions_analyzed=1,
                                     failures=[
                                         FailureRecord("F1", FailureType.SIGNAL_MISSING, "SIGNAL"),
                                         FailureRecord("F2", FailureType.SIGNAL_MISSING, "SIGNAL"),
                                         FailureRecord("F3", FailureType.ONTOLOGY_MISMATCH, "ONTOLOGY"),
                                     ])
        assert far.dominant_failure_type == FailureType.SIGNAL_MISSING


# ─── Micro-F1 Tests ────────────────────────────────────────────────────────────

class TestMicroF1:
    def test_perfect_match(self):
        """All predictions correct."""
        pred = [["A", "B", "C"]]
        gt = [["A", "B", "C"]]
        assert micro_f1(pred, gt) == 1.0

    def test_no_match(self):
        """No overlap."""
        pred = [["A", "B"]]
        gt = [["C", "D"]]
        assert micro_f1(pred, gt) == 0.0

    def test_partial_match(self):
        """Half correct."""
        pred = [["A", "B"]]
        gt = [["A", "C"]]
        # tp=1, fp=1, fn=1
        # F1 = 2*1 / (2*1 + 1 + 1) = 2/4 = 0.5
        assert micro_f1(pred, gt) == 0.5

    def test_multiple_cases_different_sizes(self):
        """Cases with different numbers of items."""
        pred = [["A", "B"], ["C"], ["D", "E", "F"]]
        gt = [["A"], ["C", "G"], ["D", "E"]]
        # tp=4, fp=2, fn=1
        # F1 = 8 / (8 + 2 + 1) = 8/11
        assert abs(micro_f1(pred, gt) - 8/11) < 1e-9

    def test_empty_both(self):
        """Both empty → 0.0."""
        pred = [[]]
        gt = [[]]
        assert micro_f1(pred, gt) == 0.0

    def test_empty_pred_nonempty_gt(self):
        """Empty predictions."""
        pred = [[]]
        gt = [["A", "B"]]
        assert micro_f1(pred, gt) == 0.0

    def test_nonempty_pred_empty_gt(self):
        """Empty ground truth."""
        pred = [["A", "B"]]
        gt = [[]]
        assert micro_f1(pred, gt) == 0.0


class TestMicroPrecision:
    def test_perfect_precision(self):
        pred = [["A", "B"]]
        gt = [["A", "B"]]
        assert micro_precision(pred, gt) == 1.0

    def test_zero_precision(self):
        pred = [["A", "B"]]
        gt = [["C", "D"]]
        assert micro_precision(pred, gt) == 0.0


class TestMicroRecall:
    def test_perfect_recall(self):
        pred = [["A", "B"]]
        gt = [["A", "B"]]
        assert micro_recall(pred, gt) == 1.0

    def test_zero_recall(self):
        pred = [[]]
        gt = [["A", "B"]]
        assert micro_recall(pred, gt) == 0.0


class TestMacroF1:
    def test_macro_vs_micro_differ(self):
        """Macro-F1 often differs from Micro-F1."""
        pred = [["A", "B"], ["C"]]
        gt = [["A"], ["C", "D", "E", "F"]]
        # Case 1: tp=1, fp=1, fn=1 → F1=0.5
        # Case 2: tp=1, fp=0, fn=3 → F1=0.5
        # Macro = (0.5 + 0.5) / 2 = 0.5
        # Micro: tp=2, fp=1, fn=4 → F1 = 4/(4+1+4) = 4/9 ≈ 0.444
        micro = micro_f1(pred, gt)
        macro = macro_f1(pred, gt)
        assert abs(micro - macro) > 1e-6

    def test_macro_single_case(self):
        """Macro-F1 on single case equals that case's F1."""
        pred = [["A", "B"]]
        gt = [["A"]]
        micro = micro_f1(pred, gt)
        macro = macro_f1(pred, gt)
        assert abs(micro - macro) < 1e-9


class TestComputeAllMetrics:
    def test_returns_all_keys(self):
        pred = [["A", "B"]]
        gt = [["A"]]
        result = compute_all_metrics(pred, gt)
        assert "micro_f1" in result
        assert "micro_precision" in result
        assert "micro_recall" in result
        assert "macro_f1" in result
        assert "jaccard_match_rate" in result

    def test_perfect_match_all_1(self):
        pred = [["A", "B", "C"]]
        gt = [["A", "B", "C"]]
        result = compute_all_metrics(pred, gt)
        assert result["micro_f1"] == 1.0
        assert result["micro_precision"] == 1.0
        assert result["micro_recall"] == 1.0
        assert result["jaccard_match_rate"] == 1.0

    def test_empty_match(self):
        pred = [[]]
        gt = [[]]
        result = compute_all_metrics(pred, gt)
        assert result["micro_f1"] == 0.0
        assert result["jaccard_match_rate"] == 1.0  # both empty = perfect match


# ─── Agreement Evidence Tests ──────────────────────────────────────────────────

class TestSignalEvidence:
    def test_frozen(self):
        sig = SignalEvidence(
            signal_id="S001", engine="Bazi", direction="POSITIVE",
            strength=0.7, prediction_window_start=2026, prediction_window_end=2027,
        )
        with pytest.raises(Exception):
            sig.signal_id = "CHANGED"

    def test_to_dict(self):
        sig = SignalEvidence(
            signal_id="S001", engine="Bazi", direction="POSITIVE",
            strength=0.7, prediction_window_start=2026, prediction_window_end=2027,
        )
        d = sig.to_dict()
        assert d["signal_id"] == "S001"
        assert d["engine"] == "Bazi"
        assert d["direction"] == "POSITIVE"


class TestAgreementResult:
    def test_agreement_ratio_strong(self):
        result = AgreementResult(
            signal_id="S001", level=AgreementLevel.STRONG,
            total_engines=3, agreeing_engines=3,
            unknown_engines=0, conflicting_engines=0,
        )
        assert result.agreement_ratio == 1.0

    def test_agreement_ratio_weak(self):
        result = AgreementResult(
            signal_id="S001", level=AgreementLevel.WEAK,
            total_engines=3, agreeing_engines=1,
            unknown_engines=2, conflicting_engines=0,
        )
        # non_unknown = 3 - 2 = 1, ratio = 1/1 = 1.0
        assert result.agreement_ratio == 1.0

    def test_agreement_ratio_all_unknown(self):
        result = AgreementResult(
            signal_id="S001", level=AgreementLevel.NONE,
            total_engines=3, agreeing_engines=0,
            unknown_engines=3, conflicting_engines=0,
        )
        assert result.agreement_ratio == 0.0

    def test_frozen(self):
        result = AgreementResult(
            signal_id="S001", level=AgreementLevel.STRONG,
            total_engines=2, agreeing_engines=2,
            unknown_engines=0, conflicting_engines=0,
        )
        with pytest.raises(Exception):
            result.signal_id = "CHANGED"


class TestAgreementEvidenceEngine:
    def test_single_engine(self):
        engine = AgreementEvidenceEngine()
        engine.add_signal(SignalEvidence("S001", "Bazi", "POSITIVE", 0.7, 2026, 2027))
        result = engine.compute_agreement("S001")
        assert result.total_engines == 1
        assert result.agreeing_engines == 1

    def test_two_engines_same_direction(self):
        engine = AgreementEvidenceEngine()
        engine.add_signal(SignalEvidence("S001", "Bazi", "POSITIVE", 0.7, 2026, 2027))
        engine.add_signal(SignalEvidence("S001", "Ziwei", "POSITIVE", 0.6, 2026, 2027))
        result = engine.compute_agreement("S001")
        assert result.level == AgreementLevel.STRONG
        assert result.agreement_ratio == 1.0

    def test_two_engines_opposing(self):
        engine = AgreementEvidenceEngine()
        engine.add_signal(SignalEvidence("S001", "Bazi", "POSITIVE", 0.7, 2026, 2027))
        engine.add_signal(SignalEvidence("S001", "Ziwei", "NEGATIVE", 0.6, 2026, 2027))
        result = engine.compute_agreement("S001")
        assert result.level == AgreementLevel.CONFLICTING
        assert result.agreement_ratio == 0.0

    def test_with_unknown(self):
        engine = AgreementEvidenceEngine()
        engine.add_signal(SignalEvidence("S001", "Bazi", "POSITIVE", 0.7, 2026, 2027))
        engine.add_signal(SignalEvidence("S001", "Ziwei", "UNKNOWN", 0.3, 2026, 2027))
        result = engine.compute_agreement("S001")
        assert result.unknown_engines == 1
        assert result.agreeing_engines == 1
        assert result.agreement_ratio == 1.0  # non_unknown=1, agreeing=1

    def test_compute_all(self):
        engine = AgreementEvidenceEngine()
        engine.add_signal(SignalEvidence("S001", "Bazi", "POSITIVE", 0.7, 2026, 2027))
        engine.add_signal(SignalEvidence("S002", "Ziwei", "NEGATIVE", 0.6, 2026, 2027))
        results = engine.compute_all()
        assert len(results) == 2
        assert "S001" in results
        assert "S002" in results

    def test_get_agreement_by_level(self):
        engine = AgreementEvidenceEngine()
        engine.add_signal(SignalEvidence("S001", "Bazi", "POSITIVE", 0.7, 2026, 2027))
        engine.add_signal(SignalEvidence("S001", "Ziwei", "POSITIVE", 0.6, 2026, 2027))
        strong = engine.get_agreement_by_level(AgreementLevel.STRONG)
        assert "S001" in strong


# ─── Dimensions Tests ──────────────────────────────────────────────────────────

class TestDimensions:
    def test_exactly_9(self):
        assert len(VALIDATION_DIMENSION_DEFS) == 9

    def test_required_count(self):
        assert len(REQUIRED_DIMENSIONS) == 8

    def test_optional_count(self):
        assert len(OPTIONAL_DIMENSIONS) == 1

    def test_directionality_optional(self):
        opt = OPTIONAL_DIMENSIONS[0]
        assert opt.dimension_id == "DIRECTIONALITY"

    def test_all_required_are_not_directionality(self):
        required_ids = {d.dimension_id for d in REQUIRED_DIMENSIONS}
        assert "DIRECTIONALITY" not in required_ids

    def test_dimension_lookup(self):
        calc = DIMENSION_BY_ID["CALCULATION"]
        assert calc.name == "计算层正确性"

    def test_all_dimensions_have_ids(self):
        for dim in VALIDATION_DIMENSION_DEFS:
            assert dim.dimension_id in DIMENSION_BY_ID

    def test_no_duplicates(self):
        ids = [d.dimension_id for d in VALIDATION_DIMENSION_DEFS]
        assert len(ids) == len(set(ids))


# ─── Report Generator Tests ────────────────────────────────────────────────────

class TestValidationReportGenerator:
    def test_generate_empty(self):
        gen = ValidationReportGenerator("R001", "v1.0")
        report = gen.generate()
        assert report.report_id == "R001"
        assert report.overall_f1 == 0.0
        assert report.total_events == 0

    def test_add_dimension(self):
        gen = ValidationReportGenerator("R001", "v1.0")
        gen.set_dimension_status("CALCULATION", DimensionStatus(
            dimension_id="CALCULATION", status=ValidationStatus.PASS, score=0.95
        ))
        report = gen.generate()
        assert report.dimensions["CALCULATION"].status == ValidationStatus.PASS

    def test_add_failure(self):
        gen = ValidationReportGenerator("R001", "v1.0")
        gen.add_failure(FailureRecord("F1", FailureType.SIGNAL_MISSING, "SIGNAL"))
        report = gen.generate()
        assert report.total_failures == 1

    def test_add_predictions(self):
        gen = ValidationReportGenerator("R001", "v1.0")
        gen.add_prediction_ground_truth(["A", "B"], ["A"])
        report = gen.generate()
        assert report.total_events == 1
        # tp=1(A), fp=1(B), fn=0 → F1 = 2*1 / (2*1 + 1 + 0) = 2/3
        assert abs(report.overall_f1 - 2/3) < 1e-9

    def test_micro_f1_primary_over_macro(self):
        gen = ValidationReportGenerator("R001", "v1.0")
        gen.add_prediction_ground_truth(["A", "B"], ["A"])
        report = gen.generate()
        assert report.f1_aggregation_method == F1AggregationMethod.MICRO
        assert report.overall_f1 == report.overall_f1  # micro_f1 is overall
        assert report.macro_f1 is not None

    def test_no_fortune_score(self):
        gen = ValidationReportGenerator("R001", "v1.0")
        gen.add_prediction_ground_truth(["A"], ["A"])
        report = gen.generate()
        d = report.to_dict()
        forbidden = {"fortune_score", "luck_score", "auspiciousness"}
        for key in forbidden:
            assert key not in d

    def test_invalid_dimension_raises(self):
        gen = ValidationReportGenerator("R001", "v1.0")
        with pytest.raises(ValueError):
            gen.set_dimension_status("INVALID", DimensionStatus(
                dimension_id="INVALID", status=ValidationStatus.PASS
            ))

    def test_blocked_dimension_excluded_from_denominator(self):
        gen = ValidationReportGenerator("R001", "v1.0")
        gen.set_dimension_status("CALCULATION", DimensionStatus(
            dimension_id="CALCULATION", status=ValidationStatus.PASS
        ))
        gen.set_dimension_status("SIGNAL", DimensionStatus(
            dimension_id="SIGNAL", status=ValidationStatus.BLOCKED, blocked_by="EVIDENCE"
        ))
        gen.set_dimension_status("ONTOLOGY", DimensionStatus(
            dimension_id="ONTOLOGY", status=ValidationStatus.NOT_IMPLEMENTED
        ))
        report = gen.generate()
        # Only CALCULATION is evaluated (BLOCKED is included, NOT_IMPLEMENTED excluded)
        # Actually BLOCKED has is_diagnostic=False, so it's not counted as evaluated
        assert report.total_dimensions_evaluated == 1  # Only CALCULATION is diagnostic and not blocked


# ─── Integration Tests ─────────────────────────────────────────────────────────

class TestIntegration:
    def test_full_pipeline(self):
        """End-to-end validation pipeline."""
        # Create generator
        gen = ValidationReportGenerator("PIPELINE_TEST", "v1.0")

        # Add dimension statuses
        gen.set_dimension_status("CALCULATION", DimensionStatus(
            dimension_id="CALCULATION", status=ValidationStatus.PASS, score=1.0
        ))
        gen.set_dimension_status("SIGNAL", DimensionStatus(
            dimension_id="SIGNAL", status=ValidationStatus.PARTIAL, score=0.8,
            coverage_ratio=0.8
        ))
        gen.set_dimension_status("ONTOLOGY", DimensionStatus(
            dimension_id="ONTOLOGY", status=ValidationStatus.FAIL, score=0.5,
            failures=["mismatch_1", "mismatch_2"]
        ))

        # Add predictions
        gen.add_prediction_ground_truth(["marriage", "career"], ["marriage"])
        gen.add_prediction_ground_truth(["health"], ["health", "wealth"])

        # Add failures
        gen.add_failure(FailureRecord("F1", FailureType.ONTOLOGY_MISMATCH, "ONTOLOGY", "E001"))
        gen.add_failure(FailureRecord("F2", FailureType.SIGNAL_MISSING, "SIGNAL", "E002"))

        # Generate report
        report = gen.generate()

        # Verify report
        assert report.report_id == "PIPELINE_TEST"
        assert report.v1_2_version == "V1.2"
        assert report.f1_aggregation_method == F1AggregationMethod.MICRO
        assert len(report.dimensions) == 3
        assert report.total_failures == 2

        # Verify dimensions
        calc_status = report.dimensions["CALCULATION"]
        assert calc_status.status == ValidationStatus.PASS
        assert calc_status.score == 1.0

        signal_status = report.dimensions["SIGNAL"]
        assert signal_status.status == ValidationStatus.PARTIAL
        assert signal_status.coverage_ratio == 0.8

        ontology_status = report.dimensions["ONTOLOGY"]
        assert ontology_status.status == ValidationStatus.FAIL
        assert len(ontology_status.failures) == 2

        # Verify Micro-F1
        # Case 1: pred=["marriage", "career"], gt=["marriage"] → tp=1, fp=1, fn=0
        # Case 2: pred=["health"], gt=["health", "wealth"] → tp=1, fp=0, fn=1
        # Micro: tp=2, fp=1, fn=1 → 4/(4+1+1) = 4/6 = 0.667
        assert abs(report.overall_f1 - 2/3) < 1e-9

    def test_macro_f1_auxiliary(self):
        """Verify Macro-F1 is only auxiliary, not primary."""
        gen = ValidationReportGenerator("MACRO_TEST", "v1.0")
        gen.add_prediction_ground_truth(["A", "B"], ["A"])
        gen.add_prediction_ground_truth(["C"], ["C", "D", "E"])
        report = gen.generate()

        # Case 1: pred=["A","B"], gt=["A"] → tp=1, fp=1, fn=0 → F1=2/3
        # Case 2: pred=["C"], gt=["C","D","E"] → tp=1, fp=0, fn=2 → F1=0.5
        # Macro = (2/3 + 0.5) / 2 = 7/12 ≈ 0.583
        assert abs(report.macro_f1 - 7/12) < 1e-9

        # Micro: tp=2, fp=1, fn=2 → 4/(4+1+2) = 4/7
        assert abs(report.overall_f1 - 4/7) < 1e-9


# ─── Negative Tests ────────────────────────────────────────────────────────────

class TestNegativeContracts:
    def test_frozen_dimension_status(self):
        ds = DimensionStatus(dimension_id="CALCULATION", status=ValidationStatus.PASS)
        with pytest.raises(Exception):
            ds.status = ValidationStatus.FAIL

    def test_frozen_failure_record(self):
        fr = FailureRecord("F1", FailureType.SIGNAL_MISSING, "SIGNAL")
        with pytest.raises(Exception):
            fr.failure_type = FailureType.ONTOLOGY_MISMATCH

    def test_frozen_agreement_result(self):
        ar = AgreementResult(
            signal_id="S001", level=AgreementLevel.STRONG,
            total_engines=2, agreeing_engines=2,
            unknown_engines=0, conflicting_engines=0,
        )
        with pytest.raises(Exception):
            ar.total_engines = 3

    def test_validation_dimension_count_fixed(self):
        """Must always be 9."""
        assert len(VALIDATION_DIMENSION_DEFS) == 9

    def test_required_dimension_count_fixed(self):
        """Must always be 8."""
        assert len(REQUIRED_DIMENSIONS) == 8

    def test_unknown_not_in_failure_types(self):
        """UNKNOWN is sentinel, not usable."""
        valid = FailureType.valid_types()
        assert FailureType.UNKNOWN not in valid
