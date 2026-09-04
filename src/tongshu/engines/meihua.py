"""梅花易数(Mei Hua Yi Shu)起卦引擎 — 独立体系

设计原则：
  1. 完全独立于河洛引擎，不混入河洛概念（元堂、先天/后天等）
  2. 使用 yi.core 共享数据（八卦五行、六十四卦映射）
  3. 三类起卦法：时间起卦 / 数字起卦 / 外应起卦
  4. 体用分析：动爻所在卦为用卦，另一卦为体卦

原典依据：《梅花易数·卷一》邵雍
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .yi.core import (
    TRIGRAM_LINES,
    TRIGRAM_ELEMENT,
    SIXTY_FOUR_MAP,
    CUO_GUA_MAP,
)


# ═══════════════════════════════════════════════════════════════
# 先天八卦数（梅花体系，非河洛洛书）
# ═══════════════════════════════════════════════════════════════

XIANTIAN_NUM: dict[int, str] = {
    1: "乾", 2: "兑", 3: "离", 4: "震",
    5: "巽", 6: "坎", 7: "艮", 8: "坤",
}
NUM_TO_XIANTIAN: dict[str, int] = {v: k for k, v in XIANTIAN_NUM.items()}

# 五行生克
WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}


@dataclass(frozen=True)
class MeihuaResult:
    """梅花易数起卦结果。"""
    ben_gua: str          # 本卦名
    upper: str            # 上卦
    lower: str            # 下卦
    lines: tuple          # 本卦六爻
    bian_gua: str         # 变卦名
    bian_upper: str       # 变卦上卦
    bian_lower: str       # 变卦下卦
    bian_lines: tuple     # 变卦六爻
    hu_gua: str           # 互卦名
    hu_upper: str         # 互卦上卦
    hu_lower: str         # 互卦下卦
    hu_lines: tuple       # 互卦六爻
    cuo_gua: str          # 错卦名
    zong_gua: str         # 综卦名
    dong_yao: int         # 动爻索引（0-5）
    dong_yao_1based: int  # 动爻（1-6）
    ti: str               # 体卦
    yong: str             # 用卦
    ti_element: str       # 体卦五行
    yong_element: str     # 用卦五行
    ti_yong_relation: str # 体用关系
    method: str           # 起卦方法
    question: str         # 所问之事


def _flip_line(lines: tuple, idx: int) -> tuple:
    lst = list(lines)
    lst[idx] = -lst[idx]
    return tuple(lst)


def _lines_to_trigram_name(lines: tuple) -> str:
    for name, tl in TRIGRAM_LINES.items():
        if tl == lines:
            return name
    return "?"


def _hexagram_name(upper: str, lower: str) -> str:
    return SIXTY_FOUR_MAP.get((upper, lower), f"{upper}{lower}")


def _get_hu_gua(lines: tuple) -> tuple:
    lower_lines = lines[1:4]
    upper_lines = lines[2:5]
    hu_lower = _lines_to_trigram_name(lower_lines)
    hu_upper = _lines_to_trigram_name(upper_lines)
    hu_lines = TRIGRAM_LINES[hu_lower] + TRIGRAM_LINES[hu_upper]
    return hu_upper, hu_lower, _hexagram_name(hu_upper, hu_lower), hu_lines


def _ti_yong(upper: str, lower: str, dong_yao_idx: int) -> tuple:
    """动爻在下卦 → 上体下用；动爻在上卦 → 下体上用。"""
    if dong_yao_idx < 3:
        ti, yong = upper, lower
    else:
        ti, yong = lower, upper
    ti_elem = TRIGRAM_ELEMENT.get(ti, "?")
    yong_elem = TRIGRAM_ELEMENT.get(yong, "?")
    if ti_elem == yong_elem:
        relation = "比和"
    elif WUXING_SHENG.get(yong_elem) == ti_elem:
        relation = "用生体（吉）"
    elif WUXING_KE.get(yong_elem) == ti_elem:
        relation = "用克体（凶）"
    elif WUXING_SHENG.get(ti_elem) == yong_elem:
        relation = "体生用（泄）"
    elif WUXING_KE.get(ti_elem) == yong_elem:
        relation = "体克用（耗）"
    else:
        relation = "未知"
    return ti, yong, ti_elem, yong_elem, relation


def cast_by_time(year: int, month: int, day: int, hour: int,
                 question: str = "") -> MeihuaResult:
    """
    时间起卦（梅花易数核心方法）。

    规则：
      上卦 = (年支数 + 月 + 日) % 8
      下卦 = (年支数 + 月 + 日 + 时辰数) % 8
      动爻 = (年支数 + 月 + 日 + 时辰数) % 6

    原典：《梅花易数·卷一》"年月日时数起卦法"
    """
    year_zhi = ((year - 4) % 12)
    shichen = ((hour + 1) // 2) % 12 or 12
    if hour == 23 or hour == 0:
        shichen = 1

    upper_num = (year_zhi + month + day) % 8 or 8
    lower_num = (year_zhi + month + day + shichen) % 8 or 8
    dong_yao_idx = ((year_zhi + month + day + shichen) % 6)

    upper = XIANTIAN_NUM[upper_num]
    lower = XIANTIAN_NUM[lower_num]
    lines = TRIGRAM_LINES[lower] + TRIGRAM_LINES[upper]
    bian_lines = _flip_line(lines, dong_yao_idx)
    bian_lower = _lines_to_trigram_name(bian_lines[:3])
    bian_upper = _lines_to_trigram_name(bian_lines[3:])

    ti, yong, ti_elem, yong_elem, relation = _ti_yong(upper, lower, dong_yao_idx)
    hu_upper, hu_lower, hu_name, hu_lines = _get_hu_gua(lines)
    cuo_upper = CUO_GUA_MAP.get(upper, upper)
    cuo_lower = CUO_GUA_MAP.get(lower, lower)
    cuo_name = _hexagram_name(cuo_upper, cuo_lower)
    zong_name = _hexagram_name(lower, upper)

    return MeihuaResult(
        ben_gua=_hexagram_name(upper, lower),
        upper=upper, lower=lower, lines=lines,
        bian_gua=_hexagram_name(bian_upper, bian_lower),
        bian_upper=bian_upper, bian_lower=bian_lower, bian_lines=bian_lines,
        hu_gua=hu_name, hu_upper=hu_upper, hu_lower=hu_lower, hu_lines=hu_lines,
        cuo_gua=cuo_name,
        zong_gua=zong_name,
        dong_yao=dong_yao_idx, dong_yao_1based=dong_yao_idx + 1,
        ti=ti, yong=yong,
        ti_element=ti_elem, yong_element=yong_elem,
        ti_yong_relation=relation,
        method="时间起卦",
        question=question,
    )


def cast_by_numbers(upper_num: int, lower_num: int,
                     question: str = "") -> MeihuaResult:
    """
    数字起卦。

    规则：
      上卦 = ((upper_num - 1) % 8) + 1
      下卦 = ((lower_num - 1) % 8) + 1
      动爻 = (upper_num + lower_num) % 6

    原典：《梅花易数·卷一》"数字起卦法"
    """
    upper = XIANTIAN_NUM[((upper_num - 1) % 8) + 1]
    lower = XIANTIAN_NUM[((lower_num - 1) % 8) + 1]
    dong_yao_idx = (upper_num + lower_num) % 6

    lines = TRIGRAM_LINES[lower] + TRIGRAM_LINES[upper]
    bian_lines = _flip_line(lines, dong_yao_idx)
    bian_lower = _lines_to_trigram_name(bian_lines[:3])
    bian_upper = _lines_to_trigram_name(bian_lines[3:])

    ti, yong, ti_elem, yong_elem, relation = _ti_yong(upper, lower, dong_yao_idx)
    hu_upper, hu_lower, hu_name, hu_lines = _get_hu_gua(lines)
    cuo_upper = CUO_GUA_MAP.get(upper, upper)
    cuo_lower = CUO_GUA_MAP.get(lower, lower)
    cuo_name = _hexagram_name(cuo_upper, cuo_lower)
    zong_name = _hexagram_name(lower, upper)

    return MeihuaResult(
        ben_gua=_hexagram_name(upper, lower),
        upper=upper, lower=lower, lines=lines,
        bian_gua=_hexagram_name(bian_upper, bian_lower),
        bian_upper=bian_upper, bian_lower=bian_lower, bian_lines=bian_lines,
        hu_gua=hu_name, hu_upper=hu_upper, hu_lower=hu_lower, hu_lines=hu_lines,
        cuo_gua=cuo_name,
        zong_gua=zong_name,
        dong_yao=dong_yao_idx, dong_yao_1based=dong_yao_idx + 1,
        ti=ti, yong=yong,
        ti_element=ti_elem, yong_element=yong_elem,
        ti_yong_relation=relation,
        method="数字起卦",
        question=question,
    )


def cast_now(question: str = "") -> MeihuaResult:
    """当前时间起卦。"""
    from datetime import datetime
    now = datetime.now()
    return cast_by_time(now.year, now.month, now.day, now.hour, question)


__all__ = [
    "MeihuaResult",
    "cast_by_time",
    "cast_by_numbers",
    "cast_now",
    "XIANTIAN_NUM",
]
