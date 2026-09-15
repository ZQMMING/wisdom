"""DTS 基础态势派生（Phase 6 §65 ·《滴天髓》基础字段）。

本轮输出（对应 DTS 规则 001-009，不依赖 strength 旺衰）：
- stem           : 日干（CAND-DTS-001/002 丙/癸 判定「陽之至/陰之至」）
- stem_yinyang   : 日干阴阳（003/004 從氣不從勢/從勢）
- branch_yinyang : 月支阴阳（005/006 動強速達/靜專否泰；口径：月支，月令为纲）
- relation       : "沖"（007/009 沖关系存在时；展开 L0 relations.liu_chong）
- pillar         : 日柱干支（018/019 甲申/戊寅/癸丑/庚寅 判定；= stem_branch_pair）

注：CAND-DTS-007（生方忌沖動）为 suppress 规则，RuleEngine 只消费 emit，
suppress 语义 V2.22 未定义条款，已记录待审批裁决；本派生只注入其前置字段。
"""

from __future__ import annotations

from typing import Any, Dict

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
    return out
