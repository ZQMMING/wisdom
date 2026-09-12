"""
Zhongzhou Feature Resolver — 中州派星系组合特征查询（P0-4-A）

严格工程边界：
- 只产生事实，不解释。
- 不得修改 FrozenZiweiChart 字段。
- 不得修改公共事实层（resolve_sanfang_sizheng / resolve_opposite 等）。
- 所有查询都是只读 + 纯函数。
- 失败/缺失时返回 None 或空集合（fail-closed）。

证据等级约束：
- 本模块中所有 Feature 派生函数均基于 P0-4-A 10 条规则的字面定义。
- 任何不属于这 10 条规则的 Feature 派生不在本模块范围。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ....ziwei_engine import FrozenZiweiChart
from ....ziwei_palace_resolution import ZiweiPalaceResolver


# ─────────────────────────────────────────────────────────────────────────
# 基础事实查询
# ─────────────────────────────────────────────────────────────────────────


def get_stars_in_palace(chart: FrozenZiweiChart, palace_name: str) -> set[str]:
    """查询指定宫位的主星+辅星集合（major + minor union）。"""
    palace = chart.palaces.get(palace_name) or {}
    stars: set[str] = set()
    for key in ("major", "minor"):
        v = palace.get(key, [])
        if isinstance(v, list):
            stars.update(str(s) for s in v)
    return stars


def get_major_stars_in_palace(chart: FrozenZiweiChart, palace_name: str) -> set[str]:
    """查询指定宫位的主星（仅 major）。"""
    palace = chart.palaces.get(palace_name) or {}
    v = palace.get("major", [])
    return {str(s) for s in v} if isinstance(v, list) else set()


def get_minor_stars_in_palace(chart: FrozenZiweiChart, palace_name: str) -> set[str]:
    """查询指定宫位的辅星（仅 minor）。"""
    palace = chart.palaces.get(palace_name) or {}
    v = palace.get("minor", [])
    return {str(s) for s in v} if isinstance(v, list) else set()


def find_star_palace(
    chart: FrozenZiweiChart, star: str
) -> str | None:
    """在 12 宫中找到某颗主星/辅星所在的宫位名（首次匹配）。"""
    for palace_name, palace in chart.palaces.items():
        stars = set()
        for key in ("major", "minor"):
            v = palace.get(key, [])
            if isinstance(v, list):
                stars.update(str(s) for s in v)
        if star in stars:
            return palace_name
    return None


def get_sanfang_sizheng(
    resolver: ZiweiPalaceResolver, palace_name: str
) -> dict[str, str]:
    """获取一个宫位的三方四正（primary + opposite + sanhe_1 + sanhe_2）。"""
    return resolver.resolve_sanfang_sizheng(palace_name)


def get_stars_in_sanfang_sizheng(
    chart: FrozenZiweiChart, resolver: ZiweiPalaceResolver, palace_name: str
) -> set[str]:
    """获取一个宫位的三方四正 + 本宫的所有星曜集合。"""
    sfs = get_sanfang_sizheng(resolver, palace_name)
    palaces = [sfs.get("primary", palace_name)] + sfs.get("supporting", [])
    stars: set[str] = set()
    for p in palaces:
        if p:
            stars.update(get_stars_in_palace(chart, p))
    return stars


def get_neighbor_palaces(
    resolver: ZiweiPalaceResolver, palace_name: str
) -> tuple[str | None, str | None]:
    """
    获取某宫的左右邻宫（左=本宫-1 地支序，右=本宫+1 地支序）。
    用途：财荫/刑忌夹印的位置铁律。
    """
    try:
        opposite = resolver.resolve_opposite(palace_name)
        # 在中州/三合中，夹=邻宫（前后各一宫地支），而非对宫。
        # 这里简化：左右邻=左右偏移 1 个地支的宫位名。
        # ZiweiPalaceResolver 公开 _branch_at_offset / _palace_at_branch 但它们是私有。
        # 用 resolve_opposite + resolver._branch_at_offset / _palace_at_branch 是可接受的内部用法（不改签名）。
        primary_palace = resolver._get_palace(palace_name)
        if not primary_palace:
            return (None, None)
        branch = primary_palace["branch"]
        idx = resolver._branch_idx(branch)
        # EARTHLY_BRANCHES 是模块常量，但不在签名中暴露。
        # 通过 _branch_at_offset 间接获取。
        left_branch = resolver._branch_at_offset(branch, -1)
        right_branch = resolver._branch_at_offset(branch, 1)
        left_palace = resolver._palace_at_branch(left_branch) if left_branch else None
        right_palace = resolver._palace_at_branch(right_branch) if right_branch else None
        return (left_palace, right_palace)
    except Exception:
        return (None, None)


def get_palace_branch(
    resolver: ZiweiPalaceResolver, palace_name: str
) -> str | None:
    """获取某宫位的地支。"""
    palace = resolver._get_palace(palace_name)
    return palace.get("branch") if palace else None


def has_any_of_in_set(stars: set[str], candidates: set[str]) -> bool:
    """判定 stars 集合与 candidates 集合是否相交（任一命中）。"""
    return bool(stars & candidates)


# ─────────────────────────────────────────────────────────────────────────
# Feature Bundle（用于 Rule 决策的批量事实集合）
# ─────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ZhongzhouFeatureBundle:
    """
    中州派 P0-4-A 10 条规则所需的 Feature 事实包。

    所有字段均为只读 + 失败/缺失返回空值。
    """
    # ── 星系查询 ──
    tianxiang_palace: str | None                       # 天相所在宫（None=未找到）
    tianxiang_left_neighbor: str | None                # 天相邻宫（左）
    tianxiang_right_neighbor: str | None               # 天相邻宫（右）
    tianxiang_sanfang_stars: frozenset[str]            # 天相所在三方四正星曜
    tianxiang_left_stars: frozenset[str]               # 天相左邻宫星曜
    tianxiang_right_stars: frozenset[str]              # 天相右邻宫星曜
    tianxiang_opposite_stars: frozenset[str]           # 天相对宫星曜

    # ── 紫微孤君 ──
    ziwei_palace: str | None
    ziwei_sanfang_stars: frozenset[str]

    # ── 命宫三方四正（机月同梁 / 杀破廉贪 / 明珠出海 / 禄马 / 暗痣） ──
    ming_sanfang_stars: frozenset[str]
    ming_palace_branch: str | None                     # 命宫地支
    body_palace_branch: str | None                     # 身宫地支

    # ── 禄马交驰 ──
    lucun_palace: str | None
    tianma_palace: str | None
    lucun_left_neighbor: str | None                    # 禄存左邻
    lucun_right_neighbor: str | None                   # 禄存右邻
    lucun_left_stars: frozenset[str]
    lucun_right_stars: frozenset[str]

    # ── 暗曜（文曲化忌所在宫） ──
    wenqu_palace: str | None                           # 文曲所在宫
    sha_po_tan_palaces: frozenset[str]                 # 七杀/破军/贪狼 所在宫集合

    # ── 廉破凶格/反格 ──
    lian_zheng_palace: str | None
    po_jun_palace: str | None
    lian_zheng_palace_branch: str | None
    po_jun_palace_branch: str | None

    # ── 杀陷震兑（七杀在卯酉 + 武曲同度） ──
    qi_sha_palace: str | None
    qi_sha_palace_branch: str | None
    wu_qu_in_qi_sha: bool

    # ── 坐贵向贵（魁/钺位置 + 命/身地支） ──
    tian_kui_palace: str | None
    tian_yue_palace: str | None


def build_feature_bundle(
    chart: FrozenZiweiChart, resolver: ZiweiPalaceResolver
) -> ZhongzhouFeatureBundle:
    """
    构建 P0-4-A 10 条规则所需的 Feature 事实包。

    注：
    - 只读公共事实层 + FrozenZiweiChart。
    - 失败/缺失返回空值（fail-closed）。
    - 不修改任何数据结构。
    """
    # 天相位置铁律
    tianxiang_palace = find_star_palace(chart, "天相")
    if tianxiang_palace:
        left, right = get_neighbor_palaces(resolver, tianxiang_palace)
        tianxiang_left_stars = frozenset(get_stars_in_palace(chart, left)) if left else frozenset()
        tianxiang_right_stars = frozenset(get_stars_in_palace(chart, right)) if right else frozenset()
        sfs = get_sanfang_sizheng(resolver, tianxiang_palace)
        opposite = sfs.get("opposite", "")
        tianxiang_opposite_stars = frozenset(get_stars_in_palace(chart, opposite)) if opposite else frozenset()
        tianxiang_sanfang_stars = frozenset(get_stars_in_sanfang_sizheng(chart, resolver, tianxiang_palace))
    else:
        tianxiang_left_neighbor = None
        tianxiang_right_neighbor = None
        tianxiang_left_stars = frozenset()
        tianxiang_right_stars = frozenset()
        tianxiang_opposite_stars = frozenset()
        tianxiang_sanfang_stars = frozenset()

    # 紫微
    ziwei_palace = find_star_palace(chart, "紫微")
    ziwei_sanfang_stars = (
        frozenset(get_stars_in_sanfang_sizheng(chart, resolver, ziwei_palace))
        if ziwei_palace
        else frozenset()
    )

    # 命宫三方四正
    ming_sanfang_stars = frozenset(get_stars_in_sanfang_sizheng(chart, resolver, "命宫"))
    ming_palace_branch = get_palace_branch(resolver, "命宫")
    body_palace_branch = get_palace_branch(resolver, "身宫")

    # 禄存 + 天马 + 邻宫
    lucun_palace = find_star_palace(chart, "禄存")
    tianma_palace = find_star_palace(chart, "天马")
    if lucun_palace:
        left, right = get_neighbor_palaces(resolver, lucun_palace)
        lucun_left_neighbor = left
        lucun_right_neighbor = right
        lucun_left_stars = frozenset(get_stars_in_palace(chart, left)) if left else frozenset()
        lucun_right_stars = frozenset(get_stars_in_palace(chart, right)) if right else frozenset()
    else:
        lucun_left_neighbor = None
        lucun_right_neighbor = None
        lucun_left_stars = frozenset()
        lucun_right_stars = frozenset()

    # 暗曜基础
    wenqu_palace = find_star_palace(chart, "文曲")
    sha_po_tan_palaces = frozenset(
        p for star in ("七杀", "破军", "贪狼")
        for p in [find_star_palace(chart, star)] if p
    )

    # 廉破
    lian_zheng_palace = find_star_palace(chart, "廉贞")
    po_jun_palace = find_star_palace(chart, "破军")
    lian_zheng_palace_branch = get_palace_branch(resolver, lian_zheng_palace) if lian_zheng_palace else None
    po_jun_palace_branch = get_palace_branch(resolver, po_jun_palace) if po_jun_palace else None

    # 七杀 + 武曲
    qi_sha_palace = find_star_palace(chart, "七杀")
    qi_sha_palace_branch = get_palace_branch(resolver, qi_sha_palace) if qi_sha_palace else None
    wu_qu_in_qi_sha = (
        "武曲" in get_major_stars_in_palace(chart, qi_sha_palace) if qi_sha_palace else False
    )

    # 魁/钺
    tian_kui_palace = find_star_palace(chart, "天魁")
    tian_yue_palace = find_star_palace(chart, "天钺")

    # 处理 tianxiang_palace 邻宫（必须放在 if-else 之外才能赋值）
    if tianxiang_palace:
        left, right = get_neighbor_palaces(resolver, tianxiang_palace)
        tianxiang_left_neighbor = left
        tianxiang_right_neighbor = right
    else:
        tianxiang_left_neighbor = None
        tianxiang_right_neighbor = None

    return ZhongzhouFeatureBundle(
        tianxiang_palace=tianxiang_palace,
        tianxiang_left_neighbor=tianxiang_left_neighbor,
        tianxiang_right_neighbor=tianxiang_right_neighbor,
        tianxiang_sanfang_stars=tianxiang_sanfang_stars,
        tianxiang_left_stars=tianxiang_left_stars,
        tianxiang_right_stars=tianxiang_right_stars,
        tianxiang_opposite_stars=tianxiang_opposite_stars,
        ziwei_palace=ziwei_palace,
        ziwei_sanfang_stars=ziwei_sanfang_stars,
        ming_sanfang_stars=ming_sanfang_stars,
        ming_palace_branch=ming_palace_branch,
        body_palace_branch=body_palace_branch,
        lucun_palace=lucun_palace,
        tianma_palace=tianma_palace,
        lucun_left_neighbor=lucun_left_neighbor,
        lucun_right_neighbor=lucun_right_neighbor,
        lucun_left_stars=lucun_left_stars,
        lucun_right_stars=lucun_right_stars,
        wenqu_palace=wenqu_palace,
        sha_po_tan_palaces=sha_po_tan_palaces,
        lian_zheng_palace=lian_zheng_palace,
        po_jun_palace=po_jun_palace,
        lian_zheng_palace_branch=lian_zheng_palace_branch,
        po_jun_palace_branch=po_jun_palace_branch,
        qi_sha_palace=qi_sha_palace,
        qi_sha_palace_branch=qi_sha_palace_branch,
        wu_qu_in_qi_sha=wu_qu_in_qi_sha,
        tian_kui_palace=tian_kui_palace,
        tian_yue_palace=tian_yue_palace,
    )
