"""
Evidence Chain Exceptions — Phase 2
"""
from __future__ import annotations

from typing import List, Optional


class ChainIntegrityError(Exception):
    """Raised when evidence chain integrity is violated."""

    def __init__(self, message: str, broken_links: Optional[List[str]] = None):
        super().__init__(message)
        self.broken_links = broken_links or []


class ProvenanceBrokenError(ChainIntegrityError):
    """Raised when provenance trace cannot be completed."""


class OrphanedNodeError(ChainIntegrityError):
    """Raised when a node references a non-existent parent."""


class LevelViolationError(ChainIntegrityError):
    """Raised when LEVEL_5 enters formal chain."""


class CreatorViolationError(ChainIntegrityError):
    """Raised when Claim is created by unauthorized creator."""
