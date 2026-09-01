"""DEPRECATED (P1.4): Cross Analysis states.

This module has been moved to archive/spec/cross_states.py.
Kept as a thin stub for backward-compatible test imports.
Production code must NOT import this module.
"""
from __future__ import annotations

# DEPRECATED: See archive/spec/cross_states.py for original
CROSS_STATES = frozenset({"ALIGNED", "PARTIAL", "INSUFFICIENT"})

REASON_CODES = frozenset({
    "CROSS_TYPE_PARTIAL",
    "SHARED_SUPERTYPE",
    "OPPOSITE_DIRECTION",
    "SAME_SIGNAL_AGREE",
    "EVIDENCE_MISSING",
    "FORBIDDEN_EXCLUDED",
    "INSUFFICIENT_RULES",
    "RULE_DEPRECATED",
})
