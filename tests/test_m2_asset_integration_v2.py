"""
M2资产集成测试 - NegationEvaluator和DayYearRelationEvaluator版本

验证新增的NegationEvaluator和DayYearRelationEvaluator
"""

import pytest
from src.tongshu.canonical.condition_evaluator import (
    EvaluationResult,
    TenGodConditionEvaluator,
    PowerComparisonEvaluator,
    CompositeConditionEvaluator,
)
from src.tongshu.canonical.negation_evaluator import NegationConditionEvaluator
from src.tongshu.canonical.day_year_evaluator import DayYearRelationEvaluator


class TestNegationEvaluator:
    """测试否定条件评估器"""
    
    def test_not_present_true(self):
        """测试：十神不存在，否定条件成立"""
        evaluator = NegationConditionEvaluator(
            evaluator_id="NEG_001",
            condition_id="PZZQ-GEJU-007",
            target_ten_god="SHANGGUAN"
        )
        
        canonical_state = {
            "ten_gods_distribution": {
                "YANGREN": 1,
                "ZHENG_GUAN": 1,
                "PIAN_CAI": 1,
                "SHANGGUAN": 0  # 伤官不存在
            }
        }
        
        result = evaluator.evaluate(canonical_state)
        assert result == EvaluationResult.TRUE
    
    def test_not_present_false(self):
        """测试：十神存在，否定条件不成立"""
        evaluator = NegationConditionEvaluator(
            evaluator_id="NEG_002",
            condition_id="PZZQ-GEJU-007",
            target_ten_god="SHANGGUAN"
        )
        
        canonical_state = {
            "ten_gods_distribution": {
                "YANGREN": 1,
                "ZHENG_GUAN": 1,
                "PIAN_CAI": 1,
                "SHANGGUAN": 2  # 伤官存在
            }
        }
        
        result = evaluator.evaluate(canonical_state)
        assert result == EvaluationResult.FALSE
    
    def test_not_present_missing(self):
        """测试：十神数据缺失，返回UNRESOLVED"""
        evaluator = NegationConditionEvaluator(
            evaluator_id="NEG_003",
            condition_id="PZZQ-GEJU-007",
            target_ten_god="SHANGGUAN"
        )
        
        canonical_state = {
            "ten_gods_distribution": {
                "YANGREN": 1,
                "ZHENG_GUAN": 1
                # 缺少SHANGGUAN数据
            }
        }
        
        result = evaluator.evaluate(canonical_state)
        assert result == EvaluationResult.UNRESOLVED


class TestDayYearRelationEvaluator:
    """测试日岁关系评估器"""
    
    def test_day_fans_suijun_true(self):
        """
        测试：日犯岁君（日干克年干）

        甲日干（木）克戊年干（土）→ 日犯岁君
        """
        evaluator = DayYearRelationEvaluator(
            evaluator_id="DAYYEAR_001",
            condition_id="YHZP-SUIJUN-002-A",
            relation_type="day_fans_suijun"  # 日干克年干
        )

        canonical_state = {
            "day_master": "JIA",  # 甲木
            "year_stem": "WU",    # 戊土
            "day_year_relation": "KE"  # 克关系
        }

        result = evaluator.evaluate(canonical_state)
        assert result == EvaluationResult.TRUE
    
    def test_day_fans_suijun_false(self):
        """测试：日干不克年干，日犯岁君不成立"""
        evaluator = DayYearRelationEvaluator(
            evaluator_id="DAYYEAR_002",
            condition_id="YHZP-SUIJUN-002-A",
            relation_type="DAY_KEEPS_YEAR"
        )
        
        canonical_state = {
            "day_master": "JIA",  # 甲木
            "year_stem": "JIA",   # 甲木（比和，不是克）
            "day_year_relation": "TONG"  # 同类关系
        }
        
        result = evaluator.evaluate(canonical_state)
        assert result == EvaluationResult.FALSE
    
    def test_year_keeps_day_true(self):
        """
        测试：岁君克日（年干克日干）

        庚年干（金）克甲日干（木）→ 岁君克日
        """
        evaluator = DayYearRelationEvaluator(
            evaluator_id="DAYYEAR_003",
            condition_id="YHZP-SUIJUN-TEST",
            relation_type="year_keeps_day"  # 年干克日干
        )

        canonical_state = {
            "day_master": "JIA",  # 甲木
            "year_stem": "GENG",  # 庚金（金克木 = 岁君克日）
            "day_year_relation": "KE"  # 年干克日干
        }

        result = evaluator.evaluate(canonical_state)
        assert result == EvaluationResult.TRUE
    
    def test_day_year_missing(self):
        """测试：日干或年干数据缺失，返回UNRESOLVED"""
        evaluator = DayYearRelationEvaluator(
            evaluator_id="DAYYEAR_004",
            condition_id="YHZP-SUIJUN-TEST",
            relation_type="DAY_KEEPS_YEAR"
        )
        
        canonical_state = {
            "day_master": "JIA",
            # 缺少year_stem
        }
        
        result = evaluator.evaluate(canonical_state)
        assert result == EvaluationResult.UNRESOLVED


class TestM2Asset_FullIntegration:
    """M2资产完整集成测试（使用新Evaluator）"""
    
    def test_PZZQ_GEJU_007_阳刃格完整验证(self):
        """
        PZZQ-GEJU-007: 阳刃透官煞而露财印，不见伤官 → 阳刃格成
        
        现在可以使用NegationEvaluator验证"不见伤官"
        """
        # 阳刃存在
        eval_yangren = TenGodConditionEvaluator(
            evaluator_id="M2_GEJU_007_1",
            condition_id="PZZQ-GEJU-007-YANGREN",
            target_ten_god="YANGREN"
        )
        
        # 官煞存在
        eval_guan = TenGodConditionEvaluator(
            evaluator_id="M2_GEJU_007_2",
            condition_id="PZZQ-GEJU-007-GUAN",
            target_ten_god="ZHENG_GUAN"
        )
        
        # 财印存在
        eval_cai = TenGodConditionEvaluator(
            evaluator_id="M2_GEJU_007_3",
            condition_id="PZZQ-GEJU-007-CAI",
            target_ten_god="PIAN_CAI"
        )
        
        # 不见伤官（使用NegationEvaluator）
        eval_no_shangguan = NegationConditionEvaluator(
            evaluator_id="M2_GEJU_007_4",
            condition_id="PZZQ-GEJU-007-NOSHANGGUAN",
            target_ten_god="SHANGGUAN"
        )
        
        # 主条件：阳刃 + 官煞 + 财印（AND）
        main_conditions = CompositeConditionEvaluator(
            evaluator_id="M2_GEJU_007_MAIN",
            condition_id="PZZQ-GEJU-007-MAIN",
            evaluators=[eval_yangren, eval_guan, eval_cai],
            logic="AND"
        )
        
        # 完整条件：主条件 + 不见伤官（AND）
        complete_condition = CompositeConditionEvaluator(
            evaluator_id="M2_GEJU_007_COMPLETE",
            condition_id="PZZQ-GEJU-007",
            evaluators=[main_conditions, eval_no_shangguan],
            logic="AND"
        )
        
        canonical_state = {
            "ten_gods_distribution": {
                "YANGREN": 1,
                "ZHENG_GUAN": 1,
                "PIAN_CAI": 1,
                "SHANGGUAN": 0  # 伤官不存在
            }
        }
        
        result = complete_condition.evaluate(canonical_state)
        assert result == EvaluationResult.TRUE
    
    def test_YHZP_SUIJUN_002A_日犯岁君完整验证(self):
        """
        YHZP-SUIJUN-002-A: 日犯岁君 → 灾殃必重

        现在可以使用DayYearRelationEvaluator验证
        """
        evaluator = DayYearRelationEvaluator(
            evaluator_id="M2_SUIJUN_002A",
            condition_id="YHZP-SUIJUN-002-A",
            relation_type="day_fans_suijun"
        )

        canonical_state = {
            "day_master": "JIA",
            "year_stem": "WU",
            "day_year_relation": "KE"
        }

        result = evaluator.evaluate(canonical_state)
        assert result == EvaluationResult.TRUE
    
    def test_YHZP_SUIJUN_003A_犯岁君者完整验证(self):
        """
        YHZP-SUIJUN-003-A: 犯岁君者 → 其年必主凶丧

        与002-A使用相同的Condition
        """
        evaluator = DayYearRelationEvaluator(
            evaluator_id="M2_SUIJUN_003A",
            condition_id="YHZP-SUIJUN-003-A",
            relation_type="day_fans_suijun"
        )

        canonical_state = {
            "day_master": "REN",  # 壬水
            "year_stem": "BING",   # 丙火（壬水克丙火 = 日犯岁君）
            "day_year_relation": "KE"
        }

        result = evaluator.evaluate(canonical_state)
        assert result == EvaluationResult.TRUE
    
    def test_PZZQ_GEJU_007_条件不成立(self):
        """阳刃格条件不成立的情况（伤官存在）"""
        eval_yangren = TenGodConditionEvaluator(
            evaluator_id="M2_GEJU_007_FAIL_1",
            condition_id="PZZQ-GEJU-007-YANGREN",
            target_ten_god="YANGREN"
        )
        
        eval_guan = TenGodConditionEvaluator(
            evaluator_id="M2_GEJU_007_FAIL_2",
            condition_id="PZZQ-GEJU-007-GUAN",
            target_ten_god="ZHENG_GUAN"
        )
        
        eval_cai = TenGodConditionEvaluator(
            evaluator_id="M2_GEJU_007_FAIL_3",
            condition_id="PZZQ-GEJU-007-CAI",
            target_ten_god="PIAN_CAI"
        )
        
        eval_no_shangguan = NegationConditionEvaluator(
            evaluator_id="M2_GEJU_007_FAIL_4",
            condition_id="PZZQ-GEJU-007-NOSHANGGUAN",
            target_ten_god="SHANGGUAN"
        )
        
        main_conditions = CompositeConditionEvaluator(
            evaluator_id="M2_GEJU_007_FAIL_MAIN",
            condition_id="PZZQ-GEJU-007-MAIN",
            evaluators=[eval_yangren, eval_guan, eval_cai],
            logic="AND"
        )
        
        complete_condition = CompositeConditionEvaluator(
            evaluator_id="M2_GEJU_007_FAIL_COMPLETE",
            condition_id="PZZQ-GEJU-007",
            evaluators=[main_conditions, eval_no_shangguan],
            logic="AND"
        )
        
        canonical_state = {
            "ten_gods_distribution": {
                "YANGREN": 1,
                "ZHENG_GUAN": 1,
                "PIAN_CAI": 1,
                "SHANGGUAN": 2  # 伤官存在，条件不成立
            }
        }
        
        result = complete_condition.evaluate(canonical_state)
        assert result == EvaluationResult.FALSE


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
