# -*- coding: utf-8 -*-
"""A轴（福德侧/支局侧）计分

精确字符串匹配 + 稼穑特判 + 官杀硬闸/财星减项
阈值全部引《渊海子平》卷二外十八格（grade=A）
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Set, Optional

@dataclass
class FudeResult:
    pattern_root: Optional[str]
    a1_day: bool
    a2_ju: bool
    a3_po: bool
    cai_po: bool
    ju_detail: str
    score: int
    gate_debug: List[str]

# 五格要件表：日主 / 三合 / 三会 / 官杀破格 / 财星破格
_REQS: Dict[str, Dict] = {
    "曲直": dict(day={"甲", "乙"}, sanhe="亥卯未合木", sanhui="寅卯辰三会木",
                 po={"庚", "辛"}, cai=set()),
    "炎上": dict(day={"丙", "丁"}, sanhe="寅午戌合火", sanhui="巳午未三会火",
                 po={"壬", "癸"}, cai={"庚", "辛"}),
    "稼穑": dict(day={"戊", "己"}, sanhe=None, sanhui="辰戌丑未三会土",
                 po={"甲", "乙"}, cai={"壬", "癸"}),
    "从革": dict(day={"庚", "辛"}, sanhe="巳酉丑合金", sanhui="申酉戌三会金",
                 po={"丙", "丁"}, cai=set()),
    "润下": dict(day={"壬", "癸"}, sanhe="申子辰合水", sanhui="亥子丑三会水",
                 po={"戊", "己"}, cai=set()),
}

def _stems(pillars):
    return (pillars["year"][0], pillars["month"][0],
            pillars["day"][0],   pillars["hour"][0])

def fude_axis(pillars: Dict, facts: Dict, gate_debug: List[str]) -> FudeResult:
    ds = pillars["day"][0]
    sh_list = set(facts.get("combination_facts", {}).get("sanhe", []))
    sf_list = set(facts.get("combination_facts", {}).get("sanhui", []))

    best, detail = None, "无"

    for ge, rq in _REQS.items():
        if ds not in rq["day"]:
            continue

        sanhe_ok = rq["sanhe"] and (rq["sanhe"] in sh_list)
        sanhui_ok = rq["sanhui"] and (rq["sanhui"] in sf_list)

        if not (sanhe_ok or sanhui_ok):
            continue

        best = ge
        if sanhe_ok:
            detail = rq["sanhe"] + "(三合)"
        else:
            detail = rq["sanhui"] + "(三会)"
        break

    if best is None:
        return FudeResult(None, True, False, False, False, "无", 0, [])

    rq = _REQS[best]
    a1 = ds in rq["day"]
    a3 = all(x not in _stems(pillars) for x in rq["po"])
    cai = any(x in _stems(pillars) for x in rq["cai"]) if rq["cai"] else False

    a2 = (detail != "无")
    score = sum([a1, a2, a3]) - (1 if cai else 0)

    return FudeResult(f"一行成象·{best}", a1, a2, a3, cai, detail, score, list(gate_debug))
