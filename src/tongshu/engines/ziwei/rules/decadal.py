# -*- coding: utf-8 -*-
"""
Decadal & Liunian Fortune — 大限/流年论断层 (Z21)

南派（倪海厦）断命重"本命 + 大限 + 流年"三盘联动：
  - 本命盘：格局定一生基调（已有）
  - 大限盘：每宫一个大限十年，主星/四化论该十年运势（本模块）
  - 流年盘：流年地支落宫，主星/四化论当年（本模块）

数据来源（全部实测，不推测）：
  - chart.palaces[宫].decadalRange/decadalStem/decadalBranch（大限基础）
  - GAN_SIHUA 天干四化表（大限四化 = decadalStem 四化）
  - 流年地支 = (year-4)%12；流年落宫 = 以命宫地支为起点顺数
  - 断言复用 NihaiAssertionResolver（倪师原话，fail-closed）
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


# 12 宫固定顺序（阳式：命→兄弟→夫妻→子女→财帛→疾厄→迁移→交友→官禄→田宅→福德→父母）
PALACE_ORDER = [
    "命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄",
    "迁移", "交友", "官禄", "田宅", "福德", "父母",
]

BRANCH_IDX = {
    "子": 0, "丑": 1, "寅": 2, "卯": 3, "辰": 4, "巳": 5,
    "午": 6, "未": 7, "申": 8, "酉": 9, "戌": 10, "亥": 11,
}
IDX_BRANCH = list(BRANCH_IDX.keys())


def _year_stem(year: int) -> str:
    """阳历年份 → 天干（与引擎一致）"""
    return {0: "庚", 1: "辛", 2: "壬", 3: "癸", 4: "甲",
            5: "乙", 6: "丙", 7: "丁", 8: "戊", 9: "己"}[year % 10]


def _sihua_of_stem(stem: str) -> List[str]:
    """天干 → 四化四星 [禄,权,科,忌]"""
    from ...ziwei_engine import GAN_SIHUA
    return list(GAN_SIHUA.get(stem, ()))


def _assertions_for_palace(chart, palace_name: str) -> List[Dict[str, Any]]:
    """指定宫位的倪师断言（主星键 + 宫位总论键，不受 resolve 上限截断）"""
    from .nihai_assertions import get_assertions
    try:
        result = []
        # 1. 宫位总论断言 (宫名, 宫名) 键 + (宫名去宫, 宫名) 主题键
        pkey = palace_name if palace_name.endswith("宫") else palace_name + "宫"
        for a in get_assertions(pkey, pkey):
            result.append({"star": a.star, "text": a.text, "category": a.category})
        pkey2 = palace_name.rstrip("宫")
        for a in get_assertions(pkey2, pkey):
            result.append({"star": a.star, "text": a.text, "category": a.category})
        # 2. 主星×宫位断言（断言库 palace 键带"宫"后缀）
        for star in chart.palaces.get(palace_name, {}).get("major", []):
            for a in get_assertions(star, pkey):
                result.append({"star": a.star, "text": a.text, "category": a.category})
        return result
    except Exception:
        return []


def build_decadal_fortune(chart) -> List[Dict[str, Any]]:
    """12 宫大限论断.

    Returns:
        list[dict]: 每宫一个大限十年
            {age_range, palace, stem, branch, sihua(list4),
             major_stars, sihua_palaces(dict: 四化星→落宫), assertions}
    """
    from ...ziwei_engine import GAN_SIHUA

    # 星→落宫（用于大限四化落宫）
    star_to_palace: Dict[str, str] = {}
    for name, pd in chart.palaces.items():
        for s in pd.get("major", []):
            star_to_palace.setdefault(s, name)

    result: List[Dict[str, Any]] = []
    for name, pd in chart.palaces.items():
        dr = pd.get("decadalRange") or []
        sihua_stars = _sihua_of_stem(pd.get("decadalStem") or "")
        sihua_palaces = {}
        for star in sihua_stars:
            sihua_palaces[star] = star_to_palace.get(star, "")

        result.append({
            "age_range": list(dr) if dr else [],
            "palace": name,
            "stem": pd.get("decadalStem", ""),
            "branch": pd.get("decadalBranch", ""),
            "sihua": sihua_stars,                     # 大限四化四星
            "sihua_palaces": sihua_palaces,           # 大限四化落宫
            "major_stars": list(pd.get("major", [])), # 大限宫位主星
            "assertions": _assertions_for_palace(chart, name),
        })
    return result


def build_liunian_fortune(chart, year: int) -> Dict[str, Any]:
    """指定年份流年论断.

    Args:
        chart: FrozenZiweiChart
        year: 阳历年（如 2026）

    Returns:
        dict: {year, branch, stem, palace, sihua, sihua_palaces,
               major_stars, assertions}
    """
    from ...ziwei_engine import GAN_SIHUA

    # 流年地支 + 流年天干
    branch = IDX_BRANCH[(year - 4) % 12]
    stem = _year_stem(year)

    # 流年落宫：以命宫地支为起点顺数
    ming_branch = chart.palaces["命宫"]["branch"]
    offset = (BRANCH_IDX[branch] - BRANCH_IDX[ming_branch]) % 12
    palace_name = PALACE_ORDER[offset]

    # 流年四化（按流年天干）→ 落宫
    sihua_stars = _sihua_of_stem(stem)
    star_to_palace: Dict[str, str] = {}
    for name, pd in chart.palaces.items():
        for s in pd.get("major", []):
            star_to_palace.setdefault(s, name)
    sihua_palaces = {s: star_to_palace.get(s, "") for s in sihua_stars}

    palace_data = chart.palaces.get(palace_name, {})
    return {
        "year": year,
        "branch": branch,
        "stem": stem,
        "palace": palace_name,
        "sihua": sihua_stars,
        "sihua_palaces": sihua_palaces,
        "major_stars": list(palace_data.get("major", [])),
        "assertions": _assertions_for_palace(chart, palace_name),
    }
