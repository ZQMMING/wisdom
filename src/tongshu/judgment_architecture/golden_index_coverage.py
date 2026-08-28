"""P6-C-3C-3 500条 Golden Index 覆盖矩阵定义 (V2 - 按经典核心维度).

核心原则:
- 不是"五本各随便找100条", 而是按每本经典的核心维度做覆盖矩阵
- 500条才是真正的算法覆盖集, 而不是500条文本
- 每本经典100条, 按其核心断法维度分布

五本经典核心维度:
  滴天髓:   STRENGTH (强弱) + QI (气势) — 日主强弱、五行气势、正变之分
  子平真诠: PATTERN (格局) — 正官、七杀、正财、偏财、食神、伤官、正印、偏印八格, 含变格
  穷通宝鉴: TUNING (调候) — 十天干×十二月的核心调候断语
  渊海子平: TEN_GOD (十神) + 赋文 — 印绶、食伤、官杀、财星等十神组合断语
  三命通会: DAY_TIME (日时) + 神煞 — 六十甲子日时断核心条目 + 神煞触发断语
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from enum import Enum


# ============================================================================
# 1. 覆盖矩阵维度定义
# ============================================================================

class JudgmentType(str, Enum):
    """断言类型 - 按经典核心维度."""
    # 滴天髓
    STRENGTH = "STRENGTH"               # 强弱
    QI_SHI = "QI_SHI"                   # 气势
    STRUCTURE_TRANSFORM = "STRUCTURE_TRANSFORM"  # 正变之分
    # 子平真诠
    PATTERN = "PATTERN"                 # 格局
    PATTERN_SUCCESS = "PATTERN_SUCCESS" # 格局成
    PATTERN_FAILURE = "PATTERN_FAILURE" # 格局败
    PATTERN_TRANSFORM = "PATTERN_TRANSFORM"  # 变格
    # 穷通宝鉴
    TUNING = "TUNING"                   # 调候
    MONTH_TUNING = "MONTH_TUNING"       # 月令调候
    SEASON_ENVIRONMENT = "SEASON_ENVIRONMENT"  # 季节环境
    # 渊海子平
    TEN_GOD = "TEN_GOD"                 # 十神
    TEN_GOD_COMBO = "TEN_GOD_COMBO"     # 十神组合
    FU_WEN = "FU_WEN"                   # 赋文
    # 三命通会
    DAY_TIME = "DAY_TIME"               # 日时断
    DAY_TIME_COMBO = "DAY_TIME_COMBO"   # 日时组合
    SHEN_SHA = "SHEN_SHA"               # 神煞
    SIXTY_JIAZI = "SIXTY_JIAZI"         # 六十甲子


class FeaturePattern(str, Enum):
    """Feature模式."""
    SINGLE = "SINGLE"                    # 单条件
    DOUBLE = "DOUBLE"                    # 双条件
    TRIPLE = "TRIPLE"                    # 三条件
    QUADRUPLE = "QUADRUPLE"              # 四条件
    COMPOSITE = "COMPOSITE"              # 复合条件


class TemporalScope(str, Enum):
    """时间范围."""
    NATAL = "NATAL"                      # 本命
    YEAR = "YEAR"                        # 流年
    MONTH = "MONTH"                      # 流月
    DAY = "DAY"                          # 流日


# ============================================================================
# 2. 每本经典的覆盖矩阵定义 (100条分布 - V2按核心维度)
# ============================================================================

@dataclass(frozen=True)
class CoverageSlot:
    """覆盖槽位 - 每条断言在覆盖矩阵中的位置."""
    judgment_type: str
    matcher_type: str
    feature_pattern: str
    temporal_scope: str
    count: int
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "judgment_type": self.judgment_type,
            "matcher_type": self.matcher_type,
            "feature_pattern": self.feature_pattern,
            "temporal_scope": self.temporal_scope,
            "count": self.count,
            "description": self.description,
        }


# ============================================================================
# 滴天髓 100条: STRENGTH (强弱) + QI (气势) + 正变之分
# ============================================================================
DI_TIAN_SUI_COVERAGE = [
    # STRENGTH 强弱 (40条)
    CoverageSlot(JudgmentType.STRENGTH.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.NATAL.value, 10, "强弱 - 单日主"),
    CoverageSlot(JudgmentType.STRENGTH.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 10, "强弱 - 日主+月令"),
    CoverageSlot(JudgmentType.STRENGTH.value, "COMPOSITE", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 10, "强弱 - 日主+月令+根气"),
    CoverageSlot(JudgmentType.STRENGTH.value, "COMPOSITE", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 5, "强弱 - 四柱全"),
    CoverageSlot(JudgmentType.STRENGTH.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.YEAR.value, 5, "强弱 - 流年"),
    # QI_SHI 气势 (40条)
    CoverageSlot(JudgmentType.QI_SHI.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.NATAL.value, 10, "气势 - 单元素"),
    CoverageSlot(JudgmentType.QI_SHI.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 10, "气势 - 双元素"),
    CoverageSlot(JudgmentType.QI_SHI.value, "GRAPH", FeaturePattern.COMPOSITE.value, TemporalScope.NATAL.value, 10, "气势 - 五行生克图"),
    CoverageSlot(JudgmentType.QI_SHI.value, "COMPOSITE", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 5, "气势 - 全局气势"),
    CoverageSlot(JudgmentType.QI_SHI.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.YEAR.value, 5, "气势 - 流年"),
    # STRUCTURE_TRANSFORM 正变之分 (20条)
    CoverageSlot(JudgmentType.STRUCTURE_TRANSFORM.value, "GRAPH", FeaturePattern.COMPOSITE.value, TemporalScope.NATAL.value, 10, "正变之分 - 正格结构"),
    CoverageSlot(JudgmentType.STRUCTURE_TRANSFORM.value, "COMPOSITE", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 5, "正变之分 - 变格结构"),
    CoverageSlot(JudgmentType.STRUCTURE_TRANSFORM.value, "CONDITION", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 5, "正变之分 - 正变判断条件"),
]

# ============================================================================
# 子平真诠 100条: PATTERN (格局) — 八格, 含变格
# ============================================================================
ZI_PING_ZHEN_QUAN_COVERAGE = [
    # 八格基础 (40条) - 正官、七杀、正财、偏财、食神、伤官、正印、偏印
    CoverageSlot(JudgmentType.PATTERN.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.NATAL.value, 8, "八格 - 月令取格 (每格1条)"),
    CoverageSlot(JudgmentType.PATTERN.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 8, "八格 - 月令+日主 (每格1条)"),
    CoverageSlot(JudgmentType.PATTERN.value, "CONDITION", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 8, "八格 - 月令+日主+透干 (每格1条)"),
    CoverageSlot(JudgmentType.PATTERN.value, "COMPOSITE", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 8, "八格 - 完整格局结构 (每格1条)"),
    CoverageSlot(JudgmentType.PATTERN.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.YEAR.value, 8, "八格 - 流年格局 (每格1条)"),
    # 格局成 (20条)
    CoverageSlot(JudgmentType.PATTERN_SUCCESS.value, "COMPOSITE", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 8, "格局成 - 用神+辅助 (每格1条)"),
    CoverageSlot(JudgmentType.PATTERN_SUCCESS.value, "COMPOSITE", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 8, "格局成 - 完整成格结构 (每格1条)"),
    CoverageSlot(JudgmentType.PATTERN_SUCCESS.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 4, "格局成 - 成格条件"),
    # 格局败 (15条)
    CoverageSlot(JudgmentType.PATTERN_FAILURE.value, "COMPOSITE", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 8, "格局败 - 忌神+破坏 (每格1条)"),
    CoverageSlot(JudgmentType.PATTERN_FAILURE.value, "COMPOSITE", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 4, "格局败 - 完整败格结构"),
    CoverageSlot(JudgmentType.PATTERN_FAILURE.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 3, "格局败 - 败格条件"),
    # 变格 (25条)
    CoverageSlot(JudgmentType.PATTERN_TRANSFORM.value, "GRAPH", FeaturePattern.COMPOSITE.value, TemporalScope.NATAL.value, 10, "变格 - 从革/稼穑/润下/炎上/曲直"),
    CoverageSlot(JudgmentType.PATTERN_TRANSFORM.value, "COMPOSITE", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 10, "变格 - 完整变格结构"),
    CoverageSlot(JudgmentType.PATTERN_TRANSFORM.value, "CONDITION", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 5, "变格 - 变格判断条件"),
]

# ============================================================================
# 穷通宝鉴 100条: TUNING (调候) — 十天干×十二月
# ============================================================================
QIONG_TONG_BAO_JIAN_COVERAGE = [
    # 十天干×十二月 核心调候 (60条)
    CoverageSlot(JudgmentType.TUNING.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 60, "十天干×十二月 核心调候断语 (10×12=120, 取核心60)"),
    # 月令调候进阶 (20条)
    CoverageSlot(JudgmentType.MONTH_TUNING.value, "CONDITION", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 10, "月令调候 - 日主+月令+透干"),
    CoverageSlot(JudgmentType.MONTH_TUNING.value, "COMPOSITE", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 10, "月令调候 - 完整调候结构"),
    # 季节环境 (10条)
    CoverageSlot(JudgmentType.SEASON_ENVIRONMENT.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 5, "季节环境 - 日主+季节"),
    CoverageSlot(JudgmentType.SEASON_ENVIRONMENT.value, "COMPOSITE", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 5, "季节环境 - 日主+季节+气候"),
    # 时间维度调候 (10条)
    CoverageSlot(JudgmentType.TUNING.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.YEAR.value, 5, "调候 - 流年"),
    CoverageSlot(JudgmentType.TUNING.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.YEAR.value, 3, "调候 - 流年+流月"),
    CoverageSlot(JudgmentType.SEASON_ENVIRONMENT.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.MONTH.value, 2, "季节环境 - 流月"),
]

# ============================================================================
# 渊海子平 100条: TEN_GOD (十神) + 赋文
# ============================================================================
YUAN_HAI_ZI_PING_COVERAGE = [
    # 十神基础 (30条) - 印绶、食伤、官杀、财星、比劫
    CoverageSlot(JudgmentType.TEN_GOD.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.NATAL.value, 10, "十神 - 单十神 (印/食伤/官杀/财/比劫 各2)"),
    CoverageSlot(JudgmentType.TEN_GOD.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 10, "十神 - 双十神组合"),
    CoverageSlot(JudgmentType.TEN_GOD.value, "CONDITION", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 10, "十神 - 三十神组合"),
    # 十神组合进阶 (30条)
    CoverageSlot(JudgmentType.TEN_GOD_COMBO.value, "SET", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 10, "十神组合 - 三元素集合 (印绶/食伤/官杀/财星)"),
    CoverageSlot(JudgmentType.TEN_GOD_COMBO.value, "SET", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 10, "十神组合 - 四元素集合"),
    CoverageSlot(JudgmentType.TEN_GOD_COMBO.value, "GRAPH", FeaturePattern.COMPOSITE.value, TemporalScope.NATAL.value, 10, "十神组合 - 生克图"),
    # 赋文 (25条)
    CoverageSlot(JudgmentType.FU_WEN.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.NATAL.value, 5, "赋文 - 单条件赋文"),
    CoverageSlot(JudgmentType.FU_WEN.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 10, "赋文 - 双条件赋文"),
    CoverageSlot(JudgmentType.FU_WEN.value, "COMPOSITE", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 10, "赋文 - 复合条件赋文"),
    # 时间维度十神 (15条)
    CoverageSlot(JudgmentType.TEN_GOD.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.YEAR.value, 5, "十神 - 流年"),
    CoverageSlot(JudgmentType.TEN_GOD.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.YEAR.value, 5, "十神 - 流年+流月"),
    CoverageSlot(JudgmentType.TEN_GOD_COMBO.value, "SET", FeaturePattern.SINGLE.value, TemporalScope.MONTH.value, 5, "十神组合 - 流月"),
]

# ============================================================================
# 三命通会 100条: DAY_TIME (日时) + 神煞
# ============================================================================
SAN_MING_TONG_HUI_COVERAGE = [
    # 六十甲子日时断核心 (50条)
    CoverageSlot(JudgmentType.DAY_TIME.value, "EXACT", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 30, "日时断 - 日柱+时柱 (六十甲子核心)"),
    CoverageSlot(JudgmentType.DAY_TIME.value, "EXACT", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 10, "日时断 - 日柱+时柱+月令"),
    CoverageSlot(JudgmentType.DAY_TIME.value, "EXACT", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 5, "日时断 - 日柱+时柱+月令+年柱"),
    CoverageSlot(JudgmentType.DAY_TIME.value, "EXACT", FeaturePattern.SINGLE.value, TemporalScope.NATAL.value, 5, "日时断 - 单日柱 (六十甲子)"),
    # 日时组合进阶 (15条)
    CoverageSlot(JudgmentType.DAY_TIME_COMBO.value, "COMPOSITE", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 8, "日时组合 - 日柱+时柱+结构"),
    CoverageSlot(JudgmentType.DAY_TIME_COMBO.value, "COMPOSITE", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 7, "日时组合 - 完整组合"),
    # 神煞触发断语 (25条)
    CoverageSlot(JudgmentType.SHEN_SHA.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.NATAL.value, 10, "神煞 - 单神煞 (天乙/文昌/桃花/驿马等)"),
    CoverageSlot(JudgmentType.SHEN_SHA.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 8, "神煞 - 神煞+位置"),
    CoverageSlot(JudgmentType.SHEN_SHA.value, "COMPOSITE", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 7, "神煞 - 神煞组合触发"),
    # 时间维度日时 (10条)
    CoverageSlot(JudgmentType.DAY_TIME.value, "EXACT", FeaturePattern.DOUBLE.value, TemporalScope.YEAR.value, 4, "日时断 - 流年"),
    CoverageSlot(JudgmentType.DAY_TIME.value, "EXACT", FeaturePattern.DOUBLE.value, TemporalScope.MONTH.value, 3, "日时断 - 流月"),
    CoverageSlot(JudgmentType.DAY_TIME_COMBO.value, "COMPOSITE", FeaturePattern.DOUBLE.value, TemporalScope.DAY.value, 3, "日时组合 - 流日"),
]

# 汇总
COVERAGE_MATRIX = {
    "DI_TIAN_SUI": DI_TIAN_SUI_COVERAGE,
    "ZI_PING_ZHEN_QUAN": ZI_PING_ZHEN_QUAN_COVERAGE,
    "QIONG_TONG_BAO_JIAN": QIONG_TONG_BAO_JIAN_COVERAGE,
    "YUAN_HAI_ZI_PING": YUAN_HAI_ZI_PING_COVERAGE,
    "SAN_MING_TONG_HUI": SAN_MING_TONG_HUI_COVERAGE,
}

# 经典核心维度说明
SCHOOL_CORE_DIMENSIONS = {
    "DI_TIAN_SUI": {
        "name": "滴天髓",
        "core_dimensions": ["STRENGTH (强弱)", "QI (气势)", "正变之分"],
        "description": "日主强弱、五行气势、正变之分",
    },
    "ZI_PING_ZHEN_QUAN": {
        "name": "子平真诠",
        "core_dimensions": ["PATTERN (格局)"],
        "description": "正官、七杀、正财、偏财、食神、伤官、正印、偏印八格，含变格",
    },
    "QIONG_TONG_BAO_JIAN": {
        "name": "穷通宝鉴",
        "core_dimensions": ["TUNING (调候)"],
        "description": "十天干×十二月的核心调候断语",
    },
    "YUAN_HAI_ZI_PING": {
        "name": "渊海子平",
        "core_dimensions": ["TEN_GOD (十神)", "赋文"],
        "description": "印绶、食伤、官杀、财星等十神组合断语",
    },
    "SAN_MING_TONG_HUI": {
        "name": "三命通会",
        "core_dimensions": ["DAY_TIME (日时)", "神煞"],
        "description": "六十甲子日时断核心条目 + 神煞触发断语",
    },
}


def verify_coverage_matrix() -> dict[str, Any]:
    """验证覆盖矩阵 - 每本经典应该100条."""
    result = {}
    for school, slots in COVERAGE_MATRIX.items():
        total = sum(slot.count for slot in slots)
        result[school] = {
            "total": total,
            "slots": len(slots),
            "valid": total == 100,
            "core_dimensions": SCHOOL_CORE_DIMENSIONS[school]["core_dimensions"],
            "description": SCHOOL_CORE_DIMENSIONS[school]["description"],
        }
    return result


def generate_coverage_report() -> str:
    """生成覆盖矩阵报告."""
    verification = verify_coverage_matrix()
    lines = [
        "=" * 90,
        "500条 Golden Index 覆盖矩阵报告 (V2 - 按经典核心维度)",
        "=" * 90,
        "",
        f"{'经典':<20} {'核心维度':<30} {'槽位数':<8} {'断言数':<8} {'状态':<6}",
        "-" * 90,
    ]
    total = 0
    for school, data in verification.items():
        status = "✓" if data["valid"] else "✗"
        dims = " / ".join(data["core_dimensions"])
        lines.append(f"{school:<20} {dims:<30} {data['slots']:<8} {data['total']:<8} {status:<6}")
        total += data["total"]
    lines.append("-" * 90)
    lines.append(f"{'合计':<20} {'':<30} {'':<8} {total:<8} {'':<6}")
    lines.append("=" * 90)
    lines.append("")
    lines.append("经典核心维度说明:")
    for school, data in SCHOOL_CORE_DIMENSIONS.items():
        lines.append(f"  {data['name']} ({school}): {data['description']}")
    lines.append("")
    lines.append("覆盖矩阵维度:")
    lines.append("  1. Judgment Type (断言类型 - 按经典核心维度)")
    lines.append("  2. Matcher Type (匹配模式: EXACT/SET/CONDITION/COMPOSITE/GRAPH)")
    lines.append("  3. Feature Pattern (Feature模式: 单条件/双条件/三条件/复合)")
    lines.append("  4. Temporal Scope (时间范围: NATAL/YEAR/MONTH/DAY)")
    lines.append("")
    lines.append("注意: 500条是算法覆盖集, 不是500条文本")
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate_coverage_report())
