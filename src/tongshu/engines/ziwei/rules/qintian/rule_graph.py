
"""
Qintian Rule Graph — 钦天门 RuleGraph 实现 (P0-7)

架构对齐：
- P0-2 抽象 (method_graphs.py BaseZiweiRuleGraph)
- P0-4-A 中州 RuleGraph 不继承 ABC（独立类 + 工厂函数）
- P0-5-A 飞星 RuleGraph 不继承 ABC（独立类 + 工厂函数）
- P0-7-A 钦天 RuleGraph 同模式

public:
  QintianRuleGraph     — 钦天 RuleGraph（独立类）
  QintianRuleMatch     — 单条匹配结果 dataclass
  QintianRuleGraphResult — 整体 match_all 结果
  make_qintian_rule_graph — 工厂函数
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional

from .combinations import (
    detect_all_production, detect_all_draft, QintianCombination,
    PRODUCTION_DETECTORS, DRAFT_DETECTORS,
)
from .evidence import EVIDENCE_BINDINGS, DRAFT_BINDINGS
from .judgments import resolve_judgment, QintianJudgment


@dataclass
class QintianRuleMatch:
    rule_id: str
    evidence_grade: int
    detected: bool
    facts: Dict[str, Any] = field(default_factory=dict)
    semantic_summary: str = ""
    judgment_strength: str = "neutral"
    neutral_facts: List[str] = field(default_factory=list)


@dataclass
class QintianRuleGraphResult:
    matched_rules: List[QintianRuleMatch]
    unmatched_production_rules: List[str]
    draft_detected: List[str]  # DRAFT 触发的（应为空）
    implementation_status: str  # "PRODUCTION" / "PARTIAL" / "DRAFT"
    profile: str


class QintianRuleGraph:
    """钦天门 RuleGraph (P0-7-A 严格派)"""

    METHOD_ID = "QINTIAN"
    PROFILE = "QINTIAN-QINTIAN_SIHA-PRODUCTION-A"
    IMPLEMENTATION_STATUS = "PARTIAL"
    PRODUCTION_RULES_COUNT = 5
    DRAFT_RULES_COUNT = 5

    def graph_id(self) -> str:
        return "QINTIAN-P0-7-A"

    def match(self, chart) -> List[QintianRuleMatch]:
        """单图匹配（仅返回 production 命中）"""
        results = []
        for combo in detect_all_production(chart):
            judgment = resolve_judgment(combo)
            results.append(QintianRuleMatch(
                rule_id=combo.rule_id,
                evidence_grade=combo.evidence_grade,
                detected=True,
                facts=combo.facts,
                semantic_summary=combo.semantic_summary,
                judgment_strength=judgment.judgment_strength,
                neutral_facts=judgment.neutral_facts,
            ))
        return results

    def match_all(self, chart) -> QintianRuleGraphResult:
        """完整匹配（production + draft）"""
        matched_production = self.match(chart)
        matched_rule_ids = {m.rule_id for m in matched_production}

        all_production_ids = {f"QTN-CMB-{i:03d}" for i in range(1, 6)}
        unmatched = sorted(all_production_ids - matched_rule_ids)

        # Draft 应不触发
        draft_combos = detect_all_draft(chart)
        draft_detected = [c.rule_id for c in draft_combos if c.detected]

        return QintianRuleGraphResult(
            matched_rules=matched_production,
            unmatched_production_rules=unmatched,
            draft_detected=draft_detected,
            implementation_status=self.IMPLEMENTATION_STATUS,
            profile=self.PROFILE,
        )

    def rule_count(self) -> int:
        return self.PRODUCTION_RULES_COUNT

    def draft_count(self) -> int:
        return self.DRAFT_RULES_COUNT

    def evidence_bindings(self) -> Dict[str, Any]:
        return dict(EVIDENCE_BINDINGS)

    def draft_bindings(self) -> Dict[str, Any]:
        return dict(DRAFT_BINDINGS)


def make_qintian_rule_graph() -> QintianRuleGraph:
    """工厂函数 (P0-4/P0-5 同模式)"""
    return QintianRuleGraph()
