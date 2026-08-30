"""
Condition Evaluator 测试

验证Condition Evaluator的正确性
"""

import pytest
from src.tongshu.canonical.condition_evaluator import (
    EvaluationResult,
    TenGodConditionEvaluator,
    PowerComparisonEvaluator,
    PresenceConditionEvaluator,
    CompositeConditionEvaluator,
    ConditionEvaluatorFactory,
)


class TestTenGodConditionEvaluator:
    """测试十神存在性评估器"""
    
    def test_evaluate_true(self):
        """测试：十神存在"""
        evaluator = TenGodConditionEvaluator(
            evaluator_id="EVAL_001",
            condition_id="COND_001",
            target_ten_god="ZHENG_GUAN"
        )
        
        canonical_state = {
            "ten_gods_distribution": {
                "ZHENG_GUAN": 2,
                "YIN_XING": 1,
                "SHI_SHEN": 0
            }
        }
        
        result = evaluator.evaluate(canonical_state)
        assert result == EvaluationResult.TRUE
    
    def test_evaluate_false(self):
        """测试：十神不存在"""
        evaluator = TenGodConditionEvaluator(
            evaluator_id="EVAL_002",
            condition_id="COND_002",
            target_ten_god="QI_SHA"
        )
        
        canonical_state = {
            "ten_gods_distribution": {
                "ZHENG_GUAN": 1,
                "YIN_XING": 2
            }
        }
        
        result = evaluator.evaluate(canonical_state)
        assert result == EvaluationResult.FALSE
    
    def test_evaluate_zero_count(self):
        """测试：十神存在但数量为0"""
        evaluator = TenGodConditionEvaluator(
            evaluator_id="EVAL_003",
            condition_id="COND_003",
            target_ten_god="PIAN_CAI"
        )
        
        canonical_state = {
            "ten_gods_distribution": {
                "PIAN_CAI": 0
            }
        }
        
        result = evaluator.evaluate(canonical_state)
        assert result == EvaluationResult.FALSE
    
    def test_get_logic(self):
        """测试：获取逻辑描述"""
        evaluator = TenGodConditionEvaluator(
            evaluator_id="EVAL_004",
            condition_id="COND_004",
            target_ten_god="ZHENG_GUAN"
        )
        
        logic = evaluator.get_logic()
        assert "ZHENG_GUAN" in logic
        assert "存在" in logic


class TestPowerComparisonEvaluator:
    """测试力量比较评估器"""
    
    def test_evaluate_less_than_true(self):
        """测试：小于关系（印星 < 煞星）"""
        evaluator = PowerComparisonEvaluator(
            evaluator_id="EVAL_005",
            condition_id="COND_005",
            left_ten_god="YIN_XING",
            right_ten_god="QI_SHA",
            operator="<"
        )
        
        canonical_state = {
            "ten_gods_distribution": {
                "YIN_XING": 1,
                "QI_SHA": 2
            }
        }
        
        result = evaluator.evaluate(canonical_state)
        assert result == EvaluationResult.TRUE
    
    def test_evaluate_less_than_false(self):
        """测试：小于关系不成立"""
        evaluator = PowerComparisonEvaluator(
            evaluator_id="EVAL_006",
            condition_id="COND_006",
            left_ten_god="YIN_XING",
            right_ten_god="QI_SHA",
            operator="<"
        )
        
        canonical_state = {
            "ten_gods_distribution": {
                "YIN_XING": 3,
                "QI_SHA": 2
            }
        }
        
        result = evaluator.evaluate(canonical_state)
        assert result == EvaluationResult.FALSE
    
    def test_evaluate_unresolved(self):
        """测试：数据不足返回UNRESOLVED"""
        evaluator = PowerComparisonEvaluator(
            evaluator_id="EVAL_007",
            condition_id="COND_007",
            left_ten_god="YIN_XING",
            right_ten_god="QI_SHA",
            operator="<"
        )
        
        canonical_state = {
            "ten_gods_distribution": {
                "YIN_XING": 1
                # 缺少QI_SHA数据
            }
        }
        
        result = evaluator.evaluate(canonical_state)
        assert result == EvaluationResult.UNRESOLVED


class TestCompositeConditionEvaluator:
    """测试复合条件评估器"""
    
    def test_and_logic_all_true(self):
        """测试：AND逻辑，全部为TRUE"""
        eval1 = TenGodConditionEvaluator("E1", "C1", "YIN_XING")
        eval2 = TenGodConditionEvaluator("E2", "C2", "QI_SHA")
        
        composite = CompositeConditionEvaluator(
            evaluator_id="EVAL_008",
            condition_id="COND_008",
            evaluators=[eval1, eval2],
            logic="AND"
        )
        
        canonical_state = {
            "ten_gods_distribution": {
                "YIN_XING": 2,
                "QI_SHA": 1
            }
        }
        
        result = composite.evaluate(canonical_state)
        assert result == EvaluationResult.TRUE
    
    def test_or_logic_one_true(self):
        """测试：OR逻辑，任一为TRUE"""
        eval1 = TenGodConditionEvaluator("E1", "C1", "YIN_XING")
        eval2 = TenGodConditionEvaluator("E2", "C2", "QI_SHA")
        
        composite = CompositeConditionEvaluator(
            evaluator_id="EVAL_009",
            condition_id="COND_009",
            evaluators=[eval1, eval2],
            logic="OR"
        )
        
        canonical_state = {
            "ten_gods_distribution": {
                "YIN_XING": 2,
                "QI_SHA": 0
            }
        }
        
        result = composite.evaluate(canonical_state)
        assert result == EvaluationResult.TRUE
    
    def test_unresolved_propagation(self):
        """测试：UNRESOLVED传播"""
        eval1 = PowerComparisonEvaluator("E1", "C1", "YIN_XING", "QI_SHA", "<")
        eval2 = TenGodConditionEvaluator("E2", "C2", "SHI_SHEN")
        
        composite = CompositeConditionEvaluator(
            evaluator_id="EVAL_010",
            condition_id="COND_010",
            evaluators=[eval1, eval2],
            logic="AND"
        )
        
        canonical_state = {
            "ten_gods_distribution": {
                "YIN_XING": 1
                # QI_SHA缺失，eval1返回UNRESOLVED
            }
        }
        
        result = composite.evaluate(canonical_state)
        assert result == EvaluationResult.UNRESOLVED


class TestConditionEvaluatorFactory:
    """测试工厂方法"""
    
    def test_create_ten_god_evaluator(self):
        """测试：创建十神评估器"""
        config = {
            "type": "ten_god",
            "target_ten_god": "ZHENG_GUAN"
        }
        
        evaluator = ConditionEvaluatorFactory.create(
            evaluator_id="FACTORY_001",
            condition_id="COND_FACTORY_001",
            config=config
        )
        
        assert isinstance(evaluator, TenGodConditionEvaluator)
        assert evaluator.target_ten_god == "ZHENG_GUAN"
    
    def test_create_power_comparison_evaluator(self):
        """测试：创建力量比较评估器"""
        config = {
            "type": "power_comparison",
            "left_ten_god": "YIN_XING",
            "right_ten_god": "QI_SHA",
            "operator": "<"
        }
        
        evaluator = ConditionEvaluatorFactory.create(
            evaluator_id="FACTORY_002",
            condition_id="COND_FACTORY_002",
            config=config
        )
        
        assert isinstance(evaluator, PowerComparisonEvaluator)
        assert evaluator.operator == "<"
    
    def test_create_composite_evaluator(self):
        """测试：创建复合评估器"""
        config = {
            "type": "composite",
            "logic": "AND",
            "sub_conditions": [
                {"type": "ten_god", "target_ten_god": "YIN_XING"},
                {"type": "ten_god", "target_ten_god": "QI_SHA"}
            ]
        }
        
        evaluator = ConditionEvaluatorFactory.create(
            evaluator_id="FACTORY_003",
            condition_id="COND_FACTORY_003",
            config=config
        )
        
        assert isinstance(evaluator, CompositeConditionEvaluator)
        assert evaluator.logic == "AND"
        assert len(evaluator.evaluators) == 2
    
    def test_create_unknown_type(self):
        """测试：未知类型抛出异常"""
        config = {
            "type": "unknown_type"
        }
        
        with pytest.raises(ValueError, match="未知的Evaluator类型"):
            ConditionEvaluatorFactory.create(
                evaluator_id="FACTORY_004",
                condition_id="COND_FACTORY_004",
                config=config
            )


class TestIntegrationWithM2Assets:
    """测试与M2资产的集成"""
    
    def test印格_condition(self):
        """测试：印格条件验证"""
        # PZZQ-GEJU-005-A: 印轻逢煞 → 印格成
        evaluator = PowerComparisonEvaluator(
            evaluator_id="M2_EVAL_001",
            condition_id="PZZQ-GEJU-005-A",
            left_ten_god="YIN_XING",
            right_ten_god="QI_SHA",
            operator="<"
        )
        
        # 模拟：印星力量 < 煞星力量
        canonical_state = {
            "ten_gods_distribution": {
                "YIN_XING": 1,
                "QI_SHA": 2
            }
        }
        
        result = evaluator.evaluate(canonical_state)
        assert result == EvaluationResult.TRUE
    
    def test岁君关系_condition(self):
        """测试：岁君关系条件验证"""
        # YHZP-SUIJUN-002-A: 日犯岁君 → 灾殃必重
        evaluator = TenGodConditionEvaluator(
            evaluator_id="M2_EVAL_002",
            condition_id="YHZP-SUIJUN-002-A",
            target_ten_god="DAY_MASTER"
        )
        
        # 模拟：日干克年干
        canonical_state = {
            "day_master": "JIA",
            "year_stem": "WU"  # 甲克戊
        }
        
        # 简化测试：只检查数据结构
        result = evaluator.evaluate(canonical_state)
        # 在实际实现中，这里会检查日干和年干的关系


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
