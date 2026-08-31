"""Test signal_engine dual-track output (P1.3)."""
from __future__ import annotations
import pytest
from pathlib import Path
from tongshu.reasoning.signal_engine import SignalEngine, build_canonical_signals
from tongshu.reasoning.matcher import RuleMatcher
from tongshu.reasoning.rule_loader import RuleLoader
from tongshu.spec.canonical_signal import CanonicalSignal, SourceEngine, SignalLayer
from tongshu.types import ComputeResult

_REPO = Path(__file__).resolve().parents[2]


def _make_matcher() -> RuleMatcher:
    loader = RuleLoader(_REPO / "data", _REPO / "docs")
    return RuleMatcher(loader.rules)


def test_build_returns_dual_track():
    """SignalEngine.build() returns dict with 'signals' and 'canonical_signals' keys."""
    matcher = _make_matcher()
    engine = SignalEngine(matcher)
    result = engine.build(None, None, None, gender="male")
    assert "signals" in result
    assert "canonical_signals" in result
    assert isinstance(result["signals"], dict)
    assert isinstance(result["canonical_signals"], dict)


def test_canonical_signals_structure():
    """Each layer in canonical_signals contains CanonicalSignal objects."""
    matcher = _make_matcher()
    canonical = build_canonical_signals(None, None, None, matcher, gender="male")
    from tongshu.reasoning.signal_engine import SIGNAL_LAYER_ORDER
    for layer in SIGNAL_LAYER_ORDER:
        assert layer in canonical
        for cs in canonical[layer]:
            assert isinstance(cs, CanonicalSignal)
            assert cs.source_engine == SourceEngine.BAZI
            assert isinstance(cs.layer, SignalLayer)


def test_direction_mapping():
    """Legacy direction values map to canonical directions."""
    from tongshu.reasoning.signal_engine import _DIRECTION_MAP
    assert _DIRECTION_MAP["INCREASE"] == "POSITIVE"
    assert _DIRECTION_MAP["DECLINE"] == "NEGATIVE"
    assert _DIRECTION_MAP["STABLE"] == "NEUTRAL"
    assert _DIRECTION_MAP["VOLATILE"] == "CHANGE"


def test_compute_result_has_canonical_signals():
    """ComputeResult includes canonical_signals field."""
    from dataclasses import fields
    field_names = [f.name for f in fields(ComputeResult)]
    assert "canonical_signals" in field_names


def test_build_canonical_signals_matches_legacy_count():
    """Canonical signals count matches legacy signals count per layer."""
    matcher = _make_matcher()
    canonical = build_canonical_signals(None, None, None, matcher, gender="male")
    from tongshu.reasoning.signal_engine import build_signals
    legacy_signals = build_signals(None, None, None, matcher, gender="male")
    for layer in legacy_signals:
        assert len(canonical[layer]) == len(legacy_signals[layer])
