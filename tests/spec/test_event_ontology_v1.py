"""
Contract Tests: Schema 3 — Event Ontology (V1.2)
G1.4, G1.5, G1.13 — HIGHEST PRIORITY

This test file validates the P0 Ontology fix:
  - 4 Domains only
  - 17 Event Types
  - Single-Parent Domain (no overlaps)
  - No CHILD_BIRTH in both FAMILY and LIFE_EVENT
"""
from __future__ import annotations

import pytest
from tongshu.spec.event_ontology_v1 import (
    Domain,
    EventDirection,
    TemporalGranularity,
    EventDefinition,
    EVENT_TYPES,
    EVENT_TYPE_BY_ID,
    DOMAIN_BY_ID,
    DIRECTION_BY_ID,
    validate_ontology_invariants,
)


# ─── Core invariants ──────────────────────────────────────────────────────────


def test_17_event_types():
    assert len(EVENT_TYPES) == 17


def test_4_domains():
    assert len(list(Domain)) == 4
    assert {d.value for d in Domain} == {"EDUCATION", "CAREER", "FAMILY", "LIFE_EVENT"}


def test_5_directions():
    assert len(list(EventDirection)) == 5
    assert {d.value for d in EventDirection} == {
        "POSITIVE", "NEGATIVE", "CHANGE", "NEUTRAL", "UNKNOWN",
    }


def test_3_granularities():
    assert len(list(TemporalGranularity)) == 3
    assert {g.value for g in TemporalGranularity} == {"YEARLY", "MONTHLY", "DAILY"}


def test_each_event_has_valid_domain():
    for e in EVENT_TYPES:
        assert e.domain in Domain, f"{e.id} has invalid domain {e.domain}"


def test_each_event_has_valid_direction():
    for e in EVENT_TYPES:
        assert e.direction in EventDirection


def test_each_event_has_valid_granularity():
    for e in EVENT_TYPES:
        assert e.granularity in TemporalGranularity


def test_all_ids_unique():
    ids = [e.id for e in EVENT_TYPES]
    assert len(ids) == len(set(ids)), f"Duplicated ids: {[i for i in ids if ids.count(i) > 1]}"


def test_all_ids_lowercase():
    for e in EVENT_TYPES:
        assert e.id == e.id.upper(), f"{e.id} should be uppercase"


# ─── Single-Parent Domain invariant ──────────────────────────────────────────


def test_single_parent_domain():
    """Each Event Type belongs to exactly one Domain."""
    domain_counts: dict[str, int] = {}
    for e in EVENT_TYPES:
        domain_counts[e.domain.value] = domain_counts.get(e.domain.value, 0) + 1
    # Must be exactly 4 keys
    assert set(domain_counts.keys()) == {"EDUCATION", "CAREER", "FAMILY", "LIFE_EVENT"}
    # Expected distribution: EDUCATION=4, CAREER=5, FAMILY=5, LIFE_EVENT=3
    assert domain_counts["EDUCATION"] == 4
    assert domain_counts["CAREER"] == 5
    assert domain_counts["FAMILY"] == 5
    assert domain_counts["LIFE_EVENT"] == 3


def test_no_event_crosses_domain():
    """No Event Type appears in more than one Domain."""
    id_to_domains: dict[str, set] = {}
    for e in EVENT_TYPES:
        id_to_domains.setdefault(e.id, set()).add(e.domain)
    for eid, domains in id_to_domains.items():
        assert len(domains) == 1, f"{eid} maps to multiple domains: {domains}"


# ─── Specific Event Type membership ───────────────────────────────────────────


def test_child_birth_in_family_not_life_event():
    """CHILD_BIRTH must be in FAMILY only, not LIFE_EVENT (P0 fix)."""
    child_birth = EVENT_TYPE_BY_ID["CHILD_BIRTH"]
    assert child_birth.domain == Domain.FAMILY
    assert child_birth.domain != Domain.LIFE_EVENT


def test_health_issue_in_life_event():
    """HEALTH_ISSUE must be in LIFE_EVENT."""
    health = EVENT_TYPE_BY_ID["HEALTH_ISSUE"]
    assert health.domain == Domain.LIFE_EVENT


def test_education_events():
    edu_ids = {e.id for e in EVENT_TYPES if e.domain == Domain.EDUCATION}
    assert edu_ids == {"EXAM", "ADMISSION", "GRADUATION", "DEGREE"}


def test_career_events():
    career_ids = {e.id for e in EVENT_TYPES if e.domain == Domain.CAREER}
    assert career_ids == {"PROMOTION", "JOB_CHANGE", "RESIGNATION", "DEMOTION", "MAJOR_INCOME"}


def test_family_events():
    family_ids = {e.id for e in EVENT_TYPES if e.domain == Domain.FAMILY}
    assert family_ids == {"MARRIAGE", "DIVORCE", "CHILD_BIRTH", "PARENT_DEATH", "FAMILY_HARMONY"}


def test_life_event_events():
    le_ids = {e.id for e in EVENT_TYPES if e.domain == Domain.LIFE_EVENT}
    assert le_ids == {"RELOCATION", "HEALTH_ISSUE", "LEGAL_ISSUE"}


# ─── Lookup tables ────────────────────────────────────────────────────────────


def test_event_type_by_id_contains_all():
    for e in EVENT_TYPES:
        assert EVENT_TYPE_BY_ID[e.id] is e


def test_domain_by_id_correct():
    for e in EVENT_TYPES:
        assert DOMAIN_BY_ID[e.id] == e.domain


def test_direction_by_id_correct():
    for e in EVENT_TYPES:
        assert DIRECTION_BY_ID[e.id] == e.direction


# ─── validate_ontology_invariants ─────────────────────────────────────────────


def test_invariants_pass():
    errors = validate_ontology_invariants()
    assert errors == [], f"Invariant violations: {errors}"


# ─── EventDefinition immutability ─────────────────────────────────────────────


def test_event_definition_frozen():
    e = EVENT_TYPES[0]
    with pytest.raises(Exception):  # FrozenInstanceError (subclass of TypeError in Python <3.10)
        e.id = "MODIFIED"  # type: ignore[misc]


# ─── Serialization round-trip ────────────────────────────────────────────────


def test_event_definition_to_dict():
    e = EVENT_TYPES[0]
    d = e.to_dict()
    assert "id" in d
    assert "domain" in d
    assert "direction" in d
    assert "granularity" in d
