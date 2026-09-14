
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
    """自化 = 本宫宫干四化出的星恰在本宫星曜中 (钦天原著定义)

    原著依据（许铨仁《钦天四化紫微斗数命理学》/四余独步讲义）：
    某宫宫干使某星化X，若该星正在此宫，则此星"自化X"（时间维度的"用"）。

    Z20 修正：原实现依赖 FlyingTransformFact.direction=="self"，
    但事实层 direction 全部为 "out"（宫干四化飞出表），导致自化永不命中。
    本函数按原著定义从 宫干四化 + 本宫星曜 重算，不改动公共事实层。

    Returns:
        自化事实列表 (direction="self" 的 FlyingTransformFact 构造体)
    """
    from ....ziwei_engine import GAN_SIHUA

    result: List[FlyingTransformFact] = []
    for pf in chart.palace_stems:
        if not pf.stem:
            continue
        sihua = GAN_SIHUA.get(pf.stem, ())
        if len(sihua) < 4:
            continue
        for key, star in (("化禄", sihua[0]), ("化权", sihua[1]),
                          ("化科", sihua[2]), ("化忌", sihua[3])):
            if star in pf.major_stars:
                result.append(FlyingTransformFact(
                    source_palace=pf.palace_name,
                    source_stem=pf.stem,
                    transformation=key,
                    target_star=star,
                    target_palace=pf.palace_name,
                    direction="self",
                ))
    return result


def get_xiangxin_mutagen(chart) -> List[FlyingTransformFact]:
    """向心自化 = 本宫发射到对宫 (direction="out" + target_palace=对宫)

    注：direction="out" 包含真正飞出 + 向心发射到对宫。
    QTN-CMB-004 注脚在对宫特指对宫场景，所以过滤对宫目标。

    Returns:
        所有目标在正对宫的自化事实
    """
    # 注: FrozenZiweiChart 应有 opposite_palace 关系 — 在此简化
    OPPOSITE_PAIRS = {
        "命": "迁移", "迁移": "命",
        "兄弟": "交友", "交友": "兄弟",
        "夫妻": "官禄", "官禄": "夫妻",
        "子女": "田宅", "田宅": "子女",
        "财帛": "福德", "福德": "财帛",
        "疾厄": "父母", "父母": "疾厄",
    }

    result = []
    for ft in chart.flying_transforms:
        # 宫干四化落对宫 = 向心自化（从本宫发射到对宫）
        # Z20 修正: 不依赖 direction 字段（事实层全 out），按对宫关系重判
        target_norm = (ft.target_palace or "").rstrip("宫")
        source_norm = (ft.source_palace or "").rstrip("宫")
        if OPPOSITE_PAIRS.get(source_norm) == target_norm:
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
