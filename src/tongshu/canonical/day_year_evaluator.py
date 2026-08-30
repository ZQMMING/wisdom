"""
DayYear Relation Evaluator - 日岁关系评估器

验证日干与年干的关系（犯岁君、岁君克日等）
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
import logging

from .condition_evaluator import BaseConditionEvaluator, EvaluationResult, EvaluationLog

logger = logging.getLogger(__name__)


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
    
    # 天干五行属性
    STEM_ELEMENT = {
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
    
    WUXING_GENERATE = {
        "WOOD": "FIRE", "FIRE": "EARTH",
        "EARTH": "METAL", "METAL": "WATER",
        "WATER": "WOOD"
    }
    
    def __init__(
        self,
        evaluator_id: str,
        condition_id: str,
        relation_type: str
    ):
        super().__init__(evaluator_id, condition_id)
        self.relation_type = relation_type
    
    def evaluate(self, canonical_state: Dict[str, Any]) -> EvaluationResult:
        """
        评估日岁关系是否成立
        
        Args:
            canonical_state: Canonical State，包含day_master和year_stem
            
        Returns:
            EvaluationResult:
            - TRUE: 日岁关系成立
            - FALSE: 日岁关系不成立
            - UNRESOLVED: 数据不足，无法判断
        """
        day_master = canonical_state.get("day_master")
        year_stem = canonical_state.get("year_stem")
        relation = canonical_state.get("day_year_relation")
        
        # 检查数据完整性
        if not day_master or not year_stem:
            self._log_evaluation(
                canonical_state,
                EvaluationResult.UNRESOLVED,
                f"日干或年干数据缺失，无法判断日岁关系"
            )
            return EvaluationResult.UNRESOLVED
        
        # 如果已有预计算的关系，直接使用
        if relation:
            result = self._check_precomputed(relation)
            self._log_evaluation(
                canonical_state,
                result,
                f"使用预计算关系: {relation}"
            )
            return result
        
        # 否则自己计算关系
        result = self._calculate_relation(day_master, year_stem)
        self._log_evaluation(
            canonical_state,
            result,
            f"日干{day_master} vs 年干{year_stem}, 关系={result.value}"
        )
        return result
    
    def _check_precomputed(self, relation: str) -> EvaluationResult:
        """检查预计算的关系"""
        if self.relation_type == "DAY_KEEPS_YEAR" and relation == "KE":
            return EvaluationResult.TRUE
        elif self.relation_type == "YEAR_KEEPS_DAY" and relation == "KE":
            # 注意：这里需要区分是日克年还是年克日
            # 简化处理：假设KE已经区分了方向
            return EvaluationResult.TRUE
        elif self.relation_type == "DAY_GENERATES_YEAR" and relation == "SHENG":
            return EvaluationResult.TRUE
        elif self.relation_type == "YEAR_GENERATES_DAY" and relation == "SHENG":
            return EvaluationResult.TRUE
        elif self.relation_type == "DAY_TONG_YEAR" and relation in ["TONG", "BI"]:
            return EvaluationResult.TRUE
        else:
            return EvaluationResult.FALSE
    
    def _calculate_relation(self, day_master: str, year_stem: str) -> EvaluationResult:
        """
        计算日干与年干的关系
        
        返回：
        - TRUE: 关系成立
        - FALSE: 关系不成立
        - UNRESOLVED: 无法判断（数据缺失）
        """
        day_element = self.STEM_ELEMENT.get(day_master)
        year_element = self.STEM_ELEMENT.get(year_stem)
        
        if not day_element or not year_element:
            return EvaluationResult.UNRESOLVED
        
        if self.relation_type == "DAY_KEEPS_YEAR":
            # 日干克年干
            return EvaluationResult.TRUE if self.WUXING_KEEP.get(day_element) == year_element else EvaluationResult.FALSE
        
        elif self.relation_type == "YEAR_KEEPS_DAY":
            # 年干克日干
            return EvaluationResult.TRUE if self.WUXING_KEEP.get(year_element) == day_element else EvaluationResult.FALSE
        
        elif self.relation_type == "DAY_GENERATES_YEAR":
            # 日干生年干
            return EvaluationResult.TRUE if self.WUXING_GENERATE.get(day_element) == year_element else EvaluationResult.FALSE
        
        elif self.relation_type == "YEAR_GENERATES_DAY":
            # 年干生日干
            return EvaluationResult.TRUE if self.WUXING_GENERATE.get(year_element) == day_element else EvaluationResult.FALSE
        
        elif self.relation_type == "DAY_TONG_YEAR":
            # 日干与年干同类（比和）
            return EvaluationResult.TRUE if day_element == year_element else EvaluationResult.FALSE
        
        else:
            return EvaluationResult.UNRESOLVED
    
    def get_logic(self) -> str:
        return f"验证日干与年干的{self.relation_type}关系"
    
    def _log_evaluation(
        self,
        input_state: Dict[str, Any],
        output: EvaluationResult,
        detail: str
    ):
        """记录评估日志"""
        self.evaluation_log = EvaluationLog(
            evaluator_id=self.evaluator_id,
            condition_id=self.condition_id,
            input_state=input_state,
            logic_description=self.get_logic(),
            output=output,
            detail=detail,
            timestamp=""
        )
        logger.debug(f"[DayYearEvaluator {self.evaluator_id}] {self.condition_id}: {output.value} - {detail}")


__all__ = ["DayYearRelationEvaluator"]
