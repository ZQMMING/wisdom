"""H6: 化工计算模块

职责：判断先天卦/后天卦是否得"天地生生化化之妙"。
原典依据：《河洛真数》起例卷下·论化工 + 逢化工诗

冻结规则：
  1. 四季对应化工卦：
     - 冬（亥子丑月）→ 坎 ☵
     - 春（寅卯辰月）→ 震 ☳
     - 夏（巳午未月）→ 离 ☲
     - 秋（申酉戌月）→ 兑 ☱
  2. 正对反对：
     - 坎 ↔ 离（冬夏相反）
     - 震 ↔ 兑（春秋相反）
  3. 状态枚举：NORMAL / REVERSE / RESCUED / UNRESOLVED
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class HuaGongState(str, Enum):
    """化工状态。"""
    NORMAL = "NORMAL"       # 得位：卦中有机气
    REVERSE = "REVERSE"     # 反位：正对反对，非当令
    RESCUED = "RESCUED"     # 救应：虽相反但有相生
    UNRESOLVED = "UNRESOLVED"  # 无据：无法判定


# 四季 → 地支月 → 化工卦
# 原典："冬至后春分前，坎水用事，为化工；春木夏火，秋金冬水"
SEASON_BRANCH_TO_HUAGONG: dict[str, str] = {
    "亥": "坎", "子": "坎", "丑": "坎",   # 冬
    "寅": "震", "卯": "震", "辰": "震",   # 春
    "巳": "离", "午": "离", "未": "离",   # 夏
    "申": "兑", "酉": "兑", "戌": "兑",   # 秋
}

# 正反对：反卦判断
OPPOSITE_TRIGRAM: dict[str, str] = {
    "坎": "离", "离": "坎",
    "震": "兑", "兑": "震",
    "艮": "巽", "巽": "艮",
    "乾": "坤", "坤": "乾",
}


@dataclass(frozen=True)
class HuaGongResult:
    """化工计算结果。"""
    state: HuaGongState
    huagong_trigram: str          # 当令化工卦
    birth_month_branch: str       # 出生月支
    has_huagong: bool             # 先天/后天卦中是否有化工卦
    has_opposite: bool            # 先天/后天卦中是否有反卦
    evidence: list[str]           # 可审计证据链


def compute_huagong(
    prenatal_upper: str,
    prenatal_lower: str,
    postnatal_upper: str,
    postnatal_lower: str,
    birth_month_branch: str,
) -> HuaGongResult:
    """
    计算化工状态。

    算法：
    1. 确定当令化工卦（出生月支 → 四季 → 卦）
    2. 检查先天卦上下卦是否有机气
    3. 检查后天卦上下卦是否有机气
    4. 检查是否有正反对（反卦）
    5. 判定状态

    原典原则：
      "根基不得化工者，灾重也"
      "有化工之气者，艰难获福"
      "大象与小象化工虽相反，却又有相生者，则吉"
    """
    evidence: list[str] = []

    # Step 1: 确定当令化工卦
    huagong_trigram = SEASON_BRANCH_TO_HUAGONG.get(birth_month_branch, "?")
    opposite_trigram = OPPOSITE_TRIGRAM.get(huagong_trigram, "")

    # Step 2: 检查卦中是否有化工卦 / 反卦
    all_trigrams = {prenatal_upper, prenatal_lower, postnatal_upper, postnatal_lower}
    has_huagong = huagong_trigram in all_trigrams
    has_opposite = opposite_trigram in all_trigrams

    evidence.append(f"出生月支{birth_month_branch} → 当令化工卦={huagong_trigram}")
    evidence.append(f"卦中含化工卦: {has_huagong}（{all_trigrams}）")
    if has_opposite:
        evidence.append(f"卦中含反卦{opposite_trigram}（{huagong_trigram}↔{opposite_trigram}）")

    # Step 3: 判定状态
    # 原典："根基得三元纯正，生气充畅者，名曰元气足"
    # 原典："根基杂乱，克贼交加者，名曰元气损"
    if has_huagong and not has_opposite:
        state = HuaGongState.NORMAL
        evidence.append("得位：卦中含当令化工卦，无正反对")
    elif has_huagong and has_opposite:
        # 虽有化工卦，但亦有反卦 → 需检查相生关系
        state = HuaGongState.RESCUED
        evidence.append(f"救应：含化工卦{huagong_trigram}但同时含反卦{opposite_trigram}，需五行相生救应")
    elif has_opposite and not has_huagong:
        state = HuaGongState.REVERSE
        evidence.append(f"反位：卦中含反卦{opposite_trigram}，无当令化工卦")
    else:
        state = HuaGongState.UNRESOLVED
        evidence.append("无据：卦中既无化工卦也无反卦")

    return HuaGongResult(
        state=state,
        huagong_trigram=huagong_trigram,
        birth_month_branch=birth_month_branch,
        has_huagong=has_huagong,
        has_opposite=has_opposite,
        evidence=evidence,
    )
