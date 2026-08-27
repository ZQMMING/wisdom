"""
Evidence Chain Context — Phase 2
Unified context with full provenance tracking and chain integrity validation.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from tongshu.spec.evidence_chain import (
    EvidenceLevel,
    Source,
    Passage,
    Claim,
    ClaimDraft,
    Evidence,
)
from .provenance import ProvenanceTrace
from .exceptions import (
    ChainIntegrityError,
    ProvenanceBrokenError,
)
from .registry import (
    SourceRegistry,
    PassageRegistry,
    EvidenceRegistry,
    ClaimRegistry,
)


class EvidenceChainContext:
    """
    Unified evidence chain context with full provenance tracking.

    Maintains:
      - Source → Passage → Evidence → Claim hierarchy
      - Provenance traces for all nodes
      - Chain integrity validation
    """

    def __init__(self) -> None:
        self.sources = SourceRegistry()
        self.passages = PassageRegistry(self.sources)
        # Use placeholder for circular dependency, will be replaced
        from .registry import EvidenceRegistry as _ER
        self.evidences = _ER(self.sources, self)  # self here will have claims set below
        self.claims = ClaimRegistry(self.passages, self.evidences)

    # ─── Provenance Tracing ───────────────────────────────────────────────────

    def trace_to_source(self, node_id: str, node_type: str) -> ProvenanceTrace:
        """
        Trace any node back to its root Source.

        Args:
            node_id: ID of the node to trace
            node_type: 'source' | 'passage' | 'evidence' | 'claim'

        Returns:
            ProvenanceTrace with full path

        Raises:
            ProvenanceBrokenError: if trace cannot be completed
        """
        if node_type == "source":
            if not self.sources.has(node_id):
                raise ProvenanceBrokenError(f"Source {node_id} not found")
            return ProvenanceTrace(source_id=node_id, depth=0)

        if node_type == "passage":
            passage = self.passages.get(node_id)
            if passage is None:
                raise ProvenanceBrokenError(f"Passage {node_id} not found")
            trace = self.trace_to_source(passage.source_id, "source")
            return ProvenanceTrace(
                source_id=trace.source_id,
                passage_ids=[node_id],
                depth=trace.depth + 1,
            )

        if node_type == "evidence":
            evidence = self.evidences.get(node_id)
            if evidence is None:
                raise ProvenanceBrokenError(f"Evidence {node_id} not found")
            passage_trace = self.trace_to_source(evidence.passage_id, "passage")
            return ProvenanceTrace(
                source_id=passage_trace.source_id,
                passage_ids=passage_trace.passage_ids + [evidence.passage_id],
                evidence_ids=[node_id],
                depth=passage_trace.depth + 1,
            )

        if node_type == "claim":
            claim = self.claims.get(node_id)
            if claim is None:
                raise ProvenanceBrokenError(f"Claim {node_id} not found")
            passage_trace = self.trace_to_source(claim.passage_id, "passage")
            return ProvenanceTrace(
                source_id=passage_trace.source_id,
                passage_ids=passage_trace.passage_ids + [claim.passage_id],
                claim_ids=[node_id],
                depth=passage_trace.depth + 1,
            )

        raise ProvenanceBrokenError(f"Unknown node_type: {node_type}")

    def verify_provenance(self, node_id: str, node_type: str) -> bool:
        """Check if a node has complete provenance back to Source."""
        try:
            trace = self.trace_to_source(node_id, node_type)
            return trace.is_complete()
        except ProvenanceBrokenError:
            return False

    # ─── Chain Integrity Validation ────────────────────────────────────────────

    def validate_chain(self) -> List[str]:
        """
        Full chain integrity validation.

        Returns:
            List of error messages (empty = chain is valid)
        """
        errors: List[str] = []

        # Schema-level validation
        from tongshu.spec.evidence_chain import validate_chain as vc
        schema_errors = vc(
            {s.source_id: s for s in self.sources._sources.values()},
            {p.passage_id: p for p in self.passages._passages.values()},
            {c.claim_id: c for c in self.claims._claims.values()},
            {e.evidence_id: e for e in self.evidences._evidences.values()},
        )
        errors.extend(schema_errors)

        # Provenance completeness check
        for pid, p in self.passages._passages.items():
            if not self.sources.has(p.source_id):
                errors.append(f"Orphaned Passage {pid}: missing Source {p.source_id}")

        for eid, e in self.evidences._evidences.items():
            claims_has = getattr(self.claims, 'has', None)
            if claims_has is None or not claims_has(e.claim_id):
                errors.append(f"Orphaned Evidence {eid}: missing Claim {e.claim_id}")
            if not self.sources.has(e.source_id):
                errors.append(f"Orphaned Evidence {eid}: missing Source {e.source_id}")

        for cid, c in self.claims._claims.items():
            if not self.passages.has(c.passage_id):
                errors.append(f"Orphaned Claim {cid}: missing Passage {c.passage_id}")

        # LEVEL_5 exclusion check
        for pid, p in self.passages._passages.items():
            if p.evidence_level == EvidenceLevel.LEVEL_5:
                errors.append(f"LEVEL_5 found in formal Passage {pid}")

        for eid, e in self.evidences._evidences.items():
            if e.evidence_level == EvidenceLevel.LEVEL_5:
                errors.append(f"LEVEL_5 found in formal Evidence {eid}")

        for cid, c in self.claims._claims.items():
            if c.evidence_level == EvidenceLevel.LEVEL_5:
                errors.append(f"LEVEL_5 found in formal Claim {cid}")

        return errors

    # ─── Node Addition ────────────────────────────────────────────────────────

    def add_source(self, source: Source) -> None:
        self.sources.add(source)

    def add_passage(self, passage: Passage) -> None:
        self.passages.add(passage)

    def add_evidence(self, evidence: Evidence) -> None:
        self.evidences.add(evidence)

    def add_claim(self, claim: Claim) -> None:
        self.claims.add(claim)

    def add_claim_draft(self, draft: ClaimDraft) -> None:
        self.claims.add_draft(draft)

    def promote_draft(self, draft_id: str, creator: str) -> Claim:
        return self.claims.promote_draft(draft_id, creator)



