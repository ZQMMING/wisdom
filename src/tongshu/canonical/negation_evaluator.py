"""
Negation Condition Evaluator - 否定条件评估器

验证某个十神在命盘中不存在（数量为0或未出现）
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
import logging

from .condition_evaluator import BaseConditionEvaluator, EvaluationResult, EvaluationLog

logger = logging.getLogger(__name__)


@dataclass
class NegationConditionEvaluator(BaseConditionEvaluator):
    """
    否定条件评估器
    
    验证目标十神在命盘中不存在（数量为0或未出现）
    
    应用场景：
    - "不见伤官" → 验证伤官数量=0
    - "无刑冲破害" → 验证特定关系不存在
    - "不逢XX" → 验证某十神未出现
    """
    
    def __init__(self, evaluator_id: str, condition_id: str, target_ten_god: str):
        super().__init__(evaluator_id, condition_id)
        self.target_ten_god = target_ten_god
    
    def evaluate(self, canonical_state: Dict[str, Any]) -> EvaluationResult:
        """
        评估目标十神是否不存在
        
        Args:
            canonical_state: Canonical State，包含ten_gods_distribution
            
        Returns:
            EvaluationResult: 
            - TRUE: 目标十神不存在（数量为0或未出现）
            - FALSE: 目标十神存在（数量>0）
            - UNRESOLVED: 数据不足，无法判断
        """
        ten_gods = canonical_state.get("ten_gods_distribution", {})
        
        # 检查目标十神是否存在于分布中
        if self.target_ten_god not in ten_gods:
            self._log_evaluation(
                canonical_state,
                EvaluationResult.TRUE,
                f"十神{self.target_ten_god}未在命盘中出现，否定条件成立"
            )
            return EvaluationResult.TRUE
        
        # 获取数量
        count = ten_gods[self.target_ten_god]
        
        if count == 0:
            self._log_evaluation(
                canonical_state,
                EvaluationResult.TRUE,
                f"十神{self.target_ten_god}存在但数量为0，否定条件成立"
            )
            return EvaluationResult.TRUE
        
        # 数量>0，否定条件不成立
        self._log_evaluation(
            canonical_state,
            EvaluationResult.FALSE,
            f"十神{self.target_ten_god}存在，数量={count}，否定条件不成立"
        )
        return EvaluationResult.FALSE
    
    def get_logic(self) -> str:
        return f"验证十神{self.target_ten_god}不存在于命盘中"
    
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
        logger.debug(f"[NegationEvaluator {self.evaluator_id}] {self.condition_id}: {output.value} - {detail}")


__all__ = ["NegationConditionEvaluator"]
