"""
Phase 4 — Temporal Alignment Engine

Contract:
  - Aligns temporal signals across engines at different granularities
  - Computes overlap_ratio between prediction windows
  - Does NOT compute convergence_score (that's the ConvergenceEngine's job)
  - Does NOT produce Fortune Score
  - Legacy engines are untouched
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from tongshu.temporal.schema import (
    PredictionWindow,
    TemporalGranularity,
    TemporalSignal,
)


@dataclass
class TemporalAlignmentResult:
    """Result of aligning temporal signals."""
    aligned: bool
    overlap_ratio: float
    common_start_year: Optional[int] = None
    common_end_year: Optional[int] = None
    common_start_month: Optional[int] = None
    common_end_month: Optional[int] = None
    mismatch_reason: str = ""

    def to_dict(self) -> dict:
        return {
            "aligned": self.aligned,
            "overlap_ratio": self.overlap_ratio,
            "common_start_year": self.common_start_year,
            "common_end_year": self.common_end_year,
            "common_start_month": self.common_start_month,
            "common_end_month": self.common_end_month,
            "mismatch_reason": self.mismatch_reason,
        }


class TemporalAlignmentEngine:
    """
    Aligns temporal signals across engines.

    Contract:
      - Only computes overlap between prediction windows
      - Does NOT aggregate or converge
      - Does NOT modify any schema
      - Handles YEARLY/MONTHLY/DAILY granularity translation
    """

    @classmethod
    def compute_overlap(
        cls,
        window_a: PredictionWindow,
        window_b: PredictionWindow,
    ) -> TemporalAlignmentResult:
        """
        Compute overlap ratio between two prediction windows.

        Returns 0.0 if no overlap, 1.0 if fully overlapping.
        """
        # Determine effective years for comparison
        start_a, end_a = cls._normalize_to_years(window_a)
        start_b, end_b = cls._normalize_to_years(window_b)

        # Compute year overlap
        overlap_start = max(start_a, start_b)
        overlap_end = min(end_a, end_b)

        if overlap_start > overlap_end:
            return TemporalAlignmentResult(
                aligned=False,
                overlap_ratio=0.0,
                mismatch_reason="No year overlap"
            )

        # Calculate overlap ratio
        duration_a = end_a - start_a + 1
        duration_b = end_b - start_b + 1
        overlap_duration = overlap_end - overlap_start + 1

        # Use minimum duration as denominator (conservative)
        min_duration = min(duration_a, duration_b)
        overlap_ratio = overlap_duration / min_duration if min_duration > 0 else 0.0

        return TemporalAlignmentResult(
            aligned=True,
            overlap_ratio=round(overlap_ratio, 4),
            common_start_year=overlap_start,
            common_end_year=overlap_end,
        )

    @classmethod
    def align_signals(
        cls,
        signal_a: TemporalSignal,
        signal_b: TemporalSignal,
    ) -> TemporalAlignmentResult:
        """Align two temporal signals by their prediction windows."""
        return cls.compute_overlap(
            signal_a.prediction_window,
            signal_b.prediction_window,
        )

    @classmethod
    def align_multiple_signals(
        cls,
        signals: List[TemporalSignal],
    ) -> Dict[str, TemporalAlignmentResult]:
        """
        Align multiple signals pairwise.
        Returns dict of (signal_id_1, signal_id_2) → alignment result.
        """
        results = {}
        n = len(signals)
        for i in range(n):
            for j in range(i + 1, n):
                key = (signals[i].signal_id, signals[j].signal_id)
                results[key] = cls.align_signals(signals[i], signals[j])
        return results

    @classmethod
    def normalize_to_common_granularity(
        cls,
        window: PredictionWindow,
        target_granularity: TemporalGranularity,
    ) -> PredictionWindow:
        """
        Normalize a window to a coarser granularity.
        YEARLY ← MONTHLY ← DAILY
        """
        if window.granularity == target_granularity:
            return window

        if target_granularity == TemporalGranularity.YEARLY:
            return PredictionWindow(
                start_year=window.start_year,
                end_year=window.end_year,
                granularity=TemporalGranularity.YEARLY,
            )
        elif target_granularity == TemporalGranularity.MONTHLY:
            return PredictionWindow(
                start_year=window.start_year,
                end_year=window.end_year,
                start_month=window.start_month,
                end_month=window.end_month,
                granularity=TemporalGranularity.MONTHLY,
            )
        else:
            # Keep original — cannot normalize to finer granularity
            return window

    @staticmethod
    def _normalize_to_years(window: PredictionWindow) -> Tuple[int, int]:
        """Extract effective year range from any window."""
        return window.start_year, window.end_year

    @staticmethod
    def _hash_id(parts: List[str]) -> str:
        """Generate a stable ID from parts."""
        raw = "|".join(parts)
        return hashlib.sha256(raw.encode()).hexdigest()[:12]
