"""
Phase 3 Contract Tests — Aggregator
"""
from __future__ import annotations

import pytest

from tongshu.signal.aggregator import CanonicalSignalAggregator, SignalGroup
from tongshu.signal.canonical_signal import CanonicalSignal, SignalTemporalScope
from tongshu.spec.event_ontology_v1 import Domain, EventDirection
from tongshu.signal.canonical_signal import SourceEngine


class TestCanonicalSignalAggregator:
    """Test aggregator contract."""

    def test_collect_valid_signal(self):
        signal = CanonicalSignal(
            signal_id="S001",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(start_year=2026, granularity="YEARLY"),
        )
        agg = CanonicalSignalAggregator()
        assert agg.collect(signal) is True
        assert len(agg.signals) == 1

    def test_collect_invalid_signal_rejected(self):
        """Invalid signals must be rejected."""
        signal = CanonicalSignal(
            signal_id="S_BAD",
            source_engine=SourceEngine.BAZI,
            event_type="MY_CUSTOM_EVENT",  # Invalid
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(granularity="YEARLY"),
        )
        agg = CanonicalSignalAggregator()
        assert agg.collect(signal) is False
        assert len(agg.signals) == 0

    def test_duplicate_signal_rejected(self):
        """G3.2: Duplicate signal IDs must be rejected."""
        signal1 = CanonicalSignal(
            signal_id="S001",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(start_year=2026, granularity="YEARLY"),
        )
        signal2 = CanonicalSignal(
            signal_id="S001",  # Duplicate ID
            source_engine=SourceEngine.HELUO,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(start_year=2026, granularity="YEARLY"),
        )
        agg = CanonicalSignalAggregator()
        assert agg.collect(signal1) is True
        assert agg.collect(signal2) is False  # Duplicate rejected

    def test_collect_batch(self):
        signals = [
            CanonicalSignal(
                signal_id=f"S{i:03d}",
                source_engine=SourceEngine.BAZI,
                event_type="PROMOTION",
                domain=Domain.CAREER,
                direction=EventDirection.POSITIVE,
                temporal_scope=SignalTemporalScope(start_year=2026, granularity="YEARLY"),
            )
            for i in range(5)
        ]
        agg = CanonicalSignalAggregator()
        collected, rejected = agg.collect_batch(signals)
        assert collected == 5
        assert rejected == 0

    def test_validate_all(self):
        """G3.1: All collected signals must pass validation."""
        signal = CanonicalSignal(
            signal_id="S001",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(start_year=2026, granularity="YEARLY"),
        )
        agg = CanonicalSignalAggregator()
        agg.collect(signal)
        errors = agg.validate_all()
        assert errors == []

    def test_deduplicate(self):
        """Remove duplicate signals (same signal_id)."""
        signals = [
            CanonicalSignal(
                signal_id="S001",
                source_engine=SourceEngine.BAZI,
                event_type="PROMOTION",
                domain=Domain.CAREER,
                direction=EventDirection.POSITIVE,
                temporal_scope=SignalTemporalScope(start_year=2026, granularity="YEARLY"),
            ),
            CanonicalSignal(
                signal_id="S002",
                source_engine=SourceEngine.HELUO,
                event_type="PROMOTION",
                domain=Domain.CAREER,
                direction=EventDirection.POSITIVE,
                temporal_scope=SignalTemporalScope(start_year=2026, granularity="YEARLY"),
            ),
        ]
        agg = CanonicalSignalAggregator()
        agg.collect_batch(signals)
        removed = agg.deduplicate()
        assert removed == 1  # One duplicate removed
        assert len(agg.signals) == 1

    def test_get_by_event(self):
        signal1 = CanonicalSignal(
            signal_id="S001",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(start_year=2026, granularity="YEARLY"),
        )
        signal2 = CanonicalSignal(
            signal_id="S002",
            source_engine=SourceEngine.HELUO,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.NEGATIVE,
            temporal_scope=SignalTemporalScope(start_year=2026, granularity="YEARLY"),
        )
        agg = CanonicalSignalAggregator()
        agg.collect(signal1)
        agg.collect(signal2)
        promotion_signals = agg.get_by_event("PROMOTION")
        assert len(promotion_signals) == 2

    def test_get_by_domain(self):
        career_signal = CanonicalSignal(
            signal_id="S_CAREER",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(start_year=2026, granularity="YEARLY"),
        )
        family_signal = CanonicalSignal(
            signal_id="S_FAMILY",
            source_engine=SourceEngine.HELUO,
            event_type="MARRIAGE",
            domain=Domain.FAMILY,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(start_year=2026, granularity="YEARLY"),
        )
        agg = CanonicalSignalAggregator()
        agg.collect(career_signal)
        agg.collect(family_signal)
        career_signals = agg.get_by_domain(Domain.CAREER)
        assert len(career_signals) == 1
        assert career_signals[0].signal_id == "S_CAREER"

    def test_summary_no_fortune_score(self):
        """G3.13: Summary must not produce Fortune Score."""
        signal = CanonicalSignal(
            signal_id="S001",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(start_year=2026, granularity="YEARLY"),
        )
        agg = CanonicalSignalAggregator()
        agg.collect(signal)
        summary = agg.summary()
        # Must have structural info, NOT fortune scores
        assert 'total_signals' in summary
        assert 'by_domain' in summary
        assert 'by_engine' in summary
        assert 'by_event_type' in summary
        # Must NOT have fortune scores
        assert 'career_score' not in summary
        assert 'overall_luck' not in summary
        assert 'fortune' not in str(summary).lower()

    def test_export_for_phase4(self):
        """Export format must be Phase 4 ready."""
        signal = CanonicalSignal(
            signal_id="S001",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(start_year=2026, granularity="YEARLY"),
        )
        agg = CanonicalSignalAggregator()
        agg.collect(signal)
        exported = agg.export_for_phase4()
        assert len(exported) == 1
        assert 'signal_id' in exported[0]
        assert 'temporal_scope' in exported[0]
        assert 'evidence_refs' in exported[0]


class TestSignalGroup:
    """Test SignalGroup operations."""

    def test_add_signal(self):
        group = SignalGroup(event_type="PROMOTION", domain=Domain.CAREER)
        signal = CanonicalSignal(
            signal_id="S001",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(granularity="YEARLY"),
        )
        group.add(signal)
        assert group.count == 1

    def test_direction_counts(self):
        group = SignalGroup(event_type="PROMOTION", domain=Domain.CAREER)
        for i in range(3):
            group.add(CanonicalSignal(
                signal_id=f"S{i:03d}",
                source_engine=SourceEngine.BAZI,
                event_type="PROMOTION",
                domain=Domain.CAREER,
                direction=EventDirection.POSITIVE,
                temporal_scope=SignalTemporalScope(granularity="YEARLY"),
            ))
        for i in range(2):
            group.add(CanonicalSignal(
                signal_id=f"S{i+3:03d}",
                source_engine=SourceEngine.HELUO,
                event_type="PROMOTION",
                domain=Domain.CAREER,
                direction=EventDirection.NEGATIVE,
                temporal_scope=SignalTemporalScope(granularity="YEARLY"),
            ))
        counts = group.get_direction_counts()
        assert counts['POSITIVE'] == 3
        assert counts['NEGATIVE'] == 2

    def test_engine_counts(self):
        group = SignalGroup(event_type="PROMOTION", domain=Domain.CAREER)
        group.add(CanonicalSignal(
            signal_id="S001",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(granularity="YEARLY"),
        ))
        group.add(CanonicalSignal(
            signal_id="S002",
            source_engine=SourceEngine.HELUO,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(granularity="YEARLY"),
        ))
        counts = group.get_engine_counts()
        assert counts['Bazi'] == 1
        assert counts['Heluo'] == 1
