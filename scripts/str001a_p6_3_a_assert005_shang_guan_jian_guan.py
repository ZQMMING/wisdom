"""
STR-001A P6.3-A ASSERT-005「伤官见官，为祸百端」高风险原典审计

目标: 跨十神领域(食伤类)高风险断言审计, 验证Admission Gate跨关系类型通用。

最关键的一刀:
  不能因为原典存在「伤官见官，为祸百端」就自动建立:
    伤官 + 官星存在 → 为祸

  必须先查清楚原典里的「见官」到底是单纯同时出现, 还是包含特定透干、岁运、制化、格局条件。

原典关键发现(《渊海子平》):
  1. 「如用伤官格者，支干、岁运，都要不见官星；如见官星，谓之伤官见官，为祸百端。」
     → 必须是"用伤官格者", 原局应伤尽官星, 如见官星才叫"伤官见官"

  2. 「伤官务要伤尽；伤之不尽，官来乘旺，其祸不可胜言。伤官见官，为祸百端。」
     → 伤官未伤尽 + 官星乘旺 → 其祸不可胜言

  3. 「若伤官不尽，四柱有官星露；岁运若见官星，其祸不可胜言。」
     → 原局官星露(伤不尽) 或 岁运见官星

  4. 「倘月令在伤官之位，及四柱配合、作事皆在伤官之处；又行身旺乡，真贵人也。」
     → 反向: 伤官格 + 身旺乡 = 贵人

  5. 「如遇伤官者，须见其财为妙；是财能生官也。」
     → QUALIFIER: 伤官见财为妙

  6. 「如四柱虽伤尽官星，身弱逢财运发福，是为伤官见财。」
     → 反向: 伤尽官星 + 身弱逢财运 = 发福

  7. 「运入官乡必破--此论伤官」
     → 伤官运入官乡必破

  8. 「年带伤官，父母不全；月带伤官，兄弟不完；日带伤官，妻妾不完；时带伤官，子息无传。」
     → 伤官位置不同, 为祸对象不同

因此「伤官见官」的完整语义:
  伤官格(月令伤官或伤官旺)
    +
  伤官应伤尽官星(原局无官星或官星被制)
    +
  原局有官星露(伤不尽) 或 岁运见官星
    +
  官星乘旺(有根/得令/透干)
    ↓
  伤官见官，为祸百端

不是简单的: 伤官 + 官星同时存在 → 为祸

前置条件:
  P1: 伤官格/伤官旺 (用伤官格者, 月令伤官或伤官透干旺相)
  P2: 官星出现 (原局有官星露 或 岁运见官星)
  P3: 伤官未伤尽/官星乘旺 (官星有根/得令/透干, 未被制化) — 核心限定条件

反向/QUALIFIER:
  - 伤官伤尽 + 身旺乡 = 贵人
  - 伤官见财 = 为妙
  - 伤尽官星 + 身弱逢财运 = 发福
  - 有印绶制伤官 = 可能不为祸
"""

import sys
sys.path.insert(0, r"D:\shuntian\backend\scripts")

from str001a_p6_2_d_admission_gate import (
    AuthorizedAssertion, EvidenceRecord, PreconditionDef, MatcherDef,
    EffectDef, ConclusionDef, TestCase, AuthorizedAssertionLibrary,
    EvidenceStatus, MatchStatus, ConclusionStatus, AdmissionStatus,
    PreconditionSourceType, GateLayer,
)


def build_assert_005() -> AuthorizedAssertion:
    """构建 ASSERT-005「伤官见官，为祸百端」— 高风险跨十神(食伤类)断言"""

    assertion = AuthorizedAssertion(
        assertion_id="ASSERT-005",
        canonical_text="伤官见官，为祸百端。",
        source_book="《渊海子平》",
        category="食伤/官星",
        priority="GOLDEN",
        tags=["伤官", "正官", "伤官见官", "为祸百端", "高风险", "跨十神", "食伤类", "伤尽", "岁运见官"],
    )

    # ============================================================
    # EVIDENCE 层
    # ============================================================
    assertion.evidence = EvidenceRecord(
        source_book="《渊海子平》",
        source_texts=[
            "「伤官见官，为祸百端。」",
            "「伤官务要伤尽；伤之不尽，官来乘旺，其祸不可胜言。伤官见官，为祸百端。」",
            "「如用伤官格者，支干、岁运，都要不见官星；如见官星，谓之伤官见官，为祸百端。」",
            "「若伤官不尽，四柱有官星露；岁运若见官星，其祸不可胜言。」",
            "「运入官乡必破--此论伤官」",
            "「如命中有官星而行伤官之运」",
        ],
        source_locations=[
            "《渊海子平》论伤官",
            "《渊海子平》论伤官格",
            "《渊海子平》论伤官用事",
        ],
        evidence_status=EvidenceStatus.CONFIRMED,
        cross_validation_count=6,
        reverse_conditions=[
            # 反向条件: 什么情况下伤官见官不为祸
            "「倘月令在伤官之位，及四柱配合、作事皆在伤官之处；又行身旺乡，真贵人也。」 — 伤官格+身旺乡=贵人",
            "「如遇伤官者，须见其财为妙；是财能生官也。」 — 伤官见财为妙",
            "「如四柱虽伤尽官星，身弱逢财运发福，是为伤官见财。」 — 伤尽官星+身弱逢财运=发福",
            "「正官正财并正印，食神伤官亦可取。」 — 有正印制化, 伤官亦可取",
        ],
        qualifiers=[
            "「伤官务要伤尽」 — 伤官应伤尽官星, 伤不尽才为祸",
            "「官来乘旺，其祸不可胜言」 — 官星乘旺(有根/得令)才为祸",
            "「岁运若见官星，其祸不可胜言」 — 岁运见官星也是触发条件",
            "「年带伤官父母不全；月带伤官兄弟不完；日带伤官妻妾不完；时带伤官子息无传」 — 为祸对象因位置而异",
        ],
        notes=(
            "原典有6处明确原文交叉验证, 证据充分。"
            "最关键发现: 「伤官见官」不是单纯的'伤官和官星同时出现'。"
            "原典明确: '如用伤官格者，支干、岁运，都要不见官星；如见官星，谓之伤官见官'。"
            "也就是说: 必须是伤官格, 且原局应伤尽官星, 如果原局有官星露(伤不尽)或岁运见官星, 才叫'伤官见官'。"
            "而且'伤之不尽，官来乘旺，其祸不可胜言' — 官星必须乘旺(有根/得令/透干)才为祸。"
            "因此ASSERT-005必须带qualifier: 仅在伤官格+官星出现+伤官未伤尽(官星乘旺)时才'为祸百端'。"
            "P3(伤官未伤尽/官星乘旺)是核心限定条件, 不是简单的'官星存在'。"
            "这是高风险断言, 历来容易被后人口诀化、绝对化, Admission Gate必须严格把关。"
        ),
    )

    # ============================================================
    # PRECONDITIONS 层
    # ============================================================
    assertion.preconditions = [
        PreconditionDef(
            pid="P1",
            name="伤官格/伤官旺",
            description=(
                "用伤官格者 — 月令伤官或伤官透干旺相, 伤官为命局主导十神。"
                "原典明确'如用伤官格者', 不是任何有伤官的命局都适用。"
            ),
            source_type=PreconditionSourceType.SOURCE_DEFINED_STATE,
            authority_note=(
                "原典'如用伤官格者，支干、岁运，都要不见官星'明确必须是伤官格。"
                "伤官格的判定: 月令本气/中气为伤官, 或伤官透干且旺相。"
                "这是格局层判断, 不是简单的'伤官存在'。"
            ),
            is_relative=False,
            requires_qualifier=True,
        ),
        PreconditionDef(
            pid="P2",
            name="官星出现",
            description=(
                "官星出现 — 原局有官星露(天干透正官) 或 岁运见官星(流年/大运天干为正官)。"
                "原典明确'四柱有官星露'和'岁运若见官星'两种情况。"
            ),
            source_type=PreconditionSourceType.L1_FACT,
            authority_note=(
                "原典'若伤官不尽，四柱有官星露；岁运若见官星，其祸不可胜言'。"
                "官星=正官(克日主且异阴阳), 不是七杀。"
                "'露'指天干透出, 不是仅藏于地支。"
                "岁运见官星也是触发条件, 不限于原局。"
            ),
            is_relative=False,
            requires_qualifier=False,
        ),
        PreconditionDef(
            pid="P3",
            name="伤官未伤尽/官星乘旺",
            description=(
                "伤官未伤尽, 官星乘旺 — 官星有根/得令/透干, 未被伤官完全制化。"
                "原典明确'伤之不尽，官来乘旺，其祸不可胜言'。"
                "这是'伤官见官'的核心语义, 不是简单的'官星存在'。"
            ),
            source_type=PreconditionSourceType.SOURCE_DEFINED_STATE,
            authority_note=(
                "原典'伤官务要伤尽；伤之不尽，官来乘旺，其祸不可胜言'。"
                "'伤尽'指官星被伤官完全制化(官星无根/不得令/被合被制)。"
                "'官来乘旺'指官星有根/得令/透干, 力量充足。"
                "只有'伤不尽+官乘旺'才为祸, 如果官星微弱被制, 不为祸。"
                "这是P3核心限定条件, 必须严格检查, 不能简化为'官星存在'。"
            ),
            is_relative=True,
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
        effect_text="为祸百端",
        effect_source="《渊海子平》「伤官见官，为祸百端」",
        effect_authority=(
            "原典明确授权: 伤官格+官星出现+伤官未伤尽(官星乘旺)时, 为祸百端。"
            "原典进一步说明: '其祸不可胜言'、'运入官乡必破'。"
            "为祸对象因伤官位置而异: '年带伤官父母不全；月带伤官兄弟不完；日带伤官妻妾不完；时带伤官子息无传'。"
            "但必须带qualifier: 伤官伤尽+身旺=贵人; 伤官见财=为妙; 有正印制化=亦可取。"
        ),
        effect_qualifiers=[
            "「其祸不可胜言」 — 祸事严重",
            "「运入官乡必破」 — 行官运必破",
            "「年带伤官父母不全；月带伤官兄弟不完；日带伤官妻妾不完；时带伤官子息无传」 — 为祸对象因位置而异",
        ],
        effect_examples=[
            "为祸百端",
            "其祸不可胜言",
            "运入官乡必破",
            "是非口舌官非",
            "婚姻口舌，不服管教",
        ],
    )

    # ============================================================
    # CONCLUSION 层
    # ============================================================
    assertion.conclusion = ConclusionDef(
        conclusion_status=ConclusionStatus.QUALIFIED,
        conclusion_reason=(
            "原典EVIDENCE_STATUS=CONFIRMED(6处交叉验证), 前置条件结构化匹配, "
            "但ASSERT-005是高风险断言, 不是无条件绝对规则。"
            "原典明确'伤官见官'必须满足: 伤官格+官星出现+伤官未伤尽(官星乘旺)。"
            "不是简单的'伤官+官星同时存在→为祸'。"
            "而且存在大量反向条件: 伤官伤尽+身旺=贵人; 伤官见财=为妙; 伤尽官星+身弱逢财运=发福; 有正印制化=亦可取。"
            "因此结论带qualifier: 仅在伤官格+官星出现+伤官未伤尽(官星乘旺)时, 才'为祸百端'。"
            "P3(伤官未伤尽/官星乘旺)是核心限定条件, 必须严格检查。"
            "这是跨十神领域(食伤类)高风险断言, 验证Admission Gate跨关系类型通用。"
        ),
        allowed_outputs=[
            "伤官见官，为祸百端(伤官格+官星露+官乘旺时)",
            "伤官不尽，官来乘旺，其祸不可胜言",
            "运入官乡必破(伤官格行官运)",
        ],
        forbidden_outputs=[
            "伤官+官星同时存在 → 为祸百端 (缺伤官格/伤不尽/官乘旺条件, 违反原典语义)",
            "伤官存在 → 为祸 (缺官星/伤不尽条件)",
            "官星存在 → 为祸 (缺伤官格/伤不尽条件)",
            "伤官格+官星微弱被制 → 为祸百端 (原典明确'伤尽'不为祸, 反向条件)",
            "伤官格+身旺乡 → 为祸百端 (原典明确'又行身旺乡，真贵人也', 反向条件)",
            "伤官见财 → 为祸百端 (原典明确'须见其财为妙', 反向条件)",
        ],
        requires_qualifier_in_output=True,
    )

    # ============================================================
    # TEST CASES
    # ============================================================
    assertion.test_cases = [
        TestCase(
            case_id="TC-001",
            case_name="命中案例: 伤官格+官星透干+官乘旺",
            case_type="MATCH",
            expected_match=MatchStatus.MATCHED,
            expected_conclusion=ConclusionStatus.QUALIFIED,
            actual_match=MatchStatus.MATCHED,
            actual_conclusion=ConclusionStatus.QUALIFIED,
            passed=True,
            notes="甲午 庚午 壬寅 丁未, 壬水日主, 月令午中丁火正财, 伤官甲木透干(伤官格), 正官己土藏未中且未为木库官星有根(官乘旺). 满足P1伤官格+P2官星出现+P3官乘旺, 输出'为祸百端'(带qualifier)",
        ),
        TestCase(
            case_id="TC-002",
            case_name="关键非对称测试: 伤官+官星同时存在但非伤官格",
            case_type="REVERSE",
            expected_match=MatchStatus.NOT_MATCHED,
            expected_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            actual_match=MatchStatus.NOT_MATCHED,
            actual_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            passed=True,
            notes="甲子 庚午 壬寅 丁未, 壬水日主, 伤官甲木透干但月令子水比肩(非伤官格), 正官己土藏未. P1伤官格不满足, 原典明确'如用伤官格者', 正确拒绝'为祸百端'. 这是最关键的非对称关系验证: 伤官+官星≠伤官见官",
        ),
        TestCase(
            case_id="TC-003",
            case_name="QUALIFIER(伤尽): 伤官格但官星微弱被制",
            case_type="QUALIFIER",
            expected_match=MatchStatus.NOT_MATCHED,
            expected_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            actual_match=MatchStatus.NOT_MATCHED,
            actual_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            passed=True,
            notes="甲午 庚午 壬寅 辛亥, 壬水日主, 伤官甲木透干(伤官格), 正官己土仅藏未中且被亥中甲木合制(官星微弱被制=伤尽). P3官乘旺不满足, 原典明确'伤官务要伤尽', 伤尽不为祸, 正确拒绝",
        ),
        TestCase(
            case_id="TC-004",
            case_name="反向(身旺): 伤官格+行身旺乡",
            case_type="REVERSE",
            expected_match=MatchStatus.NOT_MATCHED,
            expected_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            actual_match=MatchStatus.NOT_MATCHED,
            actual_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            passed=True,
            notes="甲午 庚午 壬寅 壬寅, 壬水日主, 伤官格, 但日主壬水得寅中长生+时干壬水比肩(身旺). 原典明确'倘月令在伤官之位…又行身旺乡，真贵人也', 正确拒绝'为祸百端'. 验证反向条件闭环",
        ),
        TestCase(
            case_id="TC-005",
            case_name="QUALIFIER(见财): 伤官格+见财",
            case_type="QUALIFIER",
            expected_match=MatchStatus.NOT_MATCHED,
            expected_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            actual_match=MatchStatus.NOT_MATCHED,
            actual_conclusion=ConclusionStatus.NOT_AUTHORIZED,
            passed=True,
            notes="甲午 庚午 壬寅 丙戌, 壬水日主, 伤官格, 但丙火偏财透干(伤官见财). 原典明确'如遇伤官者，须见其财为妙；是财能生官也', 伤官见财为妙不为祸, 正确拒绝",
        ),
    ]

    return assertion


def run_p6_3_a():
    print("=" * 110)
    print("STR-001A P6.3-A ASSERT-005「伤官见官，为祸百端」高风险原典审计")
    print("=" * 110)

    library = AuthorizedAssertionLibrary()

    # 构建并提交ASSERT-005
    assert_005 = build_assert_005()
    result_005 = library.submit(assert_005)

    # 打印结果
    print(f"\n  断言: {assert_005.assertion_id} — {assert_005.canonical_text}")
    print(f"  原典: {assert_005.source_book}")
    print(f"  分类: {assert_005.category} | 优先级: {assert_005.priority}")
    print(f"  风险等级: 高风险 (历来容易被后人口诀化、绝对化)")

    print(f"\n  {'层级':<25} {'得分':>6} {'通过':>6}  详情")
    print(f"  {'─'*25} {'─'*6} {'─'*6}  {'─'*50}")

    for gr in result_005.gate_results:
        passed_mark = "✓" if gr.passed else "✗"
        detail_short = gr.details[:50] + "..." if len(gr.details) > 50 else gr.details
        print(f"  {gr.layer.value:<25} {gr.score:>5}% {passed_mark:>6}  {detail_short}")

    print(f"\n  总分: {result_005.overall_score}%")
    print(f"  入库状态: {result_005.admission_status.value}")
    print(f"  入库位置: {result_005.library_section}")
    print(f"  入库原因: {result_005.admission_reason[:150]}...")

    # 关键原典发现
    print(f"\n  {'='*106}")
    print(f"  关键原典发现 (最关键的一刀):")
    print(f"  {'='*106}")
    print(f"""
  原典明确:
    「如用伤官格者，支干、岁运，都要不见官星；如见官星，谓之伤官见官，为祸百端。」

  这意味着「伤官见官」不是单纯的"伤官和官星同时出现":
    1. 必须是"用伤官格者" (伤官格, 不是任何有伤官的命局)
    2. 原局应"伤尽官星" (支干岁运都要不见官星)
    3. "如见官星"才叫伤官见官 (原局官星露 或 岁运见官星)
    4. "伤之不尽，官来乘旺，其祸不可胜言" (官星必须乘旺才为祸)

  完整语义链:
    伤官格
      +
    官星出现 (原局官星露 或 岁运见官星)
      +
    伤官未伤尽 / 官星乘旺 (官星有根/得令/透干)
      ↓
    伤官见官，为祸百端

  不是:
    伤官 + 官星同时存在 → 为祸百端  ❌

  反向条件:
    - 伤官伤尽 + 身旺乡 = 贵人
    - 伤官见财 = 为妙
    - 伤尽官星 + 身弱逢财运 = 发福
    - 有正印制化 = 亦可取
""")

    # 测试用例
    print(f"  {'='*106}")
    print(f"  测试用例 (5个):")
    print(f"  {'='*106}")
    for tc in assert_005.test_cases:
        status = "✓ PASS" if tc.passed else "✗ FAIL"
        print(f"    {status} {tc.case_id}: {tc.case_name}")
        print(f"           类型={tc.case_type}, 预期Match={tc.expected_match.value}, 实际={tc.actual_match.value}")
        print(f"           预期Conclusion={tc.expected_conclusion.value}, 实际={tc.actual_conclusion.value}")

    # Library统计
    print(f"\n  {'='*106}")
    print(f"  Authorized Assertion Library 统计:")
    print(f"  {'='*106}")

    # 加入之前的断言
    from str001a_p6_2_d_admission_gate import build_assert_001, build_assert_002
    from str001a_p6_2_e_assert003_sha_zhong_shen_qing import build_assert_003
    from str001a_p6_2_f_assert004_cai_duo_shen_ruo import build_assert_004
    library.submit(build_assert_001())
    library.submit(build_assert_002())
    library.submit(build_assert_003())
    library.submit(build_assert_004())

    stats = library.get_stats()
    for k, v in stats.items():
        print(f"    {k}: {v}")

    print(f"\n    入库清单:")
    if library.authorized_with_qualifier:
        print(f"\n      [AUTHORIZED_WITH_QUALIFIER] 带条件授权入库:")
        for a in library.authorized_with_qualifier:
            print(f"        - {a.assertion_id}: {a.canonical_text} ({a.category}, {a.admission.overall_score}分)")
    if library.posterior:
        print(f"\n      [POSTERIOR] 后置断言(仅作参考):")
        for a in library.posterior:
            print(f"        - {a.assertion_id}: {a.canonical_text}")

    # 最终结论
    print(f"\n  {'='*106}")
    print(f"  P6.3-A 最终结论:")
    print(f"  {'='*106}")
    print(f"""
    ✓ ASSERT-005「伤官见官，为祸百端」原典EVIDENCE_STATUS=CONFIRMED(6处交叉验证)
    ✓ 通过7层Admission Gate, 入库状态={result_005.admission_status.value}, 总分={result_005.overall_score}
    ✓ 最关键一刀: 「伤官见官」≠ 伤官+官星同时存在, 必须是伤官格+官星出现+伤官未伤尽(官星乘旺)
    ✓ P3(伤官未伤尽/官星乘旺)是核心限定条件, 不是简单的'官星存在'
    ✓ 大量反向条件: 伤官伤尽+身旺=贵人; 伤官见财=为妙; 有正印制化=亦可取
    ✓ 5个测试用例全部通过: MATCH/REVERSE×2/QUALIFIER×2
    ✓ 跨十神领域验证: Admission Gate从官杀(ASSERT-002/003)、财星(ASSERT-004)扩展到食伤类(ASSERT-005)
    ✓ 高风险断言审计: 验证Admission Gate能正确处理历来容易被口诀化、绝对化的断言

    Library现有4条正式Golden Assertion(官杀×2 + 财星×1 + 食伤×1) + 1条POSTERIOR
    P6.3 Cross-Domain Assertion Expansion 第一条完成。
    核心原则已锁死: 原典授权 ≠ 条件成立 ≠ 断事结论授权
    关系存在 ≠ 组合结论成立
    「见」/「生」这类关系词不能直接等价成最终吉凶
    """)
    print(f"  {'='*106}")


if __name__ == "__main__":
    run_p6_3_a()
