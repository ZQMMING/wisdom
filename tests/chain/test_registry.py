"""
Phase 2 Contract Tests — Registry Layers
"""
from __future__ import annotations

import pytest

from tongshu.spec.evidence_chain import (
    EvidenceLevel,
    ClaimType,
    Source,
    Passage,
    Claim,
    ClaimDraft,
    Evidence,
)
from tongshu.chain import (
    ChainIntegrityError,
    CreatorViolationError,
    EvidenceChainContext,
    SourceRegistry,
    PassageRegistry,
    EvidenceRegistry,
    ClaimRegistry,
)


class TestSourceRegistry:
    def test_add_and_get(self):
        reg = SourceRegistry()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        reg.add(source)
        assert reg.has("S1")
        assert reg.get("S1") == source

    def test_duplicate_raises(self):
        reg = SourceRegistry()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        reg.add(source)
        with pytest.raises(ChainIntegrityError):
            reg.add(source)

    def test_missing_returns_none(self):
        reg = SourceRegistry()
        assert reg.get("S_NONEXIST") is None


class TestPassageRegistry:
    def test_add_with_valid_source(self):
        sources = SourceRegistry()
        sources.add(Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E"))
        reg = PassageRegistry(sources)

        passage = Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        reg.add(passage)
        assert reg.has("P1")

    def test_add_missing_source_raises(self):
        reg = PassageRegistry(SourceRegistry())
        passage = Passage(passage_id="P1", source_id="S_MISSING", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        with pytest.raises(ChainIntegrityError):
            reg.add(passage)

    def test_add_level5_raises(self):
        sources = SourceRegistry()
        sources.add(Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E"))
        reg = PassageRegistry(sources)

        passage = Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_5)
        with pytest.raises(ChainIntegrityError):
            reg.add(passage)


class TestEvidenceRegistry:
    def test_add_with_valid_refs(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)
        passage = Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        ctx.add_passage(passage)
        claim = Claim(claim_id="C1", passage_id="P1", claim_text="test",
                      claim_type=ClaimType.DESCRIBE_STATE, evidence_level=EvidenceLevel.LEVEL_1,
                      created_by="HUMAN")
        ctx.add_claim(claim)

        evidence = Evidence(
            evidence_id="E1", claim_id="C1", evidence_level=EvidenceLevel.LEVEL_1,
            source_id="S1", passage_id="P1", verification_status=None,
        )
        ctx.add_evidence(evidence)
        assert ctx.evidences.has("E1")

    def test_add_missing_claim_raises(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)

        evidence = Evidence(
            evidence_id="E_BAD", claim_id="C_MISSING", evidence_level=EvidenceLevel.LEVEL_1,
            source_id="S1", passage_id="P1",
        )
        with pytest.raises(ChainIntegrityError):
            ctx.add_evidence(evidence)


class TestClaimRegistry:
    def test_add_draft_from_llm(self):
        sources = SourceRegistry()
        sources.add(Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E"))
        passages = PassageRegistry(sources)
        passages.add(Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1))
        evidences = EvidenceRegistry(sources, type('obj', (object,), {'has': lambda self, x: False})())
        claims = ClaimRegistry(passages, evidences)

        draft = ClaimDraft(draft_id="D1", passage_id="P1", claim_text="t",
                          claim_type=ClaimType.DESCRIBE_STATE, created_by="LLM")
        claims.add_draft(draft)
        assert claims.has_draft("D1")

    def test_promote_draft_requires_approval(self):
        sources = SourceRegistry()
        sources.add(Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E"))
        passages = PassageRegistry(sources)
        passages.add(Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1))
        evidences = EvidenceRegistry(sources, type('obj', (object,), {'has': lambda self, x: False})())
        claims = ClaimRegistry(passages, evidences)

        draft = ClaimDraft(draft_id="D1", passage_id="P1", claim_text="t",
                          claim_type=ClaimType.DESCRIBE_STATE, created_by="LLM",
                          review_status="PENDING_REVIEW")
        claims.add_draft(draft)

        with pytest.raises(ChainIntegrityError):
            claims.promote_draft("D1", "HUMAN")

    def test_promote_draft_requires_authorized_creator(self):
        sources = SourceRegistry()
        sources.add(Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E"))
        passages = PassageRegistry(sources)
        passages.add(Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1))
        evidences = EvidenceRegistry(sources, type('obj', (object,), {'has': lambda self, x: False})())
        claims = ClaimRegistry(passages, evidences)

        draft = ClaimDraft(draft_id="D1", passage_id="P1", claim_text="t",
                          claim_type=ClaimType.DESCRIBE_STATE, created_by="LLM",
                          review_status="APPROVED")
        claims.add_draft(draft)

        with pytest.raises(CreatorViolationError):
            claims.promote_draft("D1", "LLM")


class TestHasDraft:
    """Helper method test."""
    def test_has_draft_method_exists(self):
        sources = SourceRegistry()
        sources.add(Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E"))
        passages = PassageRegistry(sources)
        evidences = EvidenceRegistry(sources, type('obj', (object,), {'has': lambda self, x: False})())
        claims = ClaimRegistry(passages, evidences)
        assert hasattr(claims, 'has_draft')
