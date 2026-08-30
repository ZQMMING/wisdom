"""
Condition Evaluator - 条件评估器

根据GPT裁决修正后的Schema设计：
1. Condition Mapper ≠ Condition Evaluator
2. 输入：Canonical State（真实BaziChart）
3. 输出：TRUE / FALSE / UNRESOLVED
4. 不能因为"Mapper匹配到了"就认为条件成立

核心原则：
- Evaluator执行真正的逻辑验证
- 必须有明确的计算逻辑
- 输出必须是三元值
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class EvaluationResult(str, Enum):
    """条件评估结果"""
    TRUE = "true"
    FALSE = "false"
    UNRESOLVED = "unresolved"


@dataclass
class EvaluationLog:
    """评估日志"""
    evaluator_id: str
    condition_id: str
    input_state: Dict[str, Any]
    logic_description: str
    output: EvaluationResult
    detail: str
    timestamp: str


class BaseConditionEvaluator:
    """
    条件评估器基类
    
    所有具体的Condition Evaluator必须继承此类，并实现：
    1. evaluate()方法：输入Canonical State，输出EvaluationResult
    2. get_logic()方法：返回评估逻辑描述
    """
    
    def __init__(self, evaluator_id: str, condition_id: str):
        self.evaluator_id = evaluator_id
        self.condition_id = condition_id
        self.evaluation_log: Optional[EvaluationLog] = None
    
    def evaluate(self, canonical_state: Dict[str, Any]) -> EvaluationResult:
        """
        评估条件是否成立
        
        Args:
            canonical_state: Canonical State（真实BaziChart数据）
            
        Returns:
            EvaluationResult: TRUE / FALSE / UNRESOLVED
        """
        raise NotImplementedError("子类必须实现evaluate()方法")
    
    def get_logic(self) -> str:
        """返回评估逻辑描述"""
        raise NotImplementedError("子类必须实现get_logic()方法")
    
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
            timestamp=""  # TODO: 添加时间戳
        )
        logger.debug(f"[Evaluator {self.evaluator_id}] {self.condition_id}: {output.value} - {detail}")


class TenGodConditionEvaluator(BaseConditionEvaluator):
    """
    十神存在性评估器
    
    评估某个十神是否在命盘中存在
    """
    
    def __init__(self, evaluator_id: str, condition_id: str, target_ten_god: str):
        super().__init__(evaluator_id, condition_id)
        self.target_ten_god = target_ten_god
    
    def evaluate(self, canonical_state: Dict[str, Any]) -> EvaluationResult:
        """
        评估目标十神是否存在于命盘中
        
        Args:
            canonical_state: 包含ten_gods_distribution的Canonical State
            
        Returns:
            EvaluationResult: TRUE/FALSE/UNRESOLVED
        """
        ten_gods = canonical_state.get("ten_gods_distribution", {})
        
        if self.target_ten_god not in ten_gods:
            self._log_evaluation(
                canonical_state,
                EvaluationResult.FALSE,
                f"十神{self.target_ten_god}未在命盘中找到"
            )
            return EvaluationResult.FALSE
        
        count = ten_gods[self.target_ten_god]
        if count > 0:
            self._log_evaluation(
                canonical_state,
                EvaluationResult.TRUE,
                f"十神{self.target_ten_god}存在，数量={count}"
            )
            return EvaluationResult.TRUE
        else:
            self._log_evaluation(
                canonical_state,
                EvaluationResult.FALSE,
                f"十神{self.target_ten_god}存在但数量为0"
            )
            return EvaluationResult.FALSE
    
    def get_logic(self) -> str:
        return f"检查十神{self.target_ten_god}是否在命盘中存在"


class PowerComparisonEvaluator(BaseConditionEvaluator):
    """
    力量比较评估器
    
    评估两个十神的力量关系（如：印星力量 < 煞星力量）
    """
    
    def __init__(
        self,
        evaluator_id: str,
        condition_id: str,
        left_ten_god: str,
        right_ten_god: str,
        operator: str  # "<", ">", "=", ">=", "<="
    ):
        super().__init__(evaluator_id, condition_id)
        self.left_ten_god = left_ten_god
        self.right_ten_god = right_ten_god
        self.operator = operator
    
    def evaluate(self, canonical_state: Dict[str, Any]) -> EvaluationResult:
        """
        评估两个十神的力量关系
        
        注意：当前版本简化处理，仅检查存在性
        TODO: 后续实现真正的力量计算（基于月令、通根等）
        """
        ten_gods = canonical_state.get("ten_gods_distribution", {})
        
        left_count = ten_gods.get(self.left_ten_god, 0)
        right_count = ten_gods.get(self.right_ten_god, 0)
        
        if left_count == 0 or right_count == 0:
            self._log_evaluation(
                canonical_state,
                EvaluationResult.UNRESOLVED,
                f"力量计算需要完整的十神力量数据，当前只有存在性信息"
            )
            return EvaluationResult.UNRESOLVED
        
        # 简化判断：仅比较数量
        result = self._compare(left_count, right_count)
        
        self._log_evaluation(
            canonical_state,
            result,
            f"{self.left_ten_god}数量={left_count}, {self.right_ten_god}数量={right_count}, {self.operator}"
        )
        return result
    
    def _compare(self, left: int, right: int) -> EvaluationResult:
        """执行比较逻辑"""
        if self.operator == "<":
            return EvaluationResult.TRUE if left < right else EvaluationResult.FALSE
        elif self.operator == ">":
            return EvaluationResult.TRUE if left > right else EvaluationResult.FALSE
        elif self.operator == "=":
            return EvaluationResult.TRUE if left == right else EvaluationResult.FALSE
        elif self.operator == ">=":
            return EvaluationResult.TRUE if left >= right else EvaluationResult.FALSE
        elif self.operator == "<=":
            return EvaluationResult.TRUE if left <= right else EvaluationResult.FALSE
        else:
            return EvaluationResult.UNRESOLVED
    
    def get_logic(self) -> str:
        return f"比较{self.left_ten_god}和{self.right_ten_god}的力量关系（{self.operator}）"


class PresenceConditionEvaluator(BaseConditionEvaluator):
    """
    透干条件评估器
    
    评估某个十神是否透干（在天干中出现）
    """
    
    def __init__(self, evaluator_id: str, condition_id: str, target_ten_god: str):
        super().__init__(evaluator_id, condition_id)
        self.target_ten_god = target_ten_god
    
    def evaluate(self, canonical_state: Dict[str, Any]) -> EvaluationResult:
        """
        评估目标十神是否透干
        
        Args:
            canonical_state: 包含stems分布的Canonical State
        """
        stems = canonical_state.get("stems", {})
        
        # 检查年干、月干、时干
        for position in ["year", "month", "hour"]:
            if position in stems:
                stem = stems[position]
                # 简化：假设stems中已经包含了十神信息
                if stem == self.target_ten_god:
                    self._log_evaluation(
                        canonical_state,
                        EvaluationResult.TRUE,
                        f"十神{self.target_ten_god}在{position}干透干"
                    )
                    return EvaluationResult.TRUE
        
        self._log_evaluation(
            canonical_state,
            EvaluationResult.FALSE,
            f"十神{self.target_ten_god}未在任何天干透干"
        )
        return EvaluationResult.FALSE
    
    def get_logic(self) -> str:
        return f"检查十神{self.target_ten_god}是否透干"


class CompositeConditionEvaluator(BaseConditionEvaluator):
    """
    复合条件评估器
    
    评估多个子条件的组合（AND/OR逻辑）
    """
    
    def __init__(
        self,
        evaluator_id: str,
        condition_id: str,
        evaluators: List[BaseConditionEvaluator],
        logic: str  # "AND" or "OR"
    ):
        super().__init__(evaluator_id, condition_id)
        self.evaluators = evaluators
        self.logic = logic
    
    def evaluate(self, canonical_state: Dict[str, Any]) -> EvaluationResult:
        """
        评估复合条件
        
        AND逻辑：所有子条件都为TRUE，才返回TRUE
        OR逻辑：任一子条件为TRUE，就返回TRUE
        """
        results = [evaluator.evaluate(canonical_state) for evaluator in self.evaluators]
        
        if self.logic == "AND":
            # AND逻辑：全部为TRUE才返回TRUE
            # 任意一个UNRESOLVED则传播UNRESOLVED
            if all(r == EvaluationResult.TRUE for r in results):
                result = EvaluationResult.TRUE
            elif any(r == EvaluationResult.UNRESOLVED for r in results):
                result = EvaluationResult.UNRESOLVED
            elif any(r == EvaluationResult.FALSE for r in results):
                result = EvaluationResult.FALSE
            else:
                result = EvaluationResult.UNRESOLVED
        elif self.logic == "OR":
            # OR逻辑：任一为TRUE就返回TRUE
            # 全部UNRESOLVED才返回UNRESOLVED
            if any(r == EvaluationResult.TRUE for r in results):
                result = EvaluationResult.TRUE
            elif all(r == EvaluationResult.UNRESOLVED for r in results):
                result = EvaluationResult.UNRESOLVED
            elif any(r == EvaluationResult.FALSE for r in results):
                result = EvaluationResult.FALSE
            else:
                result = EvaluationResult.UNRESOLVED
        else:
            result = EvaluationResult.UNRESOLVED
        
        self._log_evaluation(
            canonical_state,
            result,
            f"复合条件({self.logic}): {results}"
        )
        return result
    
    def get_logic(self) -> str:
        return f"复合条件评估（{self.logic}逻辑）"


class ConditionEvaluatorFactory:
    """
    条件评估器工厂
    
    根据condition_id创建对应的Evaluator
    """
    
    _evaluators = {}
    
    @classmethod
    def register(cls, evaluator_class):
        """注册Evaluator类"""
        cls._evaluators[evaluator_class.__name__] = evaluator_class
    
    @classmethod
    def create(cls, evaluator_id: str, condition_id: str, config: Dict[str, Any]) -> BaseConditionEvaluator:
        """
        创建Evaluator实例
        
        Args:
            evaluator_id: 评估器ID
            condition_id: 条件ID
            config: 配置参数
        """
        evaluator_type = config.get("type", "ten_god")
        
        if evaluator_type == "ten_god":
            return TenGodConditionEvaluator(
                evaluator_id=evaluator_id,
                condition_id=condition_id,
                target_ten_god=config["target_ten_god"]
            )
        elif evaluator_type == "power_comparison":
            return PowerComparisonEvaluator(
                evaluator_id=evaluator_id,
                condition_id=condition_id,
                left_ten_god=config["left_ten_god"],
                right_ten_god=config["right_ten_god"],
                operator=config["operator"]
            )
        elif evaluator_type == "presence":
            return PresenceConditionEvaluator(
                evaluator_id=evaluator_id,
                condition_id=condition_id,
                target_ten_god=config["target_ten_god"]
            )
        elif evaluator_type == "composite":
            # 复合条件需要递归创建子评估器
            sub_evaluators = []
            for i, sub_config in enumerate(config.get("sub_conditions", [])):
                sub_evaluator = cls.create(
                    evaluator_id=f"{evaluator_id}_sub_{i}",
                    condition_id=condition_id,
                    config=sub_config
                )
                sub_evaluators.append(sub_evaluator)
            
            return CompositeConditionEvaluator(
                evaluator_id=evaluator_id,
                condition_id=condition_id,
                evaluators=sub_evaluators,
                logic=config.get("logic", "AND")
            )
        else:
            raise ValueError(f"未知的Evaluator类型: {evaluator_type}")


# 自动注册所有Evaluator
for _cls in [TenGodConditionEvaluator, PowerComparisonEvaluator, PresenceConditionEvaluator, CompositeConditionEvaluator]:
    ConditionEvaluatorFactory.register(_cls)


__all__ = [
    "EvaluationResult",
    "EvaluationLog",
    "BaseConditionEvaluator",
    "TenGodConditionEvaluator",
    "PowerComparisonEvaluator",
    "PresenceConditionEvaluator",
    "CompositeConditionEvaluator",
    "ConditionEvaluatorFactory",
]
