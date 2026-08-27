"""
Phase 2 Contract Tests — Complete Evidence Chain Integration
"""
from __future__ import annotations

import pytest

from tongshu.spec.evidence_chain import (
    EvidenceLevel,
    VerificationStatus,
    ClaimType,
    Source,
    Passage,
    Claim,
    ClaimDraft,
    Evidence,
)
from tongshu.chain import EvidenceChainContext, ChainIntegrityError


class TestCompleteChain:
    """End-to-end evidence chain construction and validation."""

    def test_build_valid_chain(self):
        ctx = EvidenceChainContext()

        # Step 1: Add Source
        source = Source(
            source_id="S001",
            source_type="CLASSICAL",
            title="易经·乾卦",
            edition="通行本",
            verified=True,
        )
        ctx.add_source(source)

        # Step 2: Add Passage
        passage = Passage(
            passage_id="P001",
            source_id="S001",
            text="元亨利贞",
            context="乾卦卦辞",
            evidence_level=EvidenceLevel.LEVEL_1,
            verified=True,
        )
        ctx.add_passage(passage)

        # Step 3: Add Claim
        claim = Claim(
            claim_id="C001",
            passage_id="P001",
            claim_text="乾卦象征天，具创始之力",
            claim_type=ClaimType.DESCRIBE_STATE,
            evidence_level=EvidenceLevel.LEVEL_1,
            created_by="HUMAN",
            verified=True,
        )
        ctx.add_claim(claim)

        # Step 4: Add Evidence
        evidence = Evidence(
            evidence_id="E001",
            claim_id="C001",
            evidence_level=EvidenceLevel.LEVEL_1,
            source_id="S001",
            passage_id="P001",
            verification_status=VerificationStatus.VERIFIED,
        )
        ctx.add_evidence(evidence)

        # Verify chain integrity
        errors = ctx.validate_chain()
        assert errors == [], f"Chain validation failed: {errors}"

        # Verify provenance
        assert ctx.verify_provenance("S001", "source") is True
        assert ctx.verify_provenance("P001", "passage") is True
        assert ctx.verify_provenance("C001", "claim") is True
        assert ctx.verify_provenance("E001", "evidence") is True

    def test_trace_full_chain(self):
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
            source_id="S1", passage_id="P1", verification_status=VerificationStatus.VERIFIED,
        )
        ctx.add_evidence(evidence)

        trace = ctx.trace_to_source("C1", "claim")
        assert trace.source_id == "S1"
        assert trace.depth >= 1
        assert "P1" in trace.passage_ids
        assert "C1" in trace.claim_ids

    def test_draft_promotion_flow(self):
        ctx = EvidenceChainContext()

        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)

        passage = Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        ctx.add_passage(passage)

        # LLM creates draft
        draft = ClaimDraft(
            draft_id="D001",
            passage_id="P1",
            claim_text="乾卦象征天",
            claim_type=ClaimType.DESCRIBE_STATE,
            created_by="LLM",
            review_status="APPROVED",
        )
        ctx.add_claim_draft(draft)
        assert ctx.claims.has_draft("D001")

        # Human promotes to formal claim
        claim = ctx.promote_draft("D001", "HUMAN")
        assert ctx.claims.has("CLM_D001")
        assert claim.created_by == "HUMAN"

    def test_llm_cannot_directly_create_claim(self):
        ctx = EvidenceChainContext()

        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)

        passage = Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        ctx.add_passage(passage)

        # LLM cannot create Claim directly
        bad_claim = Claim(
            claim_id="C_BAD",
            passage_id="P1",
            claim_text="test",
            claim_type=ClaimType.DESCRIBE_STATE,
            evidence_level=EvidenceLevel.LEVEL_1,
            created_by="LLM",
        )
        with pytest.raises(ChainIntegrityError):
            ctx.add_claim(bad_claim)
        assert not ctx.claims.has("C_BAD")

    def test_multiple_sources_and_passages(self):
        ctx = EvidenceChainContext()

        # Add two independent sources
        for i in range(2):
            source = Source(source_id=f"S{i}", source_type="CLASSICAL", title=f"T{i}", edition="E")
            ctx.add_source(source)
            passage = Passage(passage_id=f"P{i}", source_id=f"S{i}", text="t", evidence_level=EvidenceLevel.LEVEL_1)
            ctx.add_passage(passage)

        assert len(ctx.sources) == 2
        assert len(ctx.passages) == 2
        assert ctx.validate_chain() == []

    def test_level5_evidence_not_formal(self):
        """LEVEL_5 is interpretive supplement only, never formal evidence."""
        assert EvidenceLevel.LEVEL_5 not in EvidenceLevel.formal_levels()
        assert not EvidenceLevel.LEVEL_5.is_formal()

    def test_formal_levels_are_level_1_to_4(self):
        formal = EvidenceLevel.formal_levels()
        assert len(formal) == 4
        assert EvidenceLevel.LEVEL_1 in formal
        assert EvidenceLevel.LEVEL_2 in formal
        assert EvidenceLevel.LEVEL_3 in formal
        assert EvidenceLevel.LEVEL_4 in formal
        assert EvidenceLevel.LEVEL_5 not in formal
