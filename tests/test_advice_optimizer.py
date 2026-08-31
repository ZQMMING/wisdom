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
        # score = weight * (priority/5) * confidence = 0.8 * 1.0 * 0.8 = 0.64
        assert abs(item.score - 0.64) < 0.01

    def test_to_dict(self):
        item = make_advice("test", AdviceSource.HELUO, AdviceCategory.WEALTH)
        d = item.to_dict()
        assert d["content"] == "test"
        assert d["source"] == "河洛"
        assert d["category"] == "财运"
        assert "score" in d


class TestWeights:

    def test_system_weight_career(self):
        # 紫微在事业上权重高
        assert get_system_weight("ziwei", "career") > get_system_weight("heluo", "career")

    def test_system_weight_marriage(self):
        # 紫微在婚姻上权重最高
        assert get_system_weight("ziwei", "marriage") == 0.90

    def test_system_weight_health(self):
        # 子平在健康上权重最高
        assert get_system_weight("ziping", "health") == 0.85

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
            make_advice("积极把握机遇, 主动展现能力", AdviceSource.ZIWEI, confidence=0.7),
            make_advice("积极把握机遇, 主动展现能力争取晋升", AdviceSource.BLIND, confidence=0.6),
        ]
        result = deduplicate_advice(items, threshold=0.6)
        assert len(result) == 1
        assert result[0].deduplicated is True
        # 多源印证提升置信度
        assert result[0].confidence > 0.7


class TestConflictDetection:
    def test_no_conflict(self):
        items = [
            make_advice("积极把握机遇", AdviceSource.ZIWEI, AdviceCategory.CAREER),
            make_advice("稳健理财", AdviceSource.HELUO, AdviceCategory.WEALTH),
        ]
        result = detect_conflicts(items)
        assert all(not item.conflict_with for item in result)

    def test_with_conflict(self):
        items = [
            make_advice("积极投资, 把握机遇", AdviceSource.ZIWEI, AdviceCategory.WEALTH),
            make_advice("保守理财, 避免投资", AdviceSource.BLIND, AdviceCategory.WEALTH),
        ]
        result = detect_conflicts(items)
        assert any(item.conflict_with for item in result)
        # 冲突降低置信度
        assert items[0].confidence < 0.5  # 默认0.5 - 0.15


class TestCrossValidation:
    def test_single_system(self):
        items = [
            make_advice("建议A", AdviceSource.ZIWEI, AdviceCategory.CAREER, confidence=0.8),
        ]
        result, score = cross_validate(items)
        # 单体系置信度封顶0.7
        assert result[0].confidence <= 0.7
        assert score == 0.0

    def test_multi_system_agreement(self):
        items = [
            make_advice("事业偏吉", AdviceSource.ZIWEI, AdviceCategory.CAREER, confidence=0.6),
            make_advice("事业向好", AdviceSource.BLIND, AdviceCategory.CAREER, confidence=0.6),
        ]
        result, score = cross_validate(items)
        # 多体系印证提升置信度
        assert result[0].confidence > 0.6
        assert score == 1.0


class TestOptimizeAdvice:
    def test_basic_optimization(self):
        items = [
            make_advice("积极把握事业机遇", AdviceSource.ZIWEI, AdviceCategory.CAREER, priority=5, confidence=0.7),
            make_advice("稳健理财避免风险", AdviceSource.BLIND, AdviceCategory.WEALTH, priority=4, confidence=0.6),
            make_advice("注意身体健康定期体检", AdviceSource.HELUO, AdviceCategory.HEALTH, priority=3, confidence=0.5),
        ]
        result = optimize_advice(items, topic="career", max_items=3)
        assert "items" in result
        assert "text" in result
        assert "stats" in result
        assert result["stats"]["original_count"] == 3
        assert result["stats"]["final_count"] <= 3
        assert len(result["text"]) > 0

    def test_optimization_with_duplicates(self):
        items = [
            make_advice("积极把握机遇主动展现", AdviceSource.ZIWEI, AdviceCategory.CAREER, confidence=0.7),
            make_advice("积极把握机遇主动展现能力", AdviceSource.BLIND, AdviceCategory.CAREER, confidence=0.6),
            make_advice("稳健理财", AdviceSource.HELUO, AdviceCategory.WEALTH, confidence=0.5),
        ]
        result = optimize_advice(items, topic="career", max_items=5)
        assert result["stats"]["deduped_count"] >= 1
        assert result["stats"]["final_count"] < 3

    def test_empty_input(self):
        result = optimize_advice([], topic="general")
        assert result["stats"]["original_count"] == 0
        assert result["stats"]["final_count"] == 0
        assert result["text"] == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
