"""
Enhanced RootConditionEvaluator - 增强版根气评估器

使用TenGodToStemMapper进行十神到天干的映射
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Set
import logging

from .condition_evaluator import (
    EvaluationResult,
    BaseConditionEvaluator,
)
from .tengod_mapper import TenGodToStemMapper

logger = logging.getLogger(__name__)


@dataclass
class RootConditionEvaluator(BaseConditionEvaluator):
    """
    根气条件评估器 - 增强版
    
    通过TenGodToStemMapper将十神名称映射到天干，
    然后检查该天干在地支中是否有根。
    """
    
    target_ten_god: str = ""
    day_master: str = "JIA"
    strict_mode: bool = False
    
    mapper: TenGodToStemMapper = field(init=False)
    
    def __post_init__(self):
        BaseConditionEvaluator.__init__(self, "", "")
        self.mapper = TenGodToStemMapper()
        logger.info(
            f"[RootEvaluator] Initialized with ten_god={self.target_ten_god}, "
            f"day_master={self.day_master}, strict={self.strict_mode}"
        )
    
    def evaluate(self, canonical_state: Dict[str, Any]) -> EvaluationResult:
        """
        评估目标十神是否有根
        
        Args:
            canonical_state: Canonical State，包含：
                - ten_gods_distribution: 十神分布
                - branches: 地支分布
                - day_master: 日干（可选）
        
        Returns:
            EvaluationResult:
                - TRUE: 目标十神有根
                - FALSE: 目标十神无根
                - UNRESOLVED: 数据不足或映射失败
        """
        self._start_evaluation(canonical_state)
        
        # 获取地支分布
        branches = canonical_state.get("branches", {})
        if not branches:
            result = self._log_evaluation(
                canonical_state,
                EvaluationResult.UNRESOLVED,
                "缺少地支分布数据"
            )
            return result
        
        # 获取日干
        day_master = canonical_state.get("day_master", self.day_master)
        
        # 使用映射器检查根气
        try:
            has_root = self.mapper.check_has_root(
                self.target_ten_god,
                branches,
                day_master
            )
        except Exception as e:
            logger.error(
                f"[RootEvaluator] Error checking root for {self.target_ten_god}: {e}"
            )
            result = self._log_evaluation(
                canonical_state,
                EvaluationResult.UNRESOLVED,
                f"评估过程中出错: {str(e)}"
            )
            return result
        
        # 根据结果记录日志
        if has_root:
            result = self._log_evaluation(
                canonical_state,
                EvaluationResult.TRUE,
                f"十神{self.target_ten_god}(日干{day_master})有根"
            )
        else:
            if self.strict_mode:
                result = self._log_evaluation(
                    canonical_state,
                    EvaluationResult.FALSE,
                    f"十神{self.target_ten_god}(日干{day_master})无根"
                )
            else:
                result = self._log_evaluation(
                    canonical_state,
                    EvaluationResult.FALSE,
                    f"十神{self.target_ten_god}(日干{day_master})无根，但非严格模式"
                )
        
        self._finish_evaluation(canonical_state, result)
        return result

    def get_logic(self) -> str:
        return f"检查十神{self.target_ten_god}在日干{self.day_master}下是否有根"

    def get_mapping_info(self) -> Dict[str, Any]:
        """
        获取映射信息（用于调试）
        """
        stem = self.mapper.map_ten_god_to_stem(
            self.target_ten_god,
            self.day_master
        )
        roots = self.mapper.get_root_stems(
            self.target_ten_god,
            self.day_master
        )
        
        return {
            "evaluator_id": self.evaluator_id,
            "condition_id": self.condition_id,
            "target_ten_god": self.target_ten_god,
            "day_master": self.day_master,
            "mapped_stem": stem,
            "possible_roots": list(roots) if roots else [],
        }
    
    def __repr__(self):
        info = self.get_mapping_info()
        return (
            f"RootConditionEvaluator("
            f"ten_god={info['target_ten_god']}, "
            f"day={info['day_master']}, "
            f"mapped_to={info['mapped_stem']})"
        )


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/d/shuntian/backend")
    
    # 测试增强版RootEvaluator
    from src.tongshu.canonical.root_evaluator_v2 import RootConditionEvaluator
    
    print("=== Enhanced RootEvaluator Test ===")
    print()
    
    # 测试1：印星有根
    eval1 = RootConditionEvaluator(
        evaluator_id="ROOT_TEST_001",
        condition_id="TEST_001",
        target_ten_god="YIN_XING",
        day_master="JIA",
        strict_mode=False
    )
    
    canonical_state_1 = {
        "ten_gods_distribution": {"YIN_XING": 1},
        "branches": {"YIN": 1, "MAO": 1},  # 寅藏甲丙戊，卯藏乙
        "day_master": "JIA"
    }
    
    result1 = eval1.evaluate(canonical_state_1)
    print(f"Test 1: YIN_XING (day=JIA) in {{YIN:1, MAO:1}} -> {result1}")
    print(f"  Mapping: {eval1.get_mapping_info()}")
    
    # 测试2：伤官无根
    eval2 = RootConditionEvaluator(
        evaluator_id="ROOT_TEST_002",
        condition_id="TEST_002",
        target_ten_god="SHANGGUAN",
        day_master="JIA",
        strict_mode=False
    )
    
    canonical_state_2 = {
        "ten_gods_distribution": {"SHANGGUAN": 1},
        "branches": {"ZIW": 1},  # 子藏癸，无火根
        "day_master": "JIA"
    }
    
    result2 = eval2.evaluate(canonical_state_2)
    print(f"Test 2: SHANGGUAN (day=JIA) in {{ZIW:1}} -> {result2}")
    print(f"  Mapping: {eval2.get_mapping_info()}")
    
    # 测试3：数据缺失
    eval3 = RootConditionEvaluator(
        evaluator_id="ROOT_TEST_003",
        condition_id="TEST_003",
        target_ten_god="SHANGGUAN",
        day_master="JIA",
        strict_mode=False
    )
    
    canonical_state_3 = {
        "ten_gods_distribution": {"SHANGGUAN": 1},
        "day_master": "JIA"
        # 缺少branches
    }
    
    result3 = eval3.evaluate(canonical_state_3)
    print(f"Test 3: SHANGGUAN (day=JIA) missing branches -> {result3}")
    
    print()
    print("=== All tests completed ===")
