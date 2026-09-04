"""
Canonical Signal Aggregator (Phase 3)

Contract:
  - collect: gather signals from multiple sources
  - validate: check all signals pass G3 constraints
  - normalize: ensure consistent formatting
  - deduplicate: remove redundant signals
  - group: organize by event type and domain
  - NO Fortune Score generation
  - NO Temporal Convergence (that's Phase 4)
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from tongshu.signal.canonical_signal import (
    CanonicalSignal,
    CanonicalSignalValidator,
    validate_canonical_signal_schema,
)
from tongshu.spec.event_ontology_v1 import Domain, EventDirection


@dataclass
class SignalGroup:
    """Group of signals for the same event type."""

    event_type: str
    domain: Domain
    signals: List[CanonicalSignal] = field(default_factory=list)

    def add(self, signal: CanonicalSignal) -> None:
        self.signals.append(signal)

    @property
    def count(self) -> int:
        return len(self.signals)

    def get_direction_counts(self) -> Dict[str, int]:
        """Count signals by direction."""
        counts = {}
        for s in self.signals:
            d = s.direction.value
            counts[d] = counts.get(d, 0) + 1
        return counts

    def get_engine_counts(self) -> Dict[str, int]:
        """Count signals by source engine."""
        counts = {}
        for s in self.signals:
            e = s.source_engine.value
            counts[e] = counts.get(e, 0) + 1
        return counts


class CanonicalSignalAggregator:
    """
    Aggregates and manages CanonicalSignals.

    Contract:
      - Only validates and organizes signals
      - Does NOT compute scores, weights, or interpretations
      - Preserves all original signals for Phase 4 Temporal Convergence
    """

    def __init__(self):
        self._signals: Dict[str, CanonicalSignal] = {}
        self._groups: Dict[str, SignalGroup] = {}

    @property
    def signals(self) -> Dict[str, CanonicalSignal]:
        """All collected signals."""
        return self._signals.copy()

    @property
    def groups(self) -> Dict[str, SignalGroup]:
        """Signals grouped by event type."""
        return self._groups.copy()

    def collect(self, signal: CanonicalSignal) -> bool:
        """
        Collect a single signal after validation.

        Returns:
            True if collected, False if invalid
        """
        # Validate
        errors = CanonicalSignalValidator.validate(signal)
        if errors:
            return False

        # Check for duplicate signal_id
        if signal.signal_id in self._signals:
            return False  # Duplicate, skip

        # Store
        self._signals[signal.signal_id] = signal

        # Add to group
        if signal.event_type not in self._groups:
            self._groups[signal.event_type] = SignalGroup(
                event_type=signal.event_type,
                domain=signal.domain,
            )
        self._groups[signal.event_type].add(signal)

        return True

    def collect_batch(self, signals: List[CanonicalSignal]) -> Tuple[int, int]:
        """
        Collect multiple signals.

        Returns:
            (collected_count, rejected_count)
        """
        collected = 0
        rejected = 0

        for signal in signals:
            if self.collect(signal):
                collected += 1
            else:
                rejected += 1

        return collected, rejected

    def validate_all(self) -> List[str]:
        """
        Validate all collected signals.

        Returns:
            List of error messages
        """
        return validate_canonical_signal_schema(self._signals)

    def deduplicate(self) -> int:
        """
        Remove duplicate signals (same event_type + direction).

        Returns:
            Number of duplicates removed
        """
        original_count = len(self._signals)

        # Group by (event_type, direction)
        seen: Set[Tuple[str, str]] = set()
        duplicates: List[str] = []

        for sid, signal in list(self._signals.items()):
            key = (signal.event_type, signal.direction.value)
            if key in seen:
                duplicates.append(sid)
            else:
                seen.add(key)

        # Remove duplicates
        for sid in duplicates:
            signal = self._signals.pop(sid)
            if signal.event_type in self._groups:
                group = self._groups[signal.event_type]
                group.signals = [s for s in group.signals if s.signal_id != sid]

        return original_count - len(self._signals)

    def get_by_event(self, event_type: str) -> List[CanonicalSignal]:
        """Get all signals for a specific event type."""
        if event_type not in self._groups:
            return []
        return self._groups[event_type].signals.copy()

    def get_by_domain(self, domain: Domain) -> List[CanonicalSignal]:
        """Get all signals for a specific domain."""
        result = []
        for group in self._groups.values():
            if group.domain == domain:
                result.extend(group.signals)
        return result

    def get_by_engine(self, engine: str) -> List[CanonicalSignal]:
        """Get all signals from a specific engine."""
        result = []
        for signal in self._signals.values():
            if signal.source_engine.value == engine:
                result.append(signal)
        return result

    def summary(self) -> Dict:
        """
        Get summary statistics.

        IMPORTANT: This does NOT produce Fortune Score.
        Only provides structural information for Phase 4.
        """
        return {
            'total_signals': len(self._signals),
            'total_groups': len(self._groups),
            'by_domain': {
                domain.value: sum(
                    1 for s in self._signals.values() if s.domain == domain
                )
                for domain in Domain
            },
            'by_engine': {
                engine.value: sum(
                    1 for s in self._signals.values() if s.source_engine == engine
                )
                for engine in [e for e in __import__('tongshu.signal.canonical_signal', fromlist=['SourceEngine']).SourceEngine]
            },
            'by_event_type': {
                et: len(group.signals)
                for et, group in self._groups.items()
            },
        }

    def export_for_phase4(self) -> List[Dict]:
        """
        Export signals in format ready for Phase 4 Temporal Convergence.

        Returns:
            List of signal dicts with normalized structure
        """
        return [
            {
                'signal_id': s.signal_id,
                'source_engine': s.source_engine.value,
                'event_type': s.event_type,
                'domain': s.domain.value,
                'direction': s.direction.value,
                'temporal_scope': s.temporal_scope.to_dict(),
                'evidence_refs': s.evidence_refs,
                'layer': s.layer.value,
            }
            for s in self._signals.values()
        ]
