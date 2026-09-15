"""PZZQ 月令取格派生（《子平真诠·论用神》· 引擎自有 Derived Facts，§65）。

依据原著原文（精校稿第24页）：
- 「八字用神，專求月令。以日干配月令地支，而生剋不同，格局分為財官印食。
   煞傷刃劫，此用神之不善而逆用之者也。」
- 「然亦有月令無用神者，如木生寅卯，月與日同，本身不可為用……
   是建祿月劫之格，非用而即用神也。」

第二层实现（透干取格，《论用神变化》第27页）：
- 本气透出天干 → 本气定格（「格成正財，正官乃其兼格」：变而不失本格）
- 本气不透、余/中气透出 → 透出者作主（「不透甲而透丙，則同知得以作主」）
- 多透次序：原著未明示。注家口径（《八格外格》「支藏两神并透，斟酌其一，
  以有力而无克合者为上」；今人「本气优先、先取月令再取月令外」）→ 暂定
  「月干>时干>年干」（月干透出紧贴月令最有力）；「有力/克合」细化待 Human 裁定
- 会支（三合化局）变化（「支全卯未」「會午會戌」）留待第三层

第一层实现（本气取格）：
1. 月支本气（人元司令首干）与日干定十神；
2. 財官印食（正官/七殺/正偏財/正偏印/食神/傷官）→ 对应格局名；
3. 比肩（月與日同）→ 建祿月劫格；劫財 → 阳干帝旺位为陽刃格，否则建祿月劫格。

不重排盘：只消费日干/月支/月支藏干静态表/四柱天干。
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


def _pattern_by_ten_god(day_stem: str, tg: str, month_branch: str) -> str:
    """十神 → 格局名（含建祿/月劫/陽刃特殊位）。"""
    if tg == "比肩":
        return "建祿月劫格"          # 月與日同（建祿）
    if tg == "劫財":
        if YANG_REN_POS.get(day_stem) == month_branch:
            return "陽刃格"
        return "建祿月劫格"          # 月劫
    return PATTERN_NAME.get(tg, tg + "格")


def derive_pattern(day_stem: str, month_branch: str,
                   hidden: dict | None = None,
                   transparent_stems: list | None = None) -> str:
    """月令取格 → 格局名（透干第二层 + 本气第一层）。

    hidden: L0 hidden_stems 若提供则优先（键=支，值=藏干列表，首干为本气）。
    transparent_stems: 四柱天干（年/月/时），用于透干判定。

    依据《论用神变化》（第27页）：
    - 「不透甲而透丙，則如知府不臨郡，而同知得以作主」→ 本气不透、余/中气透 → 透出者作主
    - 「辛生寅月，透丙化官而又透甲，格成正財，正官乃其兼格」→ 本气透 → 本气定格，化气为兼
    """
    if not day_stem or not month_branch:
        raise FailClosedError(FailClosedReason.INPUT_FORBIDDEN, "取格需要 day_stem/month_branch")
    hd = hidden or {}
    stems = hd.get(month_branch) or BRANCH_HIDDEN.get(month_branch)
    if not stems:
        raise FailClosedError(FailClosedReason.CONTRACT_INVALID, f"未知月支: {month_branch}")
    benqi = stems[0]
    # 透干判定：本气透 → 本气定格（变而不失本格）；本气不透而余/中气透 → 透出者作主
    if transparent_stems:
        transparent = [s for s in transparent_stems if s in stems]
        if transparent:
            if benqi in transparent:
                return _pattern_by_ten_god(day_stem, _ten_god(day_stem, benqi), month_branch)
            # 多透次序（月干 > 时干 > 年干）属《论用神变化》未明示处，待 Human 裁定
            picked = next((s for s in (transparent_stems[1:2] + transparent_stems[2:3] + transparent_stems[0:1])
                           if s in transparent), transparent[0])
            return _pattern_by_ten_god(day_stem, _ten_god(day_stem, picked), month_branch)
    # 不透 → 本气定格（第一层：財官印食煞傷刃劫 + 建祿/月劫/陽刃）
    return _pattern_by_ten_god(day_stem, _ten_god(day_stem, benqi), month_branch)
