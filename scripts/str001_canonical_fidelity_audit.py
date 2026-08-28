"""STR-001 Canonical Fidelity Audit.

审计目标:
  STR-001 "日主身弱，喜印比生扶"
  Current Condition: WOOD_ratio < 0.15

审计核心:
  两个 semantic jump:
    Jump 1: WOOD比例低 → 日主身弱?
    Jump 2: 日主身弱 → 喜印比生扶?

  防止循环自证: 不能拿Engine的WOOD<0.15反过来定义"身弱"

原典来源:
  《渊海子平·玄机赋》:
    - "得时俱为旺论，失令便作衰看。"
    - "四柱无根，得时为旺；日干无气，遇劫为强。"
    - "身弱喜印，主旺宜官。"
    - "身弱者忌见财官。"
    - "身衰则喜扶喜助。"
    - "财多身弱，畏入财乡。"
"""
from __future__ import annotations
import sys
sys.path.insert(0, "src")

from dataclasses import dataclass, field
from typing import Optional
from tongshu.engines.bazi_engine import BaziEngine, STEM_ELEMENT


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class CanonicalSource:
    book: str
    chapter: str
    original_text: str
    source_url: Optional[str] = None


@dataclass
class SemanticJumpAudit:
    jump_id: str
    description: str
    canonical_basis: list = field(default_factory=list)
    engine_evidence: list = field(default_factory=list)
    gap_analysis: str = ""
    conclusion: str = ""  # VALID / PARTIAL / INVALID / PENDING


@dataclass
class STR001Audit:
    judgment_id: str = "SG-ZP-STR-001"
    canonical_statement: str = "日主身弱，喜印比生扶"
    current_condition: str = "WOOD_ratio < 0.15"
    sources: list = field(default_factory=list)
    jump1: Optional[SemanticJumpAudit] = None
    jump2: Optional[SemanticJumpAudit] = None
    current_case_analysis: dict = field(default_factory=dict)
    circular_reasoning_risk: str = ""
    feature_sufficiency: str = ""
    recommendation: str = ""
    decision: str = "PENDING_AUDIT"


# ============================================================================
# 原典来源
# ============================================================================

def build_sources() -> list:
    return [
        CanonicalSource(
            book="渊海子平",
            chapter="玄机赋",
            original_text="得时俱为旺论，失令便作衰看。四柱无根，得时为旺；日干无气，遇劫为强。身弱喜印，主旺宜官。身弱者忌见财官。身衰则喜扶喜助。财多身弱，畏入财乡。",
            source_url="https://www.luckclub.cn/bazi/001/187/",
        ),
        CanonicalSource(
            book="渊海子平",
            chapter="玄机赋",
            original_text="身坐休囚，平生未济。身旺者喜逢禄马，身弱者忌见财官。",
            source_url="https://www.luckclub.cn/bazi/001/187/",
        ),
        CanonicalSource(
            book="渊海子平",
            chapter="玄机赋",
            original_text="身弱有印，杀旺无伤，忌行财地。...身旺者用财，身弱者用印。",
            source_url="https://www.luckclub.cn/bazi/001/187/",
        ),
    ]


# ============================================================================
# Jump 1: WOOD比例低 → 日主身弱?
# ============================================================================

def audit_jump1() -> SemanticJumpAudit:
    jump = SemanticJumpAudit(
        jump_id="JUMP-1",
        description="WOOD_ratio < 0.15 → 日主身弱",
    )

    # 原典对"身弱"的判定标准
    jump.canonical_basis = [
        "1. 月令状态: '得时俱为旺论，失令便作衰看。' — 月令是核心判定标准",
        "2. 根气: '四柱无根，得时为旺；日干无气，遇劫为强。' — 根气/帮扶也是判定标准",
        "3. 日主坐旺衰: '身坐休囚，平生未济。' — 日主坐休囚也是身弱表现",
        "4. 生克力量对比: 身弱 = 克泄耗(财官杀食伤) > 生扶(印比)",
        "5. '身衰遇鬼' — 身衰时官杀变鬼",
    ]

    # Engine当前提供的证据
    jump.engine_evidence = [
        "1. WOOD_ratio = 0.125 (4天干+4地支本气简单计数中木的占比)",
        "2. 月令: 乙木生于戌月 (戌月是秋季末, 木在戌月的十二长生状态需确认)",
        "3. 根气: 未中藏乙木 (日支未中有乙木余气), 所以乙木不是完全无根",
        "4. 生扶力量: 壬水(正印)透干×2, 亥水(正印)在年支, 印星生扶力量不弱 (WATER=0.5)",
        "5. 克泄耗力量: 戊土(正财)在戌月当令, 未中己土(偏财), 午火(食神)",
    ]

    # Gap分析
    jump.gap_analysis = (
        "原典'身弱'的判定是多维度的: 月令状态 + 根气 + 生扶vs克泄耗力量对比 + 日主坐旺衰。 "
        "Engine的WOOD_ratio<0.15只覆盖了'木元素在简单计数中占比低'这一个维度, 完全没有考虑: "
        "(1) 月令得时/失令 (2) 日主根气 (3) 印星生扶力量 (4) 克泄耗力量对比。 "
        "特别是当前命例印星(水)很旺(WATER=0.5), 印星可以生扶日主, 所以即使木本身占比低, "
        "有印生扶也不一定身弱。 "
        "因此WOOD_ratio<0.15不能直接证明'日主身弱'。"
    )

    jump.conclusion = (
        "INVALID: WOOD_ratio<0.15不能直接等同于'日主身弱'。 "
        "原典身弱需要月令+根气+生克对比多维度判定, Engine当前只提供了单一维度的简单计数。 "
        "特别是印星生扶力量未被纳入身弱判定。"
    )

    return jump


# ============================================================================
# Jump 2: 日主身弱 → 喜印比生扶?
# ============================================================================

def audit_jump2() -> SemanticJumpAudit:
    jump = SemanticJumpAudit(
        jump_id="JUMP-2",
        description="日主身弱 → 喜印比生扶",
    )

    # 原典对"身弱喜印比"的依据
    jump.canonical_basis = [
        "1. '身弱喜印，主旺宜官。' (玄机赋原文) — 身弱喜印有明确原典依据",
        "2. '日干无气，遇劫为强。' (玄机赋原文) — 比劫(劫)可以帮身",
        "3. '身衰则喜扶喜助。' (玄机赋原文) — 身衰喜扶助(印比)",
        "4. '身弱有印，杀旺无伤，忌行财地。' — 身弱有印的情况",
        "5. '身旺者用财，身弱者用印。' — 伤官格中身弱用印",
        "6. '财多身弱，畏入财乡。' — 财多身弱忌财运(反证喜印比)",
    ]

    # Engine当前提供的证据
    jump.engine_evidence = [
        "1. 印星(水)在当前命例中很旺: WATER=0.5, 壬水透干×2, 亥水在年支",
        "2. 比劫(木)在当前命例中较弱: WOOD=0.125, 只有乙木日主+未中乙木余气",
        "3. Engine没有提供'印星是否可以有效生扶日主'的判定",
        "4. Engine没有提供'比劫是否可以有效帮身'的判定",
    ]

    # Gap分析
    jump.gap_analysis = (
        "'身弱喜印比生扶'有明确原典依据('身弱喜印''日干无气遇劫为强''身衰则喜扶喜助')。 "
        "但这个结论的前提是'身弱'已经被证明。如果Jump 1不成立(WOOD<0.15不能证明身弱), "
        "那么Jump 2的前提就不成立。 "
        "另外, '喜印比生扶'是一个方向性结论, 但具体到某个命例: "
        "(1) 印星是否可用? (印星是否受制/是否过多) "
        "(2) 比劫是否可用? (比劫是否夺财/是否有根) "
        "这些都需要更细的判定, Engine当前没有提供。"
    )

    jump.conclusion = (
        "CONDITIONAL: '身弱喜印比生扶'有明确原典依据, 但前提是'身弱'已经被独立证明。 "
        "当前Jump 1不成立(WOOD<0.15不能证明身弱), 因此Jump 2的前提不成立。 "
        "另外, '喜印比'是方向性结论, 具体到某个命例还需要判定印星/比劫是否可用, Engine当前没有提供。"
    )

    return jump


# ============================================================================
# 当前命例分析
# ============================================================================

def analyze_current_case() -> dict:
    engine = BaziEngine()
    chart = engine.compute((1983, 11, 3, 12), 'male')

    return {
        "八字": "癸亥 壬戌 乙未 壬午",
        "日主": "乙木",
        "月令": "戌月(戊土当令)",
        "五行分布": chart.five_element_balance,
        "imbalance": chart.five_element_imbalance,
        "身弱判定_原典维度": {
            "月令得时/失令": "乙木生于戌月, 戌为秋季末, 木在戌月处于衰地(需确认十二长生)",
            "根气": "未中藏乙木(日支未中有乙木余气), 不是完全无根",
            "生扶力量": "壬水(正印)透干×2, 亥水(正印)在年支, 印星生扶力量不弱(WATER=0.5)",
            "克泄耗力量": "戊土(正财)在戌月当令, 未中己土(偏财), 午火(食神)",
            "日主坐旺衰": "乙木坐未土, 未中有乙木余气, 不是坐休囚",
        },
        "WOOD<0.15的问题": "WOOD=0.125只证明木元素简单计数占比低, 但印星(水0.5)很旺可以生扶日主, 所以不能直接判定身弱",
        "当前命例是否身弱": "需要更复杂的判定(月令+根气+生克对比), 不能简单用WOOD<0.15判定",
    }


# ============================================================================
# 循环自证风险
# ============================================================================

def analyze_circular_reasoning() -> str:
    return (
        "循环自证风险: HIGH\n"
        "当前逻辑: Engine规定WOOD<0.15 → 标记为'身弱' → 然后拿这个证明Canonical中的'身弱'成立\n"
        "这不是验证, 是自证循环。\n"
        "正确流程应该是:\n"
        "  1. 从Canonical Source定义什么叫身弱(月令+根气+生克对比)\n"
        "  2. 建立Engine Feature来度量这些维度\n"
        "  3. 验证Engine Feature是否足以证明Canonical定义的'身弱'\n"
        "而不是: 先规定一个工程阈值, 然后拿它定义命理概念。"
    )


# ============================================================================
# Feature Sufficiency
# ============================================================================

def analyze_feature_sufficiency() -> str:
    return (
        "WOOD_ratio < 0.15 作为'身弱'的Feature是不充分的, 原因:\n"
        "1. 只考虑了日主五行的简单计数占比, 没有考虑月令旺衰\n"
        "2. 没有考虑日主根气(地支藏干中的日主五行)\n"
        "3. 没有考虑印星生扶力量(印星可以生扶日主, 即使日主本身占比低)\n"
        "4. 没有考虑克泄耗力量对比(财官杀食伤 vs 印比)\n"
        "5. 没有考虑日主坐旺衰(日支对日主的影响)\n"
        "\n"
        "如果要建立真正的'身弱'Feature, 至少需要:\n"
        "  - month_strong: 日主是否得月令(得时/失令)\n"
        "  - root_strength: 日主根气强度(地支藏干中的日主五行)\n"
        "  - support_power: 印比生扶总力量\n"
        "  - drain_power: 财官杀食伤克泄耗总力量\n"
        "  - day_master_seat: 日主坐旺衰\n"
        "  - 综合判定: support_power < drain_power 且 不得令 且 根气弱 → 身弱\n"
        "\n"
        "在这些Feature建立之前, WOOD_ratio<0.15不能作为'身弱'的充分条件。"
    )


# ============================================================================
# 主函数
# ============================================================================

def main():
    print("=" * 90)
    print("STR-001 Canonical Fidelity Audit")
    print("=" * 90)
    print("\nJudgment: SG-ZP-STR-001 '日主身弱，喜印比生扶'")
    print("Current Condition: WOOD_ratio < 0.15")
    print("审计核心: 两个semantic jump + 循环自证风险")

    # 原典来源
    print(f"\n{'='*90}")
    print("一、原典来源")
    print("=" * 90)
    sources = build_sources()
    for s in sources:
        print(f"\n  《{s.book}》{s.chapter}:")
        print(f"    原文: {s.original_text}")

    # Jump 1
    print(f"\n{'='*90}")
    print("二、Jump 1: WOOD_ratio < 0.15 → 日主身弱?")
    print("=" * 90)
    j1 = audit_jump1()
    print(f"\n  原典对'身弱'的判定标准:")
    for b in j1.canonical_basis:
        print(f"    {b}")
    print(f"\n  Engine当前提供的证据:")
    for e in j1.engine_evidence:
        print(f"    {e}")
    print(f"\n  Gap分析: {j1.gap_analysis}")
    print(f"\n  结论: {j1.conclusion}")

    # Jump 2
    print(f"\n{'='*90}")
    print("三、Jump 2: 日主身弱 → 喜印比生扶?")
    print("=" * 90)
    j2 = audit_jump2()
    print(f"\n  原典对'身弱喜印比'的依据:")
    for b in j2.canonical_basis:
        print(f"    {b}")
    print(f"\n  Engine当前提供的证据:")
    for e in j2.engine_evidence:
        print(f"    {e}")
    print(f"\n  Gap分析: {j2.gap_analysis}")
    print(f"\n  结论: {j2.conclusion}")

    # 当前命例分析
    print(f"\n{'='*90}")
    print("四、当前命例分析 (1983-11-03 午时 男)")
    print("=" * 90)
    case = analyze_current_case()
    for k, v in case.items():
        if isinstance(v, dict):
            print(f"\n  {k}:")
            for k2, v2 in v.items():
                print(f"    {k2}: {v2}")
        else:
            print(f"  {k}: {v}")

    # 循环自证风险
    print(f"\n{'='*90}")
    print("五、循环自证风险")
    print("=" * 90)
    print(f"\n{analyze_circular_reasoning()}")

    # Feature Sufficiency
    print(f"\n{'='*90}")
    print("六、Feature Sufficiency")
    print("=" * 90)
    print(f"\n{analyze_feature_sufficiency()}")

    # 汇总
    print(f"\n{'='*90}")
    print("STR-001 Canonical Fidelity Audit 汇总")
    print("=" * 90)
    print(f"""
  Judgment: SG-ZP-STR-001 '日主身弱，喜印比生扶'
  Current Condition: WOOD_ratio < 0.15

  Jump 1 (WOOD<0.15 → 身弱): INVALID
    - 原典身弱需要月令+根气+生克对比多维度判定
    - WOOD<0.15只覆盖单一维度简单计数
    - 印星(水0.5)生扶力量未被纳入
    - 当前命例不能简单判定身弱

  Jump 2 (身弱 → 喜印比): CONDITIONAL
    - '身弱喜印'有明确原典依据(玄机赋原文)
    - '日干无气遇劫为强'支持比劫帮身
    - 但前提是'身弱'已经被独立证明
    - 当前Jump 1不成立, 所以Jump 2前提不成立

  循环自证风险: HIGH
    - Engine规定WOOD<0.15=身弱 → 拿这个证明Canonical身弱成立
    - 这不是验证, 是自证循环
    - 必须先从Canonical Source定义身弱, 再问Engine是否足以证明

  Feature Sufficiency: INSUFFICIENT
    - WOOD_ratio<0.15不能作为'身弱'的充分条件
    - 需要建立: month_strong/root_strength/support_power/drain_power/day_master_seat
    - 在这些Feature建立前, STR-001不应作为ACTIVE Canonical Judgment

  Recommendation:
    1. STR-001保持CONDITIONAL/HOLD, 不作为ACTIVE Canonical Judgment
    2. 不要用WOOD_ratio定义'身弱'(防止循环自证)
    3. 先从Canonical Source定义'身弱'的判定标准(月令+根气+生克对比)
    4. 建立Engine Feature来度量这些维度
    5. 验证Engine Feature是否足以证明Canonical定义的'身弱'
    6. '喜印比生扶'有原典依据, 但需要先证明身弱才能应用

  Decision: PENDING_AUDIT (供逐项核查, 不自行定义VALID/PARTIAL/RETIRE)

  修正记录(根据用户审计4个必须修正项):
    1. PAT-001 = 月令取格/正财格, 不是'最终用神正财'; PAT-010 = '用神为正财', 二者不是同一个命题
    2. STR-004: simple imbalance ≠ sufficient proof of 偏枯, 完整条件仍需Source Mapping (不把(a)-(e)直接写成最终Canonical Contract)
    3. Feature canonical_equivalence=PARTIAL ≠ Judgment=PARTIAL; STR-004继续HOLD
    4. Feature Equivalence ≠ Judgment Equivalence (正式确立架构原则)
""")
    print("=" * 90)


if __name__ == "__main__":
    main()
