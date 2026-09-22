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

HUA_SHEN = {"甲己": "土", "己甲": "土", "乙庚": "金", "庚乙": "金",
            "丙辛": "水", "辛丙": "水", "丁壬": "木", "壬丁": "木",
            "戊癸": "火", "癸戊": "火"}

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
    b5: bool  # 化神支局全
    b6: bool  # G4：无克化神透干
    b7: bool  # G8：财星不超标（财透一位虚浮尚可，两位/根深则转格）
    b8: bool  # G7：日主有根→降档（不是硬闸，是减项）
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
        return XiuqiResult(None, "化气型", False, False, False, False, False, False, False, False, False, 0, [])

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

    # B5：化神支局全（按化神五行查三合/三会）
    cf = facts.get("combination_facts", {})
    sh_list = cf.get("sanhe", [])
    sf_list = cf.get("sanhui", [])
    hx_ju_map = {
        "木": ("亥卯未合木", "寅卯辰三会木"),
        "火": ("寅午戌合火", "巳午未三会火"),
        "土": (None, None),  # 稼穑四库全特判在A轴
        "金": ("巳酉丑合金", "申酉戌三会金"),
        "水": ("申子辰合水", "亥子丑三会水"),
    }
    sanhe_name, sanhui_name = hx_ju_map.get(hx, (None, None))
    if hx == "土":
        # 稼穑四库全
        b5 = all(x in br for x in ("辰", "戌", "丑", "未"))
    else:
        sanhe_ok = sanhe_name and sanhe_name in sh_list
        sanhui_ok = sanhui_name and sanhui_name in sf_list
        b5 = sanhe_ok or sanhui_ok

    # B6：G4 无克化神透干（排除合化之干）
    ke_map = {"木": "金", "火": "水", "土": "木", "金": "火", "水": "土"}
    ke_wx = ke_map.get(hx, "")
    ke_stems = [s for s in "甲乙丙丁戊己庚辛壬癸" if WUXING.get(s) == ke_wx]
    # 排除合化之干（日干+合神）
    exclude = {ds, g}
    check_stems = [s for s in (ys, ms, hs) if s not in exclude]
    has_ke = any(s in check_stems for s in ke_stems)
    b6 = not has_ke

    # B7：G8 财星不超标（财 = 化神所克）
    # 财 = 化神所克：木克土(戊己)、火克金(庚辛)、土克水(壬癸)、金克木(甲乙)、水克火(丙丁)
    cai_map = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
    cai_wx = cai_map.get(hx, "")
    cai_stems = [s for s in "甲乙丙丁戊己庚辛壬癸" if WUXING.get(s) == cai_wx]
    # 财透数量（排除日干和合化之干，只查年/月/时三干，且排除合神）
    other_stems = [ys, ms, hs]
    exclude = {ds, g}
    tou_cai = [s for s in other_stems if (s in cai_stems) and (s not in exclude)]
    # 财根深：地支有财五行本气
    cai_roots = sum(1 for b in br if WUXING.get(b) == cai_wx)
    # 超标条件：财透两位，或财透一位但根深(>=2)
    if len(tou_cai) >= 2:
        b7 = False
    elif len(tou_cai) == 1 and cai_roots >= 2:
        b7 = False
    else:
        b7 = True

    # B8：G7 日主有根→降档（不是硬闸，是减项）
    # 日主在地支见本气根（含库中余气）→ 化得不彻底→降MID
    # 注意：日干原五行=化神五行时不算（如甲己化土，日干己土，化神也是土，见土根是化神有根，不是日主有根）
    day_wx = WUXING.get(ds, "")
    if day_wx != hx:
        day_roots = sum(1 for b in br if WUXING.get(b) == day_wx)
        b8 = day_roots >= 1  # True=有根→降档
    else:
        b8 = False  # 日干五行=化神五行，不存在"日主有根不降"的问题

    score = sum([b1a or b1b, b2, b4, b6, b7]) + (1 if b3 else 0) + (1 if b5 else 0)
    root = f"一行成象·{hx_to_ge(hx)}" if hx else None

    return XiuqiResult(root, "化气型", b1a, b1b, b2, b3, b4, b5, b6, b7, b8, score, list(gate_debug))
