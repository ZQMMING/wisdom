"""
Provenance Trace — Phase 2
Immutable trace from any node back to its root Source.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProvenanceTrace:
    """Immutable trace from any node back to its root Source."""

    source_id: str
    passage_ids: list = field(default_factory=list)
    evidence_ids: list = field(default_factory=list)
    claim_ids: list = field(default_factory=list)
    depth: int = 0  # Number of hops from Source

    def is_complete(self) -> bool:
        """A complete trace must reach a verified Source."""
        return bool(self.source_id)
