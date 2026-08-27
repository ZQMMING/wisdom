"""
Phase 2 Contract Tests — Edge Cases and Boundary Conditions
"""
from __future__ import annotations

import pytest

from tongshu.spec.evidence_chain import (
    EvidenceLevel,
    ClaimType,
    Source,
    Passage,
    Claim,
    Evidence,
)
from tongshu.chain import EvidenceChainContext, ChainIntegrityError, ProvenanceBrokenError


class TestEdgeCases:
    def test_empty_chain_validates_cleanly(self):
        ctx = EvidenceChainContext()
        errors = ctx.validate_chain()
        assert errors == []

    def test_duplicate_source_rejected(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)
        with pytest.raises(ChainIntegrityError):
            ctx.add_source(source)

    def test_duplicate_passage_rejected(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)
        passage = Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        ctx.add_passage(passage)
        with pytest.raises(ChainIntegrityError):
            ctx.add_passage(passage)

    def test_multiple_claims_same_passage_allowed(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)
        passage = Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        ctx.add_passage(passage)

        # Multiple claims can reference same passage
        for i in range(3):
            claim = Claim(claim_id=f"C{i}", passage_id="P1", claim_text="test",
                          claim_type=ClaimType.DESCRIBE_STATE, evidence_level=EvidenceLevel.LEVEL_1,
                          created_by="HUMAN")
            ctx.add_claim(claim)

        assert len(ctx.claims) == 3

    def test_claim_with_different_creators(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)
        passage = Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        ctx.add_passage(passage)

        # HUMAN claim
        claim_h = Claim(claim_id="C_H", passage_id="P1", claim_text="test",
                        claim_type=ClaimType.DESCRIBE_STATE, evidence_level=EvidenceLevel.LEVEL_1,
                        created_by="HUMAN")
        ctx.add_claim(claim_h)

        # RULE_ENGINE claim
        claim_r = Claim(claim_id="C_R", passage_id="P1", claim_text="test",
                        claim_type=ClaimType.DESCRIBE_STATE, evidence_level=EvidenceLevel.LEVEL_1,
                        created_by="RULE_ENGINE")
        ctx.add_claim(claim_r)

        assert ctx.claims.has("C_H")
        assert ctx.claims.has("C_R")

    def test_trace_to_unknown_node_type_raises(self):
        ctx = EvidenceChainContext()
        with pytest.raises(ProvenanceBrokenError):
            ctx.trace_to_source("X", "UNKNOWN_TYPE")

    def test_evidence_references_missing_passage(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)

        claim = Claim(claim_id="C1", passage_id="P_MISSING", claim_text="test",
                      claim_type=ClaimType.DESCRIBE_STATE, evidence_level=EvidenceLevel.LEVEL_1,
                      created_by="HUMAN")
        with pytest.raises(ChainIntegrityError):
            ctx.add_claim(claim)

    def test_evidence_chain_depth_tracking(self):
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

        trace_e = ctx.trace_to_source("E1", "evidence")
        trace_c = ctx.trace_to_source("C1", "claim")
        trace_p = ctx.trace_to_source("P1", "passage")

        assert trace_e.depth >= trace_c.depth
        assert trace_c.depth >= trace_p.depth
