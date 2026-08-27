"""
Phase 4 Contract Tests — Temporal Alignment
"""
from __future__ import annotations

import pytest

from tongshu.temporal.schema import PredictionWindow, TemporalGranularity, TemporalSignal
from tongshu.temporal.alignment import TemporalAlignmentEngine


class TestTemporalAlignmentEngine:
    """Test temporal alignment between prediction windows."""

    def test_full_overlap_yearly(self):
        w1 = PredictionWindow(start_year=2026, end_year=2027)
        w2 = PredictionWindow(start_year=2026, end_year=2027)
        result = TemporalAlignmentEngine.compute_overlap(w1, w2)
        assert result.aligned is True
        assert result.overlap_ratio == 1.0

    def test_no_overlap_yearly(self):
        w1 = PredictionWindow(start_year=2026, end_year=2026)
        w2 = PredictionWindow(start_year=2028, end_year=2028)
        result = TemporalAlignmentEngine.compute_overlap(w1, w2)
        assert result.aligned is False
        assert result.overlap_ratio == 0.0

    def test_partial_overlap(self):
        w1 = PredictionWindow(start_year=2026, end_year=2028)
        w2 = PredictionWindow(start_year=2027, end_year=2029)
        result = TemporalAlignmentEngine.compute_overlap(w1, w2)
        assert result.aligned is True
        assert result.overlap_ratio > 0.0

    def test_one_year_overlap(self):
        """2026–2027 vs 2027–2028 should overlap at 2027."""
        w1 = PredictionWindow(start_year=2026, end_year=2027)
        w2 = PredictionWindow(start_year=2027, end_year=2028)
        result = TemporalAlignmentEngine.compute_overlap(w1, w2)
        assert result.aligned is True
        # Overlap is 1 year out of min(2, 2) = 2 years → 0.5
        assert result.overlap_ratio == 0.5

    def test_single_year_vs_multi_year(self):
        w1 = PredictionWindow(start_year=2026, end_year=2026)
        w2 = PredictionWindow(start_year=2024, end_year=2028)
        result = TemporalAlignmentEngine.compute_overlap(w1, w2)
        assert result.aligned is True
        assert result.overlap_ratio == 1.0  # 1/1 = 100%

    def test_signals_alignment(self):
        w1 = PredictionWindow(start_year=2026, end_year=2027)
        w2 = PredictionWindow(start_year=2026, end_year=2027)
        s1 = TemporalSignal(
            signal_id="S1", engine="Bazi",
            prediction_window=w1, direction="POSITIVE", strength=0.7,
        )
        s2 = TemporalSignal(
            signal_id="S2", engine="Heluo",
            prediction_window=w2, direction="POSITIVE", strength=0.6,
        )
        result = TemporalAlignmentEngine.align_signals(s1, s2)
        assert result.aligned is True
        assert result.overlap_ratio == 1.0

    def test_no_common_window(self):
        """G4.9: No common window = no convergence."""
        w1 = PredictionWindow(start_year=2026, end_year=2026)
        w2 = PredictionWindow(start_year=2030, end_year=2030)
        result = TemporalAlignmentEngine.compute_overlap(w1, w2)
        assert result.aligned is False
        assert result.overlap_ratio == 0.0

    def test_cross_granularity_normalization(self):
        """Normalize MONTHLY to YEARLY."""
        w = PredictionWindow(
            start_year=2026, end_year=2027,
            start_month=3, end_month=6,
            granularity=TemporalGranularity.MONTHLY,
        )
        normalized = TemporalAlignmentEngine.normalize_to_common_granularity(
            w, TemporalGranularity.YEARLY
        )
        assert normalized.granularity == TemporalGranularity.YEARLY
        assert normalized.start_year == 2026
        assert normalized.end_year == 2027
        assert normalized.start_month is None  # Lost in normalization

    def test_multiple_signals_alignment(self):
        w1 = PredictionWindow(start_year=2026, end_year=2027)
        w2 = PredictionWindow(start_year=2026, end_year=2027)
        w3 = PredictionWindow(start_year=2028, end_year=2029)  # No overlap with others
        s1 = TemporalSignal(signal_id="S1", engine="Bazi", prediction_window=w1,
                           direction="POSITIVE", strength=0.7)
        s2 = TemporalSignal(signal_id="S2", engine="Heluo", prediction_window=w2,
                           direction="POSITIVE", strength=0.6)
        s3 = TemporalSignal(signal_id="S3", engine="Ziwei", prediction_window=w3,
                           direction="NEGATIVE", strength=0.5)
        results = TemporalAlignmentEngine.align_multiple_signals([s1, s2, s3])
        assert len(results) == 3  # 3 pairs
        # S1-S2 should overlap
        assert results[("S1", "S2")].aligned is True
        assert results[("S1", "S2")].overlap_ratio == 1.0
        # S1-S3 should NOT overlap
        assert results[("S1", "S3")].aligned is False
