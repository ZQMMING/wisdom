"""
Contract Tests: Schema 7 — Evidence Chain
G1.6, G1.7: LEVEL_5 excluded from formal chain, Claim.created_by enforcement
"""
from __future__ import annotations

import pytest
from tongshu.spec.evidence_chain import (
    EvidenceLevel,
    VerificationStatus,
    ClaimType,
    ALLOWED_CLAIM_CREATORS,
    Source,
    Passage,
    Claim,
    ClaimDraft,
    Evidence,
    validate_chain,
)


# ─── EvidenceLevel (G1.6) ────────────────────────────────────────────────────


def test_five_levels_exist():
    levels = list(EvidenceLevel)
    assert len(levels) == 5
    for i, lvl in enumerate(levels, 1):
        assert lvl.value == f"LEVEL_{i}"


def test_formal_levels_exclude_level_5():
    formal = EvidenceLevel.formal_levels()
    assert len(formal) == 4
    assert EvidenceLevel.LEVEL_5 not in formal
    for lvl in formal:
        assert lvl.is_formal()
    assert not EvidenceLevel.LEVEL_5.is_formal()


def test_level_5_is_not_formal():
    assert not EvidenceLevel.LEVEL_5.is_formal()


# ─── Source ───────────────────────────────────────────────────────────────────


def test_source_creation():
    s = Source(
        source_id="src-001",
        source_type="CLASSICAL",
        title="易经",
        edition="王弼注本",
    )
    assert s.source_id == "src-001"
    assert s.verified is False


# ─── Passage (LEVEL_5 forbidden) ─────────────────────────────────────────────


def test_passage_valid_level_1():
    p = Passage(
        passage_id="pass-001",
        source_id="src-001",
        text="乾：元亨利贞。",
        evidence_level=EvidenceLevel.LEVEL_1,
    )
    assert p.validate_level() == []


def test_passage_rejects_level_5():
    p = Passage(
        passage_id="pass-002",
        source_id="src-001",
        text="LLM interpretation",
        evidence_level=EvidenceLevel.LEVEL_5,
    )
    errors = p.validate_level()
    assert len(errors) >= 1
    assert "LEVEL_5" in errors[0]


# ─── Claim (G1.7: LLM cannot directly create formal claims) ─────────────────


def test_claim_human_creator_allowed():
    c = Claim(
        claim_id="c-001",
        passage_id="pass-001",
        claim_text="此卦主变动。",
        claim_type=ClaimType.DESCRIBE_STATE,
        evidence_level=EvidenceLevel.LEVEL_1,
        created_by="HUMAN",
    )
    assert c.validate() == []


def test_claim_rule_engine_allowed():
    c = Claim(
        claim_id="c-002",
        passage_id="pass-001",
        claim_text="2026年有晋升机会。",
        claim_type=ClaimType.PREDICT_TENDENCY,
        evidence_level=EvidenceLevel.LEVEL_2,
        created_by="RULE_ENGINE",
    )
    assert c.validate() == []


def test_claim_llm_creator_rejected():
    """G1.7: LLM cannot directly create formal Claim."""
    c = Claim(
        claim_id="c-003",
        passage_id="pass-001",
        claim_text="LLM-generated claim",
        claim_type=ClaimType.PREDICT_TENDENCY,
        evidence_level=EvidenceLevel.LEVEL_1,
        created_by="LLM",
    )
    errors = c.validate()
    assert len(errors) >= 1
    assert "created_by" in errors[0]


def test_claim_level_5_rejected():
    c = Claim(
        claim_id="c-004",
        passage_id="pass-001",
        claim_text="Modern mapping",
        claim_type=ClaimType.DESCRIBE_STATE,
        evidence_level=EvidenceLevel.LEVEL_5,
        created_by="HUMAN",
    )
    errors = c.validate()
    assert len(errors) >= 1
    assert "LEVEL_5" in errors[0]


def test_allowed_claim_creators():
    assert ALLOWED_CLAIM_CREATORS == frozenset({"HUMAN", "RULE_ENGINE"})


# ─── ClaimDraft (LLM intermediate, needs review) ─────────────────────────────


def test_claim_draft_llm_allowed():
    cd = ClaimDraft(
        draft_id="cd-001",
        passage_id="pass-001",
        claim_text="LLM draft",
        claim_type=ClaimType.PREDICT_TENDENCY,
        created_by="LLM",
    )
    assert cd.validate_creator() == []
    assert cd.review_status == "PENDING_REVIEW"


def test_claim_draft_human_allowed():
    cd = ClaimDraft(draft_id="cd-002", passage_id="pass-001",
                    claim_text="Human draft", claim_type=ClaimType.DESCRIBE_STATE,
                    created_by="HUMAN")
    assert cd.validate_creator() == []


def test_claim_draft_unknown_creator_rejected():
    cd = ClaimDraft(draft_id="cd-003", passage_id="pass-001",
                    claim_text="Unknown", claim_type=ClaimType.DESCRIBE_STATE,
                    created_by="UNKNOWN_ENGINE")
    errors = cd.validate_creator()
    assert len(errors) >= 1


# ─── Evidence (LEVEL_5 forbidden) ─────────────────────────────────────────────


def test_evidence_valid_level():
    e = Evidence(
        evidence_id="ev-001",
        claim_id="c-001",
        evidence_level=EvidenceLevel.LEVEL_1,
        source_id="src-001",
        passage_id="pass-001",
    )
    assert e.validate_level() == []


def test_evidence_rejects_level_5():
    e = Evidence(
        evidence_id="ev-002",
        claim_id="c-001",
        evidence_level=EvidenceLevel.LEVEL_5,
        source_id="src-001",
        passage_id="pass-001",
    )
    errors = e.validate_level()
    assert len(errors) >= 1


# ─── Chain integrity validation ──────────────────────────────────────────────


def test_chain_intact():
    sources = {"src-001": Source(source_id="src-001", source_type="CLASSICAL", title="E", edition="v1")}
    passages = {"pass-001": Passage(passage_id="pass-001", source_id="src-001", text="x", evidence_level=EvidenceLevel.LEVEL_1)}
    claims = {"c-001": Claim(claim_id="c-001", passage_id="pass-001", claim_text="t",
                             claim_type=ClaimType.DESCRIBE_STATE, evidence_level=EvidenceLevel.LEVEL_1,
                             created_by="HUMAN")}
    evidences = {"ev-001": Evidence(evidence_id="ev-001", claim_id="c-001", evidence_level=EvidenceLevel.LEVEL_1,
                                    source_id="src-001", passage_id="pass-001")}
    errors = validate_chain(sources, passages, claims, evidences)
    assert errors == []


def test_chain_missing_passage():
    sources = {"src-001": Source(source_id="src-001", source_type="CLASSICAL", title="E", edition="v1")}
    passages: dict = {}  # empty
    claims = {"c-001": Claim(claim_id="c-001", passage_id="pass-999", claim_text="t",
                             claim_type=ClaimType.DESCRIBE_STATE, evidence_level=EvidenceLevel.LEVEL_1,
                             created_by="HUMAN")}
    evidences: dict = {}
    errors = validate_chain(sources, passages, claims, evidences)
    assert len(errors) >= 1
    assert "pass-999" in errors[0]


def test_chain_missing_source():
    sources = {}
    passages = {"pass-001": Passage(passage_id="pass-001", source_id="src-999", text="x",
                                    evidence_level=EvidenceLevel.LEVEL_1)}
    claims = {"c-001": Claim(claim_id="c-001", passage_id="pass-001", claim_text="t",
                             claim_type=ClaimType.DESCRIBE_STATE, evidence_level=EvidenceLevel.LEVEL_1,
                             created_by="HUMAN")}
    evidences = {"ev-001": Evidence(evidence_id="ev-001", claim_id="c-001", evidence_level=EvidenceLevel.LEVEL_1,
                                    source_id="src-999", passage_id="pass-001")}
    errors = validate_chain(sources, passages, claims, evidences)
    assert len(errors) >= 1
