"""
Contract Tests: Schema 8 — Relational Interpretation
G1.9: InterpInput must NOT contain raw calculation fields
"""
from __future__ import annotations

import pytest
from tongshu.spec.relational_interpretation import (
    InterpretationLayer,
    YiStructure,
    InterpInput,
    RelationalInterpretation,
)


# ─── YiStructure ──────────────────────────────────────────────────────────────


def test_yi_structure_basic():
    ys = YiStructure(
        truth_hexagram="QIAN",
        true_line=1,
        classical_quote="元亨利贞",
        image_meaning="天行健",
    )
    d = ys.to_dict()
    assert d["truth_hexagram"] == "QIAN"
    assert d["true_line"] == 1


def test_yi_structure_default_layer():
    ys = YiStructure()
    assert ys.layer == InterpretationLayer.TRUTH_HEXAGRAM


# ─── InterpInput (G1.9: NO raw calculation fields) ──────────────────────────


def test_interp_input_valid():
    """Valid InterpInput with canonicalized fields only."""
    ii = InterpInput(
        yi_structure=YiStructure(truth_hexagram="QIAN"),
        event_type_id="PROMOTION",
        severity_class="HIGH",
        evidence_refs=["ev-001"],
        interpretation_phase=6,
    )
    assert ii.yi_structure is not None
    assert ii.event_type_id == "PROMOTION"
    assert ii.severity_class == "HIGH"
    assert ii.interpretation_phase == 6


def test_interp_input_rejects_bazi_pillars():
    """G1.9: bazi_pillars must be rejected."""
    with pytest.raises(ValueError, match="forbidden"):
        InterpInput.from_dict({"bazi_pillars": [{"year": "丙", "month": "申"}]})


def test_interp_input_rejects_heluo_hexagram():
    """G1.9: heluo_hexagram must be rejected."""
    with pytest.raises(ValueError, match="forbidden"):
        InterpInput.from_dict({"heluo_hexagram": "乾为天"})


def test_interp_input_rejects_ziwei_ming_gong():
    """G1.9: ziwei_ming_gong must be rejected."""
    with pytest.raises(ValueError, match="forbidden"):
        InterpInput.from_dict({"ziwei_ming_gong": "命宫在子"})


def test_interp_input_rejects_raw_calculation():
    """G1.9: raw_calculation must be rejected."""
    with pytest.raises(ValueError, match="forbidden"):
        InterpInput.from_dict({"raw_calculation": {"bazi": "...", "numbers": [...]}})


def test_interp_input_rejects_calculation_context():
    """G1.9: calculation_context must be rejected."""
    with pytest.raises(ValueError, match="forbidden"):
        InterpInput.from_dict({"calculation_context": {"pillars": [...]}})


def test_interp_input_rejects_calculation_result():
    """G1.9: calculation_result must be rejected."""
    with pytest.raises(ValueError, match="forbidden"):
        InterpInput.from_dict({"calculation_result": {"scores": [...]}})


def test_interp_input_empty_dict_is_valid():
    """An empty InterpInput is valid — just all defaults."""
    ii = InterpInput.from_dict({})
    assert ii.yi_structure is None
    assert ii.event_type_id is None
    assert ii.interpretation_phase == 0


def test_interp_input_model_fields_no_raw_calc():
    """Schema-level check: InterpInput.model_fields must not contain raw calc fields."""
    forbidden = {"bazi_pillars", "heluo_hexagram", "ziwei_ming_gong",
                 "raw_calculation", "calculation_context", "calculation_result"}
    actual_fields = set(InterpInput.__dataclass_fields__.keys())
    intersection = forbidden & actual_fields
    assert intersection == set(), f"InterpInput contains forbidden fields: {intersection}"


# ─── RelationalInterpretation ────────────────────────────────────────────────


def test_relational_interpretation_basic():
    ri = RelationalInterpretation(
        interpretation_id="ri-001",
        interp_input_ref="ii-001",
        yi_structure=YiStructure(truth_hexagram="QIAN"),
        evidence_refs=["ev-001"],
        interpretation_text="乾卦六爻皆阳，象征天道刚健。",
        phase=6,
    )
    d = ri.to_dict()
    assert d["interpretation_id"] == "ri-001"
    assert d["phase"] == 6
    assert d["yi_structure"]["truth_hexagram"] == "QIAN"
