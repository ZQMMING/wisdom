"""PZZQ 月令取格派生（《子平真诠·论用神》· 引擎自有 Derived Facts，§65）。

依据原著原文（精校稿第24页）：
- 「八字用神，專求月令。以日干配月令地支，而生剋不同，格局分為財官印食。
   煞傷刃劫，此用神之不善而逆用之者也。」
- 「然亦有月令無用神者，如木生寅卯，月與日同，本身不可為用……
   是建祿月劫之格，非用而即用神也。」

第一层实现（本气取格）：
1. 月支本气（人元司令首干）与日干定十神；
2. 財官印食（正官/七殺/正偏財/正偏印/食神/傷官）→ 对应格局名；
3. 比肩（月與日同）→ 建祿月劫格；劫財 → 阳干帝旺位为陽刃格，否则建祿月劫格。
透干/会支（論用神變化「月令所藏不一……透干會支」）留待 Human 裁定后第二层。

不重排盘：只消费日干/月支/月支藏干静态表。
"""

from __future__ import annotations

from shared_types.fail_closed import FailClosedReason, FailClosedError

# 人元司令藏干表（通行定式；L0 hidden_stems 若提供则优先）
BRANCH_HIDDEN = {
    "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
    "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "庚", "戊"],
    "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
    "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"],
}

STEM_ELEMENT = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}
STEM_YINYANG = {
    "甲": "阳", "乙": "阴", "丙": "阳", "丁": "阴", "戊": "阳",
    "己": "阴", "庚": "阳", "辛": "阴", "壬": "阳", "癸": "阴",
}

# 阳干帝旺（阳刃）位
YANG_REN_POS = {"甲": "卯", "丙": "午", "戊": "午", "庚": "酉", "壬": "子"}

# 十神 → 格局名（原著八格）
PATTERN_NAME = {
    "正官": "正官格", "七殺": "七煞格",
    "正財": "財格", "偏財": "財格",
    "正印": "印格", "偏印": "印格",
    "食神": "食神格", "傷官": "傷官格",
}


def _ten_god(day_stem: str, target_stem: str) -> str:
    """标准十神（同我/我生/我克/克我/生我 × 阴阳）。"""
    d_el, d_yy = STEM_ELEMENT[day_stem], STEM_YINYANG[day_stem]
    t_el, t_yy = STEM_ELEMENT[target_stem], STEM_YINYANG[target_stem]
    same_yy = (d_yy == t_yy)
    if d_el == t_el:
        return "比肩" if same_yy else "劫財"
    # 生克关系
    produce = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    control = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    if produce[d_el] == t_el:      # 我生
        return "食神" if same_yy else "傷官"
    if control[d_el] == t_el:      # 我克
        return "偏財" if same_yy else "正財"
    if produce[t_el] == d_el:      # 生我
        return "偏印" if same_yy else "正印"
    if control[t_el] == d_el:      # 克我
        return "七殺" if same_yy else "正官"
    raise FailClosedError(FailClosedReason.CONTRACT_INVALID,
                          f"十神判定失败: {day_stem}/{target_stem}")


def derive_pattern(day_stem: str, month_branch: str,
                   hidden: dict | None = None) -> str:
    """月令本气取格 → 格局名。

    hidden: L0 hidden_stems 若提供则优先（键=支，值=藏干列表，首干为本气）。
    """
    if not day_stem or not month_branch:
        raise FailClosedError(FailClosedReason.INPUT_FORBIDDEN, "取格需要 day_stem/month_branch")
    hd = hidden or {}
    stems = hd.get(month_branch) or BRANCH_HIDDEN.get(month_branch)
    if not stems:
        raise FailClosedError(FailClosedReason.CONTRACT_INVALID, f"未知月支: {month_branch}")
    benqi = stems[0]
    tg = _ten_god(day_stem, benqi)
    if tg == "比肩":
        return "建祿月劫格"          # 月與日同（建祿）
    if tg == "劫財":
        if YANG_REN_POS.get(day_stem) == month_branch:
            return "陽刃格"
        return "建祿月劫格"          # 月劫
    return PATTERN_NAME.get(tg, tg + "格")
