"""
Phase 4 — Temporal Convergence Engine

Contract:
  - Aggregates TemporalSignals from multiple engines
  - Computes overlap_ratio, convergence_score, temporal_agreement
  - Does NOT produce Fortune Score or final auspiciousness rating
  - UNKNOWN direction engines are counted but not treated as positive/negative
  - No common window = no convergence (cannot fabricate convergence)
  - Legacy engines are untouched
"""
from __future__ import annotations

import hashlib
from typing import Dict, List, Optional

from tongshu.temporal.schema import (
    EvaluationToleranceWindow,
    PredictionWindow,
    TemporalConvergence,
    TemporalEvidence,
    TemporalGranularity,
    TemporalSignal,
)
from tongshu.temporal.alignment import TemporalAlignmentEngine


class TemporalConvergenceEngine:
    """
    Multi-engine temporal convergence computation.

    Contract:
      - Only computes temporal overlap and agreement metrics
      - Does NOT interpret signals or assign fortune/luck scores
      - Does NOT modify legacy engines
      - UNKNOWN direction signals are tracked but not counted as agreement
    """

    def __init__(self, target_year: int, target_month: Optional[int] = None):
        self.target_year = target_year
        self.target_month = target_month
        self._signals: Dict[str, TemporalSignal] = {}
        self._evidence: Dict[str, TemporalEvidence] = {}

    def add_signal(self, signal: TemporalSignal) -> bool:
        """Add a temporal signal. Returns False if duplicate or invalid."""
        if signal.signal_id in self._signals:
            return False  # Duplicate
        errors = signal.validate()
        if errors:
            return False  # Invalid signal
        self._signals[signal.signal_id] = signal
        return True

    def add_evidence(self, evidence: TemporalEvidence) -> bool:
        """Add temporal evidence. Validates signal_id reference."""
        if evidence.signal_id not in self._signals:
            return False
        errors = evidence.temporal_signal.validate()
        if errors:
            return False
        self._evidence[evidence.evidence_id] = evidence
        return True

    def compute_convergence(self) -> TemporalConvergence:
        """
        Compute temporal convergence from all added signals.

        Rules:
          - overlap_ratio: fraction of signals whose windows overlap
          - convergence_score: weighted by strength and overlap
          - temporal_agreement: NONE if no overlap, PARTIAL/STRONG/COMPLETE otherwise
          - UNKNOWN direction engines are NOT counted as agreeing
          - No convergence if no common temporal window exists
        """
        if len(self._signals) < 2:
            return self._build_convergence(empty=True)

        signals = list(self._signals.values())

        # Compute pairwise overlaps
        alignments = TemporalAlignmentEngine.align_multiple_signals(signals)

        # Find common overlapping signals
        overlapping_ids = self._find_overlapping_signals(signals, alignments)

        if not overlapping_ids:
            return self._build_convergence(empty=True)

        # Compute agreement metrics
        total = len(signals)
        overlapping_count = len(overlapping_ids)

        # Count agreeing engines (exclude UNKNOWN)
        agreeing_count = sum(
            1 for sid in overlapping_ids
            if self._signals[sid].direction != "UNKNOWN"
        )
        unknown_count = sum(
            1 for sid in overlapping_ids
            if self._signals[sid].direction == "UNKNOWN"
        )

        # Compute overlap_ratio
        avg_overlap = self._compute_avg_overlap(overlapping_ids, alignments)

        # Compute convergence_score
        convergence_score = self._compute_convergence_score(
            avg_overlap, agreeing_count, total, unknown_count
        )

        # Determine temporal_agreement
        agreement = self._determine_agreement(avg_overlap, agreeing_count, total)

        # Build signal_ids_by_engine
        signal_ids_by_engine = self._group_by_engine(overlapping_ids)

        return TemporalConvergence(
            convergence_id=self._generate_id(overlapping_ids),
            target_year=self.target_year,
            target_month=self.target_month,
            signal_ids_by_engine=signal_ids_by_engine,
            overlap_ratio=avg_overlap,
            convergence_score=convergence_score,
            total_engines=total,
            agreeing_engines=agreeing_count,
            unknown_engines=unknown_count,
            temporal_agreement=agreement,
        )

    def compute_agreement_with_tolerance(
        self,
        tolerance: EvaluationToleranceWindow,
    ) -> TemporalConvergence:
        """
        Compute convergence with evaluation tolerance window.
        """
        convergence = self.compute_convergence()
        # Tolerance is applied at validation layer, not here
        return convergence

    def get_signals_by_engine(self, engine: str) -> List[TemporalSignal]:
        """Get all signals from a specific engine."""
        return [s for s in self._signals.values() if s.engine == engine]

    def get_all_signals(self) -> Dict[str, TemporalSignal]:
        """Get all signals."""
        return self._signals.copy()

    def validate_all(self) -> List[str]:
        """Validate all signals and evidence."""
        errors = []
        for sig in self._signals.values():
            errors.extend(sig.validate())
        for ev in self._evidence.values():
            errors.extend(ev.temporal_signal.validate())
        return errors

    # ─── Private helpers ───────────────────────────────────────────────────────

    def _find_overlapping_signals(
        self,
        signals: List[TemporalSignal],
        alignments: Dict[tuple, object],
    ) -> List[str]:
        """Find signals that have at least one overlap with another signal."""
        overlapping = set()
        for (sid_a, sid_b), result in alignments.items():
            if result.aligned and result.overlap_ratio > 0:
                overlapping.add(sid_a)
                overlapping.add(sid_b)
        return list(overlapping)

    def _compute_avg_overlap(
        self,
        signal_ids: List[str],
        alignments: Dict[tuple, object],
    ) -> float:
        """Compute average overlap ratio among overlapping signals."""
        overlaps = []
        for (sid_a, sid_b), result in alignments.items():
            if sid_a in signal_ids and sid_b in signal_ids and result.aligned:
                overlaps.append(result.overlap_ratio)
        return sum(overlaps) / len(overlaps) if overlaps else 0.0

    def _compute_convergence_score(
        self,
        avg_overlap: float,
        agreeing_count: int,
        total: int,
        unknown_count: int,
    ) -> float:
        """
        Compute convergence score.

        Formula:
          score = avg_overlap × (agreeing_count / total) × weighted_strength

        UNKNOWN direction signals reduce agreement but don't contribute to score.
        """
        if total == 0:
            return 0.0

        # Agreement ratio (excluding UNKNOWN)
        agreement_ratio = agreeing_count / total if total > 0 else 0.0

        # Strength-weighted overlap: average strength of non-UNKNOWN overlapping signals
        strengths = [
            self._signals[sid].strength
            for sid in self._signals
            if self._signals[sid].direction != "UNKNOWN"
        ]
        avg_strength = sum(strengths) / len(strengths) if strengths else 0.5

        score = avg_overlap * agreement_ratio * avg_strength
        return round(min(score, 1.0), 4)

    def _determine_agreement(
        self,
        avg_overlap: float,
        agreeing_count: int,
        total: int,
    ) -> str:
        """
        Determine temporal agreement level.

        NONE: no overlap
        PARTIAL: some overlap, <50% agreement
        STRONG: some overlap, >=50% agreement
        COMPLETE: 100% overlap and 100% agreement
        """
        if avg_overlap == 0.0:
            return "NONE"

        agreement_ratio = agreeing_count / total if total > 0 else 0.0

        if avg_overlap >= 0.9 and agreement_ratio >= 0.9:
            return "COMPLETE"
        elif avg_overlap >= 0.5 and agreement_ratio >= 0.5:
            return "STRONG"
        elif avg_overlap > 0:
            return "PARTIAL"
        return "NONE"

    def _group_by_engine(self, signal_ids: List[str]) -> Dict[str, List[str]]:
        """Group signal IDs by engine."""
        groups: Dict[str, List[str]] = {}
        for sid in signal_ids:
            engine = self._signals[sid].engine
            if engine not in groups:
                groups[engine] = []
            groups[engine].append(sid)
        return groups

    def _build_convergence(self, empty: bool = False) -> TemporalConvergence:
        """Build an empty or minimal convergence result."""
        if empty:
            return TemporalConvergence(
                convergence_id=self._generate_id([]),
                target_year=self.target_year,
                target_month=self.target_month,
                overlap_ratio=0.0,
                convergence_score=0.0,
                temporal_agreement="NONE",
                total_engines=len(self._signals),
                agreeing_engines=0,
                unknown_engines=len(self._signals),
            )
        return TemporalConvergence(
            convergence_id=self._generate_id(list(self._signals.keys())),
            target_year=self.target_year,
            target_month=self.target_month,
            signal_ids_by_engine=self._group_by_engine(list(self._signals.keys())),
            overlap_ratio=0.0,
            convergence_score=0.0,
            temporal_agreement="NONE",
            total_engines=len(self._signals),
            agreeing_engines=0,
            unknown_engines=len(self._signals),
        )

    @staticmethod
    def _generate_id(signal_ids: List[str]) -> str:
        """Generate stable convergence ID."""
        raw = "|".join(sorted(signal_ids))
        return f"TC_{hashlib.sha256(raw.encode()).hexdigest()[:8]}"
