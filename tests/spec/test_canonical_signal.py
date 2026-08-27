"""
Contract Tests: Schema 4 — Canonical Signal
Phase 1: Schema only — no aggregation, no weights, no voting.
"""
from __future__ import annotations

import pytest
from tongshu.spec.canonical_signal import (
    SignalLayer,
    SourceEngine,
    SignalTemporalScope,
    CanonicalSignal,
)


# ─── Enum completeness ────────────────────────────────────────────────────────


def test_signal_layer_enum():
    assert {s.value for s in SignalLayer} == {"BASELINE", "CYCLE_CONTEXT", "DAILY_ACTIVATION"}


def test_source_engine_enum():
    assert {e.value for e in SourceEngine} == {"Bazi", "Heluo", "Ziwei", "Huangli", "Knowledge", "Blind"}


# ─── SignalTemporalScope ─────────────────────────────────────────────────────


def test_temporal_scope_minimal():
    s = SignalTemporalScope()
    assert s.to_dict() == {}  # all None defaults → empty dict (granularity defaults to YEARLY but excluded when minimal)


def test_temporal_scope_yearly():
    s = SignalTemporalScope(start_year=2026, end_year=2026, granularity="YEARLY")
    d = s.to_dict()
    assert d["start_year"] == 2026
    assert d["end_year"] == 2026
    # granularity="YEARLY" is the default, so excluded from dict
    assert "granularity" not in d
    assert "start_month" not in d


# ─── CanonicalSignal (Schema only — no weights/aggregation) ──────────────────


def test_canonical_signal_minimal():
    cs = CanonicalSignal(
        signal_id="sig-001",
        source_engine=SourceEngine.BAZI,
        ontology_type="ACTION",
        event_types=["PROMOTION"],
        direction="POSITIVE",
        confidence=0.85,
        temporal_scope=SignalTemporalScope(start_year=2026, granularity="YEARLY"),
        evidence_refs=["ev-001"],
        extracted_at="2026-08-22T00:00:00Z",
    )
    d = cs.to_dict()
    assert d["signal_id"] == "sig-001"
    assert d["source_engine"] == "Bazi"
    assert d["confidence"] == 0.85
    assert d["layer"] == "BASELINE"


def test_canonical_signal_no_weights():
    """CanonicalSignal must NOT have any weight fields (aggregation is Phase 5)."""
    cs = CanonicalSignal(
        signal_id="sig-002",
        source_engine=SourceEngine.HELUO,
        ontology_type="SUPPORT",
        event_types=["MARRIAGE"],
        direction="POSITIVE",
        confidence=0.70,
        temporal_scope=SignalTemporalScope(granularity="YEARLY"),
        evidence_refs=[],
    )
    # No weight, voting, or aggregation fields allowed
    assert not hasattr(cs, "weight")
    assert not hasattr(cs, "vote")
    assert not hasattr(cs, "consensus")


def test_canonical_signal_to_dict():
    cs = CanonicalSignal(
        signal_id="sig-003",
        source_engine=SourceEngine.ZIWEI,
        ontology_type="CONSTRAINT",
        event_types=["DIVORCE"],
        direction="NEGATIVE",
        confidence=0.60,
        temporal_scope=SignalTemporalScope(
            start_year=2026, end_year=2027,
            start_month=1, end_month=6,
            granularity="MONTHLY",
        ),
        evidence_refs=["ev-010", "ev-011"],
        rule_refs=["rule-001"],
        layer=SignalLayer.CYCLE_CONTEXT,
        extracted_at="2026-08-22T12:00:00Z",
    )
    d = cs.to_dict()
    assert d["signal_id"] == "sig-003"
    assert d["ontology_type"] == "CONSTRAINT"
    assert d["event_types"] == ["DIVORCE"]
    assert d["temporal_scope"]["start_month"] == 1
    assert d["evidence_refs"] == ["ev-010", "ev-011"]
    assert d["layer"] == "CYCLE_CONTEXT"
