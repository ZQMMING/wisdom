"""
P1.3 — Cross-Domain Package

跨体系证据编排层。
遵循 V13 §二：互补不比较，不投票、不评分、不多数决、不加权。
"""
from __future__ import annotations

from .orchestrator import CrossDomainOrchestrator
from .result import (
    CrossDomainResult,
    EngineEvidenceSet,
    EngineAssertionSet,
    DomainSemanticIndex,
    MultiDomainSemanticCoverage,
)

__all__ = [
    "CrossDomainOrchestrator",
    "CrossDomainResult",
    "EngineEvidenceSet",
    "EngineAssertionSet",
    "DomainSemanticIndex",
    "MultiDomainSemanticCoverage",
]
