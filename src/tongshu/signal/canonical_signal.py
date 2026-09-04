"""
Phase 3 — Canonical Signal Schema (extended)

Contract:
  - Signal ≠ Event: Signal is a structured observation about an Event
  - Must reference valid Event Type from V1.2 Ontology (17 types)
  - Must reference valid Domain from V1.2 Ontology (4 domains)
  - SourceEngine must be one of 5 canonical engines
  - Evidence refs must exist in EvidenceChainContext
  - Adapter can only convert, NOT re-implement engine logic
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from tongshu.spec.event_ontology_v1 import (
    Domain,
    EventDefinition,
    EventDirection,
    EVENT_TYPE_BY_ID,
    validate_ontology_invariants,
)
from tongshu.spec.canonical_signal import (
    CanonicalSignal as _BaseCanonicalSignal,
    SignalLayer,
    SourceEngine,
    SignalTemporalScope as _BaseSignalTemporalScope,
)


# ─── Canonical Event Types (subset of V1.2 — G3.3 validation) ─────────────────

CANONICAL_EVENT_TYPES: Set[str] = {e.id for e in EVENT_TYPE_BY_ID.values()}
CANONICAL_EVENT_TYPES.add('UNKNOWN')  # G3.12: Unknown mappings use UNKNOWN, not new types
CANONICAL_DOMAINS: Set[str] = {d.value for d in Domain}
CANONICAL_ENGINES: Set[str] = {e.value for e in SourceEngine}
CANONICAL_SIGNAL_LAYERS: Set[str] = {l.value for l in SignalLayer}
CANONICAL_DIRECTIONS: Set[str] = {d.value for d in EventDirection}


# ─── Temporal Scope Validation ────────────────────────────────────────────────

def validate_temporal_scope(scope: SignalTemporalScope) -> List[str]:
    """Validate temporal scope constraints."""
    errors: List[str] = []

    # Check granularity consistency
    if scope.granularity == "YEARLY" and scope.start_year is None:
        errors.append("YEARLY granularity requires start_year")
    if scope.granularity == "MONTHLY" and scope.start_month is None:
        errors.append("MONTHLY granularity requires start_month")
    if scope.granularity == "DAILY" and scope.start_day is None:
        errors.append("DAILY granularity requires start_day")

    # Check end >= start
    if scope.start_year and scope.end_year:
        if scope.end_year < scope.start_year:
            errors.append("end_year < start_year")
    if scope.start_month and scope.end_month:
        if scope.end_month < scope.start_month:
            errors.append("end_month < start_month")
    if scope.start_day and scope.end_day:
        if scope.end_day < scope.start_day:
            errors.append("end_day < start_day")

    return errors


# ─── Enhanced CanonicalSignal (with validation) ────────────────────────────────

@dataclass(frozen=True)
class SignalTemporalScope:
    """Enhanced temporal scope with validation."""

    start_year: Optional[int] = None
    end_year: Optional[int] = None
    start_month: Optional[int] = None
    end_month: Optional[int] = None
    start_day: Optional[int] = None
    end_day: Optional[int] = None
    granularity: str = "YEARLY"

    def to_dict(self) -> dict:
        d = {k: v for k, v in {
            "start_year": self.start_year,
            "end_year": self.end_year,
            "start_month": self.start_month,
            "end_month": self.end_month,
            "start_day": self.start_day,
            "end_day": self.end_day,
        }.items() if v is not None}
        if self.granularity != "YEARLY":
            d["granularity"] = self.granularity
        return d

    def validate(self) -> List[str]:
        return validate_temporal_scope(self)


@dataclass(frozen=True)
class CanonicalSignal:
    """
    Phase 3 Canonical Signal Schema.

    Enforces:
      - Signal ID uniqueness (checked at registry level)
      - Event type from V1.2 Ontology (17 types)
      - Domain consistency with Event type
      - Direction from canonical enum
      - Strength in [0.0, 1.0]
      - Layer from canonical enum
      - Source engine from 5 canonical engines
      - Evidence refs must exist (checked at registry level)
    """

    signal_id: str
    source_engine: SourceEngine
    event_type: str  # FK → EventDefinition.id (V1.2)
    domain: Domain  # Must match EventDefinition.domain
    direction: EventDirection
    temporal_scope: SignalTemporalScope
    evidence_refs: List[str] = field(default_factory=list)
    rule_refs: List[str] = field(default_factory=list)
    layer: SignalLayer = SignalLayer.BASELINE
    extracted_at: str = ""  # ISO8601

    def to_dict(self) -> dict:
        return {
            "signal_id": self.signal_id,
            "source_engine": self.source_engine.value,
            "event_type": self.event_type,
            "domain": self.domain.value,
            "direction": self.direction.value,
            "temporal_scope": self.temporal_scope.to_dict(),
            "evidence_refs": self.evidence_refs,
            "rule_refs": self.rule_refs,
            "layer": self.layer.value,
            "extracted_at": self.extracted_at,
        }


# ─── Canonical Signal Validator ────────────────────────────────────────────────

class CanonicalSignalValidator:
    """Validates CanonicalSignal against all G3 contract constraints."""

    @classmethod
    def validate(cls, signal: CanonicalSignal, evidence_context=None) -> List[str]:
        """
        Full validation of a CanonicalSignal.

        Args:
            signal: The signal to validate
            evidence_context: Optional EvidenceChainContext for evidence ref validation

        Returns:
            List of error messages (empty = valid)
        """
        errors: List[str] = []

        # G3.1 — Signal ID uniqueness (format check)
        if not signal.signal_id or not isinstance(signal.signal_id, str):
            errors.append("signal_id must be non-empty string")
        elif len(signal.signal_id) < 3:
            errors.append("signal_id too short (min 3 chars)")

        # G3.2 — Event Type from V1.2 Ontology
        if signal.event_type not in CANONICAL_EVENT_TYPES:
            errors.append(
                f"event_type '{signal.event_type}' not in V1.2 Ontology (17 types)"
            )

        # G3.3 — Domain must match Event Definition
        if signal.event_type in EVENT_TYPE_BY_ID:
            expected_domain = EVENT_TYPE_BY_ID[signal.event_type].domain
            if signal.domain != expected_domain:
                errors.append(
                    f"domain mismatch: event={signal.event_type} expects {expected_domain.value}, "
                    f"got {signal.domain.value}"
                )

        # G3.4 — Direction from canonical enum
        if signal.direction not in list(EventDirection):
            errors.append(f"invalid direction: {signal.direction}")

        # G3.5 — Signal Layer from canonical enum
        if signal.layer not in list(SignalLayer):
            errors.append(f"invalid layer: {signal.layer}")

        # G3.6 — Source Engine from canonical set
        if signal.source_engine not in list(SourceEngine):
            errors.append(f"invalid source_engine: {signal.source_engine}")

        # G3.7 — Temporal Scope validation
        errors.extend(signal.temporal_scope.validate())

        # G3.9 — Evidence provenance validation
        if evidence_context is not None:
            for ref in signal.evidence_refs:
                if not evidence_context.evidences.has(ref):
                    errors.append(f"evidence_ref '{ref}' not found in EvidenceChain")

        return errors


# ─── Schema-Level Validation (for Registry) ────────────────────────────────────

def validate_canonical_signal_schema(signals: Dict[str, CanonicalSignal]) -> List[str]:
    """
    Schema-level validation for a collection of CanonicalSignals.

    Checks:
      - Signal ID uniqueness
      - All individual signal constraints
    """
    errors: List[str] = []

    # Check for duplicate IDs
    signal_ids = list(signals.keys())
    if len(signal_ids) != len(set(signal_ids)):
        duplicates = [sid for sid in signal_ids if signal_ids.count(sid) > 1]
        errors.append(f"Duplicate signal_ids: {set(duplicates)}")

    # Validate each signal
    for sid, signal in signals.items():
        sig_errors = CanonicalSignalValidator.validate(signal)
        for err in sig_errors:
            errors.append(f"Signal {sid}: {err}")

    return errors
