"""
Zhongzhou Judgment Resolver — 中州派判定层（P0-4-A）

职责：
- 接收 ZhongzhouCombination 列表 → 输出 ZhongzhouJudgment 列表。
- 不重新计算星盘事实（已由 Feature / Combination 层产出）。
- 只做"组合成立 → 最终判定"的语义翻译。

证据等级约束：
- 本模块所有 Judgment 派生均基于王亭之明文规则（一级证据）。
- 判定差异（吉/凶/平）由判定层显式给出，不依赖 LLM 或综合判断。

P0-4-A 严格 10 条 Judgment：
  ZHZ-CMB-001 机月同梁（标准）→ 平格
  ZHZ-CMB-003 杀破廉贪格 → 平格（吉凶依星性 + 庙陷判定 - 留给 P0-4-B）
  ZHZ-CMB-004 财荫夹印（标准）→ 吉格
  ZHZ-CMB-006 刑忌夹印（标准）→ 凶格
  ZHZ-CMB-008 紫微孤君 → 凶格
  ZHZ-CMB-010 明珠出海格（吉）→ 吉格
  ZHZ-CMB-012 暗曜凶格（杀破贪）→ 凶格
  ZHZ-CMB-016 杀陷震兑 → 凶格
  ZHZ-CMB-017 禄存必为羊陀夹 → 平格（福祸相依）
  ZHZ-CMB-018 禄马交驰 → 吉格
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .combinations import ZhongzhouCombination

Verdict = Literal["吉", "凶", "平"]


@dataclass(frozen=True)
class ZhongzhouJudgment:
    """一条组合的最终判定。"""
    combo_id: str
    rule_id: str
    verdict: Verdict
    description: str
    evidence_grade: int | str  # 与对应 combo 一致


# Combo ID → Judgment 映射（按 P0-4 取证包裁决）
_JUDGMENT_TABLE: dict[str, ZhongzhouJudgment] = {
    "ZHZ-CMB-001": ZhongzhouJudgment(
        combo_id="ZHZ-CMB-001",
        rule_id="R-COMBO-08",
        verdict="平",
        description="机月同梁格（标准）—— 入庙会照主温和近贵；陷地则主孤寒",
        evidence_grade=1,
    ),
    "ZHZ-CMB-003": ZhongzhouJudgment(
        combo_id="ZHZ-CMB-003",
        rule_id="R-COMBO-09",
        verdict="平",
        description="杀破廉贪格 —— 刚烈，入庙主大富贵，陷地主大凶暴",
        evidence_grade=1,
    ),
    "ZHZ-CMB-004": ZhongzhouJudgment(
        combo_id="ZHZ-CMB-004",
        rule_id="R-COMBO-06",
        verdict="吉",
        description="财荫夹印（标准格）—— 巨门化禄 + 天梁在邻，主得财荫",
        evidence_grade=1,
    ),
    "ZHZ-CMB-006": ZhongzhouJudgment(
        combo_id="ZHZ-CMB-006",
        rule_id="R-COMBO-06",
        verdict="凶",
        description="刑忌夹印（标准格）—— 巨门 + 天梁 在邻（位置同财荫夹印，判定由吉转凶）",
        evidence_grade=1,
    ),
    "ZHZ-CMB-008": ZhongzhouJudgment(
        combo_id="ZHZ-CMB-008",
        rule_id="R-DEF-02",
        verdict="凶",
        description="紫微孤君 —— 紫微在命宫 + 三方无辅弼，主孤高无辅",
        evidence_grade=1,
    ),
    "ZHZ-CMB-010": ZhongzhouJudgment(
        combo_id="ZHZ-CMB-010",
        rule_id="R-COMBO-10",
        verdict="吉",
        description="明珠出海格（吉）—— 命宫三方有太阳/太阴 + 文昌/文曲 + 截空值日不在同宫",
        evidence_grade=1,
    ),
    "ZHZ-CMB-012": ZhongzhouJudgment(
        combo_id="ZHZ-CMB-012",
        rule_id="R-JDG-12",
        verdict="凶",
        description="暗曜凶格 —— 文曲所在宫 = 七杀/破军/贪狼所在宫，主暗损",
        evidence_grade=1,
    ),
    "ZHZ-CMB-016": ZhongzhouJudgment(
        combo_id="ZHZ-CMB-016",
        rule_id="R-JDG-22",
        verdict="凶",
        description="杀陷震兑 —— 七杀在卯/酉 + 武曲同度，主震兑方位凶险",
        evidence_grade=1,
    ),
    "ZHZ-CMB-017": ZhongzhouJudgment(
        combo_id="ZHZ-CMB-017",
        rule_id="R-DEF-05",
        verdict="平",
        description="禄存必为羊陀夹 —— 禄存所在宫必被擎羊+陀罗夹，福祸相依",
        evidence_grade=1,
    ),
    "ZHZ-CMB-018": ZhongzhouJudgment(
        combo_id="ZHZ-CMB-018",
        rule_id="R-JDG-18",
        verdict="吉",
        description="禄马交驰 —— 禄存 + 天马 同宫，主发财于远地",
        evidence_grade=1,
    ),
}


def judge_combinations(
    combos: list[ZhongzhouCombination],
) -> list[ZhongzhouJudgment]:
    """
    把 Combination 列表翻译为 Judgment 列表。
    严格 1:1 映射（P0-4-A 不存在 1 combo → multi judgment）。
    未知 combo_id 静默跳过（fail-closed）。
    """
    out: list[ZhongzhouJudgment] = []
    for combo in combos:
        j = _JUDGMENT_TABLE.get(combo.combo_id)
        if j is not None:
            out.append(j)
    return out
