"""
Contract Tests: Schema 6 — Severity
G1.5: Weighted arithmetic mean formula, weights sum to 1.0
Evidence Completeness ≠ Event Severity (separate schemas)
"""
from __future__ import annotations

import pytest
from tongshu.spec.severity import (
    SeverityClass,
    SEVERITY_WEIGHTS,
    SeverityInput,
    EventSeverity,
    EvidenceCompleteness,
    InterpretationAvailability,
)


# ─── SEVERITY_WEIGHTS (G1.5) ─────────────────────────────────────────────────


def test_weights_sum_to_one():
    assert abs(sum(SEVERITY_WEIGHTS.values()) - 1.0) < 1e-9, \
        f"Weights sum to {sum(SEVERITY_WEIGHTS.values())}, not 1.0"


def test_weights_exact_values():
    expected = {
        "signal_strength": 0.20,
        "temporal_convergence": 0.15,
        "ontology_specificity": 0.20,
        "evidence_quality": 0.25,
        "agreement_evidence": 0.20,
    }
    assert SEVERITY_WEIGHTS == expected


def test_severity_weights_named_correctly():
    for key in ["signal_strength", "temporal_convergence", "ontology_specificity",
                "evidence_quality", "agreement_evidence"]:
        assert key in SEVERITY_WEIGHTS, f"Missing weight key: {key}"


# ─── SeverityInput validation ────────────────────────────────────────────────


def test_severity_input_all_zeros():
    inp = SeverityInput()
    assert inp.signal_strength == 0.0
    assert inp.temporal_convergence == 0.0
    assert inp.ontology_specificity == 0.0
    assert inp.evidence_quality == 0.0
    assert inp.agreement_evidence == 0.0
    assert inp.validate_ranges() == []


def test_severity_input_all_ones():
    inp = SeverityInput(
        signal_strength=1.0,
        temporal_convergence=1.0,
        ontology_specificity=1.0,
        evidence_quality=1.0,
        agreement_evidence=1.0,
    )
    assert inp.validate_ranges() == []


def test_severity_input_out_of_range():
    inp = SeverityInput(signal_strength=1.5)
    errors = inp.validate_ranges()
    assert len(errors) >= 1
    assert "signal_strength" in errors[0]


# ─── EventSeverity formula (G1.5: arithmetic mean, not product) ──────────────


def test_severity_all_zeros_gives_low():
    inp = SeverityInput()  # all 0.0
    result = EventSeverity.calculate(inp)
    assert result.severity_score == pytest.approx(0.0)
    assert result.severity_class == SeverityClass.LOW


def test_severity_all_ones_gives_critical():
    inp = SeverityInput(
        signal_strength=1.0,
        temporal_convergence=1.0,
        ontology_specificity=1.0,
        evidence_quality=1.0,
        agreement_evidence=1.0,
    )
    result = EventSeverity.calculate(inp)
    assert result.severity_score == pytest.approx(1.0)
    assert result.severity_class == SeverityClass.CRITICAL


def test_severity_boundary_low():
    """Score in [0.0, 0.3) → LOW"""
    inp = SeverityInput(signal_strength=0.28)
    result = EventSeverity.calculate(inp)
    assert result.severity_class == SeverityClass.LOW


def test_severity_boundary_moderate():
    """Score in [0.3, 0.6) → MODERATE"""
    # 0.3 = 0.20*1.0 + 0.15*1.0 + 0.20*0.0 + 0.25*0.0 + 0.20*0.0 = 0.35 → MODERATE
    inp = SeverityInput(signal_strength=1.0, temporal_convergence=1.0)
    result = EventSeverity.calculate(inp)
    assert result.severity_class == SeverityClass.MODERATE


def test_severity_boundary_high():
    """Score in [0.6, 0.85) → HIGH"""
    # 0.85 = 0.20+0.15+0.20+0.25+0.20 * partial
    inp = SeverityInput(
        signal_strength=1.0, temporal_convergence=1.0,
        ontology_specificity=1.0, evidence_quality=1.0, agreement_evidence=0.5,
    )
    result = EventSeverity.calculate(inp)
    # 0.20+0.15+0.20+0.25+0.10 = 0.90 → CRITICAL... let me pick better values
    # 0.6 = 0.20+0.15+0.20+0.25*0.0+0.20*0.0 = 0.55 → MODERATE
    # 0.60 = 0.20*1.0 + 0.15*1.0 + 0.20*1.0 + 0.25*0.0 + 0.20*0.0 = 0.55
    # Need 0.60: signal=1, temporal=1, ontology=1, evidence=0.2, agreement=0
    # 0.20+0.15+0.20+0.05+0 = 0.60 → HIGH boundary
    inp = SeverityInput(
        signal_strength=1.0, temporal_convergence=1.0,
        ontology_specificity=1.0, evidence_quality=0.2, agreement_evidence=0.0,
    )
    result = EventSeverity.calculate(inp)
    assert result.severity_class == SeverityClass.HIGH


def test_severity_boundary_critical():
    """Score in [0.85, 1.0] → CRITICAL"""
    inp = SeverityInput(
        signal_strength=1.0, temporal_convergence=1.0,
        ontology_specificity=1.0, evidence_quality=1.0, agreement_evidence=0.75,
    )
    result = EventSeverity.calculate(inp)
    score = result.severity_score
    assert score >= 0.85
    assert result.severity_class == SeverityClass.CRITICAL


def test_severity_is_arithmetic_mean_not_product():
    """
    G1.5 critical check: the formula must be weighted SUM, not product.
    If it were product: 0.20 * 0.15 * 0.20 * 0.25 * 0.20 = 0.00003
    With arithmetic: 0.20*1.0 + 0.15*1.0 + 0.20*1.0 + 0.25*1.0 + 0.20*1.0 = 1.0
    """
    inp = SeverityInput(
        signal_strength=1.0, temporal_convergence=1.0,
        ontology_specificity=1.0, evidence_quality=1.0, agreement_evidence=1.0,
    )
    result = EventSeverity.calculate(inp)
    # If product: would be ~0.00003, not 1.0
    assert result.severity_score == pytest.approx(1.0), \
        f"Expected 1.0 (arithmetic mean), got {result.severity_score} (likely product)"


# ─── EvidenceCompleteness (SEPARATE from EventSeverity) ──────────────────────


def test_evidence_completeness_separate_schema():
    """EvidenceCompleteness must be its own class, not nested in EventSeverity."""
    ec = EvidenceCompleteness()
    assert ec.overall == 1.0


def test_evidence_completeness_partial():
    ec = EvidenceCompleteness(
        source_completeness=0.8,
        passage_completeness=0.9,
        claim_traceability=0.7,
        evidence_level_completeness=0.85,
        signal_traceability=0.6,
    )
    expected = 0.8 * 0.9 * 0.7 * 0.85 * 0.6
    assert ec.overall == pytest.approx(expected)


def test_evidence_completeness_invalid_range():
    ec = EvidenceCompleteness(source_completeness=1.5)
    errors = ec.validate_ranges()
    assert len(errors) >= 1


# ─── InterpretationAvailability (SEPARATE from both above) ───────────────────


def test_interpretation_unavailable():
    ia = InterpretationAvailability(llm_engine_ready=False, evidence_chain_readable=False)
    assert ia.available is False


def test_interpretation_available():
    ia = InterpretationAvailability(llm_engine_ready=True, evidence_chain_readable=True)
    assert ia.available is True


def test_severity_separate_from_completeness():
    """EventSeverity and EvidenceCompleteness are different classes."""
    es = EventSeverity.calculate(SeverityInput())
    ec = EvidenceCompleteness()
    assert type(es) is not type(ec)
