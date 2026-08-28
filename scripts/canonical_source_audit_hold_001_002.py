"""Canonical Source Audit - HOLD-001 and HOLD-002.

审计目标:
  HOLD-001: SG-ZP-PAT-010 "用神正财" - 原典条件审计
  HOLD-002: SG-ZP-STR-004 "五行偏枯" - 原典条件审计

审计原则:
  - 回到原典定义, 不预设现代命理解释框架
  - 由Canonical Evidence决定Feature Contract, 不是反过来
  - 不修改Resolver, 不补资产, 不解冻Assertion
  - 输出审计结果供逐项核查, 不自行定义VALID/PARTIAL/RETIRE
"""
from __future__ import annotations
import sys
sys.path.insert(0, "src")

from dataclasses import dataclass, field
from typing import Optional


# ============================================================================
# Canonical Source Audit 数据结构
# ============================================================================

@dataclass
class CanonicalSource:
    """原典来源."""
    book: str
    chapter: str
    original_text: str
    commentator: Optional[str] = None  # 注者 (如徐乐吾注)
    commentary_text: Optional[str] = None
    source_url: Optional[str] = None


@dataclass
class CanonicalConditionAudit:
    """Canonical Condition 审计."""
    hold_id: str
    judgment_id: str
    canonical_statement: str
    current_condition: str
    sources: list = field(default_factory=list)
    key_findings: list = field(default_factory=list)
    canonical_conditions: list = field(default_factory=list)  # 原典实际要求的条件
    engine_provable: list = field(default_factory=list)  # 当前Engine可证明的条件
    engine_not_provable: list = field(default_factory=list)  # 当前Engine不可证明的条件
    semantic_gap: str = ""
    recommendation: str = ""
    decision: str = "PENDING_AUDIT"  # VALID / PARTIAL / RETIRE / PENDING


# ============================================================================
# HOLD-001: SG-ZP-PAT-010 用神正财
# ============================================================================

def audit_hold_001() -> CanonicalConditionAudit:
    audit = CanonicalConditionAudit(
        hold_id="HOLD-001",
        judgment_id="SG-ZP-PAT-010",
        canonical_statement="用神正财，身强取财为用",
        current_condition="required_ten_god=ZHENG_CAI (存在正财)",
    )

    # 原典来源
    audit.sources = [
        CanonicalSource(
            book="子平真诠",
            chapter="第33章 论财",
            original_text="财为我克，使用之物也，以能生官，所以为美。为财帛，为妻妾，为才能，为驿马，皆财类也。",
            commentator="徐乐吾",
            commentary_text="财为我克，必须身强，万能克制。若身弱，虽有财不能任，则财反为祸矣。...格局之中，单用财者甚少，如身强露官，用财生官；身强煞弱，用财滋煞；身强印旺，用财损印。身强喜泄露食伤者，用食伤生财；财旺身弱，用比劫分财为美。皆非单用财也。",
            source_url="https://www.guoxuedashi.com/a/22471l/283645j.html",
        ),
        CanonicalSource(
            book="子平真诠",
            chapter="第8章 论用神",
            original_text="八字用神，专求月令，以日干配月令地支，而生克不同，格局分焉。财官印食，此用神之善而顺用之者也；煞伤劫刃，用神之不善而逆用之者也。当顺而顺，当逆而逆，配合得宜，皆为贵格。",
            source_url="https://dclef.com/xuanxuedocs/%E5%AD%90%E5%B9%B3%E7%9C%9F%E8%AF%A0/009%E7%AC%AC08%E7%AB%A0%20%E8%AE%BA%E7%94%A8%E7%A5%9E.html",
        ),
    ]

    # 关键发现
    audit.key_findings = [
        "1. 《子平真诠》论用神: '八字用神，专求月令' — 用神是从月令取的，不是从全局'存在'取的",
        "2. 正财格的用神 = 月令正财（已被SG-ZP-PAT-001覆盖），不是'存在正财'",
        "3. 徐注明确: '格局之中，单用财者甚少' — 财格通常不是单用财",
        "4. 财旺生官者，用神在官（不是财）",
        "5. 食神生财者，用在食神（不是财）",
        "6. 财格佩印者，身弱得印，用神即在于印（不是财）",
        "7. 只有极特殊情况才'单用财': '壬生午月，癸生巳月，单透财而亦贵，又月令有暗官也'",
        "8. 因此'用神正财，身强取财为用'这个Canonical Statement本身就不是子平真诠的标准表述",
        "9. 更像是现代整理的简化说法，混淆了'财格'和'用神为财'",
        "10. 当前Condition'存在正财'更是过宽: 有正财 ≠ 正财为用神, 而且在子平真诠体系中正财格用神通常不是财本身",
    ]

    # 原典实际要求的条件
    audit.canonical_conditions = [
        "月令为正财（已被PAT-001覆盖）",
        "身强（徐注: '必须身强，万能克制'）",
        "财格配合特定格局（财旺生官/食神生财/财格佩印等），用神通常不是财本身",
        "极特殊情况'单用财': 需要月令有暗官等特定条件",
    ]

    # Engine可证明
    audit.engine_provable = [
        "月令主气=正财（已被PAT-001覆盖）",
        "day_master_element_ratio（可作为身强/身弱的工程指标，但canonical equivalence未证明）",
    ]

    # Engine不可证明
    audit.engine_not_provable = [
        "'用神=正财'的判定（用神需要格局/旺衰/配合综合判断，不是简单存在）",
        "财格配合的具体格局类型（财旺生官/食神生财/财格佩印等）",
        "'单用财'的特殊条件（月令有暗官等）",
    ]

    audit.semantic_gap = (
        "Canonical Statement'用神正财'在子平真诠体系中本身就不标准: "
        "正财格的用神通常不是财本身，而是配合格局的其他神（官/食神/印等）。 "
        "当前Condition'存在正财'更是把'有正财'偷换成'正财为用神'。 "
        "这不是简单的Condition过宽，而是Canonical Statement本身需要重新定义。"
    )

    audit.recommendation = (
        "建议RETIRE当前PAT-010定义，原因: "
        "1. '用神正财'不是子平真诠标准表述，正财格用神通常不是财本身; "
        "2. 如果要保留'正财格'的判断，已被PAT-001（月令主气=正财）覆盖; "
        "3. 如果要表达'身强可任财'，需要单独建立Canonical Statement并做Source Audit，"
        "且'身强'的Feature Contract需要先证明canonical equivalence; "
        "4. 不应为了让它SELECTED而增加简单的strength_threshold。"
    )

    return audit


# ============================================================================
# HOLD-002: SG-ZP-STR-004 五行偏枯
# ============================================================================

def audit_hold_002() -> CanonicalConditionAudit:
    audit = CanonicalConditionAudit(
        hold_id="HOLD-002",
        judgment_id="SG-ZP-STR-004",
        canonical_statement="五行偏枯，气势不匀，喜调和五行",
        current_condition="required_imbalance=True (Engine five_element_imbalance=True)",
    )

    # 原典来源
    audit.sources = [
        CanonicalSource(
            book="渊海子平",
            chapter="五行元理消息赋",
            original_text="五行不可太甚，八字须得中和。...遐龄得于中和。夭折丧于偏枯。",
            source_url="https://m.gushiwen.cn/guwen/bookv_a18f5e41a43d.aspx",
        ),
        CanonicalSource(
            book="渊海子平",
            chapter="玄机赋",
            original_text="禀中和，莫令太过不及。",
            source_url="https://m.gushiwen.cn/guwen/bookv_a18f5e41a43d.aspx",
        ),
        CanonicalSource(
            book="渊海子平",
            chapter="金玉赋",
            original_text="中和为福。偏党为灾。...太过无克制者，贫贱。不及无生扶者，夭折。",
            source_url="https://m.gushiwen.cn/guwen/bookv_a18f5e41a43d.aspx",
        ),
        CanonicalSource(
            book="渊海子平",
            chapter="五行元理消息赋",
            original_text="金赖土生，土多金埋。土赖火生，火多土焦。火赖木生，木多火炽。木赖水生，水多水漂。水赖金生，金多水浊。",
            source_url="https://www.luckclub.cn/bazi/001/291/",
        ),
    ]

    # 关键发现
    audit.key_findings = [
        "1. 原典'偏枯'的核心语义: '五行不可太甚，八字须得中和'（渊海子平·五行元理消息赋）",
        "2. '遐龄得于中和。夭折丧于偏枯。' — 偏枯与中和直接对立",
        "3. '禀中和，莫令太过不及。'（玄机赋）— 偏枯 = 太过或不及",
        "4. '中和为福。偏党为灾。'（金玉赋）",
        "5. '太过无克制者，贫贱。不及无生扶者，夭折。' — 关键: 偏枯不只是'太甚'，还要看'有无克制/生扶'",
        "6. '金赖土生，土多金埋...' — 五行生克关系是判断偏枯的重要依据",
        "7. 因此'偏枯'的原典判定至少包含: (a)某行太甚/不及 (b)太甚者有无克制 (c)不及者有无生扶 (d)五行接续相生是否流通",
        "8. Engine的five_element_imbalance: 4天干+4地支本气简单计数, max>0.40或min<0.05",
        "9. Engine只覆盖了(a)的一部分（简单计数阈值），完全没有考虑(b)(c)(d)",
        "10. 当前命例: 水0.5>0.40（太甚），但水有土克（戌未土）；金0<0.05（不及），但金有土生（戌未土）；是否真的'偏枯'需要更复杂判断",
    ]

    # 原典实际要求的条件
    audit.canonical_conditions = [
        "某一行太甚（过旺）",
        "太甚者有无克制（如'土多金埋'需要土多且金无制）",
        "某一行不及（过弱/缺失）",
        "不及者有无生扶（如'金赖土生'，金弱但有土生则不一定偏枯）",
        "五行接续相生是否流通（一气流通 vs 偏枯）",
        "月令旺衰（得令/失令对五行力量的影响）",
    ]

    # Engine可证明
    audit.engine_provable = [
        "五行简单计数分布（4天干+4地支本气）",
        "max>0.40 / min<0.05 的工程阈值（可作为'太甚/不及'的初步参考）",
    ]

    # Engine不可证明
    audit.engine_not_provable = [
        "太甚者有无克制（需要五行生克关系分析）",
        "不及者有无生扶（需要五行生克关系分析）",
        "五行接续相生是否流通（需要graph/path分析）",
        "月令旺衰对五行力量的影响（得令/失令）",
        "藏干权重（Engine只看地支本气，不看藏干）",
        "刑冲合害对五行力量的改变",
    ]

    audit.semantic_gap = (
        "Engine的five_element_imbalance是工程统计指标（简单计数+硬编码阈值）， "
        "与Canonical'偏枯'（太甚/不及+有无克制/生扶+五行流通+月令旺衰）只有部分相关。 "
        "max>0.40可能对应'太甚'的一部分，但没有考虑'有无克制'; "
        "min<0.05可能对应'不及'的一部分，但没有考虑'有无生扶'; "
        "完全没有考虑五行接续相生/流通和月令旺衰。 "
        "因此Engine imbalance=True不能直接等同于Canonical'偏枯'。"
    )

    audit.recommendation = (
        "建议PARTIAL（降级），原因: "
        "1. Engine的five_element_imbalance可作为'偏枯'的初步参考指标（太甚/不及的简单计数）; "
        "2. 但不能直接等同于Canonical'偏枯'，缺少'有无克制/生扶'和'五行流通'的判断; "
        "3. 应明确标注five_element_balance的semantic_type=ENGINEERING_STATISTICAL_METRIC, "
        "canonical_equivalence=PARTIAL（与'偏枯'部分相关但不等价）; "
        "4. 如果要建立真正的'偏枯'Judgment，需要Engine扩展Feature: "
        "五行生克关系分析、五行流通性分析、月令旺衰权重等; "
        "5. 在Engine Feature扩展完成前，STR-004不应作为ACTIVE Canonical Judgment。"
    )

    return audit


# ============================================================================
# Engine Feature 元数据规范
# ============================================================================

def build_engine_feature_metadata():
    """建立Engine Feature元数据规范."""
    return {
        "feature_id": "five_element_balance",
        "version": "v1",
        "semantic_type": "ENGINEERING_STATISTICAL_METRIC",
        "calculation": {
            "basis": "4 stems + 4 branch main qi (本气)",
            "weighting": "equal weight (each stem/branch main qi = 1)",
            "normalization": "count / 8",
            "hidden_stems": "NOT considered",
            "month_strength": "NOT considered",
            "clash_harm_combine": "NOT considered",
        },
        "imbalance_threshold": {
            "max_threshold": 0.40,
            "min_threshold": 0.05,
            "basis": "hard-coded, NO canonical source",
        },
        "canonical_equivalence": {
            "status": "PARTIAL",
            "related_concepts": ["五行太甚", "五行不及"],
            "not_equivalent_to": ["五行偏枯", "五行中和", "五行流通"],
            "reason": "simple count threshold does not consider 克制/生扶/流通/月令旺衰",
        },
        "usage_restriction": "NOT to be used directly as Canonical '偏枯' condition; may be used as preliminary engineering indicator only",
    }


# ============================================================================
# 主函数
# ============================================================================

def main():
    print("=" * 90)
    print("Canonical Source Audit - HOLD-001 & HOLD-002")
    print("=" * 90)
    print("\n审计原则: 回到原典定义, 不预设现代命理解释框架; 由Canonical Evidence决定Feature Contract")
    print("不修改Resolver, 不补资产, 不解冻Assertion; 输出供逐项核查, 不自行定义VALID/PARTIAL/RETIRE")

    # HOLD-001
    print(f"\n{'='*90}")
    print("HOLD-001 Audit: SG-ZP-PAT-010 用神正财")
    print("=" * 90)
    h1 = audit_hold_001()
    print(f"\n  Judgment: {h1.judgment_id}")
    print(f"  Canonical Statement: {h1.canonical_statement}")
    print(f"  Current Condition: {h1.current_condition}")
    print(f"\n  原典来源:")
    for s in h1.sources:
        print(f"    - 《{s.book}》{s.chapter}")
        print(f"      原文: {s.original_text[:80]}...")
        if s.commentary_text:
            print(f"      {s.commentator}注: {s.commentary_text[:80]}...")
    print(f"\n  关键发现:")
    for f in h1.key_findings:
        print(f"    {f}")
    print(f"\n  原典实际要求的条件:")
    for c in h1.canonical_conditions:
        print(f"    - {c}")
    print(f"\n  Engine可证明: {h1.engine_provable}")
    print(f"  Engine不可证明: {h1.engine_not_provable}")
    print(f"\n  Semantic Gap: {h1.semantic_gap}")
    print(f"\n  Recommendation: {h1.recommendation}")
    print(f"  Decision: {h1.decision}")

    # HOLD-002
    print(f"\n{'='*90}")
    print("HOLD-002 Audit: SG-ZP-STR-004 五行偏枯")
    print("=" * 90)
    h2 = audit_hold_002()
    print(f"\n  Judgment: {h2.judgment_id}")
    print(f"  Canonical Statement: {h2.canonical_statement}")
    print(f"  Current Condition: {h2.current_condition}")
    print(f"\n  原典来源:")
    for s in h2.sources:
        print(f"    - 《{s.book}》{s.chapter}")
        print(f"      原文: {s.original_text[:80]}...")
    print(f"\n  关键发现:")
    for f in h2.key_findings:
        print(f"    {f}")
    print(f"\n  原典实际要求的条件:")
    for c in h2.canonical_conditions:
        print(f"    - {c}")
    print(f"\n  Engine可证明: {h2.engine_provable}")
    print(f"  Engine不可证明: {h2.engine_not_provable}")
    print(f"\n  Semantic Gap: {h2.semantic_gap}")
    print(f"\n  Recommendation: {h2.recommendation}")
    print(f"  Decision: {h2.decision}")

    # Engine Feature元数据
    print(f"\n{'='*90}")
    print("Engine Feature Metadata: five_element_balance v1")
    print("=" * 90)
    meta = build_engine_feature_metadata()
    for k, v in meta.items():
        if isinstance(v, dict):
            print(f"\n  {k}:")
            for k2, v2 in v.items():
                print(f"    {k2}: {v2}")
        else:
            print(f"  {k}: {v}")

    # 汇总
    print(f"\n{'='*90}")
    print("Canonical Source Audit 汇总")
    print("=" * 90)
    print(f"""
  HOLD-001 (SG-ZP-PAT-010 用神正财):
    Status: HOLD
    Core Issue: Canonical Statement本身不标准 + Condition过宽
    - '用神正财'在子平真诠体系中不标准: 正财格用神通常不是财本身
    - '存在正财' ≠ '正财为用神'
    - 正财格已被PAT-001（月令主气=正财）覆盖
    Recommendation: RETIRE当前定义, 或重新建立Canonical Statement并做Source Audit
    Decision: PENDING_AUDIT

  HOLD-002 (SG-ZP-STR-004 五行偏枯):
    Status: HOLD
    Core Issue: Engine统计指标 ≠ Canonical偏枯
    - Engine: 简单计数+硬编码阈值(max>0.40/min<0.05)
    - Canonical: 太甚/不及 + 有无克制/生扶 + 五行流通 + 月令旺衰
    - Engine只覆盖了'太甚/不及'的一部分, 缺少克制/生扶/流通/月令
    Recommendation: PARTIAL(降级), Engine可作为初步参考但不能直接等同Canonical偏枯
    Decision: PENDING_AUDIT

  Engine Feature Metadata:
    five_element_balance v1:
      semantic_type: ENGINEERING_STATISTICAL_METRIC
      canonical_equivalence: PARTIAL (与'太甚/不及'部分相关, 不等同'偏枯')
      usage_restriction: 不能直接作为Canonical'偏枯'条件

  当前有效SELECTED (排除2个HOLD后):
    PAT-001 正财格 ✓
    TUN-001 乙木戌月调候 ✓
    STR-001 身弱 (WOOD<0.15) ⚠ CONDITIONAL (Canonical Fidelity待审计)
    总计: 2 VALID + 1 CONDITIONAL = 3/20

  注意: 此审计不自行定义VALID/PARTIAL/RETIRE, 结果供逐项核查
""")
    print("=" * 90)


if __name__ == "__main__":
    main()
