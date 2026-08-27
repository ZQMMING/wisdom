"""
Phase 3 Negative Contract Tests

These tests ensure the contract CANNOT be bypassed.
Any successful bypass attempt is a bug.
"""
from __future__ import annotations

import pytest

from tongshu.signal.canonical_signal import (
    CanonicalSignal,
    CanonicalSignalValidator,
    SignalTemporalScope,
)
from tongshu.signal.aggregator import CanonicalSignalAggregator
from tongshu.signal.adapters import (
    BaziAdapter,
    HeluoAdapter,
    ZiweiAdapter,
    HuangliAdapter,
    KnowledgeAdapter,
)
from tongshu.spec.event_ontology_v1 import Domain, EventDirection
from tongshu.signal.canonical_signal import SourceEngine


class TestNegativeContracts:
    """
    Negative contract tests — ensure contract CANNOT be bypassed.
    """

    def test_cannot_create_signal_with_invalid_event_type(self):
        """G3.12: Cannot create signal with non-canonical event type."""
        signal = CanonicalSignal(
            signal_id="S_EVADE",
            source_engine=SourceEngine.BAZI,
            event_type="EVASION_ATTEMPT",  # Not in 17 types
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            strength=0.5,
            temporal_scope=SignalTemporalScope(granularity="YEARLY"),
        )
        errors = CanonicalSignalValidator.validate(signal)
        assert len(errors) > 0, "Contract must reject non-canonical event types"

    def test_cannot_map_event_to_wrong_domain(self):
        """G3.3: Cannot map event to wrong domain."""
        signal = CanonicalSignal(
            signal_id="S_EVADE",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",  # CAREER event
            domain=Domain.EDUCATION,  # Wrong domain!
            direction=EventDirection.POSITIVE,
            strength=0.5,
            temporal_scope=SignalTemporalScope(granularity="YEARLY"),
        )
        errors = CanonicalSignalValidator.validate(signal)
        assert any("domain mismatch" in e for e in errors)

    def test_cannot_set_strength_above_1(self):
        """G3.7: Cannot set strength > 1.0."""
        signal = CanonicalSignal(
            signal_id="S_EVADE",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            strength=1.5,  # Out of range
            temporal_scope=SignalTemporalScope(granularity="YEARLY"),
        )
        errors = CanonicalSignalValidator.validate(signal)
        assert any("strength" in e for e in errors)

    def test_cannot_set_strength_below_0(self):
        """G3.7: Cannot set strength < 0.0."""
        signal = CanonicalSignal(
            signal_id="S_EVADE",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            strength=-0.1,
            temporal_scope=SignalTemporalScope(granularity="YEARLY"),
        )
        errors = CanonicalSignalValidator.validate(signal)
        assert any("strength" in e for e in errors)

    def test_cannot_use_nonexistent_engine(self):
        """G3.6: Cannot use non-existent engine."""
        with pytest.raises(ValueError):
            CanonicalSignal(
                signal_id="S_EVADE",
                source_engine=SourceEngine("FAKE_ENGINE"),  # type: ignore
                event_type="PROMOTION",
                domain=Domain.CAREER,
                direction=EventDirection.POSITIVE,
                strength=0.5,
                temporal_scope=SignalTemporalScope(granularity="YEARLY"),
            )

    def test_knowledge_adapter_requires_evidence(self):
        """G3.9: Knowledge adapter MUST have evidence_id."""
        output = {
            'signal_id': 'KNOWLEDGE_EVADE',
            'source_text': 'test',
            'rule_id': 'R001',
            # Missing evidence_id
        }
        with pytest.raises(ValueError, match="evidence_id is required"):
            KnowledgeAdapter.adapt(output)

    def test_aggregator_rejects_invalid_signals(self):
        """Aggregator must reject invalid signals."""
        signal = CanonicalSignal(
            signal_id="S_EVADE",
            source_engine=SourceEngine.BAZI,
            event_type="INVALID_TYPE",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            strength=0.5,
            temporal_scope=SignalTemporalScope(granularity="YEARLY"),
        )
        agg = CanonicalSignalAggregator()
        assert agg.collect(signal) is False

    def test_aggregator_rejects_duplicate_ids(self):
        """G3.2: Aggregator must reject duplicate signal IDs."""
        signal1 = CanonicalSignal(
            signal_id="S_DUP",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            strength=0.7,
            temporal_scope=SignalTemporalScope(start_year=2026, granularity="YEARLY"),
        )
        signal2 = CanonicalSignal(
            signal_id="S_DUP",  # Same ID
            source_engine=SourceEngine.HELUO,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            strength=0.6,
            temporal_scope=SignalTemporalScope(start_year=2026, granularity="YEARLY"),
        )
        agg = CanonicalSignalAggregator()
        assert agg.collect(signal1) is True
        assert agg.collect(signal2) is False  # Duplicate rejected

    def test_adapter_cannot_create_new_event_type(self):
        """G3.12: Adapters cannot create new Event Types."""
        # Try to force an invalid event type through Bazi adapter
        output = {
            'signal_id': 'BAZI_EVADE',
            'shenshan': '正官',
            'pattern': 'CUSTOM_PATTERN',  # Invalid pattern
            'strength': 0.5,
        }
        with pytest.raises(ValueError):
            BaziAdapter.adapt(output)

    def test_temporal_scope_cannot_have_end_before_start(self):
        """Temporal scope constraints must be enforced."""
        signal = CanonicalSignal(
            signal_id="S_EVADE",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            strength=0.5,
            temporal_scope=SignalTemporalScope(
                start_year=2027,
                end_year=2026,  # End before start
                granularity="YEARLY",
            ),
        )
        errors = CanonicalSignalValidator.validate(signal)
        assert any("end_year < start_year" in e for e in errors)


class TestCrossLayerValidation:
    """Test that validation works across layers."""

    def test_full_pipeline_rejects_invalid(self):
        """Full pipeline must reject invalid signals at every layer."""
        agg = CanonicalSignalAggregator()

        # Try to collect invalid signal
        signal = CanonicalSignal(
            signal_id="S_PIPELINE",
            source_engine=SourceEngine.BAZI,
            event_type="INVALID",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            strength=0.5,
            temporal_scope=SignalTemporalScope(granularity="YEARLY"),
        )

        # Layer 1: Direct validation
        errors = CanonicalSignalValidator.validate(signal)
        assert len(errors) > 0

        # Layer 2: Through aggregator
        assert agg.collect(signal) is False

        # Layer 3: Validate all
        validation_errors = agg.validate_all()
        assert validation_errors == []  # Empty because nothing was collected
