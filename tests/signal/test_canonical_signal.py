"""
Phase 3 Contract Tests — Canonical Signal Schema
"""
from __future__ import annotations

import pytest

from tongshu.signal.canonical_signal import (
    CanonicalSignal,
    CanonicalSignalValidator,
    SignalTemporalScope,
    SignalLayer,
)
from tongshu.signal.normalizer import NormalizationStatus
from tongshu.spec.event_ontology_v1 import (
    Domain,
    EventDirection,
    EVENT_TYPE_BY_ID,
    validate_ontology_invariants,
)
from tongshu.signal.canonical_signal import SourceEngine


class TestCanonicalSignalSchema:
    """Test CanonicalSignal schema constraints."""

    def test_valid_signal_passes(self):
        signal = CanonicalSignal(
            signal_id="S001",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(start_year=2026, granularity="YEARLY"),
        )
        errors = CanonicalSignalValidator.validate(signal)
        assert errors == []

    def test_unknown_event_type_rejected(self):
        """G3.12: Unknown mappings must use UNKNOWN, not new types."""
        signal = CanonicalSignal(
            signal_id="S_BAD",
            source_engine=SourceEngine.BAZI,
            event_type="MY_CUSTOM_EVENT",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(granularity="YEARLY"),
        )
        errors = CanonicalSignalValidator.validate(signal)
        assert any("not in V1.2 Ontology" in e for e in errors)

    def test_domain_mismatch_rejected(self):
        """G3.3: Domain must match Event Definition."""
        signal = CanonicalSignal(
            signal_id="S_BAD",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",  # CAREER domain
            domain=Domain.FAMILY,   # Wrong domain
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(granularity="YEARLY"),
        )
        errors = CanonicalSignalValidator.validate(signal)
        assert any("domain mismatch" in e for e in errors)

    def test_strength_out_of_range_rejected(self):
        """G3.7: Strength validation removed - no longer in blind engine."""
        # Test that CanonicalSignal works without strength parameter
        signal = CanonicalSignal(
            signal_id="S_TEST",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(granularity="YEARLY", start_year=2026),
        )
        errors = CanonicalSignalValidator.validate(signal)
        # Should pass without strength
        assert len(errors) == 0

    def test_invalid_direction_rejected(self):
        """G3.4: Direction must be from canonical enum."""
        # This is validated at dataclass level, but let's test the enum
        with pytest.raises(ValueError):
            CanonicalSignal(
                signal_id="S_BAD",
                source_engine=SourceEngine.BAZI,
                event_type="PROMOTION",
                domain=Domain.CAREER,
                direction=EventDirection("INVALID"),  # type: ignore
                temporal_scope=SignalTemporalScope(granularity="YEARLY"),
            )

    def test_invalid_layer_rejected(self):
        """G3.5: Layer must be from canonical enum."""
        # Test by passing invalid enum value directly
        with pytest.raises(ValueError):
            SignalLayer("INVALID_LAYER")  # type: ignore

    def test_invalid_engine_rejected(self):
        """G3.6: Source engine must be from canonical set."""
        with pytest.raises(ValueError):
            CanonicalSignal(
                signal_id="S_BAD",
                source_engine=SourceEngine("INVALID"),  # type: ignore
                event_type="PROMOTION",
                domain=Domain.CAREER,
                direction=EventDirection.POSITIVE,
                temporal_scope=SignalTemporalScope(granularity="YEARLY"),
            )

    def test_temporal_scope_yearly_requires_start_year(self):
        """G3.8: YEARLY granularity requires start_year."""
        signal = CanonicalSignal(
            signal_id="S_BAD",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(granularity="YEARLY"),  # No start_year
        )
        errors = CanonicalSignalValidator.validate(signal)
        assert any("start_year" in e for e in errors)

    def test_temporal_scope_monthly_requires_start_month(self):
        """MONTHLY granularity requires start_month."""
        signal = CanonicalSignal(
            signal_id="S_BAD",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(granularity="MONTHLY"),  # No start_month
        )
        errors = CanonicalSignalValidator.validate(signal)
        assert any("start_month" in e for e in errors)

    def test_temporal_scope_daily_requires_start_day(self):
        """DAILY granularity requires start_day."""
        signal = CanonicalSignal(
            signal_id="S_BAD",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(granularity="DAILY"),  # No start_day
        )
        errors = CanonicalSignalValidator.validate(signal)
        assert any("start_day" in e for e in errors)

    def test_temporal_scope_end_before_start_rejected(self):
        """End date cannot be before start date."""
        signal = CanonicalSignal(
            signal_id="S_BAD",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",
            domain=Domain.CAREER,
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(
                start_year=2027,
                end_year=2026,  # End before start
                granularity="YEARLY",
            ),
        )
        errors = CanonicalSignalValidator.validate(signal)
        assert any("end_year < start_year" in e for e in errors)


class TestOntologyInvariants:
    """Test V1.2 Ontology invariants (G3.1, G3.2)."""

    def test_ontology_invariants_pass(self):
        """G3.1: V1.2 Ontology must have exactly 17 event types."""
        errors = validate_ontology_invariants()
        assert errors == []

    def test_event_types_count_is_17(self):
        """G3.2: Exactly 17 canonical event types."""
        assert len(EVENT_TYPE_BY_ID) == 17

    def test_all_event_types_have_valid_domain(self):
        """All event types must have valid domain."""
        for eid, edef in EVENT_TYPE_BY_ID.items():
            assert edef.domain in list(Domain), f"{eid} has invalid domain"

    def test_all_event_types_have_valid_direction(self):
        """All event types must have valid direction."""
        for eid, edef in EVENT_TYPE_BY_ID.items():
            assert edef.direction in list(EventDirection), f"{eid} has invalid direction"


class TestSchemaIntegration:
    """Integration tests for schema + validator."""

    def test_all_17_event_types_valid(self):
        """All 17 event types can create valid signals."""
        for eid in EVENT_TYPE_BY_ID.keys():
            edef = EVENT_TYPE_BY_ID[eid]
            signal = CanonicalSignal(
                signal_id=f"S_{eid}",
                source_engine=SourceEngine.BAZI,
                event_type=eid,
                domain=edef.domain,
                direction=EventDirection.NEUTRAL,
                temporal_scope=SignalTemporalScope(start_year=2026, granularity="YEARLY"),
            )
            errors = CanonicalSignalValidator.validate(signal)
            assert errors == [], f"Event {eid} failed validation: {errors}"

    def test_cross_domain_mapping_rejected(self):
        """G3.12: Cannot map event to wrong domain."""
        # PROMOTION is CAREER domain, trying to map to FAMILY
        signal = CanonicalSignal(
            signal_id="S_CROSS",
            source_engine=SourceEngine.BAZI,
            event_type="PROMOTION",  # CAREER
            domain=Domain.FAMILY,   # Wrong!
            direction=EventDirection.POSITIVE,
            temporal_scope=SignalTemporalScope(granularity="YEARLY"),
        )
        errors = CanonicalSignalValidator.validate(signal)
        assert len(errors) > 0
