"""
ZhongzhouRuleGraph — 中州派调度层（P0-4-A）

职责：
- 调度四层：features → combinations → judgments → evidence
- 返回结构化结果（ZhongzhouRuleMatch）供上游 FeixingRuleGraph / MethodGraphs 使用。

工程纪律：
- 严格不依赖其他 Method（Sanhe / Feixing / Qintian）。
- 严格不修改 FrozenZiweiChart 字段。
- 严格不修改 ZiweiPalaceResolver 签名。
- 失败 / 缺失全部 fail-closed（返回 None / 空列表）。

P0-4-A 状态：
- implementation_status = "PARTIAL" (10 条 production detect 已落 + 10 条 DRAFT 不触发)
- 不动 P0-1/2/3 任何代码。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ....ziwei_engine import FrozenZiweiChart
from ....ziwei_palace_resolution import ZiweiPalaceResolver
from .combinations import (
    P0_4_A_PRODUCTION_DETECTORS,
    DRAFT_DETECTORS,
    ZhongzhouCombination,
)
from .evidence import EVIDENCE_TABLE, ZhongzhouEvidence, get_evidence
from .features import ZhongzhouFeatureBundle, build_feature_bundle
from .judgments import ZhongzhouJudgment, judge_combinations

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class ZhongzhouRuleMatch:
    """一条完整命中（combo + judgment + evidence 三者绑定）。"""
    combo: ZhongzhouCombination
    judgment: ZhongzhouJudgment
    evidence: ZhongzhouEvidence


@dataclass(frozen=True)
class ZhongzhouRuleGraphResult:
    """ZhongzhouRuleGraph 调度的最终结果。"""
    matched_rules: tuple[ZhongzhouRuleMatch, ...]
    implementation_status: str  # "SCAFFOLD" / "PARTIAL" / "FULL"
    rule_count: int             # 生产规则数（不含 DRAFT）
    draft_count: int            # DRAFT 数量


class ZhongzhouRuleGraph:
    """
    中州派 RuleGraph（P0-4-A 终态：10 条 production + 10 条 DRAFT/CANDIDATE）。

    调用入口：match_all(chart, resolver) → ZhongzhouRuleGraphResult
    """

    METHOD_ID = "ZHONGZHOU"
    implementation_status = "PARTIAL"  # 10 条 production 已落
    rule_count = 10  # P0-4-A production detect 数量
    draft_count = 10  # DRAFT/CANDIDATE 数量

    def match_all(
        self,
        chart: FrozenZiweiChart,
        resolver: ZiweiPalaceResolver,
    ) -> ZhongzhouRuleGraphResult:
        """
        调度四层：features → combinations → judgments → evidence。
        失败/缺失全部 fail-closed。
        """
        # Layer 1: features
        bundle = build_feature_bundle(chart, resolver)

        # Layer 2: combinations (production only - DRAFT 不触发)
        combos = self._detect_combinations(bundle)

        # Layer 3: judgments
        judgments = judge_combinations(combos)

        # Layer 4: evidence + 1:1 绑定
        matches = self._bind_evidence(combos, judgments)

        return ZhongzhouRuleGraphResult(
            matched_rules=matches,
            implementation_status=self.implementation_status,
            rule_count=self.rule_count,
            draft_count=self.draft_count,
        )

    @staticmethod
    def _detect_combinations(
        bundle: ZhongzhouFeatureBundle,
    ) -> list[ZhongzhouCombination]:
        """运行所有 production detect 函数。"""
        out: list[ZhongzhouCombination] = []
        for det in P0_4_A_PRODUCTION_DETECTORS:
            r = det(bundle)
            if r is not None:
                out.append(r)
        return out

    @staticmethod
    def _bind_evidence(
        combos: list[ZhongzhouCombination],
        judgments: list[ZhongzhouJudgment],
    ) -> tuple[ZhongzhouRuleMatch, ...]:
        """把 combo + judgment + evidence 1:1 绑定。"""
        judgment_by_combo = {j.combo_id: j for j in judgments}
        out: list[ZhongzhouRuleMatch] = []
        for combo in combos:
            judgment = judgment_by_combo.get(combo.combo_id)
            evidence = get_evidence(combo.combo_id)
            if judgment is not None and evidence is not None:
                out.append(ZhongzhouRuleMatch(
                    combo=combo,
                    judgment=judgment,
                    evidence=evidence,
                ))
        return tuple(out)


# ─────────────────────────────────────────────────────────────────────────
# 兼容层：给 BaseZiweiRuleGraph ABC 用的薄包装（保留 P0-2 抽象接口）
# ─────────────────────────────────────────────────────────────────────────


def make_zhongzhou_rule_graph() -> ZhongzhouRuleGraph:
    """工厂函数，供 method_graphs.py 引用。"""
    return ZhongzhouRuleGraph()
