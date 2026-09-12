"""
Feixing Feature Resolver — 飞星派飞化特征查询（P0-5-A）

严格工程边界：
- 只产生事实，不解释。
- 不得修改 FrozenZiweiChart 字段。
- 不得修改公共事实层（PalaceStemFact / FlyingTransformFact）。
- 所有查询都是只读 + 纯函数。
- 失败/缺失时返回 None 或空集合（fail-closed）。

证据等级约束：
- 本模块中所有 Feature 派生函数均基于 P0-5-A 5 条规则的字面定义。
- 任何不属于这 5 条规则的 Feature 派生不在本模块范围。

设计决策：
- 本模块独立持有 _compute_all_flying_transforms 纯函数（与 FeixingRuleGraph 实例方法同源）
- 不 import feixing_rule_graph.py（避免循环依赖；P0-5-A 子包对外独立）
- 公共事实层 PalaceStemFact / FlyingTransformFact 从 feixing_rule_graph import
"""
from __future__ import annotations

from dataclasses import dataclass

from ....ziwei_engine import FrozenZiweiChart, GAN_SIHUA
from ..feixing_rule_graph import FlyingTransformFact, PalaceStemFact


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


def get_palace_stem(chart: FrozenZiweiChart, palace_name: str) -> str:
    """查询指定宫位的宫干。"""
    palace = chart.palaces.get(palace_name) or {}
    return str(palace.get("stem", ""))


def get_palace_branch(chart: FrozenZiweiChart, palace_name: str) -> str:
    """查询指定宫位的地支。"""
    palace = chart.palaces.get(palace_name) or {}
    return str(palace.get("branch", ""))


def find_star_palace(chart: FrozenZiweiChart, star_name: str) -> str | None:
    """查询指定星曜所在宫位（major + minor）。"""
    for palace_name, pd in chart.palaces.items():
        stars = set(pd.get("major", [])) | set(pd.get("minor", []))
        if star_name in stars:
            return palace_name
    return None


def get_neighbor_palaces(chart: FrozenZiweiChart, palace_name: str) -> tuple[str, ...]:
    """查询指定宫位相邻的两宫（地支 ±1）。

    用于"夹印"语义（财荫夹印/刑忌夹印要求天相两邻）。
    """
    palace = chart.palaces.get(palace_name) or {}
    branch = str(palace.get("branch", ""))
    if not branch:
        return ()
    branches = ("子", "丑", "寅", "卯", "辰", "巳",
                "午", "未", "申", "酉", "戌", "亥")
    if branch not in branches:
        return ()
    idx = branches.index(branch)
    target_branches = [branches[(idx - 1) % 12], branches[(idx + 1) % 12]]
    neighbors = []
    for name, pd in chart.palaces.items():
        if str(pd.get("branch", "")) in target_branches:
            neighbors.append(name)
    return tuple(sorted(neighbors))


# ─────────────────────────────────────────────────────────────────────────
# 飞化计算（纯函数版，与 FeixingRuleGraph.compute_all_flying_transforms 同源）
# ─────────────────────────────────────────────────────────────────────────


def _extract_stem_facts(chart: FrozenZiweiChart) -> tuple[PalaceStemFact, ...]:
    """提取 12 宫宫干事实（与 PalaceStemContract.extract 等价）。"""
    facts: list[PalaceStemFact] = []
    for palace_name, pd in chart.palaces.items():
        facts.append(PalaceStemFact(
            palace_name=palace_name,
            stem=str(pd.get("stem", "")),
            branch=str(pd.get("branch", "")),
            major_stars=tuple(pd.get("major", [])),
            minor_stars=tuple(pd.get("minor", [])),
        ))
    return tuple(facts)


def _compute_all_flying_transforms(
    chart: FrozenZiweiChart,
) -> tuple[FlyingTransformFact, ...]:
    """计算全部宫干的飞化事实（纯函数版）。

    流程：
      1. 提取 PalaceStemFact（12宫宫干）
      2. 对每个有宫干的宫，查 GAN_SIHUA 表
      3. 将四化星定位到目标宫位
      4. 标注 direction（入/出/自化）

    direction 判定（修正 P0-3 遗留 bug）：
      - target_palace == source_palace → "self"（自化）
      - target_palace == "命宫" 且 source_palace != "命宫" → "in"（飞入命宫）
      - 否则 → "out"（飞入他宫）

    注意：此处绝不使用 natal stem（出生年干），只用宫干。
    """
    stem_facts = _extract_stem_facts(chart)

    transforms: list[FlyingTransformFact] = []
    # star_to_palace 反向索引
    star_to_palace: dict[str, str] = {}
    for pf in stem_facts:
        for star in pf.major_stars + pf.minor_stars:
            if star not in star_to_palace:
                star_to_palace[star] = pf.palace_name

    for pf in stem_facts:
        if not pf.stem:
            continue
        sihua = GAN_SIHUA.get(pf.stem, ())
        if not sihua or len(sihua) < 4:
            continue

        for sihua_name, star_name in zip(
            ("化禄", "化权", "化科", "化忌"), sihua[:4]
        ):
            target_palace = star_to_palace.get(star_name, "")
            if not target_palace:
                continue

            # P0-5-A 修正方向判定：
            if target_palace == pf.palace_name:
                direction = "self"
            elif target_palace == "命宫":
                direction = "in"  # 任何宫飞化落入命宫 = 飞入
            else:
                direction = "out"

            transforms.append(FlyingTransformFact(
                source_palace=pf.palace_name,
                source_stem=pf.stem,
                transformation=sihua_name,
                target_star=star_name,
                target_palace=target_palace,
                direction=direction,
            ))

    return tuple(transforms)


# ─────────────────────────────────────────────────────────────────────────
# 飞化查询
# ─────────────────────────────────────────────────────────────────────────


def get_all_flying_transforms(chart: FrozenZiweiChart) -> tuple[FlyingTransformFact, ...]:
    """提取全部飞化事实。"""
    return _compute_all_flying_transforms(chart)


def get_self_transforms(chart: FrozenZiweiChart) -> tuple[FlyingTransformFact, ...]:
    """提取全部自化飞化（direction == "self"，即离心自化）。"""
    return tuple(t for t in get_all_flying_transforms(chart) if t.direction == "self")


def get_flying_in_to_palace(
    chart: FrozenZiweiChart, target_palace: str
) -> tuple[FlyingTransformFact, ...]:
    """提取飞入指定宫位的全部飞化。

    注：当前实现下，"in" 仅在 target == "命宫" 时产生。
    若要查询飞入其他宫位，使用 target_palace 一致过滤（direction 不限）。
    """
    return tuple(
        t for t in get_all_flying_transforms(chart)
        if t.target_palace == target_palace
    )


def has_self_ji_in_palace(chart: FrozenZiweiChart, palace_name: str) -> bool:
    """判断指定宫位是否有自化忌（本宫宫干使本宫星曜化忌）。"""
    for t in get_self_transforms(chart):
        if t.source_palace == palace_name and t.transformation == "化忌":
            return True
    return False


# ─────────────────────────────────────────────────────────────────────────
# Feature Bundle — 一次性计算所有 Feature（性能 + 一致性）
# ─────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class FeixingFeatureBundle:
    """飞星派特征 Bundle：一次性提取 chart 全部飞化 + 关键 Feature。

    与中州 ZhongzhouFeatureBundle 同架构（P0-4-A）。
    """
    chart: FrozenZiweiChart
    stem_facts: tuple[PalaceStemFact, ...]
    transforms: tuple[FlyingTransformFact, ...]
    self_transforms: tuple[FlyingTransformFact, ...]

    def has_lu_in_neighbor(self, center_palace: str) -> tuple[str, ...]:
        """查询中心宫两邻是否有化禄飞入（任意宫干飞化禄落入两邻）。"""
        neighbors = get_neighbor_palaces(self.chart, center_palace)
        lu_hits: list[str] = []
        for n in neighbors:
            for t in get_flying_in_to_palace(self.chart, n):
                if t.transformation == "化禄":
                    lu_hits.append(n)
                    break
        return tuple(lu_hits)

    def has_ji_in_neighbor(self, center_palace: str) -> tuple[str, ...]:
        """查询中心宫两邻是否有化忌飞入（任意宫干飞化忌落入两邻）。"""
        neighbors = get_neighbor_palaces(self.chart, center_palace)
        ji_hits: list[str] = []
        for n in neighbors:
            for t in get_flying_in_to_palace(self.chart, n):
                if t.transformation == "化忌":
                    ji_hits.append(n)
                    break
        return tuple(ji_hits)


def build_feature_bundle(chart: FrozenZiweiChart) -> FeixingFeatureBundle:
    """构建飞星派 Feature Bundle。"""
    stem_facts = _extract_stem_facts(chart)
    transforms = _compute_all_flying_transforms(chart)
    self_transforms = tuple(t for t in transforms if t.direction == "self")
    return FeixingFeatureBundle(
        chart=chart,
        stem_facts=stem_facts,
        transforms=transforms,
        self_transforms=self_transforms,
    )