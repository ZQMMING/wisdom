"""
Zhongzhou Combination Resolver — 中州派星系组合成立条件（P0-4-A）

职责：
- 只判定 Feature 之间的关系是否成立。
- 不重新计算星盘事实（已由 Feature 层产出）。
- 产出 Combo ID 列表（组合编号），供 Judgment 层使用。

证据等级约束：
- 本模块所有 Combo 派生均基于王亭之明文规则（一级证据）。
- 三级 / 四级证据（后人推论 / 现代推演）一律不进入本模块。

P0-4-A 严格 10 条生产候选（主规则）+ 10 条 DRAFT/CANDIDATE（变体/次格/反向/需要 chart 引用）。

工程纪律（user 裁决）：
- "宁可少不可编"
- "作者讲过 ≠ 直接 Boolean 化的生产规则"
- P0-4-A 主规则 10 条进入生产；其余 10 条留 DRAFT/CANDIDATE。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .features import ZhongzhouFeatureBundle

ComboId = Literal[
    # P0-4-A 主规则（10 条）
    "ZHZ-CMB-001",  # 机月同梁格（标准）
    "ZHZ-CMB-003",  # 杀破廉贪格
    "ZHZ-CMB-004",  # 财荫夹印（标准）
    "ZHZ-CMB-006",  # 刑忌夹印（标准）
    "ZHZ-CMB-008",  # 紫微孤君
    "ZHZ-CMB-010",  # 明珠出海格（吉）
    "ZHZ-CMB-012",  # 暗曜凶格（杀破贪）
    "ZHZ-CMB-016",  # 杀陷震兑
    "ZHZ-CMB-017",  # 禄存必为羊陀夹
    "ZHZ-CMB-018",  # 禄马交驰
]

# 截空值日地支
JIE_KONG_BRANCHES = {"丑", "未", "寅", "申"}

# 七杀陷地支（卯酉为震兑）
QI_SHA_XIAN_BRANCHES = {"卯", "酉"}

# 廉贞+破军 同宫+地支（卯酉）
LIAN_PO_BRANCHES = {"卯", "酉"}


@dataclass(frozen=True)
class ZhongzhouCombination:
    """一个 Combo 命中的事实快照（供 Judgment 层引用）。"""
    combo_id: str
    feature_id: str
    witness_palaces: frozenset[str]
    evidence_grade: Literal[1, 2, "1.5"]


def has_any_of_in_set(stars: set[str], candidates: set[str]) -> bool:
    return bool(stars & candidates)


# ─────────────────────────────────────────────────────────────────────────
# P0-4-A 主规则（10 条，全部进入生产候选）
# ─────────────────────────────────────────────────────────────────────────


def detect_ji_yue_tong_liang_standard(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """
    R-COMBO-08 / ZHZ-CMB-001 机月同梁格（标准）
    王亭之原文（谈星 1107 + d48733）：
      "机月同梁作吏人" - 命宫三方四正含 天机 + 天同 + 天梁 + 太阴 全 4 曜。
    证据等级：1（王亭之原文）
    """
    target = {"天机", "天同", "天梁", "太阴"}
    if target.issubset(bundle.ming_sanfang_stars):
        return ZhongzhouCombination(
            combo_id="ZHZ-CMB-001",
            feature_id="MING_SANFANG_HAS_JI_YUE_TONG_LIANG",
            witness_palaces=frozenset({"命宫"}),
            evidence_grade=1,
        )
    return None


def detect_sha_po_lian_tan(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """
    R-COMBO-09 / ZHZ-CMB-003 杀破廉贪格
    王亭之原文（d48733 + 谈星 1107）：
      "杀破廉贪四曜，性质刚烈，入庙会照主大富贵，否则主大凶暴。"
    触发条件：杀破贪廉任一在命宫三方四正内。
    证据等级：1
    """
    target = {"七杀", "破军", "贪狼", "廉贞"}
    if has_any_of_in_set(bundle.ming_sanfang_stars, target):
        return ZhongzhouCombination(
            combo_id="ZHZ-CMB-003",
            feature_id="MING_SANFANG_HAS_SHA_PO_LIAN_TAN",
            witness_palaces=frozenset({"命宫"}),
            evidence_grade=1,
        )
    return None


def detect_cai_yin_jia_yin_standard(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """
    R-COMBO-06 / ZHZ-CMB-004 财荫夹印（标准格）
    王亭之原文（谈星 1108）：
      天相 + 左右邻宫分别 巨门 + 天梁（巨门主财，天梁主荫）。
    证据等级：1
    """
    if not bundle.tianxiang_palace:
        return None
    left = bundle.tianxiang_left_stars
    right = bundle.tianxiang_right_stars
    if (("巨门" in left and "天梁" in right) or
            ("巨门" in right and "天梁" in left)):
        return ZhongzhouCombination(
            combo_id="ZHZ-CMB-004",
            feature_id="TIANXIANG_NEIGHBOR_JUMEN_AND_TIANLIANG",
            witness_palaces=frozenset({
                bundle.tianxiang_palace,
                bundle.tianxiang_left_neighbor or "",
                bundle.tianxiang_right_neighbor or "",
            } - {""}),
            evidence_grade=1,
        )
    return None


def detect_xing_ji_jia_yin_standard(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """
    R-COMBO-06 / ZHZ-CMB-006 刑忌夹印（标准格）
    王亭之原文（谈星 1108）：
      巨门 + 天梁 在天相左右邻宫，刑克主人，主官非。
    证据等级：1
    注：与财荫夹印标准格位置铁律相同，判定差异在 Judgment 层（吉 vs 凶）。
    """
    if not bundle.tianxiang_palace:
        return None
    left = bundle.tianxiang_left_stars
    right = bundle.tianxiang_right_stars
    if (("巨门" in left and "天梁" in right) or
            ("巨门" in right and "天梁" in left)):
        return ZhongzhouCombination(
            combo_id="ZHZ-CMB-006",
            feature_id="TIANXIANG_NEIGHBOR_JUMEN_HUAJI_AND_TIANLIANG",
            witness_palaces=frozenset({
                bundle.tianxiang_palace,
                bundle.tianxiang_left_neighbor or "",
                bundle.tianxiang_right_neighbor or "",
            } - {""}),
            evidence_grade=1,
        )
    return None


def detect_ziwei_gu_jun(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """
    R-DEF-02/03 / ZHZ-CMB-008 紫微孤君
    王亭之原文（谈星 1107）：
      "紫微在子午 / 辰戌 / 丑未 / 寅申，三方无左辅右弼者，为孤君。"
    触发：紫微在命宫 + 三方四正无左辅右弼。
    证据等级：1
    """
    if not bundle.ziwei_palace or bundle.ziwei_palace != "命宫":
        return None
    if "左辅" not in bundle.ziwei_sanfang_stars and \
       "右弼" not in bundle.ziwei_sanfang_stars:
        return ZhongzhouCombination(
            combo_id="ZHZ-CMB-008",
            feature_id="ZIWEI_MING_NO_FU_BI_IN_SANFANG",
            witness_palaces=frozenset({"命宫"}),
            evidence_grade=1,
        )
    return None


def detect_ming_zhu_chu_hai_auspicious(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """
    R-COMBO-10 / ZHZ-CMB-010 明珠出海格（吉）
    王亭之原文（d48733 + 谈星 1113）：
      "明珠出海"格指太阳/太阴 + 文昌/文曲 + 截空值日不在同宫。
    证据等级：1
    """
    target = {"太阳", "太阴"}
    stars = bundle.ming_sanfang_stars
    has_yin_yang = bool(target & stars)
    has_chang_qu = "文昌" in stars or "文曲" in stars
    ming_branch = bundle.ming_palace_branch
    jie_kong_safe = bool(ming_branch) and ming_branch not in JIE_KONG_BRANCHES
    if has_yin_yang and has_chang_qu and jie_kong_safe:
        return ZhongzhouCombination(
            combo_id="ZHZ-CMB-010",
            feature_id="MING_SANFANG_YINYANG_CHANG_QU_JIE_KONG_SAFE",
            witness_palaces=frozenset({"命宫"}),
            evidence_grade=1,
        )
    return None


def detect_an_yao_sha_po_tan(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """
    R-JDG-12/13 / ZHZ-CMB-012 暗曜凶格（杀破贪）
    王亭之原文（谈星 1109 / 1120）：
      "文曲化忌"与"杀破贪"同宫，主暗损。
    触发：文曲所在宫 = 七杀/破军/贪狼 任一所在宫。
    证据等级：1
    """
    if not bundle.wenqu_palace:
        return None
    if bundle.wenqu_palace in bundle.sha_po_tan_palaces:
        return ZhongzhouCombination(
            combo_id="ZHZ-CMB-012",
            feature_id="WENQU_AT_SHA_PO_TAN",
            witness_palaces=frozenset({bundle.wenqu_palace}),
            evidence_grade=1,
        )
    return None


def detect_sha_xian_zhen_dui(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """
    R-JDG-22 / ZHZ-CMB-016 杀陷震兑
    王亭之原文（谈星 1117）：
      七杀在卯/酉 + 武曲同度，主震兑方位凶险。
    证据等级：1
    """
    if not bundle.qi_sha_palace_branch:
        return None
    if bundle.qi_sha_palace_branch not in QI_SHA_XIAN_BRANCHES:
        return None
    if not bundle.wu_qu_in_qi_sha:
        return None
    return ZhongzhouCombination(
        combo_id="ZHZ-CMB-016",
        feature_id="QI_SHA_XIAN_BRANCH_WITH_WU_QU",
        witness_palaces=frozenset({bundle.qi_sha_palace or ""} - {""}),
        evidence_grade=1,
    )


def detect_lu_cun_ya_tuo_jia(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """
    R-DEF-05 / ZHZ-CMB-017 禄存必为羊陀夹
    王亭之原文（谈星 1126）：
      "禄存必为羊陀所夹" - 禄存所在宫，两个邻宫分别有擎羊+陀罗（顺序不限）。
    证据等级：1
    """
    if not bundle.lucun_palace:
        return None
    left = bundle.lucun_left_stars
    right = bundle.lucun_right_stars
    ya_present = "擎羊" in (left | right)
    tuo_present = "陀罗" in (left | right)
    if ya_present and tuo_present:
        return ZhongzhouCombination(
            combo_id="ZHZ-CMB-017",
            feature_id="LUCUN_FLANKED_BY_YA_TUO",
            witness_palaces=frozenset({
                bundle.lucun_palace,
                bundle.lucun_left_neighbor or "",
                bundle.lucun_right_neighbor or "",
            } - {""}),
            evidence_grade=1,
        )
    return None


def detect_lu_ma_jiao_chi(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """
    R-JDG-18 / ZHZ-CMB-018 禄马交驰
    王亭之原文（谈星 1126）：
      禄存 + 天马 同宫，主发财于远地。
    证据等级：1
    """
    if not (bundle.lucun_palace and bundle.tianma_palace):
        return None
    if bundle.lucun_palace == bundle.tianma_palace:
        return ZhongzhouCombination(
            combo_id="ZHZ-CMB-018",
            feature_id="LUCUN_TIANMA_SAME_PALACE",
            witness_palaces=frozenset({bundle.lucun_palace}),
            evidence_grade=1,
        )
    return None


# ─────────────────────────────────────────────────────────────────────────
# P0-4-A DRAFT/CANDIDATE（10 条 - 暂不触发，detect 函数保留供 P0-4-B + P0-5）
# 严格按"宁可少不可编"：作者讲过但需更复杂的判定，超出当前 bundle 范畴。
# ─────────────────────────────────────────────────────────────────────────


def detect_ji_yue_tong_liang_variant_draft(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """ZHZ-CMB-002 机月同梁格变格（DRAFT - 需化禄判定）"""
    return None


def detect_cai_yin_jia_yin_secondary_draft(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """ZHZ-CMB-005 财荫夹印次格（DRAFT - 需化禄判定）"""
    return None


def detect_xing_ji_jia_yin_sha_cou_draft(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """ZHZ-CMB-007 刑忌夹印煞凑（DRAFT - 需 chart 引用查同宫辅星）"""
    return None


def detect_ziwei_fei_gu_jun_draft(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """ZHZ-CMB-009 紫微非孤君（DRAFT - 反向判定，等价孤君未触发）"""
    return None


def detect_ming_zhu_chu_hai_broken_draft(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """ZHZ-CMB-011 明珠出海格破格（DRAFT - 与吉格互斥）"""
    return None


def detect_lian_po_xiong_draft(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """ZHZ-CMB-013 廉破凶格（DRAFT - 需 chart 引用 + 同宫辅星）"""
    return None


def detect_lian_zheng_fan_ge_draft(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """ZHZ-CMB-014 廉贞反格（DRAFT - 需 chart 引用 + 四化判定）"""
    return None


def detect_qi_sha_gao_ge_draft(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """ZHZ-CMB-015 七杀高格（DRAFT - 需 chart 引用 + 化禄判定）"""
    return None


def detect_zuo_gui_xiang_gui_draft(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """ZHZ-CMB-019 坐贵向贵（DRAFT - 需 chart 引用 + 身宫归属判定）"""
    return None


def detect_an_zhi_tai_ji_draft(
    bundle: ZhongzhouFeatureBundle,
) -> ZhongzhouCombination | None:
    """ZHZ-CMB-020 暗痣/胎记（DRAFT - 需 chart 引用 + 多曜同宫判定）"""
    return None


# ─────────────────────────────────────────────────────────────────────────
# 全 detect 函数列表（供 rule_graph.py 统一调度）
# 仅 P0-4-A 主规则 10 条触发；DRAFT 暂不触发。
# ─────────────────────────────────────────────────────────────────────────

P0_4_A_PRODUCTION_DETECTORS = [
    detect_ji_yue_tong_liang_standard,
    detect_sha_po_lian_tan,
    detect_cai_yin_jia_yin_standard,
    detect_xing_ji_jia_yin_standard,
    detect_ziwei_gu_jun,
    detect_ming_zhu_chu_hai_auspicious,
    detect_an_yao_sha_po_tan,
    detect_sha_xian_zhen_dui,
    detect_lu_cun_ya_tuo_jia,
    detect_lu_ma_jiao_chi,
]

DRAFT_DETECTORS = [
    detect_ji_yue_tong_liang_variant_draft,
    detect_cai_yin_jia_yin_secondary_draft,
    detect_xing_ji_jia_yin_sha_cou_draft,
    detect_ziwei_fei_gu_jun_draft,
    detect_ming_zhu_chu_hai_broken_draft,
    detect_lian_po_xiong_draft,
    detect_lian_zheng_fan_ge_draft,
    detect_qi_sha_gao_ge_draft,
    detect_zuo_gui_xiang_gui_draft,
    detect_an_zhi_tai_ji_draft,
]

ALL_DETECTORS = P0_4_A_PRODUCTION_DETECTORS + DRAFT_DETECTORS
