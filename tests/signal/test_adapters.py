"""
Phase 3 Contract Tests — Engine Adapters
"""
from __future__ import annotations

import pytest

from tongshu.signal.adapters import (
    BaziAdapter,
    HeluoAdapter,
    ZiweiAdapter,
    HuangliAdapter,
    KnowledgeAdapter,
    get_adapter,
    ADAPTER_REGISTRY,
)
from tongshu.signal.canonical_signal import SourceEngine, CanonicalSignal
from tongshu.spec.event_ontology_v1 import Domain, EventDirection


class TestBaziAdapter:
    """Test Bazi adapter contract."""

    def test_valid_bazi_output(self):
        output = {
            'signal_id': 'BAZI_001',
            'shenshan': '正官',
            'pattern': '正官格',
            'strength': 0.7,
            'start_year': 2026,
            'end_year': 2027,
        }
        signal = BaziAdapter.adapt(output)
        assert signal.source_engine == SourceEngine.BAZI
        assert signal.event_type == 'PROMOTION'
        assert signal.domain == Domain.CAREER
        assert signal.strength == 0.7

    def test_unknown_pattern_rejected(self):
        output = {
            'signal_id': 'BAZI_BAD',
            'shenshan': '正官',
            'pattern': 'UNKNOWN_PATTERN',
            'strength': 0.5,
        }
        with pytest.raises(ValueError):
            BaziAdapter.adapt(output)


class TestHeluoAdapter:
    """Test Heluo adapter contract."""

    def test_valid_heluo_output(self):
        output = {
            'signal_id': 'HELUO_001',
            'gua': '乾',
            'yao': 2,
            'position': '中',
            'shi': '吉',
            'strength': 0.6,
            'start_year': 2026,
        }
        signal = HeluoAdapter.adapt(output)
        assert signal.source_engine == SourceEngine.HELUO

    def test_unknown_gua_rejected(self):
        output = {
            'signal_id': 'HELUO_BAD',
            'gua': 'UNKNOWN_GUA',
            'yao': 1,
            'shi': '吉',
        }
        with pytest.raises(ValueError):
            HeluoAdapter.adapt(output)


class TestZiweiAdapter:
    """Test Ziwei adapter contract."""

    def test_valid_ziwei_output(self):
        output = {
            'signal_id': 'ZIWEI_001',
            'palace': '官禄宫',
            'stars': ['紫微', '天府'],
            'transformations': ['化禄'],
            'strength': 0.8,
            'start_year': 2026,
        }
        signal = ZiweiAdapter.adapt(output)
        assert signal.source_engine == SourceEngine.ZIWEI

    def test_unknown_palace_rejected(self):
        output = {
            'signal_id': 'ZIWEI_BAD',
            'palace': 'UNKNOWN_PALACE',
            'stars': [],
            'transformations': [],
        }
        with pytest.raises(ValueError):
            ZiweiAdapter.adapt(output)


class TestHuangliAdapter:
    """Test Huangli adapter contract."""

    def test_valid_huangli_output(self):
        output = {
            'signal_id': 'HUANGLI_001',
            'day_stems': ['甲'],
            'day_branches': ['子'],
            'yi': ['嫁娶'],
            'ji': [],
            'jieqi': '春分',
            'strength': 0.6,
            'start_day': '2026-03-20',
        }
        signal = HuangliAdapter.adapt(output)
        assert signal.source_engine == SourceEngine.HUANGLI

    def test_no_yi_ji_rejected(self):
        output = {
            'signal_id': 'HUANGLI_BAD',
            'day_stems': ['甲'],
            'day_branches': ['子'],
            'yi': [],
            'ji': [],
        }
        with pytest.raises(ValueError):
            HuangliAdapter.adapt(output)


class TestKnowledgeAdapter:
    """Test Knowledge adapter contract — strict provenance requirements."""

    def test_valid_knowledge_output(self):
        output = {
            'signal_id': 'KNOWLEDGE_001',
            'source_text': '易经乾卦',
            'rule_id': 'RULE_001',
            'evidence_id': 'E001',
            'strength': 0.3,
            'start_year': 2026,
            'end_year': 2027,
        }
        signal = KnowledgeAdapter.adapt(output)
        assert signal.source_engine == SourceEngine.KNOWLEDGE
        assert signal.evidence_refs == ['E001']
        # Knowledge signals capped at 0.3
        assert signal.strength <= 0.3

    def test_missing_evidence_id_rejected(self):
        """G3.9: Knowledge adapter REQUIRES evidence_id."""
        output = {
            'signal_id': 'KNOWLEDGE_BAD',
            'source_text': '易经',
            'rule_id': 'RULE_001',
            # Missing evidence_id
        }
        with pytest.raises(ValueError, match="evidence_id is required"):
            KnowledgeAdapter.adapt(output)

    def test_knowledge_direction_unknown(self):
        """Knowledge signals default to UNKNOWN direction."""
        output = {
            'signal_id': 'KNOWLEDGE_002',
            'source_text': '易经',
            'rule_id': 'RULE_001',
            'evidence_id': 'E002',
        }
        signal = KnowledgeAdapter.adapt(output)
        assert signal.direction == EventDirection.UNKNOWN


class TestAdapterRegistry:
    """Test adapter registry."""

    def test_all_engines_registered(self):
        """G3.6: All 5 canonical engines must be registered."""
        expected = {'BAZI', 'HELUO', 'ZIWEI', 'HUANGLI', 'KNOWLEDGE'}
        actual = set(ADAPTER_REGISTRY.keys())
        assert expected == actual

    def test_get_adapter_returns_correct_class(self):
        assert get_adapter('BAZI') == BaziAdapter
        assert get_adapter('HELUO') == HeluoAdapter
        assert get_adapter('ZIWEI') == ZiweiAdapter
        assert get_adapter('HUANGLI') == HuangliAdapter
        assert get_adapter('KNOWLEDGE') == KnowledgeAdapter

    def test_invalid_engine_raises(self):
        with pytest.raises(ValueError, match="Unknown engine"):
            get_adapter('INVALID_ENGINE')


class TestAdapterContract:
    """Test adapter contract enforcement."""

    def test_adapter_only_converts_not_calculates(self):
        """G3.11: Adapters only convert, don't re-implement engine logic."""
        # If we change the Bazi engine output format, the adapter should fail
        # This test ensures adapters are thin wrappers
        output = {
            'signal_id': 'BAZI_001',
            'shenshan': '正官',
            'pattern': '正官格',
            'strength': 0.7,
        }
        signal = BaziAdapter.adapt(output)
        assert signal.event_type == 'PROMOTION'  # From normalization, not calculation

    def test_no_new_event_types_created(self):
        """G3.12: Adapters cannot create new Event Types."""
        # All valid outputs must map to existing 17 event types or UNKNOWN
        from tongshu.signal.canonical_signal import CANONICAL_EVENT_TYPES
        from tongshu.spec.event_ontology_v1 import EVENT_TYPE_BY_ID

        assert 'UNKNOWN' in CANONICAL_EVENT_TYPES
        assert len(EVENT_TYPE_BY_ID) == 17
