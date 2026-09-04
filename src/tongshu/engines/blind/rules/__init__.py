"""盲派规则图系统 — 支持 requires + invalidates 的规则匹配引擎。

P0-RULE-GRAPH: 将硬编码 if/elif 分支替换为可配置的规则图。
"""
from __future__ import annotations

from .models import Rule, MatchContext
from .matcher import RuleMatcher
from .graph import RuleGraph

__all__ = ["Rule", "MatchContext", "RuleMatcher", "RuleGraph"]
