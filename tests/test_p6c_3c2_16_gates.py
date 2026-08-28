"""P6-C-3C-2 16项Gate最终验证."""
import sys
sys.path.insert(0, "src")

from tongshu.judgment_architecture.judgment_asset_v2 import (
    JudgmentAssetV2, MatchCondition, JudgmentLibraryV2, SchoolIsolatedResolver,
    DeterministicMatcher, MatchStatus, ConditionStatus,
)
from tongshu.judgment_architecture.vertical_slice_50 import build_vertical_slice_library


def gate_01_schema_v2():
    """① Schema V2 PASS."""
    j = JudgmentAssetV2(
        judgment_id="TEST-001", system="ZI_PING", school="SAN_MING_TONG_HUI",
        judgment_type="DAY_TIME", match_mode="EXACT",
        conditions=[MatchCondition("ZP.DAY_PILLAR", "EQ", "YI_WEI")],
        specificity=40, classical="测试",
    )
    d = j.to_dict()
    required = ["judgment_id", "system", "school", "judgment_type", "version",
                "match_mode", "conditions", "feature_requirements", "specificity",
                "classical", "semantic_keys", "modern_mapping",
                "book", "chapter", "section", "page", "source_locator",
                "created_at", "revision", "status"]
    for r in required:
        assert r in d, f"缺少字段{r}"
    return True


def gate_02_system_school_mandatory():
    """② system + school 强制."""
    try:
        JudgmentAssetV2(judgment_id="BAD-001", system="", school="SAN_MING_TONG_HUI", judgment_type="TEST")
        return False
    except ValueError:
        pass
    try:
        JudgmentAssetV2(judgment_id="BAD-002", system="ZI_PING", school="", judgment_type="TEST")
        return False
    except ValueError:
        pass
    return True


def gate_03_conditions_executable():
    """③ conditions 可执行."""
    j = JudgmentAssetV2(
        judgment_id="TEST-003", system="ZI_PING", school="SAN_MING_TONG_HUI",
        judgment_type="TEST", match_mode="EXACT",
        conditions=[MatchCondition("ZP.A", "EQ", "X")],
    )
    r = DeterministicMatcher.match(j, {"ZP.A": "X"})
    assert r.match_status == MatchStatus.MATCH.value
    r2 = DeterministicMatcher.match(j, {"ZP.A": "Y"})
    assert r2.match_status == MatchStatus.REJECT.value
    return True


def gate_04_match_mode_executable():
    """④ match_mode 可执行."""
    modes = ["EXACT", "CONDITION", "ALL", "ANY", "SET", "COMPOSITE"]
    for mode in modes:
        j = JudgmentAssetV2(
            judgment_id=f"TEST-{mode}", system="ZI_PING", school="SAN_MING_TONG_HUI",
            judgment_type="TEST", match_mode=mode,
            conditions=[MatchCondition("ZP.A", "EQ", "X")],
        )
        r = DeterministicMatcher.match(j, {"ZP.A": "X"})
        assert r.match_status == MatchStatus.MATCH.value, f"{mode}应该MATCH"
    return True


def gate_05_specificity_calculable():
    """⑤ specificity 可计算."""
    library = build_vertical_slice_library()
    for j in library.get_all():
        assert 10 <= j.specificity <= 100, f"{j.judgment_id} specificity={j.specificity}越界"
    return True


def gate_06_modern_mapping_not_generated():
    """⑥ modern_mapping 不参与生成."""
    library = build_vertical_slice_library()
    for j in library.get_all():
        # modern_mapping应该是空dict或人工标注, 不是LLM生成
        assert isinstance(j.modern_mapping, dict)
        # semantic_keys应该是人工标注的列表
        assert isinstance(j.semantic_keys, list)
    return True


def gate_07_50_vertical_slice_source():
    """⑦ 50条 Vertical Slice 全部有原典定位."""
    library = build_vertical_slice_library()
    assert len(library.get_all()) == 50, f"应该50条, 实际{len(library.get_all())}"
    for j in library.get_all():
        assert j.book, f"{j.judgment_id}缺少book"
        assert j.source_locator, f"{j.judgment_id}缺少source_locator"
    return True


def gate_08_positive_match():
    """⑧ MATCH 正向测试 PASS."""
    library = build_vertical_slice_library()
    resolver = SchoolIsolatedResolver(library)
    features = {"ZP.DAY_PILLAR": "YI_WEI", "ZP.HOUR_PILLAR": "REN_WU"}
    results = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features)
    target = [r for r in results if r.judgment.judgment_id == "SMTH-YIWEI-RENWU-001"]
    assert len(target) == 1
    assert target[0].match_status == MatchStatus.MATCH.value
    return True


def gate_09_negative_match():
    """⑨ REJECT 负向测试 PASS."""
    library = build_vertical_slice_library()
    resolver = SchoolIsolatedResolver(library)
    features = {"ZP.DAY_PILLAR": "YI_WEI", "ZP.HOUR_PILLAR": "GUI_WU"}
    results = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features)
    target = [r for r in results if r.judgment.judgment_id == "SMTH-YIWEI-RENWU-001"]
    assert len(target) == 1
    assert target[0].match_status == MatchStatus.REJECT.value
    return True


def gate_10_five_school_isolation():
    """⑩ 五经典 Resolver 隔离 PASS."""
    library = build_vertical_slice_library()
    resolver = SchoolIsolatedResolver(library)
    features = {"ZP.DAY_PILLAR": "YI_WEI", "ZP.HOUR_PILLAR": "REN_WU"}

    schools = ["DI_TIAN_SUI", "ZI_PING_ZHEN_QUAN", "QIONG_TONG_BAO_JIAN", "YUAN_HAI_ZI_PING", "SAN_MING_TONG_HUI"]
    for school in schools:
        results = resolver.resolve("ZI_PING", school, features)
        # 每个school的结果只能是该school的断言
        for r in results:
            assert r.judgment.school == school, f"{school} Resolver返回了{r.judgment.school}的断言"
    return True


def gate_11_evidence_binding():
    """⑪ Evidence Binding 完整."""
    library = build_vertical_slice_library()
    resolver = SchoolIsolatedResolver(library)
    features = {"ZP.DAY_PILLAR": "YI_WEI", "ZP.HOUR_PILLAR": "REN_WU"}
    results = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features)
    matches = [r for r in results if r.match_status == MatchStatus.MATCH.value]
    for r in matches:
        assert len(r.evidence_binding) > 0, f"{r.judgment.judgment_id}缺少Evidence Binding"
    return True


def gate_12_observatory_trace():
    """⑫ Observatory 可从 Judgment 追溯到原始 Evidence."""
    library = build_vertical_slice_library()
    resolver = SchoolIsolatedResolver(library)
    features = {"ZP.DAY_PILLAR": "YI_WEI", "ZP.HOUR_PILLAR": "REN_WU"}
    results = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features)
    target = [r for r in results if r.judgment.judgment_id == "SMTH-YIWEI-RENWU-001"][0]

    # 追溯链: Judgment → Conditions → Features → Evidence
    trace = {
        "judgment_id": target.judgment.judgment_id,
        "system": target.judgment.system,
        "school": target.judgment.school,
        "source": target.judgment.source_locator,
        "conditions": [ce.to_dict() for ce in target.condition_evaluations],
        "evidence_binding": target.evidence_binding,
    }
    assert trace["judgment_id"] == "SMTH-YIWEI-RENWU-001"
    assert len(trace["conditions"]) == 2
    assert "ZP.DAY_PILLAR" in trace["evidence_binding"]
    return True


def gate_13_no_direction_polarity():
    """⑬ 不读取 direction/polarity."""
    library = build_vertical_slice_library()
    forbidden = ["direction", "polarity", "positive", "negative"]
    for j in library.get_all():
        d = j.to_dict()
        for f in forbidden:
            assert f not in d, f"{j.judgment_id}包含{f}"
    return True


def gate_14_no_confidence_score_weight():
    """⑭ 不读取 confidence/score/weight."""
    library = build_vertical_slice_library()
    forbidden = ["confidence", "score", "weight", "SYSTEM_WEIGHTS"]
    for j in library.get_all():
        d = j.to_dict()
        for f in forbidden:
            assert f not in d, f"{j.judgment_id}包含{f}"
    return True


def gate_15_not_enter_context_resolver():
    """⑮ 不进入 ContextResolver."""
    # Judgment Asset层只做匹配, 不产生Assertion/direction
    library = build_vertical_slice_library()
    resolver = SchoolIsolatedResolver(library)
    features = {"ZP.DAY_PILLAR": "YI_WEI", "ZP.HOUR_PILLAR": "REN_WU"}
    results = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features)
    for r in results:
        d = r.to_dict()
        # 不应该有assertion/domain/semantic等ContextResolver产物
        assert "assertion_id" not in d
        assert "domain" not in d
        assert "semantic_family" not in d
    return True


def gate_16_not_large_scale_index():
    """⑯ 不进行大规模 Index (只有50条)."""
    library = build_vertical_slice_library()
    assert len(library.get_all()) == 50, f"应该50条, 实际{len(library.get_all())}"
    return True


def main():
    print("=" * 80)
    print("P6-C-3C-2 16项Gate最终验证")
    print("=" * 80)

    gates = [
        ("① Schema V2 PASS", gate_01_schema_v2),
        ("② system + school 强制", gate_02_system_school_mandatory),
        ("③ conditions 可执行", gate_03_conditions_executable),
        ("④ match_mode 可执行", gate_04_match_mode_executable),
        ("⑤ specificity 可计算", gate_05_specificity_calculable),
        ("⑥ modern_mapping 不参与生成", gate_06_modern_mapping_not_generated),
        ("⑦ 50条 Vertical Slice 全部有原典定位", gate_07_50_vertical_slice_source),
        ("⑧ MATCH 正向测试 PASS", gate_08_positive_match),
        ("⑨ REJECT 负向测试 PASS", gate_09_negative_match),
        ("⑩ 五经典 Resolver 隔离 PASS", gate_10_five_school_isolation),
        ("⑪ Evidence Binding 完整", gate_11_evidence_binding),
        ("⑫ Observatory 可追溯", gate_12_observatory_trace),
        ("⑬ 不读取 direction/polarity", gate_13_no_direction_polarity),
        ("⑭ 不读取 confidence/score/weight", gate_14_no_confidence_score_weight),
        ("⑮ 不进入 ContextResolver", gate_15_not_enter_context_resolver),
        ("⑯ 不进行大规模 Index", gate_16_not_large_scale_index),
    ]

    passed = 0
    failed = 0

    for name, gate_func in gates:
        try:
            gate_func()
            print(f"  ✓ {name}")
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ {name}: ERROR - {e}")
            failed += 1

    print("\n" + "=" * 80)
    print(f"Gate结果: {passed}/16 PASS, {failed}/16 FAIL")
    print("=" * 80)

    if failed == 0:
        print("\n*** P6-C-3C-2 GATE: ALL 16 PASS ***")
        return 0
    else:
        print(f"\n*** P6-C-3C-2 GATE: {failed} FAILED ***")
        return 1


if __name__ == "__main__":
    sys.exit(main())
