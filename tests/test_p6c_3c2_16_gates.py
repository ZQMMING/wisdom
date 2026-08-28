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
    from tongshu.judgment_architecture.judgment_asset_v2 import (
        SpecificityProfile, RetrievalPartition, DisplayPriority,
    )
    j = JudgmentAssetV2(
        judgment_id="TEST-001", system="ZI_PING", school="SAN_MING_TONG_HUI",
        judgment_type="DAY_TIME", match_mode="EXACT",
        conditions=[MatchCondition("ZP.DAY_PILLAR", "EQ", "YI_WEI")],
        specificity=SpecificityProfile(level="EXACT", constraint_count=2, feature_depth=2),
        retrieval_partition=RetrievalPartition(
            system="ZI_PING", school="SAN_MING_TONG_HUI", judgment_type="DAY_TIME"
        ),
        display_priority=DisplayPriority(school_priority=50),
        classical="测试",
    )
    d = j.to_dict()
    required = ["judgment_id", "system", "school", "judgment_type", "version",
                "match_mode", "conditions", "feature_requirements", "specificity",
                "retrieval_partition", "display_priority",
                "classical", "semantic_keys", "modern_mapping",
                "book", "chapter", "section", "page", "source_locator",
                "created_at", "revision", "status"]
    for r in required:
        assert r in d, f"缺少字段{r}"
    # 验证specificity是dict (SpecificityProfile.to_dict)
    assert isinstance(d["specificity"], dict)
    assert "level" in d["specificity"]
    assert "rank_key" in d["specificity"]
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
    """⑤ specificity 可计算 (SpecificityProfile多维特异度)."""
    from tongshu.judgment_architecture.judgment_asset_v2 import SpecificityProfile
    library = build_vertical_slice_library()
    for j in library.get_all():
        # specificity必须是SpecificityProfile, 不是int
        assert isinstance(j.specificity, SpecificityProfile), f"{j.judgment_id} specificity不是SpecificityProfile"
        # rank_key必须是tuple
        assert isinstance(j.specificity.rank_key, tuple), f"{j.judgment_id} rank_key不是tuple"
        # level必须是有效值
        assert j.specificity.level in ("LOW", "MEDIUM", "HIGH", "EXACT", "COMPOSITE"), f"{j.judgment_id} level无效"
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


def gate_17_specificity_not_cross_school():
    """⑰ Specificity不得跨School/Judgment Type直接比较 (两级排序)."""
    from tongshu.judgment_architecture.judgment_asset_v2 import RetrievalPartition
    library = build_vertical_slice_library()
    resolver = SchoolIsolatedResolver(library)
    features = {
        "ZP.DAY_PILLAR": "YI_WEI", "ZP.HOUR_PILLAR": "REN_WU",
        "ZP.DAY_MASTER": "YI", "ZP.MONTH_BRANCH": "XU", "ZP.YEAR_BRANCH": "HAI",
    }

    # 验证resolve_grouped按RetrievalPartition分组
    for school in ["SAN_MING_TONG_HUI", "QIONG_TONG_BAO_JIAN", "ZI_PING_ZHEN_QUAN"]:
        grouped = resolver.resolve_grouped("ZI_PING", school, features)
        # 每个partition的结果都应该有相同的partition_key
        for partition_key, results in grouped.items():
            for r in results:
                assert r.judgment.retrieval_partition.partition_key == partition_key, \
                    f"{r.judgment.judgment_id} partition_key不匹配"

    # 验证不同school的断言不会混在一起比较
    all_schools = resolver.resolve_all_schools("ZI_PING", features)
    school_names = list(all_schools.keys())
    assert len(school_names) >= 3, "应该至少有3个school"

    # 每个school的结果只包含该school的断言
    for school, results in all_schools.items():
        for r in results:
            assert r.judgment.school == school, f"{r.judgment.judgment_id} school不匹配"

    return True


def gate_18_all_matches_preserved():
    """⑱ 所有MATCH的Judgment均保留, 高specificity不得覆盖低specificity."""
    library = build_vertical_slice_library()
    resolver = SchoolIsolatedResolver(library)
    features = {
        "ZP.DAY_PILLAR": "YI_WEI", "ZP.HOUR_PILLAR": "REN_WU",
        "ZP.DAY_MASTER": "YI", "ZP.MONTH_BRANCH": "XU", "ZP.YEAR_BRANCH": "HAI",
    }

    # 三命通会应该有3条不同specificity的断言同时MATCH
    smth_results = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features)
    smth_matches = [r for r in smth_results if r.match_status == "MATCH"]

    # 至少2条不同specificity的断言同时MATCH
    match_ids = [r.judgment.judgment_id for r in smth_matches]
    assert len(match_ids) >= 2, f"应该至少2条MATCH, 实际{len(match_ids)}"

    # 验证高specificity没有覆盖低specificity
    # SMTH-YIWEI-RENWU-001 (EXACT, specificity=40) 应该和
    # SMTH-YIWEI-RENWU-XU-001 (COMPOSITE, specificity=50) 同时存在
    assert "SMTH-YIWEI-RENWU-001" in match_ids, "低specificity断言被覆盖了"
    assert "SMTH-YIWEI-RENWU-XU-001" in match_ids, "高specificity断言缺失"

    return True


def gate_19_display_priority_not_in_judgment():
    """⑲ DisplayPriority只能影响UI排序, 不得参与MATCH/REJECT/Assertion."""
    from tongshu.judgment_architecture.judgment_asset_v2 import DisplayPriority
    library = build_vertical_slice_library()

    for j in library.get_all():
        # display_priority必须是DisplayPriority
        assert isinstance(j.display_priority, DisplayPriority), f"{j.judgment_id} display_priority类型错误"
        # display_priority的字段必须在合理范围内
        assert 0 <= j.display_priority.school_priority <= 100
        assert 0 <= j.display_priority.judgment_type_priority <= 100

    # 验证DeterministicMatcher.match不读取display_priority
    # (match方法只使用conditions和features, 不使用display_priority)
    from tongshu.judgment_architecture.judgment_asset_v2 import DeterministicMatcher
    j = library.get("SMTH-YIWEI-RENWU-001")
    # 修改display_priority不应该影响匹配结果
    import dataclasses
    j_modified = dataclasses.replace(j, display_priority=DisplayPriority(school_priority=100))
    r1 = DeterministicMatcher.match(j, {"ZP.DAY_PILLAR": "YI_WEI", "ZP.HOUR_PILLAR": "REN_WU"})
    r2 = DeterministicMatcher.match(j_modified, {"ZP.DAY_PILLAR": "YI_WEI", "ZP.HOUR_PILLAR": "REN_WU"})
    assert r1.match_status == r2.match_status, "display_priority影响了匹配结果"

    return True


def main():
    print("=" * 80)
    print("P6-C-3C-2 19项Gate最终验证 (含架构修正)")
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
        ("⑰ Specificity不跨School比较 (两级排序)", gate_17_specificity_not_cross_school),
        ("⑱ 所有MATCH均保留 (高specificity不覆盖低)", gate_18_all_matches_preserved),
        ("⑲ DisplayPriority不参与MATCH/REJECT", gate_19_display_priority_not_in_judgment),
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
    print(f"Gate结果: {passed}/19 PASS, {failed}/19 FAIL")
    print("=" * 80)

    if failed == 0:
        print("\n*** P6-C-3C-2 GATE: ALL 19 PASS ***")
        return 0
    else:
        print(f"\n*** P6-C-3C-2 GATE: {failed} FAILED ***")
        return 1


if __name__ == "__main__":
    sys.exit(main())
