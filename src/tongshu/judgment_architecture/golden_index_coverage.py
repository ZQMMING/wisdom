"""P6-C-3C-3 500条 Golden Index 覆盖矩阵定义.

核心原则:
- 不是"五本各随便找100条", 而是按照 Judgment Type × Matcher × Feature Pattern × Temporal Scope 做覆盖矩阵
- 500条才是真正的算法覆盖集, 而不是500条文本
- 每本经典100条, 按覆盖矩阵分布

覆盖矩阵维度:
  1. Judgment Type (断言类型)
  2. Matcher Type (匹配模式: EXACT/SET/CONDITION/COMPOSITE/GRAPH)
  3. Feature Pattern (Feature模式: 单条件/双条件/三条件/复合)
  4. Temporal Scope (时间范围: NATAL/YEAR/MONTH/DAY)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from enum import Enum


# ============================================================================
# 1. 覆盖矩阵维度定义
# ============================================================================

class JudgmentType(str, Enum):
    """断言类型."""
    # 滴天髓
    STEM_IMAGE = "STEM_IMAGE"           # 十干取象
    QI_SHI = "QI_SHI"                   # 气势
    STRENGTH = "STRENGTH"               # 强弱
    STRUCTURE_LEVEL = "STRUCTURE_LEVEL" # 结构层次
    # 子平真诠
    PATTERN = "PATTERN"                 # 格局
    PATTERN_SUCCESS = "PATTERN_SUCCESS" # 格局成
    PATTERN_FAILURE = "PATTERN_FAILURE" # 格局败
    USE_GOD = "USE_GOD"                 # 用神
    # 穷通宝鉴
    TUNING = "TUNING"                   # 调候
    MONTH_TUNING = "MONTH_TUNING"       # 月令调候
    SEASON_ENVIRONMENT = "SEASON_ENVIRONMENT"  # 季节环境
    # 渊海子平
    TEN_GOD = "TEN_GOD"                 # 十神
    TEN_GOD_STRUCTURE = "TEN_GOD_STRUCTURE"  # 十神结构
    PATTERN_BASIC = "PATTERN_BASIC"     # 基础格局
    # 三命通会
    DAY_TIME = "DAY_TIME"               # 日时断
    DAY_TIME_COMBO = "DAY_TIME_COMBO"   # 日时组合
    SIXTY_JIAZI = "SIXTY_JIAZI"         # 六十甲子


class FeaturePattern(str, Enum):
    """Feature模式."""
    SINGLE = "SINGLE"                    # 单条件 (如 乙木)
    DOUBLE = "DOUBLE"                    # 双条件 (如 乙木+戌月)
    TRIPLE = "TRIPLE"                    # 三条件 (如 乙木+戌月+壬透)
    QUADRUPLE = "QUADRUPLE"              # 四条件 (如 乙未日+壬午时+戌月+亥年)
    COMPOSITE = "COMPOSITE"              # 复合条件 (结构图)


class TemporalScope(str, Enum):
    """时间范围."""
    NATAL = "NATAL"                      # 本命
    YEAR = "YEAR"                        # 流年
    MONTH = "MONTH"                      # 流月
    DAY = "DAY"                          # 流日


# ============================================================================
# 2. 每本经典的覆盖矩阵定义 (100条分布)
# ============================================================================

@dataclass(frozen=True)
class CoverageSlot:
    """覆盖槽位 - 每条断言在覆盖矩阵中的位置."""
    judgment_type: str
    matcher_type: str
    feature_pattern: str
    temporal_scope: str
    count: int                           # 该槽位的断言数量
    description: str = ""               # 描述

    def to_dict(self) -> dict:
        return {
            "judgment_type": self.judgment_type,
            "matcher_type": self.matcher_type,
            "feature_pattern": self.feature_pattern,
            "temporal_scope": self.temporal_scope,
            "count": self.count,
            "description": self.description,
        }


# 滴天髓 100条覆盖矩阵
DI_TIAN_SUI_COVERAGE = [
    CoverageSlot(JudgmentType.STEM_IMAGE.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.NATAL.value, 10, "十干取象 - 单天干"),
    CoverageSlot(JudgmentType.STEM_IMAGE.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 5, "十干取象 - 天干+月令"),
    CoverageSlot(JudgmentType.STEM_IMAGE.value, "COMPOSITE", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 5, "十干取象 - 天干+月令+透干"),
    CoverageSlot(JudgmentType.QI_SHI.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.NATAL.value, 10, "气势 - 单元素"),
    CoverageSlot(JudgmentType.QI_SHI.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 10, "气势 - 双元素"),
    CoverageSlot(JudgmentType.QI_SHI.value, "GRAPH", FeaturePattern.COMPOSITE.value, TemporalScope.NATAL.value, 10, "气势 - 结构图"),
    CoverageSlot(JudgmentType.STRENGTH.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.NATAL.value, 10, "强弱 - 日主"),
    CoverageSlot(JudgmentType.STRENGTH.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 10, "强弱 - 日主+月令"),
    CoverageSlot(JudgmentType.STRENGTH.value, "COMPOSITE", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 10, "强弱 - 日主+月令+根气"),
    CoverageSlot(JudgmentType.STRUCTURE_LEVEL.value, "GRAPH", FeaturePattern.COMPOSITE.value, TemporalScope.NATAL.value, 10, "结构层次 - 全局结构"),
    CoverageSlot(JudgmentType.STRUCTURE_LEVEL.value, "COMPOSITE", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 5, "结构层次 - 四柱全"),
    CoverageSlot(JudgmentType.QI_SHI.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.YEAR.value, 5, "气势 - 流年"),
]

# 子平真诠 100条覆盖矩阵
ZI_PING_ZHEN_QUAN_COVERAGE = [
    CoverageSlot(JudgmentType.PATTERN.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.NATAL.value, 10, "格局 - 月令"),
    CoverageSlot(JudgmentType.PATTERN.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 10, "格局 - 月令+日主"),
    CoverageSlot(JudgmentType.PATTERN_SUCCESS.value, "COMPOSITE", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 15, "格局成 - 月令+用神+辅助"),
    CoverageSlot(JudgmentType.PATTERN_SUCCESS.value, "COMPOSITE", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 10, "格局成 - 完整结构"),
    CoverageSlot(JudgmentType.PATTERN_FAILURE.value, "COMPOSITE", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 10, "格局败 - 月令+忌神+破坏"),
    CoverageSlot(JudgmentType.PATTERN_FAILURE.value, "COMPOSITE", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 5, "格局败 - 完整破坏结构"),
    CoverageSlot(JudgmentType.USE_GOD.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.NATAL.value, 10, "用神 - 格局"),
    CoverageSlot(JudgmentType.USE_GOD.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 10, "用神 - 格局+强弱"),
    CoverageSlot(JudgmentType.USE_GOD.value, "COMPOSITE", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 10, "用神 - 格局+强弱+调候"),
    CoverageSlot(JudgmentType.USE_GOD.value, "COMPOSITE", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 10, "用神 - 完整用神体系"),
]

# 穷通宝鉴 100条覆盖矩阵
QIONG_TONG_BAO_JIAN_COVERAGE = [
    CoverageSlot(JudgmentType.TUNING.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.NATAL.value, 10, "调候 - 日主"),
    CoverageSlot(JudgmentType.TUNING.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 20, "调候 - 日主+月令 (核心)"),
    CoverageSlot(JudgmentType.MONTH_TUNING.value, "CONDITION", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 15, "月令调候 - 日主+月令+透干"),
    CoverageSlot(JudgmentType.MONTH_TUNING.value, "COMPOSITE", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 10, "月令调候 - 完整调候结构"),
    CoverageSlot(JudgmentType.SEASON_ENVIRONMENT.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 10, "季节环境 - 日主+季节"),
    CoverageSlot(JudgmentType.SEASON_ENVIRONMENT.value, "COMPOSITE", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 10, "季节环境 - 日主+季节+气候"),
    CoverageSlot(JudgmentType.SEASON_ENVIRONMENT.value, "COMPOSITE", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 5, "季节环境 - 完整环境结构"),
    CoverageSlot(JudgmentType.TUNING.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.YEAR.value, 5, "调候 - 流年"),
    CoverageSlot(JudgmentType.TUNING.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.YEAR.value, 5, "调候 - 流年+流月"),
    CoverageSlot(JudgmentType.SEASON_ENVIRONMENT.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.MONTH.value, 5, "季节环境 - 流月"),
    CoverageSlot(JudgmentType.MONTH_TUNING.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.DAY.value, 5, "月令调候 - 流日"),
]

# 渊海子平 100条覆盖矩阵
YUAN_HAI_ZI_PING_COVERAGE = [
    CoverageSlot(JudgmentType.TEN_GOD.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.NATAL.value, 10, "十神 - 单十神"),
    CoverageSlot(JudgmentType.TEN_GOD.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 10, "十神 - 双十神"),
    CoverageSlot(JudgmentType.TEN_GOD_STRUCTURE.value, "SET", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 15, "十神结构 - 三元素集合"),
    CoverageSlot(JudgmentType.TEN_GOD_STRUCTURE.value, "SET", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 10, "十神结构 - 四元素集合"),
    CoverageSlot(JudgmentType.TEN_GOD_STRUCTURE.value, "GRAPH", FeaturePattern.COMPOSITE.value, TemporalScope.NATAL.value, 10, "十神结构 - 生克图"),
    CoverageSlot(JudgmentType.PATTERN_BASIC.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.NATAL.value, 10, "基础格局 - 月令"),
    CoverageSlot(JudgmentType.PATTERN_BASIC.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 10, "基础格局 - 月令+日主"),
    CoverageSlot(JudgmentType.PATTERN_BASIC.value, "COMPOSITE", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 10, "基础格局 - 完整格局"),
    CoverageSlot(JudgmentType.TEN_GOD.value, "CONDITION", FeaturePattern.SINGLE.value, TemporalScope.YEAR.value, 5, "十神 - 流年"),
    CoverageSlot(JudgmentType.TEN_GOD.value, "CONDITION", FeaturePattern.DOUBLE.value, TemporalScope.YEAR.value, 5, "十神 - 流年+流月"),
    CoverageSlot(JudgmentType.TEN_GOD_STRUCTURE.value, "SET", FeaturePattern.SINGLE.value, TemporalScope.MONTH.value, 5, "十神结构 - 流月"),
]

# 三命通会 100条覆盖矩阵
SAN_MING_TONG_HUI_COVERAGE = [
    CoverageSlot(JudgmentType.DAY_TIME.value, "EXACT", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 30, "日时断 - 日柱+时柱 (核心)"),
    CoverageSlot(JudgmentType.DAY_TIME.value, "EXACT", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 15, "日时断 - 日柱+时柱+月令"),
    CoverageSlot(JudgmentType.DAY_TIME.value, "EXACT", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 10, "日时断 - 日柱+时柱+月令+年柱"),
    CoverageSlot(JudgmentType.DAY_TIME_COMBO.value, "COMPOSITE", FeaturePattern.TRIPLE.value, TemporalScope.NATAL.value, 10, "日时组合 - 日柱+时柱+结构"),
    CoverageSlot(JudgmentType.DAY_TIME_COMBO.value, "COMPOSITE", FeaturePattern.QUADRUPLE.value, TemporalScope.NATAL.value, 5, "日时组合 - 完整组合"),
    CoverageSlot(JudgmentType.SIXTY_JIAZI.value, "EXACT", FeaturePattern.SINGLE.value, TemporalScope.NATAL.value, 10, "六十甲子 - 日柱"),
    CoverageSlot(JudgmentType.SIXTY_JIAZI.value, "EXACT", FeaturePattern.DOUBLE.value, TemporalScope.NATAL.value, 5, "六十甲子 - 日柱+时柱"),
    CoverageSlot(JudgmentType.DAY_TIME.value, "EXACT", FeaturePattern.DOUBLE.value, TemporalScope.YEAR.value, 5, "日时断 - 流年"),
    CoverageSlot(JudgmentType.DAY_TIME.value, "EXACT", FeaturePattern.DOUBLE.value, TemporalScope.MONTH.value, 5, "日时断 - 流月"),
    CoverageSlot(JudgmentType.DAY_TIME_COMBO.value, "COMPOSITE", FeaturePattern.DOUBLE.value, TemporalScope.DAY.value, 5, "日时组合 - 流日"),
]

# 汇总
COVERAGE_MATRIX = {
    "DI_TIAN_SUI": DI_TIAN_SUI_COVERAGE,
    "ZI_PING_ZHEN_QUAN": ZI_PING_ZHEN_QUAN_COVERAGE,
    "QIONG_TONG_BAO_JIAN": QIONG_TONG_BAO_JIAN_COVERAGE,
    "YUAN_HAI_ZI_PING": YUAN_HAI_ZI_PING_COVERAGE,
    "SAN_MING_TONG_HUI": SAN_MING_TONG_HUI_COVERAGE,
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
        }
    return result


def generate_coverage_report() -> str:
    """生成覆盖矩阵报告."""
    verification = verify_coverage_matrix()
    lines = [
        "=" * 80,
        "500条 Golden Index 覆盖矩阵报告",
        "=" * 80,
        "",
        f"{'经典':<25} {'槽位数':<10} {'断言数':<10} {'状态':<10}",
        "-" * 80,
    ]
    total = 0
    for school, data in verification.items():
        status = "✓" if data["valid"] else "✗"
        lines.append(f"{school:<25} {data['slots']:<10} {data['total']:<10} {status:<10}")
        total += data["total"]
    lines.append("-" * 80)
    lines.append(f"{'合计':<25} {'':<10} {total:<10} {'':<10}")
    lines.append("=" * 80)
    lines.append("")
    lines.append("覆盖矩阵维度:")
    lines.append("  1. Judgment Type (断言类型)")
    lines.append("  2. Matcher Type (匹配模式: EXACT/SET/CONDITION/COMPOSITE/GRAPH)")
    lines.append("  3. Feature Pattern (Feature模式: 单条件/双条件/三条件/复合)")
    lines.append("  4. Temporal Scope (时间范围: NATAL/YEAR/MONTH/DAY)")
    lines.append("")
    lines.append("注意: 500条是算法覆盖集, 不是500条文本")
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate_coverage_report())
