"""
Evidence Chain Implementation — Phase 2

Runtime layer for evidence chain infrastructure.
Builds on spec/evidence_chain.py Schema 7.
"""
from __future__ import annotations

from .exceptions import (
    ChainIntegrityError,
    ProvenanceBrokenError,
    OrphanedNodeError,
    LevelViolationError,
    CreatorViolationError,
)
from .provenance import ProvenanceTrace
from .registry import (
    SourceRegistry,
    PassageRegistry,
    EvidenceRegistry,
    ClaimRegistry,
)
from .chain_context import EvidenceChainContext


def validate_chain(sources, passages, claims, evidences):
    """Wrapper for spec.validate_chain."""
    from tongshu.spec.evidence_chain import validate_chain as vc
    return vc(sources, passages, claims, evidences)

__all__ = [
    # Exceptions
    "ChainIntegrityError",
    "ProvenanceBrokenError",
    "OrphanedNodeError",
    "LevelViolationError",
    "CreatorViolationError",
    # Types
    "ProvenanceTrace",
    # Registries
    "SourceRegistry",
    "PassageRegistry",
    "EvidenceRegistry",
    "ClaimRegistry",
    # Context
    "EvidenceChainContext",
    "validate_chain",
]
