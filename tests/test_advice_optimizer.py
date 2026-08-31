# -*- coding: utf-8 -*-
"""断言优化核心模块测试 — advice_optimizer."""
import pytest

from tongshu.assertion.advice_optimizer import (
    AdviceItem, AdviceSource, AdviceCategory,
    make_advice, deduplicate_advice, detect_conflicts,
    cross_validate, optimize_advice,
    get_system_weight, get_source_weight,
)


class TestAdviceItem:
    def test_make_advice(self):
        item = make_advice("测试建议", AdviceSource.ZIWEI, AdviceCategory.CAREER, priority=4, confidence=0.7)
        assert item.content == "测试建议"
        assert item.source == AdviceSource.ZIWEI
        assert item.category == AdviceCategory.CAREER
        assert item.priority == 4
        assert item.confidence == 0.7

    def test_score_calculation(self):
        item = AdviceItem(
            content="test", source=AdviceSource.ZIWEI,
            weight=0.8, priority=5, confidence=0.8,
        )
        assert abs(item.score - 0.64) < 0.01

    def test_to_dict(self):
        item = make_advice("test", AdviceSource.HELUO, AdviceCategory.WEALTH)
        d = item.to_dict()
        assert d["content"] == "test"
        assert d["source"] == "河洛"
        assert d["category"] == "财运"
        assert "score" in d


class TestWeights:
    """V13治理: SYSTEM_WEIGHTS已删除, 所有系统权重统一为0.5 (互补不比较). 测试验证此行为."""

    def test_system_weight_career(self):
        # V13治理: 所有系统权重统一为0.5
        assert get_system_weight("ziwei", "career") == 0.5
        assert get_system_weight("heluo", "career") == 0.5

    def test_system_weight_marriage(self):
        # V13治理: 所有系统权重统一为0.5
        assert get_system_weight("ziwei", "marriage") == 0.5
        assert get_system_weight("blind", "marriage") == 0.5

    def test_system_weight_health(self):
        # V13治理: 所有系统权重统一为0.5
        assert get_system_weight("ziping", "health") == 0.5
        assert get_system_weight("blindsight", "health") == 0.5

    def test_source_weight(self):
        # 古籍引用权重最高
        assert get_source_weight(AdviceSource.CLASSICAL) > get_source_weight(AdviceSource.MASTER)


class TestDeduplication:
    def test_no_duplicate(self):
        items = [
            make_advice("建议A", AdviceSource.ZIWEI, confidence=0.7),
            make_advice("完全不同的建议B", AdviceSource.BLIND, confidence=0.6),
        ]
        result = deduplicate_advice(items, threshold=0.6)
        assert len(result) == 2

    def test_with_duplicate(self):
        items = [
            make_advice("建议A", AdviceSource.ZIWEI, confidence=0.7),
            make_advice("建议A", AdviceSource.BLIND, confidence=0.6),
        ]
        result = deduplicate_advice(items, threshold=0.6)
        assert len(result) == 1


class TestConflictDetection:
    def test_detect_conflict(self):
        items = [
            make_advice("事业吉", AdviceSource.ZIWEI, AdviceCategory.CAREER, confidence=0.8),
            make_advice("事业凶", AdviceSource.BLIND, AdviceCategory.CAREER, confidence=0.7),
        ]
        conflicts = detect_conflicts(items)
        assert len(conflicts) > 0
