"""
飞星派规则图谱（向后兼容层）— Z13

本模块为已删除的 feixing_rule_graph.py 提供向后兼容。
公共事实层已迁移至 stem_facts.py。

Public API（保持与旧接口一致）：
    PalaceStemContract    — 宫干事实契约（静态方法）
    FlyingTransformFact   — 单次飞化事实 dataclass
    PalaceStemFact        — 单宫宫干事实 dataclass
    FeixingRuleGraph      — 飞星派 RuleGraph（独立类）
    FeixingRuleMatch      — 单条匹配结果 dataclass
    FeixingRuleGraphResult — 整体 match 结果 dataclass
    make_feixing_rule_graph — 工厂函数
    create_feixing_rule_graph — 工厂函数别名（向后兼容）
"""
from __future__ import annotations

from typing import Any

from .stem_facts import FlyingTransformFact, PalaceStemFact, PalaceStemContract
from .rule_graph import (
    FeixingRuleGraph,
    FeixingRuleMatch,
    FeixingRuleGraphResult,
    make_feixing_rule_graph,
)

# 向后兼容别名
create_feixing_rule_graph = make_feixing_rule_graph

__all__ = [
    "PalaceStemFact",
    "FlyingTransformFact",
    "PalaceStemContract",
    "FeixingRuleGraph",
    "FeixingRuleMatch",
    "FeixingRuleGraphResult",
    "make_feixing_rule_graph",
    "create_feixing_rule_graph",
]
