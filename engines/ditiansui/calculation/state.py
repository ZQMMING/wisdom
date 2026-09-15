"""DTS 基础态势派生（Phase 6 §65 ·《滴天髓》基础字段）。

本轮输出（对应 DTS 规则 001-009，不依赖 strength 旺衰）：
- stem           : 日干（CAND-DTS-001/002 丙/癸 判定「陽之至/陰之至」）
- stem_yinyang   : 日干阴阳（003/004 從氣不從勢/從勢）
- branch_yinyang : 月支阴阳（005/006 動強速達/靜專否泰；口径：月支，月令为纲）
- relation       : "沖"（007/009 沖关系存在时；展开 L0 relations.liu_chong）
- pillar         : 日柱干支（018/019 甲申/戊寅/癸丑/庚寅 判定；= stem_branch_pair）
- tian_status    : 四天干同五行 → "全一氣"（012，DTS-010-004）
- di_status      : 四地支成三会/三合局 → "全三物"（013，DTS-010-006/007 注：寅卯辰、亥卯未）
- stem_position  : 日干阳+日支阳 → "陽乘陽位"；阴+阴 → "陰乘陰位"（014/015，DTS-010-008/010）
- xing_state     : 四柱干支五行覆盖（DTS-011-003/008：五行俱全→"形全"；有缺→"形缺"）

注：CAND-DTS-007（生方忌沖動）为 suppress 规则，RuleEngine 只消费 emit，
suppress 语义 V2.22 未定义条款，已记录待审批裁决；本派生只注入其前置字段。
旺衰类字段（source_strength/target_strength/day_master_strength 等）依赖
strength_state 判定（《滴天髓》衰旺篇规则），后续篇章派生接入。
"""

from __future__ import annotations

from typing import Any, Dict

# 干五行
STEM_ELEMENT: Dict[str, str] = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}
# 支五行
BRANCH_ELEMENT: Dict[str, str] = {
    "寅": "木", "卯": "木", "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水", "子": "水", "丑": "土",
}
# 三合局（任两支成局即视为局气，取完整组判定：组内三支齐全）
SANHE: Dict[str, set] = {
    "寅午戌": {"寅", "午", "戌"},
    "申子辰": {"申", "子", "辰"},
    "巳酉丑": {"巳", "酉", "丑"},
    "亥卯未": {"亥", "卯", "未"},
}
# 三会方（DTS-010-007 注「寅卯辰、亥卯未」）
SANHUI: Dict[str, set] = {
    "寅卯辰": {"寅", "卯", "辰"},
    "巳午未": {"巳", "午", "未"},
    "申酉戌": {"申", "酉", "戌"},
    "亥子丑": {"亥", "子", "丑"},
}
# 干阴阳（阳干：甲丙戊庚壬）
STEM_YINYANG: Dict[str, str] = {
    "甲": "陽", "丙": "陽", "戊": "陽", "庚": "陽", "壬": "陽",
    "乙": "陰", "丁": "陰", "己": "陰", "辛": "陰", "癸": "陰",
}
# 支阴阳（阳支：子寅辰午申戌）
BRANCH_YINYANG: Dict[str, str] = {
    "子": "陽", "寅": "陽", "辰": "陽", "午": "陽", "申": "陽", "戌": "陽",
    "丑": "陰", "卯": "陰", "巳": "陰", "未": "陰", "酉": "陰", "亥": "陰",
}


def _has_bureau(branches: list) -> bool:
    """四地支是否成三会/三合局（组内三支齐全）。"""
    bset = set(branches)
    for grp in list(SANHE.values()) + list(SANHUI.values()):
        if grp <= bset:
            return True
    return False


def derive_state(day_stem: str | None = None,
                 month_branch: str | None = None,
                 hidden: Any = None,
                 transparent_stems: Any = None,
                 branches: Any = None,
                 base: Dict[str, Any] | None = None,
                 l0_chart: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """DTS 基础态势派生（§65）：注入 stem/阴阳/冲关系。"""
    out: Dict[str, Any] = {}
    if day_stem:
        out["stem"] = day_stem
        out["stem_yinyang"] = STEM_YINYANG.get(day_stem)
    if month_branch:
        out["branch_yinyang"] = BRANCH_YINYANG.get(month_branch)
    relations = (base or {}).get("relations") or {}
    if relations.get("liu_chong"):
        out["relation"] = "沖"
    if base and base.get("stem_branch_pair"):
        out["pillar"] = base["stem_branch_pair"]
    # 全一氣：四天干同五行（DTS-010-004）
    if base:
        stems = [base.get("year_stem"), base.get("month_stem"), day_stem, base.get("hour_stem")]
        if all(stems) and len({STEM_ELEMENT.get(s) for s in stems}) == 1:
            out["tian_status"] = "全一氣"
    # 全三物：四地支成三会/三合局（DTS-010-006/007）
    if branches and _has_bureau(list(branches)):
        out["di_status"] = "全三物"
    # 陽乘陽位 / 陰乘陰位（DTS-010-008/010；口径：日干坐日支）
    if day_stem and (base or {}).get("day_branch"):
        ds_yy = STEM_YINYANG.get(day_stem)
        db_yy = BRANCH_YINYANG.get((base or {}).get("day_branch"))
        if ds_yy == "陽" and db_yy == "陽":
            out["stem_position"] = "陽乘陽位"
        elif ds_yy == "陰" and db_yy == "陰":
            out["stem_position"] = "陰乘陰位"
    # 形全/形缺：四柱干支五行覆盖（DTS-011-003/008「形全者宜損其有餘，形缺者宜補其不足」）
    if base:
        els = {STEM_ELEMENT.get(s) for s in (base.get("year_stem"), base.get("month_stem"),
                                             day_stem, base.get("hour_stem"))}
        els |= {BRANCH_ELEMENT.get(b) for b in (base.get("year_branch"), base.get("month_branch"),
                                                base.get("day_branch"), base.get("hour_branch"))}
        els.discard(None)
        out["xing_state"] = "形全" if len(els) >= 5 else "形缺"
    return out
