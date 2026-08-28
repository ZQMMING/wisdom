"""P3-RERUN-AUDIT HOLD - Canonical Condition Audit for HOLD-001 and HOLD-002.

审计目标:
  HOLD-001: SG-ZP-PAT-010 "用神正财" - Current Condition: "存在正财"
  HOLD-002: SG-ZP-STR-004 "五行偏枯" - Current Condition: five_element_imbalance=True

审计原则:
  - 不补资产, 不改Resolver
  - 只审计Canonical Condition定义是否合法
  - 输出审计结果供逐项核查, 不自行定义PASS/FAIL
"""
from __future__ import annotations
import sys
sys.path.insert(0, "src")

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from tongshu.engines.bazi_engine import BaziEngine, STEM_ELEMENT


# ============================================================================
# HOLD 定义
# ============================================================================

@dataclass
class HoldAudit:
    hold_id: str
    judgment_id: str
    canonical_statement: str
    current_condition: str
    problem: str
    gap_type: str
    status: str = "HOLD"
    audit_findings: list = field(default_factory=list)
    recommendation: str = ""
    decision: str = ""  # KEEP / MODIFY / DOWNGRADE / REMOVE


def build_hold_001() -> HoldAudit:
    """HOLD-001: SG-ZP-PAT-010 用神正财."""
    return HoldAudit(
        hold_id="HOLD-001",
        judgment_id="SG-ZP-PAT-010",
        canonical_statement="用神正财，身强取财为用",
        current_condition="required_ten_god=ZHENG_CAI (存在正财)",
        problem="Presence ≠ Use-God Identity. 有正财 ≠ 正财为用神.",
        gap_type="CANONICAL_CONDITION_FIDELITY / ASSET_SCHEMA",
        audit_findings=[
            "1. Canonical Statement包含'用神'和'身强'两个关键限定",
            "2. Current Condition仅检查'存在正财'(has_ten_god=ZHENG_CAI)",
            "3. 缺少'身强'条件: 用神正财通常要求身强才能任财",
            "4. 缺少'用神'判定逻辑: 用神需要格局/旺衰综合判断, 不是简单存在",
            "5. 当前命例(乙木, 水0.5极旺, WOOD=0.125身弱)即使有正财, 也未必'身强取财为用'",
            "6. 因此当前SELECTED是因为'存在正财', 不是因为'正财为用神'",
        ],
        recommendation="修正Condition: 增加身强条件(day_master_element_ratio > threshold), 或增加use_god=ZHENG_CAI的Engine Evidence. 如果无法证明'用神=正财'的确定性条件, 则将此Judgment降级为PARTIAL或从生产Index移除.",
        decision="PENDING_AUDIT",
    )


def build_hold_002() -> HoldAudit:
    """HOLD-002: SG-ZP-STR-004 五行偏枯."""
    return HoldAudit(
        hold_id="HOLD-002",
        judgment_id="SG-ZP-STR-004",
        canonical_statement="五行偏枯，气势不匀，喜调和五行",
        current_condition="required_imbalance=True (Engine five_element_imbalance=True)",
        problem="Engine statistical imbalance ≠ Canonical '偏枯'. 工程统计指标不等于命理概念.",
        gap_type="CANONICAL_CONDITION_FIDELITY",
        audit_findings=[
            "1. Engine calc_five_element_balance()算法:",
            "   - 4天干 + 4地支本气 = 8个元素简单计数",
            "   - 每个天干/地支本气五行各计1, 权重相同",
            "   - 不考虑藏干权重",
            "   - 不考虑月令旺衰权重",
            "   - 不考虑刑冲合害对五行力量的影响",
            "   - 归一化: balance = count / 8",
            "   - imbalance阈值: max > 0.40 或 min < 0.05",
            "2. 当前命例计算:",
            "   - 天干: 癸(水)壬(水)乙(木)壬(水) → 水3, 木1",
            "   - 地支: 亥(水)戌(土)未(土)午(火) → 水1, 土2, 火1",
            "   - 总计: 水4, 木1, 土2, 火1, 金0",
            "   - 归一化: 水0.5, 木0.125, 土0.25, 火0.125, 金0",
            "   - imbalance: max=0.5 > 0.40 → True",
            "3. 子平语境'五行偏枯'通常指:",
            "   - 某一行过旺或过弱, 导致五行之气不流通",
            "   - 需要考虑月令旺衰(得令/失令)",
            "   - 需要考虑藏干权重(本气/中气/余气)",
            "   - 需要考虑刑冲合害对五行力量的改变",
            "   - 是一个更复杂的命理判断, 不是简单的数学阈值",
            "4. 因此Engine的five_element_imbalance(True)是工程统计指标,",
            "   不能直接等同于Canonical的'五行偏枯'.",
            "5. 当前SELECTED是因为Engine统计指标触发, 不是因为Canonical'偏枯'被验证.",
        ],
        recommendation="需要做Canonical Source审计: 查找'五行偏枯'的原典出处和判定标准. 如果原典'偏枯'确实可以用简单五行计数阈值表达, 则明确threshold并写入Feature Contract; 如果原典'偏枯'需要更复杂的判定(月令/藏干/刑冲), 则当前Condition不合法, 应降级为PARTIAL或从生产Index移除, 直到Engine提供更精确的'偏枯'Feature.",
        decision="PENDING_AUDIT",
    )


# ============================================================================
# Engine Feature Contract 审计
# ============================================================================

def audit_engine_feature_contract():
    """审计Engine的five_element_balance Feature Contract."""
    engine = BaziEngine()
    chart = engine.compute((1983, 11, 3, 12), 'male')

    print("=" * 80)
    print("Engine Feature Contract Audit: five_element_balance")
    print("=" * 80)

    print(f"\n  Feature Name: five_element_balance")
    print(f"  Feature Version: v1 (current implementation)")
    print(f"  Calculation Method:")
    print(f"    - 4天干 + 4地支本气 = 8个元素")
    print(f"    - 每个天干/地支本气五行各计1 (权重相同)")
    print(f"    - 不考虑藏干权重")
    print(f"    - 不考虑月令旺衰权重")
    print(f"    - 不考虑刑冲合害")
    print(f"    - 归一化: count / 8")
    print(f"  Imbalance Threshold: max > 0.40 OR min < 0.05")
    print(f"  Nature: ENGINEERING_STATISTICAL_METRIC (不是命理事实)")

    print(f"\n  当前命例计算 (GOLDEN_CASE_1983_MALE):")
    print(f"    天干: 癸(水) 壬(水) 乙(木) 壬(水) → 水3, 木1")
    print(f"    地支: 亥(水) 戌(土) 未(土) 午(火) → 水1, 土2, 火1")
    print(f"    总计: 水4, 木1, 土2, 火1, 金0")
    print(f"    归一化: {chart.five_element_balance}")
    print(f"    imbalance: {chart.five_element_imbalance} (max=0.5 > 0.40)")

    print(f"\n  Feature Contract Status:")
    print(f"    - 计算逻辑: 确定性, 可复现")
    print(f"    - 阈值: 硬编码 0.40/0.05, 无原典依据")
    print(f"    - 与Canonical'偏枯'的关系: 未验证, 可能不等价")
    print(f"    - 建议: 明确标注为ENGINEERING_METRIC, 不直接用于Canonical Judgment")

    return chart


# ============================================================================
# 主函数
# ============================================================================

def main():
    print("=" * 80)
    print("P3-RERUN-AUDIT HOLD - Canonical Condition Audit")
    print("=" * 80)
    print("\n审计范围: HOLD-001 (SG-ZP-PAT-010) + HOLD-002 (SG-ZP-STR-004)")
    print("审计原则: 不补资产, 不改Resolver, 只审计Canonical Condition定义")
    print("输出: 审计结果供逐项核查, 不自行定义PASS/FAIL")

    # Engine Feature Contract审计
    chart = audit_engine_feature_contract()

    # HOLD-001审计
    print(f"\n{'='*80}")
    print("HOLD-001 Audit: SG-ZP-PAT-010 用神正财")
    print("=" * 80)
    h1 = build_hold_001()
    print(f"\n  Judgment ID: {h1.judgment_id}")
    print(f"  Canonical Statement: {h1.canonical_statement}")
    print(f"  Current Condition: {h1.current_condition}")
    print(f"  Problem: {h1.problem}")
    print(f"  Gap Type: {h1.gap_type}")
    print(f"\n  Audit Findings:")
    for f in h1.audit_findings:
        print(f"    {f}")
    print(f"\n  Recommendation: {h1.recommendation}")
    print(f"  Decision: {h1.decision}")

    # HOLD-002审计
    print(f"\n{'='*80}")
    print("HOLD-002 Audit: SG-ZP-STR-004 五行偏枯")
    print("=" * 80)
    h2 = build_hold_002()
    print(f"\n  Judgment ID: {h2.judgment_id}")
    print(f"  Canonical Statement: {h2.canonical_statement}")
    print(f"  Current Condition: {h2.current_condition}")
    print(f"  Problem: {h2.problem}")
    print(f"  Gap Type: {h2.gap_type}")
    print(f"\n  Audit Findings:")
    for f in h2.audit_findings:
        print(f"    {f}")
    print(f"\n  Recommendation: {h2.recommendation}")
    print(f"  Decision: {h2.decision}")

    # 汇总
    print(f"\n{'='*80}")
    print("HOLD Audit 汇总")
    print("=" * 80)
    print(f"""
  HOLD-001 (SG-ZP-PAT-010 用神正财):
    Status: HOLD
    Problem: 有正财 ≠ 正财为用神 (Presence ≠ Use-God Identity)
    Missing: 身强条件 / 用神判定逻辑
    Impact: 当前SELECTED是因为'存在正财', 不是'正财为用神'
    Recommendation: 修正Condition增加身强/用神条件, 或降级为PARTIAL

  HOLD-002 (SG-ZP-STR-004 五行偏枯):
    Status: HOLD
    Problem: Engine统计imbalance ≠ Canonical'偏枯'
    Engine Method: 4天干+4地支本气简单计数, 阈值max>0.40/min<0.05
    Missing: 月令旺衰/藏干权重/刑冲合害/原典'偏枯'判定标准
    Impact: 当前SELECTED是因为Engine统计指标, 不是Canonical'偏枯'
    Recommendation: 做Canonical Source审计, 明确'偏枯'的Feature Contract, 或降级

  共同原则:
    - 不补资产, 不改Resolver
    - 只修正Asset/Condition定义
    - 两个HOLD未解决前, PAT-010和STR-004的SELECTED不计入有效Canonical Assertion

  当前有效SELECTED (排除HOLD):
    Phase 3-1 格局: SG-ZP-PAT-001 (正财格) = 1/10
    Phase 3-2 调候: SG-ZP-TUN-001 (乙木戌月调候) = 1/5
    Phase 3-3 强弱: SG-ZP-STR-001 (身弱) = 1/5
    总计: 3/20 (排除2个HOLD后)

  注意: 此审计不自行定义PASS/FAIL, 结果供逐项核查
""")
    print("=" * 80)


if __name__ == "__main__":
    main()
