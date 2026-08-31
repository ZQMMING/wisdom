"""
P1.3 - Cross-Domain Result Models

Design principles:
  1. EvidenceCoverage is structural organization only, produces no Judgment
  2. Each engine produces Assertion independently, no cross-engine direction comparison
  3. Maintain system Provenance (by_engine separation)
  4. Coverage indexed by domain x semantic x engine
  5. Follow V13 Section 2: complementary not comparative
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class EngineEvidenceSet:
    """Single engine evidence set (maintains system Provenance)."""
    engine: str
    evidence_ids: List[str] = field(default_factory=list)
    assertion_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "engine": self.engine,
            "evidence_ids": list(self.evidence_ids),
            "assertion_ids": list(self.assertion_ids),
        }


@dataclass(frozen=True)
class EngineAssertionSet:
    """Assertions for a single engine at a specific domain x semantic."""
    engine: str
    assertion_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "engine": self.engine,
            "assertion_ids": list(self.assertion_ids),
        }


@dataclass(frozen=True)
class DomainSemanticIndex:
    """Cross-index at domain x semantic: which engines have Assertions here."""
    domain: str
    semantic: str
    by_engine: Dict[str, EngineAssertionSet] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "semantic": self.semantic,
            "by_engine": {k: v.to_dict() for k, v in self.by_engine.items()},
        }


@dataclass(frozen=True)
class MultiDomainSemanticCoverage:
    """True cross-system Coverage index.

    Structure:
        coverage
        ├── domain A
        │   ├── semantic X
        │   │   ├── ZI_PING: [assertion_ids]
        │   │   └── ZI_WEI: [assertion_ids]
        │   └── semantic Y
        │       └── ZI_PING: [assertion_ids]
        └── domain B
            └── ...

    Forbidden:
    - direction / polarity / strength / confidence / score / weight
    - CONFLICTED / ALIGNED / PARTIAL states
    - vote / compare / rank logic
    """
    # domain -> DomainSemanticIndex
    coverage: Dict[str, Dict[str, DomainSemanticIndex]] = field(default_factory=dict)

    @property
    def domains(self) -> List[str]:
        return sorted(self.coverage.keys())

    @property
    def semantics(self) -> List[str]:
        all_sem = set()
        for domain_index in self.coverage.values():
            all_sem.update(domain_index.keys())
        return sorted(all_sem)

    @property
    def engines(self) -> List[str]:
        all_eng = set()
        for domain_index in self.coverage.values():
            for ds_index in domain_index.values():
                all_eng.update(ds_index.by_engine.keys())
        return sorted(all_eng)

    @property
    def total_assertions(self) -> int:
        count = 0
        for domain_index in self.coverage.values():
            for ds_index in domain_index.values():
                for eng_set in ds_index.by_engine.values():
                    count += len(eng_set.assertion_ids)
        return count

    def get_assertion_ids(self, domain: str, semantic: str) -> List[str]:
        """Get all Assertion IDs at a specific domain x semantic (merged across engines)."""
        if domain not in self.coverage:
            return []
        if semantic not in self.coverage[domain]:
            return []
        ids: List[str] = []
        for eng_set in self.coverage[domain][semantic].by_engine.values():
            ids.extend(eng_set.assertion_ids)
        return ids

    def to_dict(self) -> dict:
        return {
            "coverage": {
                domain: {
                    semantic: ds.to_dict()
                    for semantic, ds in domain_index.items()
                }
                for domain, domain_index in self.coverage.items()
            },
            "domains": self.domains,
            "semantics": self.semantics,
            "engines": self.engines,
            "total_assertions": self.total_assertions,
        }


@dataclass(frozen=True)
class CrossDomainResult:
    """Cross-domain orchestration result (Structured Observation).

    Structure:
        CrossDomainResult
        ├── by_engine: {engine_name: EngineEvidenceSet}
        └── coverage: MultiDomainSemanticCoverage
            └── domain x semantic x engine -> assertion_ids

    Forbidden:
    - direction / polarity / strength / confidence / score / weight fields
    - CONFLICTED / ALIGNED / PARTIAL states
    - vote / compare / rank logic
    - evidence_count global summary (use coverage.total_assertions instead)
    """
    case_id: str
    temporal_scope: str
    by_engine: Dict[str, "EngineEvidenceSet"]
    coverage: MultiDomainSemanticCoverage

    def verify_no_cross_comparison(self) -> List[str]:
        """Verify: no cross-system direction comparison logic was called."""
        errors: List[str] = []
        forbidden_attrs = {"direction", "polarity", "strength", "confidence", "score", "weight"}
        for attr in forbidden_attrs:
            if hasattr(self, attr):
                errors.append(f"CrossDomainResult has forbidden attribute: {attr}")
        return errors

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "temporal_scope": self.temporal_scope,
            "by_engine": {k: v.to_dict() for k, v in self.by_engine.items()},
            "coverage": self.coverage.to_dict(),
        }
