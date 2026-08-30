"""
DayYear Relation Evaluator - 日岁关系评估器

验证日干与年干的生克关系（犯岁君、岁君克日等）
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
import logging

from .condition_evaluator import BaseConditionEvaluator, EvaluationResult, EvaluationLog

logger = logging.getLogger(__name__)

# 天干五行属性
STEM_WUXING = {
    "JIA": "WOOD", "YI": "WOOD",
    "BING": "FIRE", "DING": "FIRE",
    "WU": "EARTH", "JI": "EARTH",
    "GENG": "METAL", "XIN": "METAL",
    "REN": "WATER", "GUI": "WATER"
}

# 五行生克关系
WUXING_KEEP = {
    "WOOD": "EARTH", "EARTH": "WATER",
    "WATER": "FIRE", "FIRE": "METAL",
    "METAL": "WOOD"
}


@dataclass
class DayYearRelationEvaluator(BaseConditionEvaluator):
    """
    日岁关系评估器
    
    验证日干与年干的生克关系
    
    关系类型：
    - DAY_KEEPS_YEAR: 日干克年干（日犯岁君）
    - YEAR_KEEPS_DAY: 年干克日干（岁君克日）
    - DAY_GENERATES_YEAR: 日干生年干
    - YEAR_GENERATES_DAY: 年干生日干
    - DAY_TONG_YEAR: 日干与年干同类（比和）
    """
    
    def __init__(
        self,
        evaluator_id: str,
        condition_id: str,
        relation_type: str
    ):
        super().__init__(evaluator_id, condition_id)
        self.relation_type = relation_type
        logger.info(
            f"[DayYearRelation] Initialized with relation_type={relation_type}"
        )
    
    def evaluate(self, canonical_state: Dict[str, Any]) -> EvaluationResult:
        """
        评估日岁关系是否成立

        Args:
            canonical_state: Canonical State，包含：
                - day_stem: 日干（如 "JIA"）
                - year_stem: 年干（如 "WU"）
                - day_master: 日干（同day_stem，兼容不同命名）

        Returns:
            EvaluationResult:
                - TRUE: 日岁关系成立
                - FALSE: 日岁关系不成立
                - UNRESOLVED: 数据不足，无法判断
        """
        # 获取日干和年干
        day_stem = canonical_state.get("day_stem") or canonical_state.get("day_master")
        year_stem = canonical_state.get("year_stem")
        
        # 检查数据完整性
        if not day_stem or not year_stem:
            result = self._log_evaluation(
                canonical_state,
                EvaluationResult.UNRESOLVED,
                "缺少日干或年干数据，无法判断日岁关系"
            )
            return result
        
        # 验证天干有效性
        if day_stem not in STEM_WUXING or year_stem not in STEM_WUXING:
            result = self._log_evaluation(
                canonical_state,
                EvaluationResult.UNRESOLVED,
                f"无效的天干数据: day={day_stem}, year={year_stem}"
            )
            return result
        
        # 计算五行生克关系
        day_wuxing = STEM_WUXING[day_stem]
        year_wuxing = STEM_WUXING[year_stem]
        
        logger.debug(
            f"[DayYearRelation] day_stem={day_stem}({day_wuxing}), "
            f"year_stem={year_stem}({year_wuxing})"
        )
        
        # 根据关系类型评估
        result = self._check_relation(day_wuxing, year_wuxing)
        
        logger.debug(
            f"[DayYearRelation] {self.condition_id}: {result.value} - "
            f"{day_stem}({day_wuxing}) vs {year_stem}({year_wuxing})"
        )
        return result
    
    def _check_relation(self, day_wuxing: str, year_wuxing: str) -> EvaluationResult:
        """
        检查五行生克关系
        
        Args:
            day_wuxing: 日干五行
            year_wuxing: 年干五行
        
        Returns:
            EvaluationResult
        """
        # 同类（比和）
        if day_wuxing == year_wuxing:
            logger.debug(f"[DayYearRelation] 同类（比和）: {day_wuxing}")
            if self.relation_type == "day_tong_year":
                return EvaluationResult.TRUE
            else:
                return EvaluationResult.FALSE
        
        # 日干克年干（日犯岁君）
        if WUXING_KEEP.get(day_wuxing) == year_wuxing:
            logger.debug(f"[DayYearRelation] 日干克年干（日犯岁君）: {day_wuxing}克{year_wuxing}")
            if self.relation_type == "day_fans_suijun":
                return EvaluationResult.TRUE
            else:
                return EvaluationResult.FALSE
        
        # 年干克日干（岁君克日）
        if WUXING_KEEP.get(year_wuxing) == day_wuxing:
            logger.debug(f"[DayYearRelation] 年干克日干（岁君克日）: {year_wuxing}克{day_wuxing}")
            if self.relation_type == "year_keeps_day":
                return EvaluationResult.TRUE
            else:
                return EvaluationResult.FALSE
        
        # 日干生年干
        WUXING_GENERATE = {
            "WOOD": "FIRE", "FIRE": "EARTH",
            "EARTH": "METAL", "METAL": "WATER",
            "WATER": "WOOD"
        }
        if WUXING_GENERATE.get(day_wuxing) == year_wuxing:
            logger.debug(f"[DayYearRelation] 日干生年干: {day_wuxing}生{year_wuxing}")
            if self.relation_type == "day_generates_year":
                return EvaluationResult.TRUE
            else:
                return EvaluationResult.FALSE
        
        # 年干生日干
        if WUXING_GENERATE.get(year_wuxing) == day_wuxing:
            logger.debug(f"[DayYearRelation] 年干生日干: {year_wuxing}生{day_wuxing}")
            if self.relation_type == "year_generates_day":
                return EvaluationResult.TRUE
            else:
                return EvaluationResult.FALSE
        
        # 无法判断的关系
        logger.warning(
            f"[DayYearRelation] 无法判断的关系: {day_wuxing} vs {year_wuxing}"
        )
        return EvaluationResult.UNRESOLVED
    
    def get_logic(self) -> str:
        return f"评估日干与年干的{self.relation_type}关系"
    
    def __repr__(self):
        return (
            f"DayYearRelationEvaluator("
            f"relation_type={self.relation_type})"
        )


if __name__ == "__main__":
    # 测试日岁关系评估器
    eval_day_year = DayYearRelationEvaluator(
        evaluator_id="TEST_DAY_YEAR",
        condition_id="TEST_001",
        relation_type="day_fans_suijun"
    )
    
    # 测试1: 甲木日干，戊土年干 = 木克土 = 日犯岁君
    canonical_state_1 = {
        "day_stem": "JIA",
        "year_stem": "WU",
        "day_master": "JIA"
    }
    
    result1 = eval_day_year.evaluate(canonical_state_1)
    print(f"Test 1: JIA(木) vs WU(土) = 木克土 -> {result1}")
    assert result1 == EvaluationResult.TRUE, "甲木克戊土，应该是日犯岁君"
    
    # 测试2: 戊土日干，甲木年干 = 木克土 = 岁君克日
    eval_year_keeps = DayYearRelationEvaluator(
        evaluator_id="TEST_YEAR_KEEPS",
        condition_id="TEST_002",
        relation_type="year_keeps_day"
    )
    
    canonical_state_2 = {
        "day_stem": "WU",
        "year_stem": "JIA",
        "day_master": "WU"
    }
    
    result2 = eval_year_keeps.evaluate(canonical_state_2)
    print(f"Test 2: WU(土) vs JIA(木) = 木克土 -> {result2}")
    assert result2 == EvaluationResult.TRUE, "甲木克戊土，应该是岁君克日"
    
    # 测试3: 缺少数据
    canonical_state_3 = {
        "day_stem": "JIA"
        # 缺少year_stem
    }
    
    result3 = eval_day_year.evaluate(canonical_state_3)
    print(f"Test 3: missing year_stem -> {result3}")
    assert result3 == EvaluationResult.UNRESOLVED, "缺少数据应该返回UNRESOLVED"
    
    print("\n=== All tests passed ===")
