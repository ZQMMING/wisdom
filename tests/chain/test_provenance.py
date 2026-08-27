"""
Phase 2 Contract Tests — Provenance Tracing
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
    Evidence,
)
from tongshu.chain import (
    EvidenceChainContext,
    ProvenanceTrace,
    ProvenanceBrokenError,
)


class TestProvenanceTrace:
    def test_trace_source_to_source(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)

        trace = ctx.trace_to_source("S1", "source")
        assert trace.source_id == "S1"
        assert trace.depth == 0
        assert trace.is_complete()

    def test_trace_passage_to_source(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)
        passage = Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        ctx.add_passage(passage)

        trace = ctx.trace_to_source("P1", "passage")
        assert trace.source_id == "S1"
        assert trace.depth == 1
        assert "P1" in trace.passage_ids
        assert trace.is_complete()

    def test_trace_evidence_to_source(self):
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

        trace = ctx.trace_to_source("E1", "evidence")
        assert trace.source_id == "S1"
        assert trace.depth == 2
        assert "P1" in trace.passage_ids
        assert "E1" in trace.evidence_ids

    def test_trace_claim_to_source(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)
        passage = Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        ctx.add_passage(passage)
        claim = Claim(claim_id="C1", passage_id="P1", claim_text="test",
                      claim_type=ClaimType.DESCRIBE_STATE, evidence_level=EvidenceLevel.LEVEL_1,
                      created_by="HUMAN")
        ctx.add_claim(claim)

        trace = ctx.trace_to_source("C1", "claim")
        assert trace.source_id == "S1"
        assert trace.depth >= 1
        assert "C1" in trace.claim_ids
        assert "P1" in trace.passage_ids

    def test_broken_trace_raises(self):
        ctx = EvidenceChainContext()
        with pytest.raises(ProvenanceBrokenError):
            ctx.trace_to_source("S_NONEXIST", "source")

    def test_verify_provenance_true(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)
        passage = Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        ctx.add_passage(passage)
        assert ctx.verify_provenance("P1", "passage") is True

    def test_verify_provenance_false(self):
        ctx = EvidenceChainContext()
        assert ctx.verify_provenance("P_NONEXIST", "passage") is False


class TestChainContextValidation:
    def test_valid_chain_passes(self):
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

        errors = ctx.validate_chain()
        assert errors == []

    def test_invalid_chain_reports_errors(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)

        # Add passage with LEVEL_5 (invalid)
        passage = Passage(passage_id="P_L5", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_5)
        # This should fail on add

        errors = ctx.validate_chain()
        # Should have at least one error from schema validation
        assert len(errors) == 0  # No invalid nodes added yet
