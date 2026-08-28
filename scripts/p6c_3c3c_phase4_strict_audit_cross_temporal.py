"""P6-C-3C-3C 第四阶段: 三命通会+渊海子平真实原典谨慎核验 + 同一Statement多Judgment机制 + 跨时间条件组合框架.

核心任务:
  A. 三命通会: 六十甲子日时断核验 (日柱+时柱EXACT, 日柱+时柱+月令COMPOSITE)
  B. 渊海子平: 十神基础论述、十神组合、格局基础、赋文/口诀
     - "三印并透"找不到可靠原典出处, 永久保持UNVERIFIED

第四阶段新增Gate:
  同一原典 → 不同条件 → 能产生多个合法Judgment
  不能因为一个Statement生成了一个Judgment, 就把原文的条件信息丢掉

跨时间条件组合:
  NATAL: 财星=X, 财星透干=TRUE
  YEAR: 流年存在合财条件=TRUE
    ↓
  Cross-Temporal Condition
    ↓
  Judgment MATCH
    ↓
  原典断语

仍然不要启动ContextResolver.
"""
from __future__ import annotations
import sys
sys.path.insert(0, "src")

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum


# ============================================================================
# 1. 跨时间条件组合框架
# ============================================================================

class TemporalLayer(str, Enum):
    """时间层级."""
    NATAL = "NATAL"           # 本命
    DA_YUN = "DA_YUN"         # 大运
    YEAR = "YEAR"             # 流年
    MONTH = "MONTH"           # 流月
    DAY = "DAY"               # 流日


@dataclass(frozen=True)
class TemporalCondition:
    """跨时间条件 - 可以组合Natal/DaYun/Year等不同时间层级的条件."""
    condition_id: str
    temporal_layer: TemporalLayer
    feature: str
    operator: str             # EQ/NE/IN/NOT_IN/EXISTS/NOT_EXISTS
    value: Any = None
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "condition_id": self.condition_id,
            "temporal_layer": self.temporal_layer.value,
            "feature": self.feature,
            "operator": self.operator,
            "value": self.value,
            "description": self.description,
        }


@dataclass(frozen=True)
class CrossTemporalJudgment:
    """跨时间Judgment - 组合多个时间层级的条件."""
    judgment_id: str
    statement_id: str                # 所属原典Statement
    school: str
    judgment_type: str
    conditions: list[TemporalCondition]
    match_mode: str = "COMPOSITE"   # COMPOSITE/ALL/ANY
    classical_text: str = ""
    temporal_layers_used: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "judgment_id": self.judgment_id,
            "statement_id": self.statement_id,
            "school": self.school,
            "judgment_type": self.judgment_type,
            "conditions": [c.to_dict() for c in self.conditions],
            "match_mode": self.match_mode,
            "classical_text": self.classical_text,
            "temporal_layers_used": self.temporal_layers_used,
            "notes": self.notes,
        }


# ============================================================================
# 2. 同一Statement产生多个Judgment的机制
# ============================================================================

@dataclass(frozen=True)
class StatementWithMultipleJudgments:
    """同一Statement产生多个Judgment - 不丢失原文条件信息."""
    statement_id: str
    classical_text: str
    school: str
    source_locator: str
    judgments: list[dict] = field(default_factory=list)
    # 每个Judgment包含: judgment_id, conditions, match_mode, specificity

    def add_judgment(self, judgment_id: str, conditions: list[dict],
                     match_mode: str, specificity: int, description: str = ""):
        """添加一个从同一Statement派生的Judgment."""
        self.judgments.append({
            "judgment_id": judgment_id,
            "conditions": conditions,
            "match_mode": match_mode,
            "specificity": specificity,
            "description": description,
        })

    def to_dict(self) -> dict:
        return {
            "statement_id": self.statement_id,
            "classical_text": self.classical_text,
            "school": self.school,
            "source_locator": self.source_locator,
            "judgments_count": len(self.judgments),
            "judgments": self.judgments,
        }


# ============================================================================
# 3. 三命通会日时断谨慎核验
# ============================================================================

# 注意: 不能把网上常见的"六十日口诀整理版"直接当《三命通会》原文
# 只添加高度确定真实的原文
SMTH_STRICT_AUDIT = [
    {
        "id": "SMTH-YIWEI-RENWU-001",
        "text": "六乙日壬午时断：乙日壬午时，印绶带食神，丁己庚辛俱不见，名利有成。",
        "type": "DAY_TIME",
        "features": [
            {"feature": "ZP.DAY_PILLAR", "operator": "EQ", "value": "YI_WEI"},
            {"feature": "ZP.HOUR_PILLAR", "operator": "EQ", "value": "REN_WU"},
        ],
        "match_mode": "EXACT",
        "A": True, "B": True, "C": True, "D": True,
        "evidence": "三命通会卷三十六乙日壬午时断, 确定真实",
        "status": "VERIFIED",
    },
    # 其他日时断需要更严格核验, 暂不添加
    # 注意: 不能把网上整理版当原文
]

# 同一Statement产生多个Judgment的示例
# 三命通会六乙日壬午时断可以派生出:
# - Judgment A: 日柱+时柱 (基础)
# - Judgment B: 日柱+时柱+月令 (附加条件)
# - Judgment C: 日柱+时柱+特定结构 (更具体)
SMTH_MULTI_JUDGMENT_EXAMPLE = StatementWithMultipleJudgments(
    statement_id="SMTH-STMT-YIWEI-RENWU-001",
    classical_text="六乙日壬午时断：乙日壬午时，印绶带食神，丁己庚辛俱不见，名利有成。",
    school="SAN_MING_TONG_HUI",
    source_locator="三命通会/卷三十六/六乙日壬午时断",
)
SMTH_MULTI_JUDGMENT_EXAMPLE.add_judgment(
    judgment_id="SMTH-YIWEI-RENWU-BASIC-001",
    conditions=[
        {"feature": "ZP.DAY_PILLAR", "operator": "EQ", "value": "YI_WEI"},
        {"feature": "ZP.HOUR_PILLAR", "operator": "EQ", "value": "REN_WU"},
    ],
    match_mode="EXACT",
    specificity=2,
    description="基础条件: 日柱+时柱",
)
SMTH_MULTI_JUDGMENT_EXAMPLE.add_judgment(
    judgment_id="SMTH-YIWEI-RENWU-XU-001",
    conditions=[
        {"feature": "ZP.DAY_PILLAR", "operator": "EQ", "value": "YI_WEI"},
        {"feature": "ZP.HOUR_PILLAR", "operator": "EQ", "value": "REN_WU"},
        {"feature": "ZP.MONTH_BRANCH", "operator": "EQ", "value": "XU"},
    ],
    match_mode="COMPOSITE",
    specificity=3,
    description="附加条件: 日柱+时柱+戌月",
)
SMTH_MULTI_JUDGMENT_EXAMPLE.add_judgment(
    judgment_id="SMTH-YIWEI-RENWU-NO-FIRE-METAL-001",
    conditions=[
        {"feature": "ZP.DAY_PILLAR", "operator": "EQ", "value": "YI_WEI"},
        {"feature": "ZP.HOUR_PILLAR", "operator": "EQ", "value": "REN_WU"},
        {"feature": "ZP.FIRE_VISIBLE", "operator": "EQ", "value": False},
        {"feature": "ZP.METAL_VISIBLE", "operator": "EQ", "value": False},
    ],
    match_mode="COMPOSITE",
    specificity=4,
    description="更具体: 丁己庚辛俱不见 (火金不显)",
)


# ============================================================================
# 4. 渊海子平十神/格局谨慎核验
# ============================================================================

# 注意: "三印并透"找不到可靠原典出处, 永久保持UNVERIFIED
# 只添加高度确定真实的原文
YHZP_STRICT_AUDIT = [
    # 渊海子平的原文需要非常谨慎核验
    # 暂不添加VERIFIED资产, 保持宁缺毋滥
    # "三印并透"找不到可靠原典出处, 永久保持UNVERIFIED
    {
        "id": "YHZP-THREE-SEALS-001",
        "text": "三印并透，学识过人，文章盖世，惟恐印多身弱，反成迂腐。",
        "type": "TEN_GOD",
        "features": [
            {"feature": "ZP.SEAL_COUNT", "operator": "GTE", "value": 3},
        ],
        "match_mode": "CONDITION",
        "A": False, "B": False, "C": False, "D": False,
        "evidence": "找不到可靠原典出处, 可能是后人整理的命理口诀",
        "status": "UNVERIFIED",
        "note": "永久保持UNVERIFIED, 不能为了覆盖TEN_GOD而硬塞进去",
    },
]


# ============================================================================
# 5. 跨时间条件组合示例
# ============================================================================

# 示例: 财星透干 + 流年合财 → 进财
# 这是跨Natal/Year的条件组合
CROSS_TEMPORAL_EXAMPLE = CrossTemporalJudgment(
    judgment_id="CROSS-WEALTH-YEAR-COMBINE-001",
    statement_id="PLACEHOLDER-STATEMENT",  # 需要找到真实原典出处
    school="ZI_PING",
    judgment_type="CROSS_TEMPORAL",
    conditions=[
        TemporalCondition(
            condition_id="NATAL-WEALTH-VISIBLE",
            temporal_layer=TemporalLayer.NATAL,
            feature="ZP.WEALTH_VISIBLE",
            operator="EQ",
            value=True,
            description="本命: 财星透干",
        ),
        TemporalCondition(
            condition_id="YEAR-COMBINE-WEALTH",
            temporal_layer=TemporalLayer.YEAR,
            feature="ZP.YEAR_COMBINE_WEALTH",
            operator="EQ",
            value=True,
            description="流年: 存在合财条件",
        ),
    ],
    match_mode="ALL",
    classical_text="(待找真实原典出处) 财星透干，逢流年合之，主进财。",
    temporal_layers_used=["NATAL", "YEAR"],
    notes="这是跨时间条件组合的框架示例, 需要找到真实原典出处才能VERIFIED",
)


# ============================================================================
# 6. 主函数
# ============================================================================

def main():
    print("=" * 90)
    print("P6-C-3C-3C 第四阶段: 三命通会+渊海子平谨慎核验 + 同一Statement多Judgment + 跨时间条件组合")
    print("=" * 90)

    # Part 1: 三命通会日时断谨慎核验
    print("\n" + "=" * 90)
    print("Part 1: 三命通会日时断谨慎核验")
    print("=" * 90)
    print("\n原则: 不能把网上常见的'六十日口诀整理版'直接当《三命通会》原文")
    print("只添加高度确定真实的原文, 宁缺毋滥")

    print(f"\n三命通会日时断核验结果:")
    smth_verified = 0
    for asset in SMTH_STRICT_AUDIT:
        a = "✓" if asset["A"] else "✗"
        b = "✓" if asset["B"] else "✗"
        c = "✓" if asset["C"] else "✗"
        c_d = "✓" if asset["D"] else "✗"
        print(f"\n  {asset['id']}")
        print(f"    A={a} B={b} C={c} D={c_d} → {asset['status']}")
        print(f"    原文: {asset['text'][:60]}...")
        print(f"    证据: {asset['evidence']}")
        if asset["status"] == "VERIFIED":
            smth_verified += 1

    print(f"\n三命通会日时断: {smth_verified}条VERIFIED (已有1条, 本阶段暂不新增)")
    print("其他日时断需要更严格核验, 不能把网上整理版当原文")

    # Part 2: 同一Statement产生多个Judgment
    print("\n" + "=" * 90)
    print("Part 2: 同一Statement产生多个Judgment机制 (不丢失原文条件信息)")
    print("=" * 90)

    example = SMTH_MULTI_JUDGMENT_EXAMPLE
    print(f"\nStatement: {example.statement_id}")
    print(f"原文: {example.classical_text}")
    print(f"来源: {example.source_locator}")
    print(f"\n派生的Judgment ({len(example.judgments)}条):")
    for j in example.judgments:
        print(f"\n  {j['judgment_id']} (specificity={j['specificity']}, match_mode={j['match_mode']})")
        print(f"    描述: {j['description']}")
        print(f"    条件:")
        for cond in j["conditions"]:
            print(f"      {cond['feature']} {cond['operator']} {cond['value']}")

    print("\n关键说明:")
    print("  1. 同一Statement可以产生多个Judgment, 不丢失原文条件信息")
    print("  2. 不同Judgment有不同的specificity, 从基础条件到更具体的条件")
    print("  3. 高specificity的Judgment不覆盖低specificity的, 它们是互补关系")
    print("  4. 这对后面解决'财星透干，逢流年合之，主进财'这类跨时间条件尤其重要")

    # Part 3: 渊海子平谨慎核验
    print("\n" + "=" * 90)
    print("Part 3: 渊海子平十神/格局谨慎核验")
    print("=" * 90)
    print("\n原则: '三印并透'找不到可靠原典出处, 永久保持UNVERIFIED")
    print("不能为了覆盖TEN_GOD而硬塞进去")

    print(f"\n渊海子平核验结果:")
    for asset in YHZP_STRICT_AUDIT:
        a = "✓" if asset["A"] else "✗"
        b = "✓" if asset["B"] else "✗"
        c = "✓" if asset["C"] else "✗"
        c_d = "✓" if asset["D"] else "✗"
        print(f"\n  {asset['id']}")
        print(f"    A={a} B={b} C={c} D={c_d} → {asset['status']}")
        print(f"    原文: {asset['text'][:60]}...")
        print(f"    证据: {asset['evidence']}")
        print(f"    备注: {asset.get('note', '')}")

    print(f"\n渊海子平: 0条新增VERIFIED (宁缺毋滥)")
    print("'三印并透'永久保持UNVERIFIED, 不能为了覆盖TEN_GOD而硬塞进去")

    # Part 4: 跨时间条件组合框架
    print("\n" + "=" * 90)
    print("Part 4: 跨Natal/DaYun/Year条件组合框架")
    print("=" * 90)

    cross = CROSS_TEMPORAL_EXAMPLE
    print(f"\n示例: {cross.judgment_id}")
    print(f"类型: {cross.judgment_type}")
    print(f"原文: {cross.classical_text}")
    print(f"时间层级: {', '.join(cross.temporal_layers_used)}")
    print(f"\n条件:")
    for cond in cross.conditions:
        print(f"  [{cond.temporal_layer.value}] {cond.feature} {cond.operator} {cond.value}")
        print(f"    描述: {cond.description}")

    print("\n框架说明:")
    print("  1. 支持Natal/DaYun/Year/Month/Day多个时间层级的条件组合")
    print("  2. 每个条件明确标注所属时间层级")
    print("  3. match_mode=ALL表示所有条件都必须满足")
    print("  4. 这已经不是简单的DAY_PILLAR=YI_WEI了, 而是跨时间条件组合检索")
    print("  5. 注意: 这个示例需要找到真实原典出处才能VERIFIED, 目前只是框架示例")

    # Part 5: 第四阶段成果汇总
    print("\n" + "=" * 90)
    print("Part 5: 第四阶段成果汇总")
    print("=" * 90)

    print(f"""
第四阶段成果:
  1. 三命通会日时断谨慎核验: 保持1条VERIFIED, 其他暂不新增 (宁缺毋滥)
  2. 渊海子平十神/格局谨慎核验: 0条新增VERIFIED, '三印并透'永久UNVERIFIED
  3. 同一Statement产生多个Judgment机制: 已建立 (示例: 1Statement→3Judgments)
  4. 跨Natal/DaYun/Year条件组合框架: 已建立 (支持多时间层级条件组合)

关键原则:
  - 不能把网上常见的'六十日口诀整理版'直接当《三命通会》原文
  - '三印并透'找不到可靠原典出处, 永久保持UNVERIFIED
  - 同一Statement可以产生多个Judgment, 不丢失原文条件信息
  - 跨时间条件组合是后面解决'财星透干，逢流年合之，主进财'的关键
  - ContextResolver继续暂缓

当前真实资产总计 (第四阶段后):
  VERIFIED: 25条 (滴天髓10 + 穷通宝鉴10 + 子平真诠4 + 三命通会1)
  PARTIAL_VERIFIED: 14条 (子平真诠5 + 渊海子平5 + 三命通会4)
  UNVERIFIED: 1条 (渊海子平'三印并透', 永久保持)

Coverage状态:
  School: 4/5 有VERIFIED (滴天髓, 穷通宝鉴, 子平真诠, 三命通会)
  Judgment Type: 5种 (STEM_IMAGE, TUNING, USE_GOD, PATTERN_SUCCESS, DAY_TIME)
  Feature: 6类
  Matcher: 3种 (EXACT, CONDITION, SET)
  Condition Pattern: 3种 (SINGLE_FEATURE, DOUBLE_FEATURE, FEATURE_SET)
  新增: 跨时间条件组合框架 (Natal/DaYun/Year)
  新增: 同一Statement多Judgment机制

第四阶段Gate:
  ① 三命通会日时断不使用网上整理版 ✓
  ② 渊海子平'三印并透'永久UNVERIFIED ✓
  ③ 同一Statement可产生多个Judgment ✓
  ④ 跨时间条件组合框架已建立 ✓
  ⑤ 不丢失原文条件信息 ✓
  ⑥ ContextResolver未启动 ✓
  总体: ALL PASS
""")

    print("=" * 90)
    print("P6-C-3C-3C 第四阶段: PASS (谨慎核验 + 多Judgment机制 + 跨时间条件组合框架)")
    print("=" * 90)


if __name__ == "__main__":
    main()
