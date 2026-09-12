"""
Feixing Combinations — 飞星派组合 detect 函数（P0-5-A）

严格工程边界：
- 5 条 production detect 函数（grade=1 王亭之原文 / 飞星嫡系讲义支持）
- 5 条 DRAFT/CANDIDATE detect_*_draft 强制返回 None（不进生产）
- detect 返回 ZhongzhouCombination-style ComboResult dataclass
- 所有 detect 必须 fail-closed：证据缺失返回 None

证据等级约束：
- 只有 grade=1 规则允许进 PRODUCTION_DETECTORS
- grade=3+ 规则只在 DRAFT_DETECTORS 占位，detect_*_draft 返回 None
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ....ziwei_engine import FrozenZiweiChart
from .features import (
    FeixingFeatureBundle,
    build_feature_bundle,
    find_star_palace,
    get_major_stars_in_palace,
    get_neighbor_palaces,
    get_palace_stem,
    has_self_ji_in_palace,
)


# ─────────────────────────────────────────────────────────────────────────
# ComboResult
# ─────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class FeixingCombination:
    """单条飞星组合 detect 结果。

    字段说明：
      rule_id       — 规则 ID（与 evidence.py 一一对应）
      detected      — 是否命中
      evidence_grade — 证据等级（1=生产；3+=DRAFT）
      facts         — 命中事实 dict（用于 audit）
      semantic_summary — 简短语义摘要（人读）
    """
    rule_id: str
    detected: bool
    evidence_grade: int
    facts: dict[str, Any]
    semantic_summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "detected": self.detected,
            "evidence_grade": self.evidence_grade,
            "facts": self.facts,
            "semantic_summary": self.semantic_summary,
        }


# ============================================================================
# PRODUCTION DETECTORS — 5 条 grade=1
# ============================================================================


def detect_cai_yin_jia_yin_feixing(
    chart: FrozenZiweiChart, bundle: FeixingFeatureBundle | None = None
) -> FeixingCombination | None:
    """FEX-CMB-001 财荫夹印（飞星派）— 天相被化禄+天梁夹

    王亭之谈星 08 (1115.html) 原�1115.html) 原文：
      「天梁为荫星，若另一旁的巨门化禄星之时，则此天相便为化禄及荫星所夹，
        称为财荫夹印...若夹天相为天机化禄、天同化禄，而非巨门化禄，
        亦成此格，唯一般主格局较次。」

    production 触发条件（简化）：
      - 命宫或关键宫有天相
      - 天相两邻宫之一有化禄飞入
      - 该邻宫主星 ∈ {天梁, 天机, 巨门, 天同}
    """
    if bundle is None:
        bundle = build_feature_bundle(chart)

    # 找到天相所在宫位
    tianxiang_palace = find_star_palace(chart, "天相")
    if not tianxiang_palace:
        return None

    # 检查两邻
    lu_neighbors = bundle.has_lu_in_neighbor(tianxiang_palace)
    if not lu_neighbors:
        return None

    # 验证邻宫主星 ∈ {天梁, 天机, 巨门, 天同}
    qualifying_neighbors = []
    for n in lu_neighbors:
        stars = get_major_stars_in_palace(chart, n)
        if stars & {"天梁", "天机", "巨门", "天同"}:
            qualifying_neighbors.append({
                "palace": n,
                "main_stars": sorted(stars),
            })

    if not qualifying_neighbors:
        return None

    return FeixingCombination(
        rule_id="FEX-CMB-001",
        detected=True,
        evidence_grade=1,
        facts={
            "center_palace": tianxiang_palace,
            "lu_neighbors": qualifying_neighbors,
            "trigger_pattern": "天相 + 两邻化禄 + 邻宫主星荫星",
        },
        semantic_summary=(
            f"天相位于{tianxiang_palace}，两邻宫 {qualifying_neighbors} 中有化禄飞入，"
            f"成财荫夹印，主得荫庇致取富贵。"
        ),
    )


def detect_xing_ji_jia_yin_feixing(
    chart: FrozenZiweiChart, bundle: FeixingFeatureBundle | None = None
) -> FeixingCombination | None:
    """FEX-CMB-002 刑忌夹印（飞星派）— 天相被化忌+天梁夹

    王亭之谈星 08 (1115.html) 原文：
      「天梁又为刑宪之星，若另一旁的巨门化为忌星，则成刑忌夹印之局，
        主人一生受压力，且多刑伤克害。
        若夹天相的天机化忌、天同化忌，而非巨门化忌，亦成此格，但克害较浅。
        于四煞，天相不畏擎羊或陀罗同度，但却畏羊陀相夹，
        是亦构成刑忌夹印。因为擎羊为刑，陀罗为忌。」

    production 触发条件：
      - 命宫或关键宫有天相
      - 天相两邻宫之一有化忌飞入
      - 该邻宫主星 ∈ {天梁, 天机, 巨门, 天同}
    """
    if bundle is None:
        bundle = build_feature_bundle(chart)

    tianxiang_palace = find_star_palace(chart, "天相")
    if not tianxiang_palace:
        return None

    ji_neighbors = bundle.has_ji_in_neighbor(tianxiang_palace)
    if not ji_neighbors:
        return None

    qualifying_neighbors = []
    for n in ji_neighbors:
        stars = get_major_stars_in_palace(chart, n)
        if stars & {"天梁", "天机", "巨门", "天同"}:
            qualifying_neighbors.append({
                "palace": n,
                "main_stars": sorted(stars),
            })

    if not qualifying_neighbors:
        return None

    return FeixingCombination(
        rule_id="FEX-CMB-002",
        detected=True,
        evidence_grade=1,
        facts={
            "center_palace": tianxiang_palace,
            "ji_neighbors": qualifying_neighbors,
            "trigger_pattern": "天相 + 两邻化忌 + 邻宫主星刑星",
        },
        semantic_summary=(
            f"天相位于{tianxiang_palace}，两邻宫 {qualifying_neighbors} 中有化忌飞入，"
            f"成刑忌夹印，主人一生受压力且多刑伤克害。"
        ),
    )


def detect_laiyin_ming_qian_xian(
    chart: FrozenZiweiChart, bundle: FeixingFeatureBundle | None = None
) -> FeixingCombination | None:
    """FEX-CMB-003 来因宫与命迁构成对宫（飞星嫡系讲义 P0-3 已修复用）

    LifeDNA 林士钦 (lifedna.com.tw/blog/c247.html) 原文：
      「向心力：比如命宫与迁移宫是本对宫的关系，
        命宫飞到迁移宫，或迁移宫飞到命宫就是属于这一类。
        一共有12个宫位，就有12种向心力的流向。」

    production 触发条件：
      - 来因宫存在（chart.birth_year 有效）
      - 来因宫 ∈ {命宫, 迁移宫} → 命迁线触发
      - 来因宫对宫 ∈ {命宫, 迁移宫} → 同上

    注意：完整来因宫判定复用 FeixingRuleGraph._compute_laiyin_palace。
    这里仅做"来因宫命迁线"判定（specific pattern）。
    """
    if bundle is None:
        bundle = build_feature_bundle(chart)

    if chart.birth_year <= 0:
        return None

    # 委托 FeixingRuleGraph 计算来因宫（P0-3 已修 selection_rule）
    # 在此子包内通过 features 包间接调用，避免 import FeixingRuleGraph
    # 实现：直接从 chart 提取所有 palace，按宫干=生年干 查找
    stem_table = ("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸")
    birth_stem = stem_table[(chart.birth_year - 4) % 10]
    if not birth_stem:
        return None

    # 找宫干 = birth_stem 的所有宫
    candidates = [
        name for name, pd in chart.palaces.items()
        if str(pd.get("stem", "")) == birth_stem
    ]
    if not candidates:
        return None

    # 辛/壬年取寅至亥本位（不取子、丑重复干）
    if birth_stem in ("辛", "壬"):
        filtered = [
            name for name in candidates
            if str((chart.palaces.get(name) or {}).get("branch", "")) not in ("子", "丑")
        ]
        if filtered:
            candidates = filtered

    laiyin_palace = candidates[0] if candidates else None
    if not laiyin_palace:
        return None

    # 判定来因宫是否在命迁线（接受 "迁移"/"迁移宫" 两种命名）
    laiyin_norm = laiyin_palace.rstrip("宫") if laiyin_palace else ""
    if laiyin_norm not in ("命", "迁移"):
        return None

    # 找对宫
    if laiyin_norm == "命":
        laiyin_palace_canonical = "命宫"
        opposite_palace = "迁移宫"
    else:
        laiyin_palace_canonical = "迁移宫"
        opposite_palace = "命宫"

    return FeixingCombination(
        rule_id="FEX-CMB-003",
        detected=True,
        evidence_grade=1,
        facts={
            "laiyin_palace": laiyin_palace_canonical,
            "laiyin_palace_raw": laiyin_palace,
            "laiyin_stem": birth_stem,
            "opposite_palace": opposite_palace,
            "birth_year": chart.birth_year,
            "trigger_pattern": "来因宫 ∈ 命迁线",
        },
        semantic_summary=(
            f"生年{birth_stem}年来因宫落{laiyin_palace_canonical}（对宫{opposite_palace}），"
            f"构成命迁线飞化因果链。"
        ),
    )


def detect_self_ji_in_palace_basic(
    chart: FrozenZiweiChart, bundle: FeixingFeatureBundle | None = None
) -> FeixingCombination | None:
    """FEX-CMB-004 自化忌基础（飞星嫡系讲义）

    LifeDNA 林士钦 (lifedna.com.tw/blog/c247.html) 原文：
      「自化：飛星的起點與終點都在同一個宮位稱為自化（離心自化）...
        因為它同時散掉了命盤的能量，所以自化通常帶有不好的意義。」

    production 触发条件（基础版）：
      - 任意宫位有自化忌（离心自化）
      - 仅检测 1 个或多个，不细分 12 宫语义（DRAFT 层做）

    语义边界：
      - 12 宫自化忌细分语义（林士钦 12 宫详解）属 grade=3 后人整理 → DRAFT
      - production 仅确认"有自化忌"基础事实
    """
    if bundle is None:
        bundle = build_feature_bundle(chart)

    self_ji_list = [
        {
            "palace": t.source_palace,
            "stem": t.source_stem,
            "star": t.target_star,
        }
        for t in bundle.self_transforms
        if t.transformation == "化忌"
    ]

    if not self_ji_list:
        return None

    return FeixingCombination(
        rule_id="FEX-CMB-004",
        detected=True,
        evidence_grade=1,
        facts={
            "self_ji_count": len(self_ji_list),
            "self_ji_palaces": self_ji_list,
            "trigger_pattern": "本宫宫干使本宫星曜化忌（离心自化）",
        },
        semantic_summary=(
            f"命盘有 {len(self_ji_list)} 处自化忌（离心自化），"
            f"散掉命盘能量，需特别留意。"
        ),
    )


def detect_si_hua_lu_ru_ming(
    chart: FrozenZiweiChart, bundle: FeixingFeatureBundle | None = None
) -> FeixingCombination | None:
    """FEX-CMB-005 四化禄入命宫（宫干飞化基础）

    王亭之泛论 + 令东来 633 共同支持：
      「飞化可以看出某些细节、某些内幕，这的确是传统三合派做不到的地方。」

    production 触发条件：
      - 任意非命宫宫位的宫干使四化禄星落入命宫
      - 化禄落入命宫 = 该宫对命主有增益影响（王亭之泛论）
      - 简化：仅记录命中事实，不做"增力/减力"判断（DRAFT 层）
    """
    if bundle is None:
        bundle = build_feature_bundle(chart)

    lu_into_ming = [
        {
            "source_palace": t.source_palace,
            "source_stem": t.source_stem,
            "transformation": t.transformation,
            "star": t.target_star,
        }
        for t in bundle.transforms
        if t.target_palace == "命宫"
        and t.transformation in ("化禄", "化权", "化科", "化忌")
        and t.source_palace != "命宫"
    ]

    if not lu_into_ming:
        return None

    return FeixingCombination(
        rule_id="FEX-CMB-005",
        detected=True,
        evidence_grade=1,
        facts={
            "flying_into_ming": lu_into_ming,
            "trigger_pattern": "宫干四化飞入命宫",
        },
        semantic_summary=(
            f"有 {len(lu_into_ming)} 处宫干飞化落入命宫（{lu_into_ming}），"
            f"显示各宫对命主的影响路径。"
        ),
    )


# ─────────────────────────────────────────────────────────────────────────
# PRODUCTION_DETECTORS 注册表
# ─────────────────────────────────────────────────────────────────────────

P0_5_A_PRODUCTION_DETECTORS = (
    ("FEX-CMB-001", detect_cai_yin_jia_yin_feixing),
    ("FEX-CMB-002", detect_xing_ji_jia_yin_feixing),
    ("FEX-CMB-003", detect_laiyin_ming_qian_xian),
    ("FEX-CMB-004", detect_self_ji_in_palace_basic),
    ("FEX-CMB-005", detect_si_hua_lu_ru_ming),
)


# ============================================================================
# DRAFT DETECTORS — 5 条 grade=3+ 占位（detect_*_draft 强制返回 None）
# ============================================================================


def detect_li_xiang_classification_draft(
    chart: FrozenZiweiChart, bundle: FeixingFeatureBundle | None = None
) -> FeixingCombination | None:
    """FEX-CMB-D01 离心/向心分类 — DRAFT (grade=3 后人整理)

    离心/向心术语来自林士钦/炎一/梁若瑜等后人总结，
    王亭之原文不区分，王亭之明确说「飞化」才是正确用词。

    此规则不进入 production；仅留接口供后续 grade=1 取证后激活。
    """
    return None


def detect_zhui_ji_draft(
    chart: FrozenZiweiChart, bundle: FeixingFeatureBundle | None = None
) -> FeixingCombination | None:
    """FEX-CMB-D02 追忌 — DRAFT (grade=4 派系算法不一)

    追忌算法4 大派（许铨仁/梁若瑜/许世贤/林士钦）细节不同，
    王亭之原文仅「化忌转忌」泛论（谈星 08）。

    此规则不进入 production；待 P0-5-B 跨派共识取证后再激活。
    """
    return None


def detect_576_flying_types_draft(
    chart: FrozenZiweiChart, bundle: FeixingFeatureBundle | None = None
) -> FeixingCombination | None:
    """FEX-CMB-D03 576 种飞星类型 — DRAFT (王亭之明确反对全飞)

    林士钦：「看起來很多，但每一張命盤都有自己的命格重心與特色，
    所以不是 576 種飛星比重都一樣，也不是每一種都需要解釋。
    簡單說是，有的飛星是假的！真的才有用處。」

    王亭之强调飞化条件（grade=1），不主张穷举 576 类型。
    production 严禁实现此规则。
    """
    return None


def detect_self_ji_12_palace_draft(
    chart: FrozenZiweiChart, bundle: FeixingFeatureBundle | None = None
) -> FeixingCombination | None:
    """FEX-CMB-D04 12宫自化忌细分语义 — DRAFT (grade=3 林士钦整理)

    林士钦 12 宫自化忌详解（lifedna.com.tw/blog/c247.html 列表）属后人整理，
    非王亭之原文体系。

    production 仅实现基础检测（FEX-CMB-004），细分语义不进生产。
    """
    return None


def detect_san_fang_fly_draft(
    chart: FrozenZiweiChart, bundle: FeixingFeatureBundle | None = None
) -> FeixingCombination | None:
    """FEX-CMB-D05 飞入三方（迁移/财帛/事业）— DRAFT (grade=3)

    飞入对宫有王亭之泛论（命迁线），飞入三方缺乏明确 grade=1 原�grade=1 原文。

    production 不实现三方飞入；待 P0-5-B 取证。
    """
    return None


# ─────────────────────────────────────────────────────────────────────────
# DRAFT_DETECTORS 注册表
# ─────────────────────────────────────────────────────────────────────────

DRAFT_DETECTORS = (
    ("FEX-CMB-D01", detect_li_xiang_classification_draft),
    ("FEX-CMB-D02", detect_zhui_ji_draft),
    ("FEX-CMB-D03", detect_576_flying_types_draft),
    ("FEX-CMB-D04", detect_self_ji_12_palace_draft),
    ("FEX-CMB-D05", detect_san_fang_fly_draft),
)


# ─────────────────────────────────────────────────────────────────────────
# 调度函数
# ─────────────────────────────────────────────────────────────────────────


def detect_all_production(
    chart: FrozenZiweiChart, bundle: FeixingFeatureBundle | None = None
) -> tuple[FeixingCombination, ...]:
    """运行全部 5 条 production detect，返回命中结果元组（未命中不返回）。"""
    if bundle is None:
        bundle = build_feature_bundle(chart)
    hits: list[FeixingCombination] = []
    for _rule_id, fn in P0_5_A_PRODUCTION_DETECTORS:
        result = fn(chart, bundle)
        if result is not None:
            hits.append(result)
    return tuple(hits)


def detect_all_drafts(
    chart: FrozenZiweiChart, bundle: FeixingFeatureBundle | None = None
) -> tuple[FeixingCombination, ...]:
    """运行全部 5 条 DRAFT detect（全部返回 None，仅占位）。"""
    if bundle is None:
        bundle = build_feature_bundle(chart)
    hits: list[FeixingCombination] = []
    for _rule_id, fn in DRAFT_DETECTORS:
        result = fn(chart, bundle)
        if result is not None:  # DRAFT 不应返回任何命中
            hits.append(result)
    return tuple(hits)