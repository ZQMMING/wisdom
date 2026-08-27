"""
Evidence Chain Registry Layer — Phase 2
Registry classes for Source, Passage, Evidence, Claim nodes.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set

from tongshu.spec.evidence_chain import (
    EvidenceLevel,
    ClaimType,
    ALLOWED_CLAIM_CREATORS,
    ALLOWED_CLAIM_DRAFT_CREATORS,
    Source,
    Passage,
    Claim,
    ClaimDraft,
    Evidence,
    validate_chain as validate_chain_schema,
)
from .exceptions import (
    ChainIntegrityError,
    ProvenanceBrokenError,
    OrphanedNodeError,
    LevelViolationError,
    CreatorViolationError,
)


class SourceRegistry:
    """Registry of canonical evidence sources."""

    def __init__(self) -> None:
        self._sources: Dict[str, Source] = {}

    def add(self, source: Source) -> None:
        if source.source_id in self._sources:
            raise ChainIntegrityError(
                f"Duplicate source_id: {source.source_id}"
            )
        self._sources[source.source_id] = source

    def get(self, source_id: str) -> Optional[Source]:
        return self._sources.get(source_id)

    def has(self, source_id: str) -> bool:
        return source_id in self._sources

    def all_ids(self) -> Set[str]:
        return set(self._sources.keys())

    def __len__(self) -> int:
        return len(self._sources)


class PassageRegistry:
    """Registry of passages, each must reference a valid Source."""

    def __init__(self, sources: SourceRegistry) -> None:
        self._sources = sources
        self._passages: Dict[str, Passage] = {}

    def add(self, passage: Passage) -> None:
        errors: List[str] = []

        if passage.passage_id in self._passages:
            errors.append(f"Duplicate passage_id: {passage.passage_id}")

        if not self._sources.has(passage.source_id):
            errors.append(
                f"Passage {passage.passage_id} references missing Source {passage.source_id}"
            )

        for err in passage.validate_level():
            errors.append(f"Passage {passage.passage_id}: {err}")

        if errors:
            raise ChainIntegrityError(
                f"Invalid Passage: {passage.passage_id}",
                broken_links=errors,
            )

        self._passages[passage.passage_id] = passage

    def get(self, passage_id: str) -> Optional[Passage]:
        return self._passages.get(passage_id)

    def has(self, passage_id: str) -> bool:
        return passage_id in self._passages

    def all_ids(self) -> Set[str]:
        return set(self._passages.keys())

    def __len__(self) -> int:
        return len(self._passages)


class EvidenceRegistry:
    """Registry of Evidence nodes, each must reference valid Claim and Source."""

    def __init__(
        self,
        sources: SourceRegistry,
        claims_ref,  # ClaimRegistry or EvidenceChainContext
    ) -> None:
        self._sources = sources
        self._claims_ref = claims_ref
        self._evidences: Dict[str, Evidence] = {}

    def add(self, evidence: Evidence) -> None:
        errors: List[str] = []

        if evidence.evidence_id in self._evidences:
            errors.append(f"Duplicate evidence_id: {evidence.evidence_id}")

        # Support both ClaimRegistry and EvidenceChainContext
        claims_obj = getattr(self._claims_ref, 'claims', self._claims_ref)
        claims_has = getattr(claims_obj, 'has', None)
        if claims_has is None or not claims_has(evidence.claim_id):
            errors.append(
                f"Evidence {evidence.evidence_id} references missing Claim {evidence.claim_id}"
            )

        if not self._sources.has(evidence.source_id):
            errors.append(
                f"Evidence {evidence.evidence_id} references missing Source {evidence.source_id}"
            )

        for err in evidence.validate_level():
            errors.append(f"Evidence {evidence.evidence_id}: {err}")

        if errors:
            raise ChainIntegrityError(
                f"Invalid Evidence: {evidence.evidence_id}",
                broken_links=errors,
            )

        self._evidences[evidence.evidence_id] = evidence

    def get(self, evidence_id: str) -> Optional[Evidence]:
        return self._evidences.get(evidence_id)

    def has(self, evidence_id: str) -> bool:
        return evidence_id in self._evidences

    def by_claim(self, claim_id: str) -> List[Evidence]:
        return [e for e in self._evidences.values() if e.claim_id == claim_id]

    def all_ids(self) -> Set[str]:
        return set(self._evidences.keys())

    def __len__(self) -> int:
        return len(self._evidences)


class ClaimRegistry:
    """Registry of formal Claims, creator-enforced."""

    def __init__(
        self,
        passages: PassageRegistry,
        evidences: EvidenceRegistry,
    ) -> None:
        self._passages = passages
        self._evidences = evidences
        self._claims: Dict[str, Claim] = {}
        self._drafts: Dict[str, ClaimDraft] = {}

    def add_draft(self, draft: ClaimDraft) -> None:
        """LLM can create drafts — they don't enter formal chain yet."""
        errors = draft.validate_creator()
        if errors:
            raise ChainIntegrityError(
                f"Invalid ClaimDraft: {draft.draft_id}",
                broken_links=errors,
            )
        self._drafts[draft.draft_id] = draft

    def add(self, claim: Claim) -> None:
        """Only HUMAN or RULE_ENGINE can create formal Claims."""
        errors: List[str] = []

        if claim.claim_id in self._claims:
            errors.append(f"Duplicate claim_id: {claim.claim_id}")

        if claim.created_by not in ALLOWED_CLAIM_CREATORS:
            errors.append(
                f"Claim {claim.claim_id} created_by={claim.created_by!r} "
                f"not in {ALLOWED_CLAIM_CREATORS}"
            )

        if not self._passages.has(claim.passage_id):
            errors.append(
                f"Claim {claim.claim_id} references missing Passage {claim.passage_id}"
            )

        for err in claim.validate():
            errors.append(f"Claim {claim.claim_id}: {err}")

        if errors:
            raise ChainIntegrityError(
                f"Invalid Claim: {claim.claim_id}",
                broken_links=errors,
            )

        self._claims[claim.claim_id] = claim

    def promote_draft(self, draft_id: str, creator: str) -> Claim:
        """Convert approved draft to formal Claim (creator must be authorized)."""
        if draft_id not in self._drafts:
            raise ChainIntegrityError(f"Draft {draft_id} not found")

        draft = self._drafts[draft_id]
        if draft.review_status != "APPROVED":
            raise ChainIntegrityError(
                f"Draft {draft_id} not APPROVED, status={draft.review_status}"
            )

        if creator not in ALLOWED_CLAIM_CREATORS:
            raise CreatorViolationError(
                f"Creator {creator!r} cannot promote draft to Claim"
            )

        claim = Claim(
            claim_id=f"CLM_{draft_id}",
            passage_id=draft.passage_id,
            claim_text=draft.claim_text,
            claim_type=draft.claim_type,
            evidence_level=EvidenceLevel.LEVEL_1,
            created_by=creator,
            created_at=datetime.utcnow().isoformat(),
            verified=False,
            review_status="APPROVED",
        )

        self.add(claim)
        return claim

    def get(self, claim_id: str) -> Optional[Claim]:
        return self._claims.get(claim_id)

    def has(self, claim_id: str) -> bool:
        return claim_id in self._claims

    def all_ids(self) -> Set[str]:
        return set(self._claims.keys())

    def has_draft(self, draft_id: str) -> bool:
        return draft_id in self._drafts

    def __len__(self) -> int:
        return len(self._claims)
