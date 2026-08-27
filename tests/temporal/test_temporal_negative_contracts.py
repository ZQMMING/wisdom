"""
Phase 4 Negative Contract Tests

These tests ensure the contract CANNOT be bypassed.
Any successful bypass attempt is a bug.
"""
from __future__ import annotations

import pytest

from tongshu.temporal.schema import (
    PredictionWindow,
    EvaluationToleranceWindow,
    TemporalSignal,
    TemporalConvergence,
)
from tongshu.temporal.convergence import TemporalConvergenceEngine


class TestNegativeContracts:
    """
    Negative contract tests — ensure contract CANNOT be bypassed.
    """

    def test_cannot_fabricate_convergence_without_overlap(self):
        """G4.9: No common window = no convergence."""
        engine = TemporalConvergenceEngine(target_year=2026)
        pw1 = PredictionWindow(start_year=2026, end_year=2026)
        pw2 = PredictionWindow(start_year=2030, end_year=2030)
        engine.add_signal(TemporalSignal(
            signal_id="S1", engine="Bazi",
            prediction_window=pw1, direction="POSITIVE", strength=0.7,
        ))
        engine.add_signal(TemporalSignal(
            signal_id="S2", engine="Heluo",
            prediction_window=pw2, direction="POSITIVE", strength=0.6,
        ))
        result = engine.compute_convergence()
        assert result.overlap_ratio == 0.0
        assert result.convergence_score == 0.0
        assert result.temporal_agreement == "NONE"

    def test_unknown_cannot_be_treated_as_positive(self):
        """G4.10: UNKNOWN direction must not inflate convergence."""
        engine = TemporalConvergenceEngine(target_year=2026)
        pw = PredictionWindow(start_year=2026, end_year=2027)
        # One POSITIVE, one UNKNOWN
        engine.add_signal(TemporalSignal(
            signal_id="S1", engine="Bazi",
            prediction_window=pw, direction="POSITIVE", strength=0.7,
        ))
        engine.add_signal(TemporalSignal(
            signal_id="S2", engine="Knowledge",
            prediction_window=pw, direction="UNKNOWN", strength=0.3,
        ))
        result = engine.compute_convergence()
        # Agreement should be reduced by UNKNOWN
        assert result.agreeing_engines < result.total_engines
        assert result.unknown_engines >= 1

    def test_cannot_add_duplicate_signal(self):
        engine = TemporalConvergenceEngine(target_year=2026)
        pw = PredictionWindow(start_year=2026, end_year=2027)
        sig = TemporalSignal(
            signal_id="S_DUP", engine="Bazi",
            prediction_window=pw, direction="POSITIVE", strength=0.7,
        )
        assert engine.add_signal(sig) is True
        assert engine.add_signal(sig) is False  # Duplicate rejected

    def test_prediction_window_cannot_be_mutated(self):
        """PredictionWindow is frozen — cannot be modified after creation."""
        pw = PredictionWindow(start_year=2026, end_year=2027)
        with pytest.raises((TypeError, Exception)):  # frozen dataclass raises either
            pw.start_year = 2028

    def test_evaluation_window_is_different_type(self):
        """G4.2: PredictionWindow and EvaluationToleranceWindow are different types."""
        pw = PredictionWindow(start_year=2026, end_year=2027)
        ew = EvaluationToleranceWindow(severity_class="LOW", tolerance_days=365)
        assert type(pw) is not type(ew)

    def test_convergence_cannot_have_invalid_ratio(self):
        """TemporalConvergence must validate overlap_ratio."""
        tc = TemporalConvergence(
            convergence_id="TC_BAD",
            target_year=2026,
            overlap_ratio=1.5,  # Out of range
        )
        errors = tc.validate()
        assert any("overlap_ratio" in e for e in errors)

    def test_convergence_cannot_have_fortune_score(self):
        """G4.11: TemporalConvergence must NOT have fortune score fields."""
        tc = TemporalConvergence(
            convergence_id="TC001",
            target_year=2026,
            overlap_ratio=0.5,
            convergence_score=0.3,
        )
        d = tc.to_dict()
        forbidden = {"fortune_score", "luck_score", "auspiciousness", "final_score"}
        for key in forbidden:
            assert key not in d, f"Forbidden field '{key}' found in TemporalConvergence"

    def test_temporal_signal_requires_valid_strength(self):
        pw = PredictionWindow(start_year=2026, end_year=2027)
        sig = TemporalSignal(
            signal_id="S_BAD", engine="Bazi",
            prediction_window=pw, direction="POSITIVE", strength=-0.1,
        )
        errors = sig.validate()
        assert any("strength" in e for e in errors)

    def test_temporal_signal_requires_valid_direction(self):
        pw = PredictionWindow(start_year=2026, end_year=2027)
        sig = TemporalSignal(
            signal_id="S_BAD", engine="Bazi",
            prediction_window=pw, direction="FORTUNE", strength=0.5,
        )
        errors = sig.validate()
        assert any("direction" in e for e in errors)

    def test_invalid_evidence_signal_id_rejected(self):
        engine = TemporalConvergenceEngine(target_year=2026)
        from tongshu.temporal.schema import TemporalEvidence
        pw = PredictionWindow(start_year=2026, end_year=2027)
        evidence = TemporalEvidence(
            evidence_id="E_BAD",
            signal_id="S_NONEXISTENT",
            engine="Bazi",
            temporal_signal=TemporalSignal(
                signal_id="S_NONEXISTENT", engine="Bazi",
                prediction_window=pw, direction="POSITIVE", strength=0.7,
            ),
        )
        assert engine.add_evidence(evidence) is False
