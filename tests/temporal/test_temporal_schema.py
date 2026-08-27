"""
Phase 4 Contract Tests — Temporal Schema
"""
from __future__ import annotations

import pytest

from tongshu.temporal.schema import (
    PredictionWindow,
    EvaluationToleranceWindow,
    TemporalGranularity,
    TemporalSignal,
    TemporalEvidence,
    TemporalConvergence,
)


class TestPredictionWindow:
    """Test PredictionWindow schema."""

    def test_valid_yearly_window(self):
        w = PredictionWindow(start_year=2026, end_year=2027)
        assert w.start_year == 2026
        assert w.end_year == 2027
        assert w.granularity == TemporalGranularity.YEARLY

    def test_valid_monthly_window(self):
        w = PredictionWindow(
            start_year=2026, end_year=2026,
            start_month=3, end_month=6,
            granularity=TemporalGranularity.MONTHLY,
        )
        assert w.start_month == 3
        assert w.end_month == 6

    def test_end_before_start_rejected(self):
        w = PredictionWindow(start_year=2027, end_year=2026)
        errors = w.validate()
        assert len(errors) > 0

    def test_month_end_before_month_start_rejected(self):
        w = PredictionWindow(
            start_year=2026, end_year=2026,
            start_month=6, end_month=3,
        )
        errors = w.validate()
        assert any("month" in e for e in errors)

    def test_to_dict_roundtrip(self):
        w = PredictionWindow(start_year=2026, end_year=2027, granularity=TemporalGranularity.YEARLY)
        d = w.to_dict()
        assert d["start_year"] == 2026
        assert d["end_year"] == 2027
        assert d["granularity"] == "YEARLY"


class TestEvaluationToleranceWindow:
    """Test EvaluationToleranceWindow schema — strict separation from PredictionWindow."""

    def test_from_severity_valid(self):
        w = EvaluationToleranceWindow.from_severity("HIGH", 30, "2026-06-15")
        assert w.severity_class == "HIGH"
        assert w.tolerance_days == 30

    def test_invalid_severity_raises(self):
        with pytest.raises(ValueError):
            EvaluationToleranceWindow.from_severity("UNKNOWN", 30)

    def test_negative_tolerance_rejected(self):
        w = EvaluationToleranceWindow(severity_class="LOW", tolerance_days=-1)
        errors = w.validate()
        assert any("tolerance_days" in e for e in errors)

    def test_is_not_prediction_window(self):
        """G4.2: Types must be completely separate."""
        w1 = PredictionWindow(start_year=2026, end_year=2027)
        w2 = EvaluationToleranceWindow(severity_class="LOW", tolerance_days=365)
        assert type(w1) is not type(w2)
        assert not isinstance(w1, EvaluationToleranceWindow)
        assert not isinstance(w2, PredictionWindow)


class TestTemporalSignal:
    """Test TemporalSignal schema."""

    def test_valid_signal(self):
        pw = PredictionWindow(start_year=2026, end_year=2027)
        sig = TemporalSignal(
            signal_id="S001",
            engine="Bazi",
            prediction_window=pw,
            direction="POSITIVE",
            strength=0.75,
        )
        assert sig.signal_id == "S001"
        assert sig.engine == "Bazi"

    def test_unknown_direction_allowed(self):
        pw = PredictionWindow(start_year=2026, end_year=2027)
        sig = TemporalSignal(
            signal_id="S001",
            engine="Knowledge",
            prediction_window=pw,
            direction="UNKNOWN",
            strength=0.3,
        )
        errors = sig.validate()
        assert errors == []  # UNKNOWN is valid direction

    def test_strength_out_of_range_rejected(self):
        pw = PredictionWindow(start_year=2026, end_year=2027)
        sig = TemporalSignal(
            signal_id="S_BAD",
            engine="Bazi",
            prediction_window=pw,
            direction="POSITIVE",
            strength=1.5,
        )
        errors = sig.validate()
        assert any("strength" in e for e in errors)

    def test_invalid_direction_rejected(self):
        pw = PredictionWindow(start_year=2026, end_year=2027)
        sig = TemporalSignal(
            signal_id="S_BAD",
            engine="Bazi",
            prediction_window=pw,
            direction="FORTUNE",
            strength=0.5,
        )
        errors = sig.validate()
        assert any("direction" in e for e in errors)

    def test_immutability(self):
        """TemporalSignal must be immutable."""
        pw = PredictionWindow(start_year=2026, end_year=2027)
        sig = TemporalSignal(
            signal_id="S001",
            engine="Bazi",
            prediction_window=pw,
            direction="POSITIVE",
            strength=0.7,
        )
        with pytest.raises(Exception):
            sig.signal_id = "CHANGED"


class TestTemporalConvergence:
    """Test TemporalConvergence schema."""

    def test_valid_convergence(self):
        tc = TemporalConvergence(
            convergence_id="TC001",
            target_year=2026,
            overlap_ratio=0.75,
            convergence_score=0.5,
            temporal_agreement="STRONG",
            total_engines=3,
            agreeing_engines=2,
        )
        errors = tc.validate()
        assert errors == []

    def test_overlap_ratio_out_of_range_rejected(self):
        tc = TemporalConvergence(
            convergence_id="TC_BAD",
            target_year=2026,
            overlap_ratio=1.5,
        )
        errors = tc.validate()
        assert any("overlap_ratio" in e for e in errors)

    def test_convergence_score_out_of_range_rejected(self):
        tc = TemporalConvergence(
            convergence_id="TC_BAD",
            target_year=2026,
            convergence_score=-0.1,
        )
        errors = tc.validate()
        assert any("convergence_score" in e for e in errors)

    def test_invalid_agreement_rejected(self):
        tc = TemporalConvergence(
            convergence_id="TC_BAD",
            target_year=2026,
            temporal_agreement="GOD_MODE",
        )
        errors = tc.validate()
        assert any("temporal_agreement" in e for e in errors)

    def test_no_fortune_score_field(self):
        """G4.11: Must NOT have fortune score field."""
        tc = TemporalConvergence(
            convergence_id="TC001",
            target_year=2026,
        )
        d = tc.to_dict()
        assert "fortune_score" not in d
        assert "luck_score" not in d
        assert "auspiciousness" not in d
        assert "final_score" not in d
