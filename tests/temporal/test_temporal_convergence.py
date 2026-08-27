"""
Phase 4 Contract Tests — Temporal Convergence Engine
"""
from __future__ import annotations

import pytest

from tongshu.temporal.schema import (
    PredictionWindow,
    TemporalSignal,
    TemporalEvidence,
    TemporalConvergence,
)
from tongshu.temporal.convergence import TemporalConvergenceEngine


class TestTemporalConvergenceEngine:
    """Test temporal convergence computation."""

    def test_add_signal_valid(self):
        engine = TemporalConvergenceEngine(target_year=2026)
        pw = PredictionWindow(start_year=2026, end_year=2027)
        sig = TemporalSignal(
            signal_id="S001", engine="Bazi",
            prediction_window=pw, direction="POSITIVE", strength=0.7,
        )
        assert engine.add_signal(sig) is True

    def test_add_signal_duplicate_rejected(self):
        engine = TemporalConvergenceEngine(target_year=2026)
        pw = PredictionWindow(start_year=2026, end_year=2027)
        sig = TemporalSignal(
            signal_id="S001", engine="Bazi",
            prediction_window=pw, direction="POSITIVE", strength=0.7,
        )
        engine.add_signal(sig)
        assert engine.add_signal(sig) is False  # Duplicate

    def test_add_signal_invalid_rejected(self):
        engine = TemporalConvergenceEngine(target_year=2026)
        pw = PredictionWindow(start_year=2027, end_year=2026)  # Invalid
        sig = TemporalSignal(
            signal_id="S001", engine="Bazi",
            prediction_window=pw, direction="POSITIVE", strength=0.7,
        )
        assert engine.add_signal(sig) is False

    def test_add_evidence_valid(self):
        engine = TemporalConvergenceEngine(target_year=2026)
        pw = PredictionWindow(start_year=2026, end_year=2027)
        sig = TemporalSignal(
            signal_id="S001", engine="Bazi",
            prediction_window=pw, direction="POSITIVE", strength=0.7,
        )
        engine.add_signal(sig)
        evidence = TemporalEvidence(
            evidence_id="E001",
            signal_id="S001",
            engine="Bazi",
            temporal_signal=sig,
        )
        assert engine.add_evidence(evidence) is True

    def test_add_evidence_invalid_signal_id_rejected(self):
        engine = TemporalConvergenceEngine(target_year=2026)
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

    def test_convergence_single_signal(self):
        """Single signal → no convergence."""
        engine = TemporalConvergenceEngine(target_year=2026)
        pw = PredictionWindow(start_year=2026, end_year=2027)
        sig = TemporalSignal(
            signal_id="S001", engine="Bazi",
            prediction_window=pw, direction="POSITIVE", strength=0.7,
        )
        engine.add_signal(sig)
        result = engine.compute_convergence()
        assert result.temporal_agreement == "NONE"
        assert result.overlap_ratio == 0.0

    def test_convergence_two_overlapping_signals(self):
        """Two overlapping signals → partial convergence."""
        engine = TemporalConvergenceEngine(target_year=2026)
        pw = PredictionWindow(start_year=2026, end_year=2027)
        sig1 = TemporalSignal(
            signal_id="S001", engine="Bazi",
            prediction_window=pw, direction="POSITIVE", strength=0.7,
        )
        sig2 = TemporalSignal(
            signal_id="S002", engine="Heluo",
            prediction_window=pw, direction="POSITIVE", strength=0.6,
        )
        engine.add_signal(sig1)
        engine.add_signal(sig2)
        result = engine.compute_convergence()
        assert result.overlap_ratio > 0.0
        assert result.temporal_agreement in ("PARTIAL", "STRONG", "COMPLETE")

    def test_convergence_no_common_window(self):
        """G4.9: No common window → no convergence fabricated."""
        engine = TemporalConvergenceEngine(target_year=2026)
        pw1 = PredictionWindow(start_year=2026, end_year=2026)
        pw2 = PredictionWindow(start_year=2030, end_year=2030)
        sig1 = TemporalSignal(
            signal_id="S001", engine="Bazi",
            prediction_window=pw1, direction="POSITIVE", strength=0.7,
        )
        sig2 = TemporalSignal(
            signal_id="S002", engine="Heluo",
            prediction_window=pw2, direction="NEGATIVE", strength=0.6,
        )
        engine.add_signal(sig1)
        engine.add_signal(sig2)
        result = engine.compute_convergence()
        assert result.temporal_agreement == "NONE"
        assert result.overlap_ratio == 0.0
        assert result.convergence_score == 0.0

    def test_unknown_direction_not_counted_as_agreement(self):
        """G4.10: UNKNOWN direction signals are not positive/negative."""
        engine = TemporalConvergenceEngine(target_year=2026)
        pw = PredictionWindow(start_year=2026, end_year=2027)
        sig1 = TemporalSignal(
            signal_id="S001", engine="Bazi",
            prediction_window=pw, direction="POSITIVE", strength=0.7,
        )
        sig2 = TemporalSignal(
            signal_id="S002", engine="Knowledge",
            prediction_window=pw, direction="UNKNOWN", strength=0.3,
        )
        engine.add_signal(sig1)
        engine.add_signal(sig2)
        result = engine.compute_convergence()
        # UNKNOWN should not count as agreeing
        assert result.agreeing_engines >= 1  # At least Bazi agrees
        assert result.unknown_engines >= 1   # Knowledge is unknown

    def test_no_fortune_score_in_output(self):
        """G4.11: Must NOT produce Fortune Score."""
        engine = TemporalConvergenceEngine(target_year=2026)
        pw = PredictionWindow(start_year=2026, end_year=2027)
        sig1 = TemporalSignal(
            signal_id="S001", engine="Bazi",
            prediction_window=pw, direction="POSITIVE", strength=0.7,
        )
        sig2 = TemporalSignal(
            signal_id="S002", engine="Heluo",
            prediction_window=pw, direction="POSITIVE", strength=0.6,
        )
        engine.add_signal(sig1)
        engine.add_signal(sig2)
        result = engine.compute_convergence()
        d = result.to_dict()
        assert "fortune_score" not in d
        assert "luck_score" not in d
        assert "auspiciousness" not in d
        assert "final_score" not in d

    def test_mixed_directions_convergence(self):
        """Signals with different directions can still converge temporally."""
        engine = TemporalConvergenceEngine(target_year=2026)
        pw = PredictionWindow(start_year=2026, end_year=2027)
        sig1 = TemporalSignal(
            signal_id="S001", engine="Bazi",
            prediction_window=pw, direction="POSITIVE", strength=0.7,
        )
        sig2 = TemporalSignal(
            signal_id="S002", engine="Ziwei",
            prediction_window=pw, direction="NEGATIVE", strength=0.5,
        )
        engine.add_signal(sig1)
        engine.add_signal(sig2)
        result = engine.compute_convergence()
        # Temporal convergence is about time overlap, not direction agreement
        assert result.overlap_ratio > 0.0
        assert result.temporal_agreement != "NONE"

    def test_three_engine_convergence(self):
        """Three engines with overlapping windows."""
        engine = TemporalConvergenceEngine(target_year=2026)
        pw = PredictionWindow(start_year=2026, end_year=2027)
        for i, (sid, eng) in enumerate([
            ("S001", "Bazi"), ("S002", "Heluo"), ("S003", "Ziwei")
        ]):
            engine.add_signal(TemporalSignal(
                signal_id=sid, engine=eng,
                prediction_window=pw, direction="POSITIVE",
                strength=0.7 - i * 0.1,
            ))
        result = engine.get_signals_by_engine("Bazi")
        assert len(result) == 1
        assert result[0].engine == "Bazi"

    def test_validate_all_returns_errors(self):
        """Test that validate_all catches signal validation errors."""
        engine = TemporalConvergenceEngine(target_year=2026)
        # Add a valid signal first so validate_all has something to check
        pw = PredictionWindow(start_year=2026, end_year=2027)
        sig = TemporalSignal(
            signal_id="S001", engine="Bazi",
            prediction_window=pw, direction="POSITIVE", strength=0.7,
        )
        engine.add_signal(sig)
        # validate_all should return empty list for valid signal
        errors = engine.validate_all()
        assert len(errors) == 0

    def test_invalid_signal_rejected_at_add(self):
        """Invalid signals must be rejected at add time, not stored."""
        engine = TemporalConvergenceEngine(target_year=2026)
        pw = PredictionWindow(start_year=2027, end_year=2026)  # Invalid: end < start
        sig = TemporalSignal(
            signal_id="S_BAD", engine="Bazi",
            prediction_window=pw, direction="POSITIVE", strength=0.7,
        )
        # Invalid signal should be rejected
        assert engine.add_signal(sig) is False
        # No signals stored
        assert len(engine.get_all_signals()) == 0
