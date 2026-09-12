
"""
Qintian Feature Resolver — 钦天门特征查询 (P0-7)

严格工程边界：
- 只产生事实，不解释。
- 不得修改 FrozenZiweiChart 字段。
- 不得修改公共事实层（FlyingTransformFact）。
- 所有查询都是只读 + 纯函数。
- 失败/缺失时返回 None 或空集合（fail-closed）。

钦天门事实层 = 复用飞星派 Z13-B FlyingTransformFact（钦天四化与飞星共用四化基础）
"""

from __future__ import annotations

from typing import List, Optional

from ..feixing_rule_graph import FlyingTransformFact, PalaceStemFact


# 钦天门六亲宫位 (用于 QTN-CMB-005 忌入六亲宫 = 亏欠)
SIX_RELATIVES = {
    "父母宫", "兄弟宫", "夫妻宫", "子女宫",
    "奴仆宫", "田宅宫",
}


def get_laiyin_palace(birth_year: int, palace_stems: List[PalaceStemFact]) -> Optional[str]:
    """来因宫 = 生年干所在宫位

    Args:
        birth_year: 阳历出生年
        palace_stems: 12 宫宫干事实列表

    Returns:
        来因宫名 (e.g. "命宫", "官禄宫") 或 None (e.g. 子/丑位例外)
    """
    if not palace_stems:
        return None

    # 生年干公式 (与 P0-3 一致)
    birth_stem_idx = (birth_year - 4) % 10
    stems_10 = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    birth_stem = stems_10[birth_stem_idx]

    # 找到宫干 = birth_stem 的宫位
    for pf in palace_stems:
        if pf.stem == birth_stem:
            # 排除子/丑位 (DRAFT QTN-CMB-009 例外, P0-7-A 严格派暂不实现)
            if pf.branch in ("子", "丑"):
                return None
            return pf.palace_name

    return None


def get_self_mutagen(chart) -> List[FlyingTransformFact]:
    """自化 = 本宫星曜自化 (direction="self")

    Returns:
        所有 direction="self" 的飞化事实 (时空维度的"用")
    """
    palace_stems = PalaceStemFact  # type: ignore
    return [
        ft for ft in chart.flying_transforms
        if ft.direction == "self"
    ]


def get_xiangxin_mutagen(chart) -> List[FlyingTransformFact]:
    """向心自化 = 本宫发射到对宫 (direction="out" + target_palace=对宫)

    注：direction="out" 包含真正飞出 + 向心发射到对宫。
    QTN-CMB-004 注脚在对宫特指对宫场景，所以过滤对宫目标。

    Returns:
        所有目标在正对宫的自化事实
    """
    # 注: FrozenZiweiChart 应有 opposite_palace 关系 — 在此简化
    OPPOSITE_PAIRS = {
        "命宫": "迁移宫", "迁移宫": "命宫",
        "兄弟宫": "交友宫", "交友宫": "兄弟宫",
        "夫妻宫": "官禄宫", "官禄宫": "夫妻宫",
        "子女宫": "田宅宫", "田宅宫": "子女宫",
        "财帛宫": "福德宫", "福德宫": "财帛宫",
        "疾厄宫": "父母宫", "父母宫": "疾厄宫",
    }

    result = []
    for ft in chart.flying_transforms:
        # direction "in" + target=本宫 = 对宫发射过来
        # 但 P0-3 简化版 direction 判定可能不区分 — 这里用 facts 字段辅助
        if ft.direction == "in" and ft.facts.get("opposite_palace") is True:
            result.append(ft)
    return result


def get_xuanji_palace(base_palace: str, target_relationship: str) -> str:
    """立太极 (Xuanji): 从 base_palace 立太极后, target_relationship 是哪个宫

    Args:
        base_palace: 立太极的宫 (e.g. "夫妻宫")
        target_relationship: 关系 (e.g. "夫妻的夫妻" → 财帛宫)

    Returns:
        中太极下的目标宫位

    Notes:
        钦天门特色: 任何宫都可立太极, 形成"中太极"分析。
        简化的标准太极映射 (许铨仁原文):
          - 命宫立太极 → 标准 12 宫
          - 夫妻宫立太极 → 财帛宫是"夫妻的夫妻"
          - 兄弟宫立太极 → 夫妻宫是"兄弟的夫妻"(兄弟的桃花)
          - ...
    """
    # 简化实现: 12 宫立太极后, 关系是相对位移
    # 完整的钦天太极映射 = 12×12 = 144 种, 不在 P0-7-A 范围
    return None  # P0-7-A 严格派: 不实现完整太极映射, 仅返回 None
