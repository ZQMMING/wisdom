"""
Feixing Rule Graph — 飞星派 RuleGraph 实现（P0-5-A）

架构对齐：
- P0-2 抽象 (method_graphs.py BaseZiweiRuleGraph) — 4 派 SCAFFOLD 共用接口
- P0-4-A 中州 RuleGraph 不继承 ABC（独立类 + 工厂函数集成）
- P0-5-A 本模块同样采用独立类 + make_feixing_rule_graph() 工厂函数

严格工程边界：
- 不实现 InferenceChain 大引擎
- 多步推理用 inference_chain_id 显式标记（本模块范围无多步）
- production 规则全 grade=1，evidence 由 evidence.py 绑定
- fail-closed：DRAFT 规则不进 rule_graph.match_all()

Public API:
    FeixingRuleGraph        — 飞星派 RuleGraph（独立类）
    FeixingRuleGraphResult  — 匹配结果 dataclass
    FeixingRuleMatch        — 单条匹配结果 dataclass
    make_feixing_rule_graph — 工厂函数（供 method_graphs.py 集成）
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ....ziwei_engine import FrozenZiweiChart
from .combinations import (
    FeixingCombination,
    P0_5_A_PRODUCTION_DETECTORS,
    detect_all_production,
)
from .evidence import evidence_grade
from .features import build_feature_bundle
from .judgments import FeixingJudgment, judge_all


# ─────────────────────────────────────────────────────────────────────────
# 数据类
# ─────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class FeixingRuleMatch:
    """单条飞星 RuleGraph 匹配结果。"""
    combo: FeixingCombination
    judgment: FeixingJudgment | None
    evidence_grade: int
    rule_id: str  # = combo.rule_id（冗余，方便索引）

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "combination": self.combo.to_dict(),
            "judgment": self.judgment.to_dict() if self.judgment else None,
            "evidence_grade": self.evidence_grade,
        }


@dataclass(frozen=True)
class FeixingRuleGraphResult:
    """飞星派 RuleGraph 匹配总结果。"""
    matched_rules: tuple[FeixingRuleMatch, ...]
    implementation_status: str  # "SCAFFOLD" / "PARTIAL" / "FULL"
    rule_count: int             # production 规则数
    draft_count: int            # DRAFT 规则数


# ─────────────────────────────────────────────────────────────────────────
# 主类
# ─────────────────────────────────────────────────────────────────────────


class FeixingRuleGraph:
    """飞星派 RuleGraph（P0-5-A 终态：5 条 production + 5 条 DRAFT/CANDIDATE）。

    完整覆盖 P0-2 SCAFFOLD 抽象（不继承 ABC，与 P0-4 中州同模式）：
      - 5 条 production 规则 detect（evidence_grade=1）
      - 5 条 DRAFT 规则占位（detect_*_draft 强制返回 None，不进 match_all）
      - 命中即映射 judgment（强/中/弱/中性 + 吉/凶/中性）
      - 全部产出 FeixingRuleMatch dataclass 列表

    调用入口：match_all(chart) → FeixingRuleGraphResult
    """

    METHOD_ID = "FEIXING"
    implementation_status = "PARTIAL"  # 5 条 production 已落
    rule_count = 5  # P0-5-A production detect 数量
    draft_count = 5  # DRAFT/CANDIDATE 数量

    def match_all(self, chart: FrozenZiweiChart) -> FeixingRuleGraphResult:
        """调度四层：features → combinations → judgments → evidence。

        失败/缺失全部 fail-closed。

        注意：P0-5-A 不需要 ZiweiPalaceResolver（飞化逻辑不依赖公共事实层
        resolve_sanfang_sizheng()，只用 FrozenZiweiChart 12 宫基础事实）。
        """
        # Layer 1: features
        bundle = build_feature_bundle(chart)

        # Layer 2: combinations (production only - DRAFT 不触发)
        combos = detect_all_production(chart, bundle)

        # Layer 3: judgments
        judgments = judge_all(combos)

        # Layer 4: evidence + 1:1 绑定
        matches = self._bind_evidence(combos, judgments)

        return FeixingRuleGraphResult(
            matched_rules=matches,
            implementation_status=self.implementation_status,
            rule_count=self.rule_count,
            draft_count=self.draft_count,
        )

    @staticmethod
    def _bind_evidence(
        combos: tuple[FeixingCombination, ...],
        judgments: tuple[FeixingJudgment, ...],
    ) -> tuple[FeixingRuleMatch, ...]:
        """把 combo + judgment + evidence 1:1 绑定。

        fail-closed：evidence_grade > 2 不进生产。
        """
        judgment_by_rule = {j.rule_id: j for j in judgments}
        out: list[FeixingRuleMatch] = []
        for combo in combos:
            grade = evidence_grade(combo.rule_id)
            if grade > 2:
                continue  # fail-closed
            j = judgment_by_rule.get(combo.rule_id)
            out.append(FeixingRuleMatch(
                combo=combo,
                judgment=j,
                evidence_grade=grade,
                rule_id=combo.rule_id,
            ))
        return tuple(out)

    # ── 飞星派扩展 API ────────────────────────────────────────────────

    def list_production_rules(self) -> tuple[str, ...]:
        """返回全部 production rule_id。"""
        return tuple(rid for rid, _fn in P0_5_A_PRODUCTION_DETECTORS)

    def list_draft_rules(self) -> tuple[str, ...]:
        """返回全部 DRAFT rule_id。"""
        return (
            "FEX-CMB-D01",
            "FEX-CMB-D02",
            "FEX-CMB-D03",
            "FEX-CMB-D04",
            "FEX-CMB-D05",
        )

    def graph_id(self) -> str:
        """返回 RuleGraph ID。"""
        return f"FEIXING-P0-5-A"

    def rules(self) -> tuple[dict[str, Any], ...]:
        """返回全部 production 规则的元数据（不含 chart-specific 命中）。"""
        rules_meta: list[dict[str, Any]] = []
        for rid in self.list_production_rules():
            rules_meta.append({
                "rule_id": rid,
                "evidence_grade": evidence_grade(rid),
                "rule_graph_id": self.graph_id(),
                "status": "production" if evidence_grade(rid) <= 2 else "draft",
            })
        return tuple(rules_meta)


# ─────────────────────────────────────────────────────────────────────────
# 工厂函数（与 P0-4 中州同模式）
# ─────────────────────────────────────────────────────────────────────────


def make_feixing_rule_graph() -> FeixingRuleGraph:
    """工厂函数，供 method_graphs.py 引用。"""
    return FeixingRuleGraph()