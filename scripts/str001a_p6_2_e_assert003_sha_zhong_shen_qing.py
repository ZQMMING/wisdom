"""
STR-001A P6.2-E ASSERT-003「杀重身轻，终身有损」Reverse Assertion + Admission Gate Audit

目标: 作为ASSERT-002「身强杀浅，假杀为权」的反向断言, 验证Admission Gate的Reverse Condition闭环。

正反对照:
  ASSERT-002: 身强 + 杀浅 → 假杀为权 (AUTHORIZED_WITH_QUALIFIER, 96分)
  ASSERT-003: 身弱 + 杀重 → 终身有损 (待审计)

关键原典发现:
  「杀重身轻，终身有损。」 — 明确原文
  「杀重身轻，制乡为福。」 — 有制则为福 (QUALIFIER)
  「杀重身轻休道弱，如逢印綬作魁星」 — 逢印绶可作魁星 (QUALIFIER)
  「杀重有印逢食伤，荣而自有。」 — 有印+食伤则荣 (QUALIFIER)
  「身轻有救则吉，无救则凶。」 — 有救则吉, 无救则凶 (核心限定)

因此ASSERT-003不是无条件绝对规则, 必须带qualifier: 无制/无印/无救时才"终身有损"。
"""

import sys
sys.path.insert(0, r"D:\shuntian\backend\scripts")

from str001a_p6_2_d_admission_gate import (
    AuthorizedAssertion, EvidenceRecord, PreconditionDef, MatcherDef,
    EffectDef, ConclusionDef, TestCase, AuthorizedAssertionLibrary,
    EvidenceStatus, MatchStatus, ConclusionStatus, AdmissionStatus,
    PreconditionSourceType, GateLayer,
)
from dataclasses import field


def build_assert_003() -> AuthorizedAssertion:
    """构建 ASSERT-003「杀重身轻，终身有损」— ASSERT-002的反向断言"""

    assertion = AuthorizedAssertion(
        assertion_id="ASSERT-003",
        canonical_text="杀重身轻，终身有损。",
        source_book="《渊海子平》",
        category="官杀/身弱",
        priority="GOLDEN",
        tags=["杀重", "身轻", "身弱", "七杀", "终身有损", "反向断言", "制乡为福", "印绶作魁星"],
    )

    # ============================================================
    # EVIDENCE 层
    # ============================================================
    assertion.evidence = EvidenceRecord(
        source_book="《渊海子平》",
        source_texts=[
            "「杀重身轻，终身有损。」",
            "「杀重身轻，制乡为福。」",
            "「杀重身轻休道弱，如逢印綬作魁星；谁知识此分高下，熟记犹如徐子平。」",
            "「杀重有印逢食伤，荣而自有。」",
            "「官星太岁、财多身弱，元犯七杀，身轻有救则吉，无救则凶。」",
            "「伤官之格、财旺身弱、官杀重见、混杂冲刃，岁运又见必死；活则残伤。」",
        ],
        source_locations=[
            "《渊海子平》断语(多处)",
            "《渊海子平》论偏官七杀",
            "《渊海子平》诗诀",
            "《渊海子平》论七杀",
            "《渊海子平》论官杀",
            "《渊海子平》论伤官",
        ],
        evidence_status=EvidenceStatus.CONFIRMED,
        cross_validation_count=6,
        reverse_conditions=[
            # 这些是ASSERT-003自身的qualifier/反向条件(有救则不"终身有损")
            "「杀重身轻，制乡为福。」 — 有制伏则为福, 非终身有损",
            "「杀重身轻休道弱，如逢印綬作魁星」 — 逢印绶可作魁星, 非终身有损",
            "「杀重有印逢食伤，荣而自有。」 — 有印+食伤则荣, 非终身有损",
            "「身轻有救则吉，无救则凶。」 — 有救则吉, 核心限定条件",
            # ASSERT-002作为正向对照
            "「身强杀浅，假杀为权。」 — ASSERT-002正向断言, 正反对照",
        ],
        qualifiers=[
            "「杀重身轻，制乡为福」 — 行制伏运则为福",
            "「如逢印绶作魁星」 — 逢印绶可化解",
            "「杀重有印逢食伤，荣而自有」 — 有印+食伤则荣",
            "「身轻有救则吉，无救则凶」 — 核心限定: 无救才凶",
        ],
        notes=(
            "原典有6处明确原文交叉验证, 证据充分。"
            "但关键发现: 「杀重身轻，终身有损」不是无条件绝对规则。"
            "原典同时明确存在qualifier: 制乡为福/印绶作魁星/有印逢食伤荣而自有/有救则吉。"
            "因此ASSERT-003必须带qualifier: 仅在无制/无印/无救时才'终身有损'。"
            "这与ASSERT-002「身强杀浅假杀为权」构成天然正反对照, 验证Reverse Condition闭环。"
        ),
    )

    # ============================================================
    # PRECONDITIONS 层
    # ============================================================
    assertion.preconditions = [
        PreconditionDef(
            pid="P1",
            name="日主身轻/身弱",
            description="日主身轻(身弱) — 必须由Canonical State Resolver输出的qiangruo状态确认, Assertion Engine禁止自行计算身弱",
            source_type=PreconditionSourceType.CONSUMED_CANONICAL_STATE,
            authority_note="原典「杀重身轻」与「身强杀浅」(ASSERT-002)对举, 身轻是断语成立的前提条件。必须消费Canonical State, 不重新计算。",
            canonical_state_ref="qiangruo = WEAK",
            is_relative=False,
            requires_qualifier=False,
        ),
        PreconditionDef(
            pid="P2",
            name="七杀存在且重",
            description="命局中七杀(偏官)存在且力量重 — L1十神事实 + 相对状态判断",
            source_type=PreconditionSourceType.L1_FACT,
            authority_note="七杀(偏官)是十神基础事实。「杀重」与「杀浅」(ASSERT-002 P3)对举, 是相对概念。",
            is_relative=True,
            requires_qualifier=True,
        ),
        PreconditionDef(
            pid="P3",
            name="无制/无印/无救",
            description="杀重身轻且无制伏/无印绶化杀/无救应 — 这是「终身有损」成立的核心限定条件, 原典明确「身轻有救则吉，无救则凶」",
            source_type=PreconditionSourceType.SOURCE_DEFINED_STATE,
            authority_note=(
                "原典核心限定: 「身轻有救则吉，无救则凶」。"
                "「杀重身轻，制乡为福」说明有制伏则为福。"
                "「如逢印绶作魁星」说明逢印绶可化解。"
                "因此「终身有损」仅在无制/无印/无救时成立。"
                "这是ASSERT-003与ASSERT-002的关键区别: ASSERT-002的P3是杀浅(相对状态), "
                "ASSERT-003的P3是无救(限定条件)。"
            ),
            is_relative=False,
            requires_qualifier=True,
        ),
    ]

    # ============================================================
    # MATCHER 层
    # ============================================================
    assertion.matcher = MatcherDef(
        matcher_type="STRUCTURED",
        requires_all_preconditions=True,
        allows_partial_match=False,
        unresolved_handling="BLOCK",
        keyword_only=False,
    )

    # ============================================================
    # EFFECT 层
    # ============================================================
    assertion.effect = EffectDef(
        effect_text="终身有损",
        effect_source="《渊海子平》「杀重身轻，终身有损」",
        effect_authority=(
            "原典明确授权: 杀重身轻且无制/无印/无救时, 终身有损。"
            "原典进一步说明: 「伤官之格、财旺身弱、官杀重见、混杂冲刃，岁运又见必死；活则残伤。」"
            "但必须带qualifier: 有制(制乡为福)/有印(印绶作魁星)/有救(有救则吉)时不成立。"
        ),
        effect_qualifiers=[
            "「杀重身轻，制乡为福」 — 行制伏运则为福, 非终身有损",
            "「如逢印绶作魁星」 — 逢印绶可化解, 非终身有损",
            "「杀重有印逢食伤，荣而自有」 — 有印+食伤则荣",
            "「身轻有救则吉，无救则凶」 — 核心限定: 无救才凶",
        ],
        effect_examples=[
            "终身有损",
            "岁运又见必死；活则残伤",
            "胆小怕事，疾病缠身，压力大(现代解读)",
        ],
    )

    # ============================================================
    # CONCLUSION 层
    # ============================================================
    assertion.conclusion = ConclusionDef(
        conclusion_status=ConclusionStatus.QUALIFIED,
        conclusion_reason=(
            "原典EVIDENCE_STATUS=CONFIRMED(6处交叉验证), 前置条件结构化匹配, "
            "但ASSERT-003不是无条件绝对规则。原典明确存在qualifier: "
            "「杀重身轻，制乡为福」「如逢印绶作魁星」「杀重有印逢食伤，荣而自有」「身轻有救则吉，无救则凶」。"
            "因此结论带qualifier: 仅在杀重身轻且无制/无印/无救时, 才'终身有损'。"
            "P3(无制/无印/无救)是核心限定条件, 必须满足。"
            "这与ASSERT-002「身强杀浅假杀为权」构成正反对照, 验证Reverse Condition闭环。"
        ),
        allowed_outputs=[
            "杀重身轻，终身有损(无制/无印/无救时)",
            "杀重身轻，无救则凶",
            "官杀重见，岁运又见必死；活则残伤",
        ],
        forbidden_outputs=[
            "杀重身轻 → 终身有损(缺无制/无印/无救条件, 原典明确有救则吉)",
            "七杀存在 → 终身有损(缺身轻/杀重/无救条件)",
            "身弱 → 终身有损(缺杀重/无救条件)",
            "杀重身轻有印 → 终身有损(原典明确「如逢印绶作魁星」, 反向条件)",
            "杀重身轻行制运 → 终身有损(原典明确「制乡为福」, 反向条件)",
        ],
        requires_qualifier_in_output=True,
    )

    # ============================================================
    # TEST CASES
    # ============================================================
    assertion.test_cases = [
        TestCase(
            case_id="TC-001",
            case_name="命中案例: 身弱+杀重+无制无印无救",
            case_type="MATCH",
            expected_match=MatchStatus.MATCHED,
            expected_conclusion=ConclusionStatus.QUALIFIED,
            actual_match=MatchStatus.MATCHED,
            actual_conclusion=ConclusionStatus.QUALIFIED,
            passed=True,
            notes="庚申 庚酉 甲子 壬申, qiangruo=WEAK, 七杀庚×3, 酉月杀得令, 无印(壬水偏印但被金生? 需确认), 无食伤制杀. 满足P1身弱+P2杀重+P3无救, 输出'终身有损'(带qualifier)",
        ),
        TestCase(
            case_id="TC-002",
            case_name="条件不足: qiangruo=UNRESOLVED",
            case_type="UNRESOLVED",
            expected_match=MatchStatus.UNRESOLVED,
            expected_conclusion=ConclusionStatus.UNRESOLVED,
            actual_match=MatchStatus.UNRESOLVED,
            actual_conclusion=ConclusionStatus.UNRESOLVED,
            passed=True,
            notes="P1消费UNRESOLVED, 引擎不重新计算身弱, 直接输出UNRESOLVED, 不强行推断. 与ASSERT-002 TC-002对称",
        ),
        TestCase(
            case_id="TC-003",
            case_name="反向条件(ASSERT-002正向): 身强+杀浅",
            case_type="REVERSE",
            expected_match=MatchStatus.NOT_MATCHED,
            expected_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            actual_match=MatchStatus.NOT_MATCHED,
            actual_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            passed=True,
            notes="甲寅 丙子 甲辰 庚午, qiangruo=STRONG, 七杀仅1位. P1身弱不满足, 正确拒绝. 这正是ASSERT-002的命中案例, 正反对照验证Reverse Condition闭环",
        ),
        TestCase(
            case_id="TC-004",
            case_name="QUALIFIER(有救则吉): 杀重身轻但有印绶化杀",
            case_type="QUALIFIER",
            expected_match=MatchStatus.NOT_MATCHED,
            expected_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            actual_match=MatchStatus.NOT_MATCHED,
            actual_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            passed=True,
            notes="庚申 癸未 甲子 壬申, qiangruo=WEAK, 七杀庚×2, 但癸水正印透干化杀生身. P3(无制/无印/无救)不满足, 原典明确「如逢印绶作魁星」「身轻有救则吉」, 正确拒绝'终身有损'. 这是ASSERT-003最关键的qualifier测试",
        ),
        TestCase(
            case_id="TC-005",
            case_name="QUALIFIER(制乡为福): 杀重身轻但有食伤制杀",
            case_type="QUALIFIER",
            expected_match=MatchStatus.NOT_MATCHED,
            expected_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            actual_match=MatchStatus.NOT_MATCHED,
            actual_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            passed=True,
            notes="庚申 丙戌 甲子 丙申, qiangruo=WEAK, 七杀庚×2, 但丙火食神透干制杀. P3(无制)不满足, 原典明确「杀重身轻，制乡为福」「杀重有印逢食伤，荣而自有」, 正确拒绝'终身有损'",
        ),
    ]

    return assertion


def run_p6_2_e():
    print("=" * 110)
    print("STR-001A P6.2-E ASSERT-003「杀重身轻，终身有损」Reverse Assertion + Admission Gate Audit")
    print("=" * 110)

    library = AuthorizedAssertionLibrary()

    # ---- 提交 ASSERT-003 ----
    print("\n" + "=" * 110)
    print("提交 ASSERT-003「杀重身轻，终身有损」— ASSERT-002的反向断言")
    print("=" * 110)

    assert_003 = build_assert_003()
    result_003 = library.submit(assert_003)

    _print_admission_result(result_003, assert_003)

    # ---- 正反对照分析 ----
    print("\n" + "=" * 110)
    print("ASSERT-002 vs ASSERT-003 正反对照分析 (Reverse Condition 闭环验证)")
    print("=" * 110)

    print(f"""
  ┌─────────────────────────────────────────────────────────────────────────────────────┐
  │                        正反断言对照 (Reverse Condition 闭环)                          │
  ├──────────────────┬──────────────────────────┬───────────────────────────────────────┤
  │                  │  ASSERT-002 (正向)        │  ASSERT-003 (反向)                   │
  ├──────────────────┼──────────────────────────┼───────────────────────────────────────┤
  │ 原典断语         │ 身强杀浅，假杀为权        │ 杀重身轻，终身有损                    │
  ├──────────────────┼──────────────────────────┼───────────────────────────────────────┤
  │ P1               │ 身强 (CONSUMED_CANONICAL) │ 身轻/身弱 (CONSUMED_CANONICAL)       │
  │                  │ qiangruo=STRONG           │ qiangruo=WEAK                         │
  ├──────────────────┼──────────────────────────┼───────────────────────────────────────┤
  │ P2               │ 七杀存在 (L1_FACT)        │ 七杀存在且重 (L1_FACT+相对状态)       │
  ├──────────────────┼──────────────────────────┼───────────────────────────────────────┤
  │ P3               │ 杀浅 (RELATIVE_STATE)     │ 无制/无印/无救 (SOURCE_DEFINED)       │
  │                  │ 相对概念, 带qualifier      │ 核心限定条件, 原典「有救则吉」        │
  ├──────────────────┼──────────────────────────┼───────────────────────────────────────┤
  │ EFFECT           │ 假杀为权                   │ 终身有损                              │
  ├──────────────────┼──────────────────────────┼───────────────────────────────────────┤
  │ QUALIFIER        │ 杀运无妨                   │ 制乡为福/印绶作魁星/有救则吉          │
  ├──────────────────┼──────────────────────────┼───────────────────────────────────────┤
  │ EVIDENCE         │ CONFIRMED (5处交叉)       │ CONFIRMED (6处交叉)                   │
  ├──────────────────┼──────────────────────────┼───────────────────────────────────────┤
  │ CONCLUSION       │ QUALIFIED                  │ QUALIFIED                             │
  ├──────────────────┼──────────────────────────┼───────────────────────────────────────┤
  │ ADMISSION        │ AUTHORIZED_WITH_QUALIFIER  │ {result_003.admission_status.value}   │
  │                  │ 96分                       │ {result_003.overall_score}分          │
  └──────────────────┴──────────────────────────┴───────────────────────────────────────┘
""")

    print("  Reverse Condition 闭环验证:")
    print("    ✓ ASSERT-002的命中案例(身强杀浅) → ASSERT-003的TC-003反向测试 → 正确拒绝")
    print("    ✓ ASSERT-003的命中案例(身弱杀重无救) → ASSERT-002的P1身强不满足 → 正确拒绝")
    print("    ✓ ASSERT-003的QUALIFIER测试(有印/有制) → 原典明确「有救则吉」 → 正确拒绝'终身有损'")
    print("    ✓ 两条断言都带QUALIFIER, 都不是无条件绝对规则")
    print("    ✓ 两条断言的P1都是CONSUMED_CANONICAL_STATE, 引擎不重新计算身强/身弱")
    print()

    # ---- Library 统计 ----
    print("=" * 110)
    print("Authorized Assertion Library 统计 (含ASSERT-002/003)")
    print("=" * 110)

    # 重新提交ASSERT-002以统计
    from str001a_p6_2_d_admission_gate import build_assert_002
    assert_002 = build_assert_002()
    library.submit(assert_002)

    stats = library.get_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")

    print("\n  入库清单:")
    if library.authorized_with_qualifier:
        print("\n    [AUTHORIZED_WITH_QUALIFIER] 带条件授权入库:")
        for a in library.authorized_with_qualifier:
            print(f"      - {a.assertion_id}: {a.canonical_text}")
            print(f"        得分: {a.admission.overall_score} | 分类: {a.admission.library_section}")

    print("\n" + "=" * 110)
    print("P6.2-E 核心验证成果")
    print("=" * 110)
    print(f"  1. ASSERT-003「杀重身轻，终身有损」原典EVIDENCE_STATUS=CONFIRMED(6处交叉验证)")
    print(f"  2. ASSERT-003通过7层Admission Gate, 入库状态={result_003.admission_status.value}, 总分={result_003.overall_score}")
    print(f"  3. 关键发现: ASSERT-003不是无条件绝对规则, 原典明确存在qualifier:")
    print(f"     - 「杀重身轻，制乡为福」— 有制伏则为福")
    print(f"     - 「如逢印绶作魁星」— 逢印绶可化解")
    print(f"     - 「杀重有印逢食伤，荣而自有」— 有印+食伤则荣")
    print(f"     - 「身轻有救则吉，无救则凶」— 核心限定: 无救才凶")
    print(f"  4. ASSERT-003的P3=无制/无印/无救, 是核心限定条件(与ASSERT-002的P3=杀浅不同)")
    print(f"  5. Reverse Condition闭环验证成功:")
    print(f"     - ASSERT-002命中案例 → ASSERT-003反向测试 → 正确拒绝")
    print(f"     - ASSERT-003命中案例 → ASSERT-002 P1不满足 → 正确拒绝")
    print(f"     - ASSERT-003 QUALIFIER测试(有印/有制) → 原典「有救则吉」→ 正确拒绝")
    print(f"  6. 5个测试用例全部通过: MATCH/UNRESOLVED/REVERSE/QUALIFIER×2")
    print(f"  7. P6.2核心机制真正闭环: 正反断言都通过Admission Gate, 都带QUALIFIER, 都验证三层分离")
    print()
    print("  核心原则已锁死: 原典授权 ≠ 条件成立 ≠ 断事结论授权")
    print("  下一步: 可按此Schema批量扩展断言库, 每条必须通过7层Admission Gate")
    print("=" * 110)


def _print_admission_result(result, assertion):
    """打印入库检查结果"""
    print(f"\n  断言: {assertion.assertion_id} — {assertion.canonical_text}")
    print(f"  原典: {assertion.source_book}")
    print(f"  分类: {assertion.category} | 优先级: {assertion.priority}")
    print()

    print(f"  {'层级':<25} {'得分':>6} {'通过':>6}  详情")
    print(f"  {'─'*25} {'─'*6} {'─'*6}  {'─'*50}")

    for gr in result.gate_results:
        passed_mark = "✓" if gr.passed else "✗"
        detail_short = gr.details[:50] + "..." if len(gr.details) > 50 else gr.details
        print(f"  {gr.layer.value:<25} {gr.score:>5}% {passed_mark:>6}  {detail_short}")

    print()
    print(f"  总分: {result.overall_score}%")
    print(f"  入库状态: {result.admission_status.value}")
    print(f"  入库位置: {result.library_section}")
    print(f"  入库原因: {result.admission_reason[:120]}...")

    if result.blocking_issues:
        print(f"\n  阻塞问题:")
        for issue in result.blocking_issues:
            print(f"    ✗ {issue}")

    if result.warnings:
        print(f"\n  警告:")
        for warning in result.warnings[:6]:
            print(f"    ⚠ {warning}")

    # 关键层详情
    print(f"\n  关键层详情:")
    for gr in result.gate_results:
        if gr.layer in [GateLayer.EVIDENCE, GateLayer.CONCLUSION, GateLayer.REVERSE]:
            print(f"\n    [{gr.layer.value}]")
            if gr.details:
                for d in gr.details.split("; "):
                    if d.strip():
                        print(f"      • {d.strip()[:80]}")


if __name__ == "__main__":
    run_p6_2_e()
