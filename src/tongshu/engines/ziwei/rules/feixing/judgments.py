"""
Feixing Judgment Resolver — 飞星派判定层（P0-5-A）

严格工程边界：
- 本模块只负责"组合命中 → 判定结论"映射
- 不涉及数据计算（combinations / features 负责）
- 不涉及规则图谱匹配（rule_graph 负责）
- 不做最终用户判断（结论文字给"辨"层用）
- judgment_strength 仅作 raw 输出（"强/中/弱/中性"），不做百分比换算

P0-5-A 状态：
- 5 条 production 组合的 judgment 全部 hard-coded 字面映射
- 不引入 LLM / 综合判断 / 模糊打分
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .combinations import FeixingCombination


@dataclass(frozen=True)
class FeixingJudgment:
    """飞星判定单元。"""
    rule_id: str
    judgment_strength: str  # "strong" / "moderate" / "weak" / "neutral"
    direction: str          # "auspicious" / "inauspicious" / "neutral"
    raw_text: str           # 字面判定（无 LLM，无解释）

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "judgment_strength": self.judgment_strength,
            "direction": self.direction,
            "raw_text": self.raw_text,
        }


# ============================================================================
# Judgment 字面映射表（与 evidence.py verbatim_quote 严格对应）
# ============================================================================

_JUDGMENT_MAP: dict[str, FeixingJudgment] = {
    "FEX-CMB-001": FeixingJudgment(
        rule_id="FEX-CMB-001",
        judgment_strength="strong",
        direction="auspicious",
        raw_text=(
            "财荫夹印：王亭之原文「主一生得人助力或荫庇，从而致取富贵」，"
            "production 命中即视作 strong + 吉。"
        ),
    ),
    "FEX-CMB-002": FeixingJudgment(
        rule_id="FEX-CMB-002",
        judgment_strength="strong",
        direction="inauspicious",
        raw_text=(
            "刑忌夹印：王亭之原文「主人一生受压力，且多刑伤克害」，"
            "production 命中即视作 strong + 凶。"
        ),
    ),
    "FEX-CMB-003": FeixingJudgment(
        rule_id="FEX-CMB-003",
        judgment_strength="moderate",
        direction="neutral",
        raw_text=(
            "来因宫命迁线：飞星嫡系「向心力 12 种流向」之一，"
            "production 命中即视作 moderate + 中性（具体吉凶取决于四化星本身）。"
        ),
    ),
    "FEX-CMB-004": FeixingJudgment(
        rule_id="FEX-CMB-004",
        judgment_strength="moderate",
        direction="inauspicious",
        raw_text=(
            "自化忌基础：林士钦原文「自化通常带有不好的意义...散掉命盘能量」，"
            "production 命中即视作 moderate + 凶（具体程度取决于宫位）。"
        ),
    ),
    "FEX-CMB-005": FeixingJudgment(
        rule_id="FEX-CMB-005",
        judgment_strength="weak",
        direction="neutral",
        raw_text=(
            "四化入命：王亭之 + 令东来泛论「飞化可看细节、内幕」，"
            "production 命中仅记录事实，不预设吉凶（视作 weak + 中性）。"
        ),
    ),
}


def judge_combination(combo: FeixingCombination) -> FeixingJudgment | None:
    """按 rule_id 查询判定。

    Args:
        combo: 单条飞星组合命中结果

    Returns:
        FeixingJudgment 或 None（rule_id 未在判定表中）
    """
    return _JUDGMENT_MAP.get(combo.rule_id)


def judge_all(
    combos: tuple[FeixingCombination, ...]
) -> tuple[FeixingJudgment, ...]:
    """批量判定。"""
    judgments: list[FeixingJudgment] = []
    for c in combos:
        j = judge_combination(c)
        if j is not None:
            judgments.append(j)
    return tuple(judgments)