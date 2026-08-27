"""
Contract Tests: Schema 5 — Temporal Evidence
G1.8: PredictionWindow ≠ EvaluationToleranceWindow
TemporalSignal does NOT contain convergence
"""
from __future__ import annotations

import pytest
from tongshu.spec.temporal_evidence import (
    TemporalSignal,
    TemporalConvergence,
    PredictionWindow,
    EvaluationToleranceWindow,
)


# ─── TemporalSignal (no convergence) ────────────────────────────────────────


def test_temporal_signal_basic():
    ts = TemporalSignal(
        signal_id="sig-001",
        engine="Bazi",
        year=2026,
        granularity="YEARLY",
    )
    d = ts.to_dict()
    assert d["signal_id"] == "sig-001"
    assert d["engine"] == "Bazi"
    assert d["year"] == 2026
    assert "convergence_score" not in d
    assert "overlap_ratio" not in d


def test_temporal_signal_no_convergence_field():
    """TemporalSignal must NOT have convergence fields."""
    ts = TemporalSignal(signal_id="s1", engine="Heluo", year=2026)
    assert not hasattr(ts, "convergence_score")
    assert not hasattr(ts, "overlap_ratio")
    assert not hasattr(ts, "agreeing_engines")


def test_temporal_signal_with_month():
    ts = TemporalSignal(
        signal_id="s2", engine="Bazi", year=2026, month=6, granularity="MONTHLY",
    )
    assert ts.month == 6
    assert ts.granularity == "MONTHLY"


# ─── TemporalConvergence (separate from TemporalSignal) ──────────────────────


def test_temporal_convergence_basic():
    tc = TemporalConvergence(
        convergence_id="tc-001",
        target_year=2026,
        signal_ids_by_engine={"Bazi": ["sig-001"], "Heluo": ["sig-002"]},
        overlap_ratio=0.8,
        convergence_score=0.75,
        total_engines=2,
        agreeing_engines=2,
    )
    d = tc.to_dict()
    assert d["convergence_id"] == "tc-001"
    assert d["overlap_ratio"] == 0.8
    assert d["agreeing_engines"] == 2


# ─── PredictionWindow vs EvaluationToleranceWindow (G1.8) ───────────────────


def test_prediction_window_type():
    pw = PredictionWindow(start_year=2026, end_year=2026)
    assert isinstance(pw, PredictionWindow)
    assert not isinstance(pw, EvaluationToleranceWindow)


def test_evaluation_tolerance_window_type():
    etw = EvaluationToleranceWindow(severity_class="LOW", tolerance_days=365)
    assert isinstance(etw, EvaluationToleranceWindow)
    assert not isinstance(etw, PredictionWindow)


def test_window_types_are_different():
    """G1.8: These must be two distinct types, not interchangeable."""
    pw = PredictionWindow(start_year=2026, end_year=2027)
    etw = EvaluationToleranceWindow(severity_class="HIGH", tolerance_days=90)
    assert type(pw) is not type(etw)
    assert type(pw).__name__ == "PredictionWindow"
    assert type(etw).__name__ == "EvaluationToleranceWindow"


def test_prediction_window_fields():
    pw = PredictionWindow(start_year=2025, end_year=2025, start_month=1, end_month=12)
    assert pw.start_year == 2025
    assert pw.end_year == 2025
    assert pw.start_month == 1
    assert pw.end_month == 12


def test_evaluation_tolerance_window_severity_dependent():
    low = EvaluationToleranceWindow(severity_class="LOW", tolerance_days=365)
    crit = EvaluationToleranceWindow(severity_class="CRITICAL", tolerance_days=7)
    assert low.tolerance_days != crit.tolerance_days


def test_temporal_signal_and_convergence_are_distinct():
    ts = TemporalSignal(signal_id="s1", engine="Bazi", year=2026)
    tc = TemporalConvergence(convergence_id="tc1", target_year=2026)
    assert type(ts) is not type(tc)
