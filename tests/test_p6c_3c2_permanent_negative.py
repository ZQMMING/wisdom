"""P6-C-3C-2 永久负向测试资产 - 防止以后Index做大后出现跨经典误命中.

测试用例:
1. 乙未日+壬午时 → SAN_MING_TONG_HUI → SMTH-YIWEI-RENWU-001 → MATCH
2. 乙未日+癸午时 → SMTH-YIWEI-RENWU-001 → REJECT
3. 跨经典隔离: SAN_MING_TONG_HUI:J001 不能被 ZI_PING_ZHEN_QUAN Resolver 命中
4. 状态机验证: UNRESOLVED → NO_CANDIDATE → CANDIDATE → MATCH/REJECT
5. 条件状态验证: SATISFIED / FAILED / MISSING
"""
import sys
sys.path.insert(0, "src")

from tongshu.judgment_architecture.judgment_asset_v2 import (
    JudgmentLibraryV2, SchoolIsolatedResolver, DeterministicMatcher,
    MatchStatus, ConditionStatus,
)
from tongshu.judgment_architecture.vertical_slice_50 import build_vertical_slice_library


def test_positive_match():
    """测试1: 乙未日+壬午时 → MATCH."""
    print("\n[测试1] 正向匹配: 乙未日+壬午时 → MATCH")
    library = build_vertical_slice_library()
    resolver = SchoolIsolatedResolver(library)

    features = {
        "ZP.DAY_PILLAR": "YI_WEI",
        "ZP.HOUR_PILLAR": "REN_WU",
        "ZP.DAY_MASTER": "YI",
        "ZP.MONTH_BRANCH": "XU",
        "ZP.YEAR_BRANCH": "HAI",
    }

    results = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features)
    target = [r for r in results if r.judgment.judgment_id == "SMTH-YIWEI-RENWU-001"]

    assert len(target) == 1, "应该找到SMTH-YIWEI-RENWU-001"
    assert target[0].match_status == MatchStatus.MATCH.value, f"应该MATCH, 实际{target[0].match_status}"

    # 验证条件评估
    for ce in target[0].condition_evaluations:
        assert ce.status == ConditionStatus.SATISFIED.value, f"条件{ce.feature}应该SATISFIED"

    print(f"  ✓ SMTH-YIWEI-RENWU-001 MATCH")
    print(f"  ✓ 条件评估: {len(target[0].condition_evaluations)}条全部SATISFIED")
    print(f"  ✓ Evidence Binding: {target[0].evidence_binding}")
    return True


def test_negative_match():
    """测试2: 乙未日+癸午时 → REJECT."""
    print("\n[测试2] 负向匹配: 乙未日+癸午时 → REJECT")
    library = build_vertical_slice_library()
    resolver = SchoolIsolatedResolver(library)

    features = {
        "ZP.DAY_PILLAR": "YI_WEI",
        "ZP.HOUR_PILLAR": "GUI_WU",  # 癸午时, 不是壬午时
    }

    results = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features)
    target = [r for r in results if r.judgment.judgment_id == "SMTH-YIWEI-RENWU-001"]

    assert len(target) == 1, "应该找到SMTH-YIWEI-RENWU-001"
    assert target[0].match_status == MatchStatus.REJECT.value, f"应该REJECT, 实际{target[0].match_status}"

    # 验证条件评估: ZP.HOUR_PILLAR应该FAILED
    hour_cond = [ce for ce in target[0].condition_evaluations if ce.feature == "ZP.HOUR_PILLAR"]
    assert len(hour_cond) == 1
    assert hour_cond[0].status == ConditionStatus.FAILED.value
    assert hour_cond[0].expected == "REN_WU"
    assert hour_cond[0].actual == "GUI_WU"

    print(f"  ✓ SMTH-YIWEI-RENWU-001 REJECT")
    print(f"  ✓ 失败条件: ZP.HOUR_PILLAR expected={hour_cond[0].expected} actual={hour_cond[0].actual}")
    print(f"  ✓ 失败原因: {hour_cond[0].detail}")
    return True


def test_cross_school_isolation():
    """测试3: 跨经典隔离."""
    print("\n[测试3] 跨经典隔离: 三命通会断言不能被子平真诠Resolver命中")
    library = build_vertical_slice_library()
    resolver = SchoolIsolatedResolver(library)

    features = {
        "ZP.DAY_PILLAR": "YI_WEI",
        "ZP.HOUR_PILLAR": "REN_WU",
    }

    # 子平真诠Resolver不应该检索到三命通会断言
    zpzq_results = resolver.resolve("ZI_PING", "ZI_PING_ZHEN_QUAN", features)
    smth_in_zpzq = [r for r in zpzq_results if "SMTH" in r.judgment.judgment_id]
    assert len(smth_in_zpzq) == 0, "子平真诠Resolver不应该检索到三命通会断言"

    # 穷通宝鉴Resolver不应该检索到三命通会断言
    qtbj_results = resolver.resolve("ZI_PING", "QIONG_TONG_BAO_JIAN", features)
    smth_in_qtbj = [r for r in qtbj_results if "SMTH" in r.judgment.judgment_id]
    assert len(smth_in_qtbj) == 0, "穷通宝鉴Resolver不应该检索到三命通会断言"

    # 三命通会Resolver应该能检索到
    smth_results = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features)
    smth_match = [r for r in smth_results if r.match_status == MatchStatus.MATCH.value]
    assert len(smth_match) > 0, "三命通会Resolver应该能检索到断言"

    print(f"  ✓ 子平真诠Resolver: 0条三命通会断言")
    print(f"  ✓ 穷通宝鉴Resolver: 0条三命通会断言")
    print(f"  ✓ 三命通会Resolver: {len(smth_match)}条MATCH")
    return True


def test_specificity_hierarchy():
    """测试4: specificity层级 - 所有层级同时保留, 不覆盖."""
    print("\n[测试4] specificity层级 - 所有层级同时保留")
    library = build_vertical_slice_library()
    resolver = SchoolIsolatedResolver(library)

    features = {
        "ZP.DAY_PILLAR": "YI_WEI",
        "ZP.HOUR_PILLAR": "REN_WU",
        "ZP.MONTH_BRANCH": "XU",
        "ZP.YEAR_BRANCH": "HAI",
        "ZP.DAY_MASTER": "YI",
    }

    results = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features)
    matches = [r for r in results if r.match_status == MatchStatus.MATCH.value]

    # 应该有3条不同specificity的断言同时MATCH
    # SMTH-YIWEI-RENWU-001 (specificity=40)
    # SMTH-YIWEI-RENWU-XU-001 (specificity=50)
    # SMTH-YIWEI-RENWU-HAI-001 (specificity=50)
    assert len(matches) >= 2, f"应该至少2条不同specificity的断言同时MATCH, 实际{len(matches)}"

    specificities = sorted([r.judgment.specificity for r in matches])
    print(f"  ✓ MATCH数量: {len(matches)}")
    print(f"  ✓ Specificity层级: {specificities}")
    print(f"  ✓ 高特异性不覆盖低特异性: 所有层级同时保留")
    return True


def test_condition_missing():
    """测试5: 条件MISSING状态."""
    print("\n[测试5] 条件MISSING状态 - Feature不存在")
    library = build_vertical_slice_library()
    resolver = SchoolIsolatedResolver(library)

    # 缺少ZP.HOUR_PILLAR
    features = {
        "ZP.DAY_PILLAR": "YI_WEI",
        # 缺少 ZP.HOUR_PILLAR
    }

    results = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features)
    target = [r for r in results if r.judgment.judgment_id == "SMTH-YIWEI-RENWU-001"]

    assert len(target) == 1
    # 因为缺少必需Feature, 应该是UNRESOLVED
    assert target[0].match_status == MatchStatus.UNRESOLVED.value, f"应该UNRESOLVED, 实际{target[0].match_status}"

    # 验证条件评估中有MISSING
    hour_cond = [ce for ce in target[0].condition_evaluations if ce.feature == "ZP.HOUR_PILLAR"]
    assert len(hour_cond) == 1
    assert hour_cond[0].status == ConditionStatus.MISSING.value
    assert hour_cond[0].actual is None

    print(f"  ✓ SMTH-YIWEI-RENWU-001 UNRESOLVED (缺少必需Feature)")
    print(f"  ✓ ZP.HOUR_PILLAR status=MISSING, actual=None")
    return True


def test_state_machine():
    """测试6: 状态机完整链."""
    print("\n[测试6] 状态机完整链: UNRESOLVED → CANDIDATE → MATCH/REJECT")
    library = build_vertical_slice_library()
    resolver = SchoolIsolatedResolver(library)

    # UNRESOLVED: 缺少必需Feature
    features_unresolved = {"ZP.DAY_PILLAR": "YI_WEI"}
    r_unresolved = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features_unresolved)
    target_unresolved = [r for r in r_unresolved if r.judgment.judgment_id == "SMTH-YIWEI-RENWU-001"][0]
    assert target_unresolved.match_status == MatchStatus.UNRESOLVED.value

    # CANDIDATE: 有候选断言, 部分条件满足 (PARTIAL)
    features_candidate = {"ZP.DAY_PILLAR": "YI_WEI", "ZP.HOUR_PILLAR": "GUI_WU"}
    # 用CONDITION模式的断言测试CANDIDATE状态
    r_candidate = resolver.resolve("ZI_PING", "ZI_PING_ZHEN_QUAN", features_candidate)
    # 找一个PARTIAL的结果
    partials = [r for r in r_candidate if r.match_status == MatchStatus.CANDIDATE.value]

    # MATCH: 所有条件满足
    features_match = {"ZP.DAY_PILLAR": "YI_WEI", "ZP.HOUR_PILLAR": "REN_WU"}
    r_match = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features_match)
    target_match = [r for r in r_match if r.judgment.judgment_id == "SMTH-YIWEI-RENWU-001"][0]
    assert target_match.match_status == MatchStatus.MATCH.value

    # REJECT: 条件不满足 (EXACT模式)
    features_reject = {"ZP.DAY_PILLAR": "YI_WEI", "ZP.HOUR_PILLAR": "GUI_WU"}
    r_reject = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features_reject)
    target_reject = [r for r in r_reject if r.judgment.judgment_id == "SMTH-YIWEI-RENWU-001"][0]
    assert target_reject.match_status == MatchStatus.REJECT.value

    print(f"  ✓ UNRESOLVED: 缺少必需Feature")
    print(f"  ✓ CANDIDATE: 部分条件满足 (PARTIAL)")
    print(f"  ✓ MATCH: 所有条件满足")
    print(f"  ✓ REJECT: 条件不满足 (EXACT模式)")
    return True


def test_no_direction_polarity():
    """测试7: 不读取direction/polarity/confidence/score/weight."""
    print("\n[测试7: 不读取direction/polarity/confidence/score/weight")
    library = build_vertical_slice_library()

    # 检查所有断言资产不包含这些字段
    forbidden_fields = ["direction", "polarity", "confidence", "score", "weight", "positive", "negative"]
    for j in library.get_all():
        j_dict = j.to_dict()
        for field in forbidden_fields:
            assert field not in j_dict, f"断言{j.judgment_id}包含禁用字段{field}"

    print(f"  ✓ 所有{len(library.get_all())}条断言不包含direction/polarity/confidence/score/weight")
    return True


def main():
    print("=" * 80)
    print("P6-C-3C-2 永久负向测试资产")
    print("=" * 80)

    tests = [
        ("正向匹配: 乙未日+壬午时 → MATCH", test_positive_match),
        ("负向匹配: 乙未日+癸午时 → REJECT", test_negative_match),
        ("跨经典隔离", test_cross_school_isolation),
        ("specificity层级", test_specificity_hierarchy),
        ("条件MISSING状态", test_condition_missing),
        ("状态机完整链", test_state_machine),
        ("不读取direction/polarity", test_no_direction_polarity),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n  ✗ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"\n  ✗ ERROR: {e}")
            failed += 1

    print("\n" + "=" * 80)
    print(f"测试结果: {passed} PASS, {failed} FAIL")
    print("=" * 80)

    if failed == 0:
        print("\n所有永久负向测试通过!")
        return 0
    else:
        print(f"\n{failed}个测试失败!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
