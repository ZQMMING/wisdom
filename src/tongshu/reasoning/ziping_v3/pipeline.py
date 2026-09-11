# -*- coding: utf-8 -*-
"""ZIPING V3.1 §79 依赖图编排器 (REV-AR 裁决链并行化).

子平**不是**单链流水线 (REV-AR-003): 是并行诊断域 + 显式依赖关系。
本编排器按 §79 依赖图串接, 但域内互不阻塞 (并行), 域间按依赖边喂入。

依赖图 (§79):
    FrozenBazi → 事实层
      ├─ 月令/根气/干支结构/气势源流   (基础域, 无上游域依赖)
      ├─ 特殊结构 (SPECIAL, P1 优先, 决定普通判断是否适用)
      ├─ 病药/通关/调候/寒暖燥湿       (独立诊断域)
      ├─ 格局系统 (PATTERN)            (依赖 月令/根)
      ├─ 清浊/真假/有情/有力           (依赖 格局)
      └─ 用神体系 (YONG, 六方法隔离)  (依赖 格局/调候/病药/通关/特殊/相神)
             → 喜忌 (XIJI, 七输入)
             → 时间 Overlay (TEMPORAL)
             → Final ZiPing State

编排规则:
  - 每域 = 一个 RuleSet + 该域 resolver (域内布尔求值, 产出 derived.states)。
  - 域命中即产 ZiPingJudgment (强制四要素); 缺前置 → UNDETERMINED(分因)。
  - SPECIAL 域 (P1) 先行: 若特殊结构 VALID → 普通强弱 NOT_APPLICABLE (ARCH-016)。
  - 并行域互不阻塞: 某域 UNDETERMINED 不影响其他域。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from .engine import EngineContext, JudgmentBuilder, RuleSet
from .types import (
    MethodScope,
    UndeterminedReason,
    ZiPingDerivedFact,
    ZiPingJudgment,
    synthesize_output,
)

# §79 依赖边 (下游 → 上游): 域执行前其上游须已产出
_DEPENDENCY: Dict[str, Set[str]] = {
    "facts": set(),
    "sibling_month": set(),          # 月令/根气/干支/气势源流 (基础, 无上游域)
    "special": set(),                # P1: 特殊结构
    "pattern": {"sibling_month"},    # 格局 依赖 月令/根
    "purity": {"pattern"},           # 清浊 依赖 格局
    "trufalse": {"pattern"},         # 真假 依赖 格局
    "affinity": {"pattern"},         # 有情/有力 依赖 格局
    "yongshen": {"pattern", "purity", "trufalse", "affinity",
                 "sibling_month", "special"},
    "xiji": {"yongshen"},
    "temporal": {"yongshen", "xiji"},
}

# P1 特殊结构先行 (ARCH-016): 特殊结构 VALID 时普通强弱 NOT_APPLICABLE
_P1_GATE = "special"


@dataclass
class DomainResolver:
    """一个诊断域: 名称 + 规则集 + (可选)自定义求值函数."""
    name: str
    rule_set: RuleSet
    resolve: Optional[callable] = None  # type: ignore[name-defined]

    def run(self, ctx: EngineContext, derived: ZiPingDerivedFact) -> List[ZiPingJudgment]:
        if self.resolve is not None:
            return self.resolve(ctx, derived, self.rule_set)
        # 默认: 命中即产判断, 前置缺失 → UNDETERMINED
        hits = self.rule_set.hit(ctx, derived)
        if hits:
            return [JudgmentBuilder.from_hits(self.rule_set.domain, hits[0].result_state, hits)]
        miss = self.rule_set.undetermined_reason(ctx, derived)
        if miss:
            return [JudgmentBuilder.undetermined(
                self.rule_set.domain, UndeterminedReason.DEPENDENCY_UNRESOLVED,
                f"前置未满足: {[r.rule_id for r in miss]}")]
        return [JudgmentBuilder.undetermined(
            self.rule_set.domain, UndeterminedReason.RULE_MISSING,
            f"域 {self.rule_set.domain} 无命中规则")]


class Pipeline:
    """§79 依赖图执行器."""

    def __init__(self, domains: Dict[str, DomainResolver]) -> None:
        self.domains = domains
        self._check_deps()

    def _check_deps(self) -> None:
        for name, up in _DEPENDENCY.items():
            for u in up:
                if u not in self.domains and u not in ("facts",):
                    raise EngineDependencyError(f"域 {name} 依赖 {u} 未注册")

    def run(
        self,
        ctx: EngineContext,
        derived: Optional[ZiPingDerivedFact] = None,
    ) -> Dict:
        derived = derived or ZiPingDerivedFact()
        judgments: List[ZiPingJudgment] = []
        undet: List = []
        ordered = _topo_order(self.domains)
        for name in ordered:
            dom = self.domains[name]
            for j in dom.run(ctx, derived):
                judgments.append(j)
                if j.state == "UNDETERMINED":
                    undet.append((name, UndeterminedReason(j.reason or "RULE_MISSING"),
                                  j.reason_detail or ""))
        return synthesize_output(judgments, undet)


class EngineDependencyError(Exception):
    pass


def _topo_order(domains: Dict[str, DomainResolver]) -> List[str]:
    seen: Set[str] = set()
    out: List[str] = []

    def visit(n: str) -> None:
        if n in seen or n not in domains:
            return
        seen.add(n)
        for u in _DEPENDENCY.get(n, set()):
            visit(u)
        out.append(n)

    for n in list(domains):
        visit(n)
    return out
