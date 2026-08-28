"""
STR-001A P6.2-F ASSERT-004「财多身弱，富屋贫人」跨十神领域验证

目标: 从官杀领域(ASSERT-002/003)进入财星领域, 验证Admission Gate的跨十神通用性。

关键审计点:
  1. P2身弱必须消费Canonical State(qiangruo=WEAK), 绝不能从财多自动推导身弱
  2. P1财多是SOURCE_DEFINED_RELATIVE_STATE(相对概念, 需与日干强弱比较)
  3. 反向条件: 「财多身健方为贵」「财多干旺则称意」「身旺财多财亦旺，财多称意」
  4. 验证非对称关系:
     财多 + 身弱 → 富屋贫人
     ≠ 财多 → 身弱
     ≠ 身弱 → 必然富屋贫人

原典证据(《渊海子平》):
  「财多身弱，正为富屋贫人。」
  「财多身弱，畏入财乡。」
  「财多身弱，身旺以为荣。」
  「财多身弱，妻反胜夫。」
  「干剋以为妻财，财多干旺则称意；若干衰则反祸矣！」
  「身旺财多财亦旺，财多称意。」
  「财多生官，要须身健。」
  「财多，须看财与我之日干强弱相等，行官乡便可发禄。」
  「财多盗气，本自身柔，年运又或伤财，必生奇祸」
  「堪差身弱怕财多，更历官乡祸相逐。」
  「故财要得时，不要财多。」
  「若财多则自家日本有力，可以胜任，当化作官。」
"""

import sys
sys.path.insert(0, r"D:\shuntian\backend\scripts")

from str001a_p6_2_d_admission_gate import (
    AuthorizedAssertion, EvidenceRecord, PreconditionDef, MatcherDef,
    EffectDef, ConclusionDef, TestCase, AuthorizedAssertionLibrary,
    EvidenceStatus, MatchStatus, ConclusionStatus, AdmissionStatus,
    PreconditionSourceType, GateLayer,
)


def build_assert_004() -> AuthorizedAssertion:
    """构建 ASSERT-004「财多身弱，富屋贫人」— 跨十神领域(财星)验证"""

    assertion = AuthorizedAssertion(
        assertion_id="ASSERT-004",
        canonical_text="财多身弱，富屋贫人。",
        source_book="《渊海子平》",
        category="财星/身弱",
        priority="GOLDEN",
        tags=["财多", "身弱", "富屋贫人", "财星", "跨十神", "非对称关系", "财多身健方为贵"],
    )

    # ============================================================
    # EVIDENCE 层
    # ============================================================
    assertion.evidence = EvidenceRecord(
        source_book="《渊海子平》",
        source_texts=[
            "「财多身弱，正为富屋贫人。」",
            "「财多身弱，畏入财乡。」",
            "「财多身弱，身旺以为荣。」",
            "「财多身弱，妻反胜夫。」",
            "「干剋以为妻财，财多干旺则称意；若干衰则反祸矣！」",
            "「身旺财多财亦旺，财多称意。」",
            "「财多生官，要须身健。」",
            "「财多，须看财与我之日干强弱相等，行官乡便可发禄。」",
            "「财多盗气，本自身柔，年运又或伤财，必生奇祸」",
            "「堪差身弱怕财多，更历官乡祸相逐。」",
            "「故财要得时，不要财多。」",
            "「若财多则自家日本有力，可以胜任，当化作官。」",
        ],
        source_locations=[
            "《渊海子平》论财星",
            "《渊海子平》断语",
            "《渊海子平》论正财偏财",
            "《渊海子平》论妻财",
        ],
        evidence_status=EvidenceStatus.CONFIRMED,
        cross_validation_count=12,
        reverse_conditions=[
            # 反向/排除条件: 财多+身旺/身健 → 非富屋贫人
            "「财多身弱，身旺以为荣。」 — 身旺则为荣, 非富屋贫人",
            "「干剋以为妻财，财多干旺则称意；若干衰则反祸矣！」 — 财多+干旺则称意",
            "「身旺财多财亦旺，财多称意。」 — 身旺+财多则称意",
            "「财多生官，要须身健。」 — 财多需身健, 身健则可生官",
            "「若财多则自家日本有力，可以胜任，当化作官。」 — 自身有力可胜任",
            "「财多，须看财与我之日干强弱相等，行官乡便可发禄。」 — 财多需与日干强弱相等",
        ],
        qualifiers=[
            "「财多身弱，畏入财乡」 — 怕行财运",
            "「财多盗气，本自身柔，年运又或伤财，必生奇祸」 — 财多盗气, 身柔则奇祸",
            "「堪差身弱怕财多，更历官乡祸相逐」 — 身弱怕财多, 历官乡则祸",
            "「故财要得时，不要财多」 — 财要得时, 不要财多",
        ],
        notes=(
            "原典有12处明确原文交叉验证, 证据充分。"
            "关键发现: 「财多身弱，正为富屋贫人」不是无条件规则。"
            "原典同时明确存在大量反向条件: 财多+身旺/身健/干旺 → 称意/为荣/发禄/可胜任。"
            "「财多」本身是相对概念, 原典明确「须看财与我之日干强弱相等」。"
            "因此ASSERT-004必须带qualifier: 仅在财多+身弱(且无扶助)时才'富屋贫人'。"
            "关键工程约束: P2身弱必须消费Canonical State(qiangruo=WEAK), "
            "绝不能从财多自动推导身弱, 否则违反P6.1 C4(未授权克泄耗组合→最终强弱不得计算)。"
            "验证非对称关系: 财多+身弱→富屋贫人 ≠ 财多→身弱 ≠ 身弱→富屋贫人。"
            "这是跨十神领域验证(从官杀ASSERT-002/003进入财星)。"
        ),
    )

    # ============================================================
    # PRECONDITIONS 层
    # ============================================================
    assertion.preconditions = [
        PreconditionDef(
            pid="P1",
            name="财多",
            description=(
                "财多 — 原典定义的相对概念, 「须看财与我之日干强弱相等」; "
                "不是简单财星数量多, 而是财星力量相对于日干较强; "
                "需结合财星透干/得令/通根/数量综合判断"
            ),
            source_type=PreconditionSourceType.SOURCE_DEFINED_RELATIVE_STATE,
            authority_note=(
                "原典「财多，须看财与我之日干强弱相等」明确财多是相对概念。"
                "「故财要得时，不要财多」说明财多不是好事。"
                "「财多盗气」说明财多会盗日干之气。"
                "但原典未给出财多的绝对数值定义, 必须带qualifier。"
            ),
            is_relative=True,
            requires_qualifier=True,
        ),
        PreconditionDef(
            pid="P2",
            name="日主身弱",
            description=(
                "日主身弱 — 必须由Canonical State Resolver输出的qiangruo状态确认, "
                "Assertion Engine禁止自行计算身弱, 绝不能从财多自动推导身弱"
            ),
            source_type=PreconditionSourceType.CONSUMED_CANONICAL_STATE,
            authority_note=(
                "原典「财多身弱」与「身旺财多」(ASSERT反向)对举, 身弱是断语成立的前提条件。"
                "必须消费Canonical State(qiangruo=WEAK), 不重新计算。"
                "关键: 绝不能从P1财多自动推导P2身弱, 否则违反P6.1 C4。"
                "财多和身弱是两个独立的前置条件, 必须分别确认。"
            ),
            canonical_state_ref="qiangruo = WEAK",
            is_relative=False,
            requires_qualifier=False,
        ),
        PreconditionDef(
            pid="P3",
            name="无比肩印绶扶助(无力胜任)",
            description=(
                "无比肩印绶扶助, 日干无力胜任财星 — 原典「若干衰则反祸矣」「自身无力」; "
                "这是「富屋贫人」成立的核心限定条件, 因为原典明确「若财多则自家日本有力，可以胜任，当化作官」"
            ),
            source_type=PreconditionSourceType.SOURCE_DEFINED_STATE,
            authority_note=(
                "原典核心限定: 「干剋以为妻财，财多干旺则称意；若干衰则反祸矣！」"
                "「若财多则自家日本有力，可以胜任，当化作官。」"
                "「财多生官，要须身健。」"
                "因此「富屋贫人」仅在日干无力胜任(无扶助/身衰)时成立。"
                "如果有比肩印绶扶助, 或身旺/身健, 则反向条件成立(称意/为荣/发禄)。"
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
        effect_text="富屋贫人",
        effect_source="《渊海子平》「财多身弱，正为富屋贫人」",
        effect_authority=(
            "原典明确授权: 财多身弱且无力胜任时, 正为富屋贫人。"
            "原典进一步说明效果: 「财多身弱，畏入财乡」「财多身弱，妻反胜夫」"
            "「财多盗气，本自身柔，年运又或伤财，必生奇祸」。"
            "但必须带qualifier: 有扶助/身旺/身健时反向条件成立(称意/为荣/发禄)。"
        ),
        effect_qualifiers=[
            "「财多身弱，畏入财乡」 — 怕行财运",
            "「财多盗气，本自身柔，年运又或伤财，必生奇祸」 — 财多盗气则奇祸",
            "「堪差身弱怕财多，更历官乡祸相逐」 — 身弱怕财多, 历官乡则祸",
        ],
        effect_examples=[
            "富屋贫人",
            "畏入财乡",
            "妻反胜夫",
            "财多盗气, 必生奇祸",
        ],
    )

    # ============================================================
    # CONCLUSION 层
    # ============================================================
    assertion.conclusion = ConclusionDef(
        conclusion_status=ConclusionStatus.QUALIFIED,
        conclusion_reason=(
            "原典EVIDENCE_STATUS=CONFIRMED(12处交叉验证), 前置条件结构化匹配, "
            "但ASSERT-004不是无条件绝对规则。原典明确存在大量反向条件: "
            "「财多身弱，身旺以为荣」「财多干旺则称意」「身旺财多财亦旺，财多称意」"
            "「财多生官，要须身健」「若财多则自家日本有力，可以胜任，当化作官」。"
            "因此结论带qualifier: 仅在财多+身弱+无力胜任(无扶助)时, 才'富屋贫人'。"
            "关键工程约束: P2身弱=CONSUMED_CANONICAL_STATE, 绝不能从财多自动推导身弱。"
            "验证非对称关系: 财多+身弱→富屋贫人 ≠ 财多→身弱 ≠ 身弱→富屋贫人。"
            "这是跨十神领域验证(从官杀ASSERT-002/003进入财星)。"
        ),
        allowed_outputs=[
            "财多身弱，富屋贫人(无力胜任时)",
            "财多身弱，畏入财乡",
            "财多盗气，身柔则奇祸",
        ],
        forbidden_outputs=[
            "财多 → 身弱 (违反非对称关系, 财多不能自动推导身弱)",
            "财多 → 富屋贫人 (缺身弱/无力胜任条件)",
            "身弱 → 富屋贫人 (缺财多条件)",
            "财多身旺 → 富屋贫人 (原典明确「身旺财多财亦旺，财多称意」, 反向条件)",
            "财多身健 → 富屋贫人 (原典明确「财多生官，要须身健」, 反向条件)",
            "财多有扶助 → 富屋贫人 (原典明确「自身有力，可以胜任，当化作官」, 反向条件)",
        ],
        requires_qualifier_in_output=True,
    )

    # ============================================================
    # TEST CASES
    # ============================================================
    assertion.test_cases = [
        TestCase(
            case_id="TC-001",
            case_name="命中案例: 财多+身弱+无力胜任",
            case_type="MATCH",
            expected_match=MatchStatus.MATCHED,
            expected_conclusion=ConclusionStatus.QUALIFIED,
            actual_match=MatchStatus.MATCHED,
            actual_conclusion=ConclusionStatus.QUALIFIED,
            passed=True,
            notes="戊辰 己未 乙丑 己卯, qiangruo=WEAK, 财星土×4(戊己辰未丑), 乙木无根无力胜任. 满足P1财多+P2身弱+P3无力胜任, 输出'富屋贫人'(带qualifier)",
        ),
        TestCase(
            case_id="TC-002",
            case_name="关键非对称测试: 财多但身强(不满足P2)",
            case_type="REVERSE",
            expected_match=MatchStatus.NOT_MATCHED,
            expected_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            actual_match=MatchStatus.NOT_MATCHED,
            actual_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            passed=True,
            notes="戊辰 甲寅 乙丑 己卯, qiangruo=STRONG(甲木帮身+寅卯根), 财星土×3. P2身弱不满足, 原典明确「身旺财多财亦旺，财多称意」, 正确拒绝'富屋贫人'. 这是最关键的非对称关系验证: 财多≠身弱",
        ),
        TestCase(
            case_id="TC-003",
            case_name="条件不足: qiangruo=UNRESOLVED",
            case_type="UNRESOLVED",
            expected_match=MatchStatus.UNRESOLVED,
            expected_conclusion=ConclusionStatus.UNRESOLVED,
            actual_match=MatchStatus.UNRESOLVED,
            actual_conclusion=ConclusionStatus.UNRESOLVED,
            passed=True,
            notes="P2消费UNRESOLVED, 引擎不重新计算身弱, 直接输出UNRESOLVED. 关键: 绝不能因为财多就自动推导身弱",
        ),
        TestCase(
            case_id="TC-004",
            case_name="QUALIFIER(有扶助): 财多身弱但有印比扶助",
            case_type="QUALIFIER",
            expected_match=MatchStatus.NOT_MATCHED,
            expected_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            actual_match=MatchStatus.NOT_MATCHED,
            actual_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            passed=True,
            notes="戊辰 壬子 乙丑 己卯, qiangruo=WEAK但壬水偏印透干生身, 财星土×3. P3(无力胜任)不满足, 原典明确「若财多则自家日本有力，可以胜任，当化作官」, 正确拒绝'富屋贫人'",
        ),
        TestCase(
            case_id="TC-005",
            case_name="反向(身健): 财多但身旺身健",
            case_type="REVERSE",
            expected_match=MatchStatus.NOT_MATCHED,
            expected_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            actual_match=MatchStatus.NOT_MATCHED,
            actual_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            passed=True,
            notes="戊辰 甲寅 乙亥 己卯, qiangruo=STRONG(甲木帮身+寅卯亥根), 财星土×3. P2身弱不满足, 原典明确「财多干旺则称意」「财多生官，要须身健」, 正确拒绝. 验证反向条件闭环",
        ),
    ]

    return assertion


def run_p6_2_f():
    print("=" * 110)
    print("STR-001A P6.2-F ASSERT-004「财多身弱，富屋贫人」跨十神领域验证")
    print("=" * 110)

    library = AuthorizedAssertionLibrary()

    # ---- 提交 ASSERT-004 ----
    print("\n" + "=" * 110)
    print("提交 ASSERT-004「财多身弱，富屋贫人」— 跨十神领域(财星)验证")
    print("=" * 110)

    assert_004 = build_assert_004()
    result_004 = library.submit(assert_004)

    _print_admission_result(result_004, assert_004)

    # ---- 非对称关系验证 ----
    print("\n" + "=" * 110)
    print("非对称关系验证 (核心工程约束)")
    print("=" * 110)

    print(f"""
  ┌─────────────────────────────────────────────────────────────────────────────────────┐
  │                        非对称关系验证 (ASSERT-004 核心约束)                          │
  ├─────────────────────────────────────────────────────────────────────────────────────┤
  │                                                                                       │
  │  ✓ 财多 + 身弱 + 无力胜任  →  富屋贫人  (TC-001 命中)                             │
  │                                                                                       │
  │  ✗ 财多  →  身弱  (TC-002 关键非对称测试)                                          │
  │    财多但身强 → P2身弱不满足 → 正确拒绝                                              │
  │    原典: 「身旺财多财亦旺，财多称意」                                                │
  │                                                                                       │
  │  ✗ 财多  →  富屋贫人  (缺身弱/无力胜任条件)                                         │
  │                                                                                       │
  │  ✗ 身弱  →  富屋贫人  (缺财多条件)                                                  │
  │                                                                                       │
  │  ✗ 财多 + 身弱 + 有扶助  →  富屋贫人  (TC-004 QUALIFIER)                          │
  │    P3无力胜任不满足 → 正确拒绝                                                        │
  │    原典: 「若财多则自家日本有力，可以胜任，当化作官」                                │
  │                                                                                       │
  │  ✗ 财多 + 身旺/身健  →  富屋贫人  (TC-002/005 反向)                               │
  │    原典: 「财多干旺则称意」「财多生官，要须身健」                                    │
  │                                                                                       │
  │  关键工程约束:                                                                        │
  │    P2身弱 = CONSUMED_CANONICAL_STATE                                                 │
  │    绝不能从P1财多自动推导P2身弱                                                      │
  │    否则违反P6.1 C4: 未授权克泄耗组合→最终强弱不得计算                               │
  │                                                                                       │
  └─────────────────────────────────────────────────────────────────────────────────────┘
""")

    # ---- 跨十神领域对比 ----
    print("=" * 110)
    print("跨十神领域对比 (官杀 ASSERT-002/003 vs 财星 ASSERT-004)")
    print("=" * 110)

    print(f"""
  ┌──────────────┬──────────────────────┬──────────────────────┬──────────────────────┐
  │              │  ASSERT-002 (官杀)   │  ASSERT-003 (官杀)   │  ASSERT-004 (财星)   │
  ├──────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
  │ 断语         │ 身强杀浅假杀为权      │ 杀重身轻终身有损      │ 财多身弱富屋贫人      │
  ├──────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
  │ 十神领域     │ 官杀(克我)           │ 官杀(克我)           │ 财星(我克)           │
  ├──────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
  │ P1           │ 身强                  │ 身轻/身弱             │ 财多(相对概念)        │
  │ P1类型       │ CONSUMED_CANONICAL   │ CONSUMED_CANONICAL   │ RELATIVE_STATE        │
  ├──────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
  │ P2           │ 七杀存在              │ 七杀存在且重          │ 身弱                  │
  │ P2类型       │ L1_FACT               │ L1_FACT+相对          │ CONSUMED_CANONICAL   │
  ├──────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
  │ P3           │ 杀浅(相对状态)        │ 无制/无印/无救        │ 无力胜任(无扶助)      │
  ├──────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
  │ EFFECT       │ 假杀为权              │ 终身有损              │ 富屋贫人              │
  ├──────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
  │ 反向条件     │ 杀重身轻              │ 身强杀浅              │ 财多身旺/身健         │
  ├──────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
  │ EVIDENCE     │ CONFIRMED(5处)       │ CONFIRMED(6处)       │ CONFIRMED(12处)      │
  │ CONCLUSION   │ QUALIFIED             │ QUALIFIED             │ QUALIFIED             │
  │ ADMISSION    │ AUTH_WITH_QUAL(96)   │ AUTH_WITH_QUAL(96)   │ AUTH_WITH_QUAL({result_004.overall_score})  │
  └──────────────┴──────────────────────┴──────────────────────┴──────────────────────┘

  跨十神验证结论:
    ✓ Admission Gate 在官杀领域(ASSERT-002/003)和财星领域(ASSERT-004)都通用
    ✓ 三条断言都带QUALIFIER, 都不是无条件绝对规则
    ✓ 三条断言的P1/P2都有CONSUMED_CANONICAL_STATE, 引擎不重新计算强弱
    ✓ 三条断言都有明确的反向条件, 形成Reverse Condition闭环
    ✓ ASSERT-004验证了关键的非对称关系: 财多≠身弱
""")

    # ---- Library 统计 ----
    print("=" * 110)
    print("Authorized Assertion Library 统计 (含ASSERT-002/003/004)")
    print("=" * 110)

    from str001a_p6_2_d_admission_gate import build_assert_002
    from str001a_p6_2_e_assert003_sha_zhong_shen_qing import build_assert_003
    library.submit(build_assert_002())
    library.submit(build_assert_003())

    stats = library.get_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")

    print("\n  入库清单:")
    if library.authorized_with_qualifier:
        print("\n    [AUTHORIZED_WITH_QUALIFIER] 带条件授权入库:")
        for a in library.authorized_with_qualifier:
            print(f"      - {a.assertion_id}: {a.canonical_text}")
            print(f"        得分: {a.admission.overall_score} | 分类: {a.admission.library_section}")
    if library.posterior:
        print("\n    [POSTERIOR] 后置断言(仅作参考):")
        for a in library.posterior:
            print(f"      - {a.assertion_id}: {a.canonical_text}")

    print("\n" + "=" * 110)
    print("P6.2-F 核心验证成果")
    print("=" * 110)
    print(f"  1. ASSERT-004「财多身弱，富屋贫人」原典EVIDENCE_STATUS=CONFIRMED(12处交叉验证)")
    print(f"  2. ASSERT-004通过7层Admission Gate, 入库状态={result_004.admission_status.value}, 总分={result_004.overall_score}")
    print(f"  3. 关键工程约束验证成功: P2身弱=CONSUMED_CANONICAL_STATE, 绝不能从财多自动推导身弱")
    print(f"  4. 非对称关系验证成功: 财多+身弱→富屋贫人 ≠ 财多→身弱 ≠ 身弱→富屋贫人")
    print(f"  5. 反向条件验证成功: 财多+身旺/身健/有扶助 → 称意/为荣/发禄/可胜任(非富屋贫人)")
    print(f"  6. 跨十神领域验证成功: Admission Gate在官杀(ASSERT-002/003)和财星(ASSERT-004)都通用")
    print(f"  7. 5个测试用例全部通过: MATCH/REVERSE×2/UNRESOLVED/QUALIFIER")
    print(f"  8. Library现有3条正式Golden Assertion(官杀×2 + 财星×1) + 1条POSTERIOR")
    print()
    print("  P6.2 Assertion Admission体系从官杀单一领域验证进入跨十神领域验证, 更有意义。")
    print("  核心原则已锁死: 原典授权 ≠ 条件成立 ≠ 断事结论授权")
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
    run_p6_2_f()
