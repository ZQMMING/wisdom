# -*- coding: utf-8 -*-
"""B轴（秀气侧/干合侧）计分

修正Bug A(争合统计方向) + Bug B(化神取错) + B4复用闸门
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

HE = {"甲": "己", "己": "甲", "乙": "庚", "庚": "乙",
      "丙": "辛", "辛": "丙", "丁": "壬", "壬": "丁",
      "戊": "癸", "癸": "戊"}

HUA_SHEN = {"甲己": "土", "乙庚": "金", "丙辛": "水", "丁壬": "木", "戊癸": "火"}

WUXING = {}
for g in "甲乙寅卯": WUXING[g] = "木"
for g in "丙丁巳午": WUXING[g] = "火"
for g in "戊己辰戌丑未": WUXING[g] = "土"
for g in "庚辛申酉": WUXING[g] = "金"
for g in "壬癸亥子": WUXING[g] = "水"

MONTH_WANG = {"寅": "木", "卯": "木", "巳": "火", "午": "火",
              "申": "金", "酉": "金", "亥": "水", "子": "水",
              "辰": "土", "戌": "土", "丑": "土", "未": "土"}

@dataclass
class XiuqiResult:
    pattern_root: Optional[str]
    pattern_type: str
    b1a: bool
    b1b: bool
    b2: bool
    b3: bool
    b4: bool
    score: int
    gate_debug: List[str]

def hx_to_ge(hx: str) -> str:
    return {"木": "曲直", "火": "炎上", "土": "稼穑", "金": "从革", "水": "润下"}[hx]

def _stems(pillars: Dict[str, List[str]]) -> tuple:
    return (pillars["year"][0], pillars["month"][0],
            pillars["day"][0],   pillars["hour"][0])

def _branches(pillars: Dict[str, List[str]]) -> tuple:
    return (pillars["year"][1], pillars["month"][1],
            pillars["day"][1],   pillars["hour"][1])

def xiuqi_axis(pillars: Dict[str, List[str]],
               facts: Dict[str, Any],
               gate_debug: List[str]) -> XiuqiResult:
    ys, ms, ds, hs = _stems(pillars)
    br = _branches(pillars)
    mb = facts["month_branch"]

    g = HE.get(ds)
    if g is None or g not in (ms, hs):
        return XiuqiResult(None, "化气型", False, False, False, False, False, 0, [])

    # B1：独合/争合（修正Bug A：统计方向反了）
    same_day = sum(1 for x in (ys, ms, hs) if x == ds)
    same_he  = sum(1 for x in (ys, ms, hs) if x == g)
    zheng_he = (same_day >= 2) or (same_he >= 2)
    b1a, b1b = (not zheng_he), zheng_he

    # B2：化神当令（修正Bug B：化神由合对定非由日干定）
    pair = "".join(sorted([ds, g]))
    hx = HUA_SHEN.get(pair, "")
    b2 = (MONTH_WANG.get(mb) == hx)

    # B3：逢龙引化，与稼穑去重
    chen = ("辰" in br)
    si_zhu_cxsw = all(x in br for x in ("辰", "戌", "丑", "未"))
    b3 = chen and (not si_zhu_cxsw)

    # B4：无破（复用现有闸门）
    b4 = (len(gate_debug) == 0)

    score = sum([b1a or b1b, b2, b4]) + (1 if b3 else 0)
    root = f"一行成象·{hx_to_ge(hx)}" if hx else None

    return XiuqiResult(root, "化气型", b1a, b1b, b2, b3, b4, score, list(gate_debug))
