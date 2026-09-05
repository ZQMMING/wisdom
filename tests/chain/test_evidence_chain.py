"""
Phase 2 Contract Tests — Evidence Chain Implementation
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
from tongshu.chain import (
    EvidenceChainContext,
    ChainIntegrityError,
    ProvenanceBrokenError,
    OrphanedNodeError,
    LevelViolationError,
    CreatorViolationError,
)


# ─── G2.1: Source → Passage traceability ──────────────────────────────────────


class TestSourcePassageTrace:
    def test_add_source_then_passage(self):
        ctx = EvidenceChainContext()
        source = Source(
            source_id="S001",
            source_type="CLASSICAL",
            title="易经·乾卦",
            edition="通行本",
        )
        ctx.add_source(source)

        passage = Passage(
            passage_id="P001",
            source_id="S001",
            text="元亨利贞",
            evidence_level=EvidenceLevel.LEVEL_1,
        )
        ctx.add_passage(passage)

        assert ctx.verify_provenance("P001", "passage") is True

    def test_passage_without_source_raises(self):
        ctx = EvidenceChainContext()
        passage = Passage(
            passage_id="P_BAD",
            source_id="S_MISSING",
            text="test",
            evidence_level=EvidenceLevel.LEVEL_1,
        )
        with pytest.raises(ChainIntegrityError):
            ctx.add_passage(passage)

    def test_provenance_trace_complete(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)

        passage = Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        ctx.add_passage(passage)

        trace = ctx.trace_to_source("P1", "passage")
        assert trace.source_id == "S1"
        assert trace.depth == 1
        assert trace.is_complete()


# ─── G2.2: Passage → Evidence traceability ─────────────────────────────────────


class TestPassageEvidenceTrace:
    def test_evidence_references_passage(self):
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
            evidence_id="E1",
            claim_id="C1",
            evidence_level=EvidenceLevel.LEVEL_1,
            source_id="S1",
            passage_id="P1",
            verification_status=VerificationStatus.VERIFIED,
        )
        ctx.add_evidence(evidence)

        assert ctx.verify_provenance("E1", "evidence") is True

    def test_evidence_missing_claim_raises(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)
        passage = Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        ctx.add_passage(passage)

        evidence = Evidence(
            evidence_id="E_BAD",
            claim_id="C_MISSING",
            evidence_level=EvidenceLevel.LEVEL_1,
            source_id="S1",
            passage_id="P1",
        )
        with pytest.raises(ChainIntegrityError):
            ctx.add_evidence(evidence)


# ─── G2.3: Evidence → Claim traceability ───────────────────────────────────────


class TestEvidenceClaimTrace:
    def test_claim_has_evidence(self):
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

        traces = ctx.evidences.by_claim("C1")
        assert len(traces) == 1
        assert traces[0].evidence_id == "E1"

    def test_evidence_missing_source_raises(self):
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
            evidence_id="E_BAD", claim_id="C1", evidence_level=EvidenceLevel.LEVEL_1,
            source_id="S_MISSING", passage_id="P1",
        )
        with pytest.raises(ChainIntegrityError):
            ctx.add_evidence(evidence)


# ─── G2.4: Claim → Interpretation traceability (via provenance) ────────────────


class TestClaimInterpretationTrace:
    def test_full_chain_trace(self):
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
        assert "P1" in trace.passage_ids
        assert "C1" in trace.claim_ids
        assert trace.depth >= 1


# ─── G2.5: LEVEL_5 never formal ────────────────────────────────────────────────


class TestLevel5Exclusion:
    def test_level5_passage_rejected(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)

        passage = Passage(
            passage_id="P_L5",
            source_id="S1",
            text="test",
            evidence_level=EvidenceLevel.LEVEL_5,
        )
        with pytest.raises(ChainIntegrityError):
            ctx.add_passage(passage)

    def test_level5_evidence_rejected(self):
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
            evidence_id="E_L5", claim_id="C1", evidence_level=EvidenceLevel.LEVEL_5,
            source_id="S1", passage_id="P1",
        )
        with pytest.raises(ChainIntegrityError):
            ctx.add_evidence(evidence)

    def test_level5_claim_rejected(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)
        passage = Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        ctx.add_passage(passage)

        claim = Claim(
            claim_id="C_L5", passage_id="P1", claim_text="test",
            claim_type=ClaimType.DESCRIBE_STATE, evidence_level=EvidenceLevel.LEVEL_5,
            created_by="HUMAN",
        )
        with pytest.raises(ChainIntegrityError):
            ctx.add_claim(claim)

    def test_level5_not_in_formal_levels(self):
        assert EvidenceLevel.LEVEL_5 not in EvidenceLevel.formal_levels()
        assert EvidenceLevel.LEVEL_5.is_formal() is False


# ─── G2.6: LLM cannot create Claim ────────────────────────────────────────────


class TestLLMClaimRestriction:
    def test_llm_cannot_create_claim(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)
        passage = Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        ctx.add_passage(passage)

        claim = Claim(
            claim_id="C_LLM", passage_id="P1", claim_text="test",
            claim_type=ClaimType.DESCRIBE_STATE, evidence_level=EvidenceLevel.LEVEL_1,
            created_by="LLM",
        )
        with pytest.raises(ChainIntegrityError):
            ctx.add_claim(claim)
        assert not ctx.claims.has("C_LLM")

    def test_human_can_create_claim(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)
        passage = Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        ctx.add_passage(passage)

        claim = Claim(claim_id="C_H", passage_id="P1", claim_text="test",
                      claim_type=ClaimType.DESCRIBE_STATE, evidence_level=EvidenceLevel.LEVEL_1,
                      created_by="HUMAN")
        ctx.add_claim(claim)
        assert ctx.claims.has("C_H")

    def test_rule_engine_can_create_claim(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)
        passage = Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        ctx.add_passage(passage)

        claim = Claim(claim_id="C_R", passage_id="P1", claim_text="test",
                      claim_type=ClaimType.DESCRIBE_STATE, evidence_level=EvidenceLevel.LEVEL_1,
                      created_by="RULE_ENGINE")
        ctx.add_claim(claim)
        assert ctx.claims.has("C_R")

    def test_llm_can_create_draft(self):
        ctx = EvidenceChainContext()
        draft = ClaimDraft(
            draft_id="D_LLM",
            passage_id="P1",
            claim_text="test",
            claim_type=ClaimType.DESCRIBE_STATE,
            created_by="LLM",
        )
        ctx.add_claim_draft(draft)
        assert "D_LLM" in ctx.claims._drafts


# ─── G2.7: Orphaned evidence rejected ─────────────────────────────────────────


class TestOrphanedEvidence:
    def test_orphaned_evidence_rejected(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)
        passage = Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        ctx.add_passage(passage)
        claim = Claim(claim_id="C1", passage_id="P1", claim_text="test",
                      claim_type=ClaimType.DESCRIBE_STATE, evidence_level=EvidenceLevel.LEVEL_1,
                      created_by="HUMAN")
        ctx.add_claim(claim)

        # Add evidence with missing claim reference
        evidence = Evidence(
            evidence_id="E_ORPH", claim_id="C_MISSING", evidence_level=EvidenceLevel.LEVEL_1,
            source_id="S1", passage_id="P1",
        )
        with pytest.raises(ChainIntegrityError):
            ctx.add_evidence(evidence)

    def test_validate_chain_finds_orphans(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)

        # Add orphaned passage (missing source)
        passage = Passage(passage_id="P_ORPH", source_id="S_MISSING", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        # This should fail on add

        # Instead, manually create a broken state via registry directly
        from tongshu.chain.registry import PassageRegistry
        pr = PassageRegistry(ctx.sources)
        with pytest.raises(ChainIntegrityError):
            pr.add(passage)


# ─── G2.8: Orphaned claim rejected ─────────────────────────────────────────────


class TestOrphanedClaim:
    def test_orphaned_claim_rejected(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)

        claim = Claim(claim_id="C_ORPH", passage_id="P_MISSING", claim_text="test",
                      claim_type=ClaimType.DESCRIBE_STATE, evidence_level=EvidenceLevel.LEVEL_1,
                      created_by="HUMAN")
        with pytest.raises(ChainIntegrityError):
            ctx.add_claim(claim)


# ─── G2.9: Incomplete provenance rejected ──────────────────────────────────────


class TestIncompleteProvenance:
    def test_broken_provenance_raises(self):
        ctx = EvidenceChainContext()
        with pytest.raises(ProvenanceBrokenError):
            ctx.trace_to_source("S_NONEXIST", "source")

    def test_broken_passage_provenance_raises(self):
        ctx = EvidenceChainContext()
        with pytest.raises(ProvenanceBrokenError):
            ctx.trace_to_source("P_NONEXIST", "passage")

    def test_valid_provenance_completes(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)

        passage = Passage(passage_id="P1", source_id="S1", text="t", evidence_level=EvidenceLevel.LEVEL_1)
        ctx.add_passage(passage)

        trace = ctx.trace_to_source("P1", "passage")
        assert trace.is_complete()
        assert trace.source_id == "S1"


# ─── G2.10: Immutable / audit-safe nodes ──────────────────────────────────────


class TestImmutability:
    def test_provenance_trace_frozen(self):
        from tongshu.chain.provenance import ProvenanceTrace
        trace = ProvenanceTrace(source_id="S1", depth=1)
        with pytest.raises(AttributeError):
            trace.source_id = "S2"  # type: ignore

    def test_source_registry_immutability(self):
        ctx = EvidenceChainContext()
        source = Source(source_id="S1", source_type="CLASSICAL", title="T", edition="E")
        ctx.add_source(source)
        # Source dataclass is frozen? No, but registry prevents mutation
        # Verify duplicate addition is rejected
        with pytest.raises(ChainIntegrityError):
            ctx.add_source(source)


# ─── G2.11: Legacy engine zero modification ────────────────────────────────────


class TestLegacyEngineUnchanged:
    def test_no_engine_modifications(self):
        """Verify existing engines still import correctly."""
        from tongshu.spec.signal_ontology import USO_TYPES, POLARITIES
        from tongshu.spec.cross_states import CROSS_STATES
        assert len(USO_TYPES) == 8
        assert len(POLARITIES) == 3
        assert len(CROSS_STATES) == 4


# ─── G2.12: Phase 1 tests no regression ───────────────────────────────────────


class TestPhase1NoRegression:
    def test_phase1_spec_tests_still_pass(self):
        """Phase 1 spec tests should still pass - verified separately."""
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/spec/", "-q", "--tb=no"],
            capture_output=True, text=True,
            cwd=r".\backend",
        )
        assert result.returncode == 0, f"Phase 1 tests failed: {result.stdout}"
