"""
Root Condition Evaluator - 根气评估器

验证某个十神是否有根（在地支藏干中出现）
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Set
import logging

from .condition_evaluator import BaseConditionEvaluator, EvaluationResult, EvaluationLog

logger = logging.getLogger(__name__)


# 地支藏干表（简化版）
BRANCH_HIDDEN_STEMS = {
    "ZI": {"GUI"},           # 子藏癸水
    "CHOU": {"JI", "XIN", "GUI"},   # 丑藏己辛癸
    "YIN": {"JIA", "BING", "WU"},   # 寅藏甲丙戊
    "MAO": {"YI"},           # 卯藏乙木
    "CHEN": {"WU", "YI", "GUI"},   # 辰藏戊乙癸
    "SI": {"BING", "WU", "GENG"},   # 巳藏丙戊庚
    "WU": {"DING", "JI"},   # 午藏丁己
    "WEI": {"JI", "DING", "YI"},   # 未藏己丁乙
    "SHEN": {"GENG", "REN", "WU"},   # 申藏庚壬戊
    "YOU": {"XIN"},          # 酉藏辛金
    "XU": {"WU", "XIN", "DING"},   # 戌藏戊辛丁
    "HAI": {"REN", "JIA"},   # 亥藏壬甲
}


@dataclass
class RootConditionEvaluator(BaseConditionEvaluator):
    """
    根气评估器
    
    验证目标十神是否在地支藏干中有根
    
    应用场景：
    - "印有根" → 验证印星在地支藏干中存在
    - "伤官旺" → 需要更复杂的力量计算，此Evaluator仅验证存在性
    """
    
    def __init__(self, evaluator_id: str, condition_id: str, target_ten_god: str):
        super().__init__(evaluator_id, condition_id)
        self.target_ten_god = target_ten_god
    
    def evaluate(self, canonical_state: Dict[str, Any]) -> EvaluationResult:
        """
        评估目标十神是否有根
        
        Args:
            canonical_state: Canonical State，包含branches分布
            
        Returns:
            EvaluationResult:
            - TRUE: 目标十神在地支藏干中存在（有根）
            - FALSE: 目标十神在地支藏干中不存在（无根）
            - UNRESOLVED: 数据不足，无法判断
        """
        branches = canonical_state.get("branches", {})
        
        if not branches:
            self._log_evaluation(
                canonical_state,
                EvaluationResult.UNRESOLVED,
                f"地支数据缺失，无法判断{self.target_ten_god}是否有根"
            )
            return EvaluationResult.UNRESOLVED
        
        # 检查所有地支的藏干
        has_root = False
        root_locations = []
        
        for branch in branches.keys():
            hidden_stems = BRANCH_HIDDEN_STEMS.get(branch, set())
            # 简化：直接检查ten_god名称是否在藏干中
            if self.target_ten_god in hidden_stems:
                has_root = True
                root_locations.append(branch)
        
        if has_root:
            self._log_evaluation(
                canonical_state,
                EvaluationResult.TRUE,
                f"十神{self.target_ten_god}在地支{root_locations}中有根"
            )
            return EvaluationResult.TRUE
        else:
            self._log_evaluation(
                canonical_state,
                EvaluationResult.FALSE,
                f"十神{self.target_ten_god}在地支中无根"
            )
            return EvaluationResult.FALSE
    
    def get_logic(self) -> str:
        return f"验证十神{self.target_ten_god}是否在地支藏干中有根"
    
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
        logger.debug(f"[RootEvaluator {self.evaluator_id}] {self.condition_id}: {output.value} - {detail}")


__all__ = ["RootConditionEvaluator"]
