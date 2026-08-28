"""P6-C-3C-2 50条五经典Vertical Slice断言资产.

刻意选择不同Matcher类型:
- 滴天髓: 3 CONDITION + 3 GRAPH + 2 COMPOSITE + 2 STEM_IMAGE = 10
- 子平真诠: 4 PATTERN + 3 PATTERN_SUCCESS + 3 USE_GOD = 10
- 穷通宝鉴: 5 DAY_MASTER+MONTH + 3 CONDITION + 2 COMPOSITE = 10
- 渊海子平: 4 TEN_GOD + 3 SET + 3 PATTERN_BASIC = 10
- 三命通会: 8 EXACT DAY_TIME + 2 COMPOSITE = 10
"""
from __future__ import annotations
from tongshu.judgment_architecture.judgment_asset_v2 import (
    JudgmentAssetV2, MatchCondition, JudgmentLibraryV2,
    SpecificityProfile, RetrievalPartition, DisplayPriority,
    SpecificityLevel, MatchExactness,
)


def _int_to_specificity(specificity_int: int, match_mode: str, conditions_count: int) -> SpecificityProfile:
    """将旧的specificity=int转换成SpecificityProfile.

    映射规则:
    - 10-19: LOW (单条件, 如 乙木)
    - 20-29: MEDIUM (双条件, 如 乙木+戌月)
    - 30-39: HIGH (三条件, 如 乙木+戌月+壬透)
    - 40-49: EXACT (精确匹配, 如 乙未日+壬午时)
    - 50+: COMPOSITE (复合匹配, 如 乙未日+壬午时+戌月)
    """
    if specificity_int >= 50:
        level = SpecificityLevel.COMPOSITE.value
    elif specificity_int >= 40:
        level = SpecificityLevel.EXACT.value
    elif specificity_int >= 30:
        level = SpecificityLevel.HIGH.value
    elif specificity_int >= 20:
        level = SpecificityLevel.MEDIUM.value
    else:
        level = SpecificityLevel.LOW.value

    # match_exactness映射
    exactness_map = {
        "EXACT": MatchExactness.EXACT.value,
        "SET": MatchExactness.SET.value,
        "CONDITION": MatchExactness.CONDITION.value,
        "ALL": MatchExactness.CONDITION.value,
        "ANY": MatchExactness.CONDITION.value,
        "COMPOSITE": MatchExactness.COMPOSITE.value,
        "GRAPH": MatchExactness.GRAPH.value,
        "RANGE": MatchExactness.CONDITION.value,
    }
    match_exactness = exactness_map.get(match_mode, MatchExactness.CONDITION.value)

    # feature_depth = conditions_count (近似)
    feature_depth = min(conditions_count, 6)

    return SpecificityProfile(
        level=level,
        constraint_count=conditions_count,
        feature_depth=feature_depth,
        match_exactness=match_exactness,
        structural_depth=1 if level in (SpecificityLevel.HIGH.value, SpecificityLevel.EXACT.value, SpecificityLevel.COMPOSITE.value) else 0,
        temporal_depth=0,
        scope="NATAL",
        discrimination="HIGH" if level in (SpecificityLevel.EXACT.value, SpecificityLevel.COMPOSITE.value) else "MEDIUM",
    )


def legacy_judgment(**kwargs) -> JudgmentAssetV2:
    """兼容旧格式的断言创建函数.

    自动将旧的specificity=int转换成SpecificityProfile,
    自动生成RetrievalPartition和DisplayPriority.
    """
    # 提取旧的specificity=int
    specificity_int = kwargs.pop("specificity", 10)
    match_mode = kwargs.get("match_mode", "CONDITION")
    conditions = kwargs.get("conditions", [])
    conditions_count = len(conditions)

    # 转换为SpecificityProfile
    kwargs["specificity"] = _int_to_specificity(specificity_int, match_mode, conditions_count)

    # 自动生成RetrievalPartition
    system = kwargs.get("system", "ZI_PING")
    school = kwargs.get("school", "SAN_MING_TONG_HUI")
    judgment_type = kwargs.get("judgment_type", "DEFAULT")
    kwargs["retrieval_partition"] = RetrievalPartition(
        system=system, school=school, judgment_type=judgment_type,
        retrieval_family="DEFAULT"
    )

    # 自动生成DisplayPriority (仅UI, 不参与判断)
    kwargs["display_priority"] = DisplayPriority(
        school_priority=50, judgment_type_priority=50, display_order=0
    )

    return JudgmentAssetV2(**kwargs)


def build_vertical_slice_library() -> JudgmentLibraryV2:
    """建立50条五经典Vertical Slice断言库."""
    library = JudgmentLibraryV2()
    judgments = []

    # ========================================================================
    # 滴天髓 (10条): 3 CONDITION + 3 GRAPH + 2 COMPOSITE + 2 STEM_IMAGE
    # ========================================================================

    # CONDITION (3条)
    judgments.append(legacy_judgment(
        judgment_id="DTS-YI-001", system="ZI_PING", school="DI_TIAN_SUI",
        judgment_type="STEM_IMAGE", match_mode="CONDITION",
        conditions=[MatchCondition("ZP.DAY_MASTER", "EQ", "YI")],
        feature_requirements=["ZP.DAY_MASTER"], specificity=10,
        classical="乙木虽柔，刲羊解牛，怀丁抱丙，跨鸡乘猴。",
        semantic_keys=["WOOD", "FLEXIBILITY", "FIRE", "METAL"],
        book="滴天髓", chapter="乙木章", source_locator="滴天髓/乙木章",
    ))

    judgments.append(legacy_judgment(
        judgment_id="DTS-REN-001", system="ZI_PING", school="DI_TIAN_SUI",
        judgment_type="QI_SHI", match_mode="CONDITION",
        conditions=[MatchCondition("ZP.YEAR_STEM", "EQ", "REN")],
        feature_requirements=["ZP.YEAR_STEM"], specificity=10,
        classical="壬水汪洋，周流不滞，能生甲木，能克丙火。",
        semantic_keys=["WATER", "FLOW", "RESOURCE", "EXPANSIVENESS"],
        book="滴天髓", chapter="壬水章", source_locator="滴天髓/壬水章",
    ))

    judgments.append(legacy_judgment(
        judgment_id="DTS-GUI-001", system="ZI_PING", school="DI_TIAN_SUI",
        judgment_type="QI_SHI", match_mode="CONDITION",
        conditions=[MatchCondition("ZP.MONTH_STEM", "EQ", "GUI")],
        feature_requirements=["ZP.MONTH_STEM"], specificity=10,
        classical="癸水至弱，达于天津，得龙而运，功化斯神。",
        semantic_keys=["WATER", "GENTLENESS", "YIN", "TRANSFORMATION"],
        book="滴天髓", chapter="癸水章", source_locator="滴天髓/癸水章",
    ))

    # GRAPH (3条) - 气势/结构
    judgments.append(legacy_judgment(
        judgment_id="DTS-WATER-ABUNDANT-001", system="ZI_PING", school="DI_TIAN_SUI",
        judgment_type="QI_SHI", match_mode="GRAPH",
        conditions=[
            MatchCondition("ZP.YEAR_STEM", "EQ", "GUI"),
            MatchCondition("ZP.MONTH_STEM", "EQ", "REN"),
            MatchCondition("ZP.HOUR_STEM", "EQ", "REN"),
        ],
        feature_requirements=["ZP.YEAR_STEM", "ZP.MONTH_STEM", "ZP.HOUR_STEM"],
        specificity=30,
        classical="三水并透，汪洋之势，喜木泄秀，忌火土交战。",
        semantic_keys=["WATER", "ABUNDANT", "EXPRESSION", "BALANCE"],
        book="滴天髓", chapter="气势篇", source_locator="滴天髓/气势篇/三水并透",
    ))

    judgments.append(legacy_judgment(
        judgment_id="DTS-FIRE-EARTH-001", system="ZI_PING", school="DI_TIAN_SUI",
        judgment_type="STRUCTURE_LEVEL", match_mode="GRAPH",
        conditions=[
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "XU"),
            MatchCondition("ZP.DAY_BRANCH", "EQ", "WEI"),
            MatchCondition("ZP.HOUR_BRANCH", "EQ", "WU"),
        ],
        feature_requirements=["ZP.MONTH_BRANCH", "ZP.DAY_BRANCH", "ZP.HOUR_BRANCH"],
        specificity=30,
        classical="戌未午三会火土，燥气当权，喜水润局，忌木助火。",
        semantic_keys=["FIRE", "EARTH", "DRYNESS", "HARMONIZATION"],
        book="滴天髓", chapter="结构篇", source_locator="滴天髓/结构篇/火土三会",
    ))

    judgments.append(legacy_judgment(
        judgment_id="DTS-HAI-WEI-WOOD-001", system="ZI_PING", school="DI_TIAN_SUI",
        judgment_type="STRUCTURE_LEVEL", match_mode="GRAPH",
        conditions=[
            MatchCondition("ZP.YEAR_BRANCH", "EQ", "HAI"),
            MatchCondition("ZP.DAY_BRANCH", "EQ", "WEI"),
        ],
        feature_requirements=["ZP.YEAR_BRANCH", "ZP.DAY_BRANCH"],
        specificity=20,
        classical="亥未拱木，暗生乙木，得根而旺，喜火通明。",
        semantic_keys=["WOOD", "ROOT", "HARMONY", "EXPRESSION"],
        book="滴天髓", chapter="结构篇", source_locator="滴天髓/结构篇/亥未拱木",
    ))

    # COMPOSITE (2条)
    judgments.append(legacy_judgment(
        judgment_id="DTS-YI-XU-COMPOSITE-001", system="ZI_PING", school="DI_TIAN_SUI",
        judgment_type="STRUCTURE_LEVEL", match_mode="COMPOSITE",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "XU"),
            MatchCondition("ZP.YEAR_STEM", "EQ", "GUI"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH", "ZP.YEAR_STEM"],
        specificity=30,
        classical="乙木生戌月，癸水透年，燥中有润，才官印全，格局可观。",
        semantic_keys=["WOOD", "EARTH", "WATER", "BALANCE", "STRUCTURE"],
        book="滴天髓", chapter="格局篇", source_locator="滴天髓/格局篇/乙木戌月癸透",
    ))

    judgments.append(legacy_judgment(
        judgment_id="DTS-YI-RENWU-COMPOSITE-001", system="ZI_PING", school="DI_TIAN_SUI",
        judgment_type="QI_SHI", match_mode="COMPOSITE",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.HOUR_STEM", "EQ", "REN"),
            MatchCondition("ZP.HOUR_BRANCH", "EQ", "WU"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.HOUR_STEM", "ZP.HOUR_BRANCH"],
        specificity=30,
        classical="乙木日，壬午时，印绶带食神，水火既济，文秀之象。",
        semantic_keys=["WOOD", "WATER", "FIRE", "HARMONY", "EXPRESSION"],
        book="滴天髓", chapter="气势篇", source_locator="滴天髓/气势篇/乙木壬午时",
    ))

    # STEM_IMAGE (2条)
    judgments.append(legacy_judgment(
        judgment_id="DTS-YI-IMAGE-002", system="ZI_PING", school="DI_TIAN_SUI",
        judgment_type="STEM_IMAGE", match_mode="CONDITION",
        conditions=[MatchCondition("ZP.DAY_STEM", "EQ", "YI")],
        feature_requirements=["ZP.DAY_STEM"], specificity=10,
        classical="乙木为花草之木，性柔而韧，喜向阳，忌寒风。",
        semantic_keys=["WOOD", "FLEXIBILITY", "GROWTH", "SUNLIGHT"],
        book="滴天髓", chapter="十干取象", source_locator="滴天髓/十干取象/乙木",
    ))

    judgments.append(legacy_judgment(
        judgment_id="DTS-REN-IMAGE-002", system="ZI_PING", school="DI_TIAN_SUI",
        judgment_type="STEM_IMAGE", match_mode="CONDITION",
        conditions=[MatchCondition("ZP.MONTH_STEM", "EQ", "REN")],
        feature_requirements=["ZP.MONTH_STEM"], specificity=10,
        classical="壬水为江河之水，奔流不息，喜东方木泄，忌西方土塞。",
        semantic_keys=["WATER", "FLOW", "DIRECTION", "MOVEMENT"],
        book="滴天髓", chapter="十干取象", source_locator="滴天髓/十干取象/壬水",
    ))

    # ========================================================================
    # 子平真诠 (10条): 4 PATTERN + 3 PATTERN_SUCCESS + 3 USE_GOD
    # ========================================================================

    # PATTERN (4条)
    judgments.append(legacy_judgment(
        judgment_id="ZPZQ-ZHENG-CAI-001", system="ZI_PING", school="ZI_PING_ZHEN_QUAN",
        judgment_type="PATTERN", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "XU"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH"],
        specificity=20,
        classical="乙木生戌月，戊土当权，为正财格。",
        semantic_keys=["PATTERN", "WEALTH", "EARTH", "STRUCTURE"],
        book="子平真诠", chapter="论正财格", source_locator="子平真诠/论正财格",
    ))

    judgments.append(legacy_judgment(
        judgment_id="ZPZQ-PIAN-CAI-001", system="ZI_PING", school="ZI_PING_ZHEN_QUAN",
        judgment_type="PATTERN", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "WEI"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH"],
        specificity=20,
        classical="乙木生未月，己土当权，为偏财格。",
        semantic_keys=["PATTERN", "WEALTH", "EARTH", "STRUCTURE"],
        book="子平真诠", chapter="论偏财格", source_locator="子平真诠/论偏财格",
    ))

    judgments.append(legacy_judgment(
        judgment_id="ZPZQ-ZHENG-GUAN-001", system="ZI_PING", school="ZI_PING_ZHEN_QUAN",
        judgment_type="PATTERN", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "SHEN"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH"],
        specificity=20,
        classical="乙木生申月，庚金当权，为正官格。",
        semantic_keys=["PATTERN", "AUTHORITY", "METAL", "STRUCTURE"],
        book="子平真诠", chapter="论正官格", source_locator="子平真诠/论正官格",
    ))

    judgments.append(legacy_judgment(
        judgment_id="ZPZQ-PIAN-GUAN-001", system="ZI_PING", school="ZI_PING_ZHEN_QUAN",
        judgment_type="PATTERN", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "YOU"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH"],
        specificity=20,
        classical="乙木生酉月，辛金当权，为七杀格（偏官）。",
        semantic_keys=["PATTERN", "AUTHORITY", "PRESSURE", "METAL", "STRUCTURE"],
        book="子平真诠", chapter="论七杀格", source_locator="子平真诠/论七杀格",
    ))

    # PATTERN_SUCCESS (3条)
    judgments.append(legacy_judgment(
        judgment_id="ZPZQ-ZHENG-CAI-SUCCESS-001", system="ZI_PING", school="ZI_PING_ZHEN_QUAN",
        judgment_type="PATTERN_SUCCESS", match_mode="COMPOSITE",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "XU"),
            MatchCondition("ZP.HOUR_STEM", "EQ", "REN"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH", "ZP.HOUR_STEM"],
        specificity=30,
        classical="正财格，壬水印绶透时，财生官，官生印，印生身，格局流通。",
        semantic_keys=["PATTERN_SUCCESS", "WEALTH", "RESOURCE", "FLOW", "HARMONY"],
        book="子平真诠", chapter="论正财格成败", source_locator="子平真诠/论正财格/成格",
    ))

    judgments.append(legacy_judgment(
        judgment_id="ZPZQ-ZHENG-GUAN-SUCCESS-001", system="ZI_PING", school="ZI_PING_ZHEN_QUAN",
        judgment_type="PATTERN_SUCCESS", match_mode="COMPOSITE",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "SHEN"),
            MatchCondition("ZP.YEAR_STEM", "EQ", "REN"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH", "ZP.YEAR_STEM"],
        specificity=30,
        classical="正官格，壬水印绶透年，官印相生，功名可许。",
        semantic_keys=["PATTERN_SUCCESS", "AUTHORITY", "RESOURCE", "FAME", "HARMONY"],
        book="子平真诠", chapter="论正官格成败", source_locator="子平真诠/论正官格/成格",
    ))

    judgments.append(legacy_judgment(
        judgment_id="ZPZQ-QISHA-SUCCESS-001", system="ZI_PING", school="ZI_PING_ZHEN_QUAN",
        judgment_type="PATTERN_SUCCESS", match_mode="COMPOSITE",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "YOU"),
            MatchCondition("ZP.HOUR_BRANCH", "EQ", "WU"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH", "ZP.HOUR_BRANCH"],
        specificity=30,
        classical="七杀格，午时丁火食神制杀，食神制杀，英雄独压万人。",
        semantic_keys=["PATTERN_SUCCESS", "PRESSURE", "EXPRESSION", "CONTROL", "POWER"],
        book="子平真诠", chapter="论七杀格成败", source_locator="子平真诠/论七杀格/食神制杀",
    ))

    # USE_GOD (3条)
    judgments.append(legacy_judgment(
        judgment_id="ZPZQ-YI-XU-USE-001", system="ZI_PING", school="ZI_PING_ZHEN_QUAN",
        judgment_type="USE_GOD", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "XU"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH"],
        specificity=20,
        classical="乙木生戌月，正财格，身弱喜印比，身强喜食伤财。",
        semantic_keys=["USE_GOD", "BALANCE", "RESOURCE", "EXPRESSION", "WEALTH"],
        book="子平真诠", chapter="论用神", source_locator="子平真诠/论用神/正财格",
    ))

    judgments.append(legacy_judgment(
        judgment_id="ZPZQ-YI-SHEN-USE-001", system="ZI_PING", school="ZI_PING_ZHEN_QUAN",
        judgment_type="USE_GOD", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "SHEN"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH"],
        specificity=20,
        classical="乙木生申月，正官格，喜印绶化官生身，忌财星坏印。",
        semantic_keys=["USE_GOD", "AUTHORITY", "RESOURCE", "PROTECTION", "BALANCE"],
        book="子平真诠", chapter="论用神", source_locator="子平真诠/论用神/正官格",
    ))

    judgments.append(legacy_judgment(
        judgment_id="ZPZQ-YI-YOU-USE-001", system="ZI_PING", school="ZI_PING_ZHEN_QUAN",
        judgment_type="USE_GOD", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "YOU"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH"],
        specificity=20,
        classical="乙木生酉月，七杀格，喜食神制杀，忌财星生杀。",
        semantic_keys=["USE_GOD", "PRESSURE", "EXPRESSION", "CONTROL", "BALANCE"],
        book="子平真诠", chapter="论用神", source_locator="子平真诠/论用神/七杀格",
    ))

    # ========================================================================
    # 穷通宝鉴 (10条): 5 DAY_MASTER+MONTH + 3 CONDITION + 2 COMPOSITE
    # ========================================================================

    # DAY_MASTER+MONTH (5条)
    judgments.append(legacy_judgment(
        judgment_id="QTBJ-YI-XU-001", system="ZI_PING", school="QIONG_TONG_BAO_JIAN",
        judgment_type="TUNING", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "XU"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH"],
        specificity=20,
        classical="乙木戌月，戊土当权，先用癸水，次取丙火。",
        semantic_keys=["TUNING", "WATER", "FIRE", "CLIMATE", "BALANCE"],
        book="穷通宝鉴", chapter="乙木篇", section="戌月乙木",
        source_locator="穷通宝鉴/乙木篇/戌月乙木",
    ))

    judgments.append(legacy_judgment(
        judgment_id="QTBJ-YI-HAI-001", system="ZI_PING", school="QIONG_TONG_BAO_JIAN",
        judgment_type="TUNING", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "HAI"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH"],
        specificity=20,
        classical="乙木亥月，水旺木相，先取丙火，次取戊土。",
        semantic_keys=["TUNING", "FIRE", "EARTH", "WARMTH", "BALANCE"],
        book="穷通宝鉴", chapter="乙木篇", section="亥月乙木",
        source_locator="穷通宝鉴/乙木篇/亥月乙木",
    ))

    judgments.append(legacy_judgment(
        judgment_id="QTBJ-YI-ZI-001", system="ZI_PING", school="QIONG_TONG_BAO_JIAN",
        judgment_type="TUNING", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "ZI"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH"],
        specificity=20,
        classical="乙木子月，寒木向阳，专用丙火，无丙则寒。",
        semantic_keys=["TUNING", "FIRE", "WARMTH", "SUNLIGHT", "VITALITY"],
        book="穷通宝鉴", chapter="乙木篇", section="子月乙木",
        source_locator="穷通宝鉴/乙木篇/子月乙木",
    ))

    judgments.append(legacy_judgment(
        judgment_id="QTBJ-YI-WU-001", system="ZI_PING", school="QIONG_TONG_BAO_JIAN",
        judgment_type="TUNING", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "WU"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH"],
        specificity=20,
        classical="乙木午月，火旺木焚，先取癸水，次取壬水。",
        semantic_keys=["TUNING", "WATER", "COOLING", "PROTECTION", "BALANCE"],
        book="穷通宝鉴", chapter="乙木篇", section="午月乙木",
        source_locator="穷通宝鉴/乙木篇/午月乙木",
    ))

    judgments.append(legacy_judgment(
        judgment_id="QTBJ-YI-MAO-001", system="ZI_PING", school="QIONG_TONG_BAO_JIAN",
        judgment_type="TUNING", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "MAO"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH"],
        specificity=20,
        classical="乙木卯月，木旺秉令，先取庚金，次取丙火。",
        semantic_keys=["TUNING", "METAL", "FIRE", "DISCIPLINE", "EXPRESSION"],
        book="穷通宝鉴", chapter="乙木篇", section="卯月乙木",
        source_locator="穷通宝鉴/乙木篇/卯月乙木",
    ))

    # CONDITION (3条)
    judgments.append(legacy_judgment(
        judgment_id="QTBJ-YI-XU-GUI-001", system="ZI_PING", school="QIONG_TONG_BAO_JIAN",
        judgment_type="MONTH_TUNING", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "XU"),
            MatchCondition("ZP.YEAR_STEM", "EQ", "GUI"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH", "ZP.YEAR_STEM"],
        specificity=30,
        classical="乙木戌月，癸水透年，调候得宜，燥中有润，文章秀发。",
        semantic_keys=["TUNING", "WATER", "HARMONY", "EXPRESSION", "WISDOM"],
        book="穷通宝鉴", chapter="乙木篇", section="戌月乙木/癸透",
        source_locator="穷通宝鉴/乙木篇/戌月乙木/癸水透年",
    ))

    judgments.append(legacy_judgment(
        judgment_id="QTBJ-YI-XU-REN-001", system="ZI_PING", school="QIONG_TONG_BAO_JIAN",
        judgment_type="MONTH_TUNING", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "XU"),
            MatchCondition("ZP.HOUR_STEM", "EQ", "REN"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH", "ZP.HOUR_STEM"],
        specificity=30,
        classical="乙木戌月，壬水透时，调候有力，水源不绝，福泽深厚。",
        semantic_keys=["TUNING", "WATER", "RESOURCE", "SUSTAINABILITY", "BLESSING"],
        book="穷通宝鉴", chapter="乙木篇", section="戌月乙木/壬透",
        source_locator="穷通宝鉴/乙木篇/戌月乙木/壬水透时",
    ))

    judgments.append(legacy_judgment(
        judgment_id="QTBJ-YI-XU-BING-001", system="ZI_PING", school="QIONG_TONG_BAO_JIAN",
        judgment_type="MONTH_TUNING", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "XU"),
            MatchCondition("ZP.HOUR_BRANCH", "EQ", "WU"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH", "ZP.HOUR_BRANCH"],
        specificity=30,
        classical="乙木戌月，午时丁火，丙火调候，木火通明，文彩可观。",
        semantic_keys=["TUNING", "FIRE", "EXPRESSION", "BRILLIANCE", "CREATIVITY"],
        book="穷通宝鉴", chapter="乙木篇", section="戌月乙木/丙火",
        source_locator="穷通宝鉴/乙木篇/戌月乙木/丙火调候",
    ))

    # COMPOSITE (2条)
    judgments.append(legacy_judgment(
        judgment_id="QTBJ-YI-XU-GUI-REN-COMPOSITE-001", system="ZI_PING", school="QIONG_TONG_BAO_JIAN",
        judgment_type="SEASON_ENVIRONMENT", match_mode="COMPOSITE",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "XU"),
            MatchCondition("ZP.YEAR_STEM", "EQ", "GUI"),
            MatchCondition("ZP.HOUR_STEM", "EQ", "REN"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH", "ZP.YEAR_STEM", "ZP.HOUR_STEM"],
        specificity=40,
        classical="乙木戌月，癸壬并透，调候太过，水多木漂，宜取戊土止水。",
        semantic_keys=["TUNING", "WATER", "EXCESS", "EARTH", "CONTROL", "BALANCE"],
        book="穷通宝鉴", chapter="乙木篇", section="戌月乙木/水多",
        source_locator="穷通宝鉴/乙木篇/戌月乙木/癸壬并透",
    ))

    judgments.append(legacy_judgment(
        judgment_id="QTBJ-YI-XU-NO-WATER-001", system="ZI_PING", school="QIONG_TONG_BAO_JIAN",
        judgment_type="SEASON_ENVIRONMENT", match_mode="COMPOSITE",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "XU"),
            MatchCondition("ZP.HOUR_BRANCH", "EQ", "WU"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH", "ZP.HOUR_BRANCH"],
        specificity=30,
        classical="乙木戌月，午时火旺，局中无水，燥土脆金，宜行水运润局。",
        semantic_keys=["TUNING", "DRYNESS", "FIRE", "WATER_NEEDED", "HARMONIZATION"],
        book="穷通宝鉴", chapter="乙木篇", section="戌月乙木/无水",
        source_locator="穷通宝鉴/乙木篇/戌月乙木/局中无水",
    ))

    # ========================================================================
    # 渊海子平 (10条): 4 TEN_GOD + 3 SET + 3 PATTERN_BASIC
    # ========================================================================

    # TEN_GOD (4条)
    judgments.append(legacy_judgment(
        judgment_id="YHZP-ZHENG-CAI-001", system="ZI_PING", school="YUAN_HAI_ZI_PING",
        judgment_type="TEN_GOD", match_mode="CONDITION",
        conditions=[MatchCondition("ZP.DAY_BRANCH_MAIN_TEN_GOD", "EQ", "正财")],
        feature_requirements=["ZP.DAY_BRANCH_MAIN_TEN_GOD"], specificity=15,
        classical="正财坐日支，妻贤子孝，勤俭持家，财源稳定。",
        semantic_keys=["WEALTH", "STABILITY", "FAMILY", "DILIGENCE"],
        book="渊海子平", chapter="论十神", section="正财",
        source_locator="渊海子平/论十神/正财",
    ))

    judgments.append(legacy_judgment(
        judgment_id="YHZP-PIAN-CAI-001", system="ZI_PING", school="YUAN_HAI_ZI_PING",
        judgment_type="TEN_GOD", match_mode="CONDITION",
        conditions=[MatchCondition("ZP.DAY_BRANCH_MAIN_TEN_GOD", "EQ", "偏财")],
        feature_requirements=["ZP.DAY_BRANCH_MAIN_TEN_GOD"], specificity=15,
        classical="偏财坐日支，慷慨好施，人缘广阔，意外之财。",
        semantic_keys=["WEALTH", "GENEROSITY", "SOCIAL", "OPPORTUNITY"],
        book="渊海子平", chapter="论十神", section="偏财",
        source_locator="渊海子平/论十神/偏财",
    ))

    judgments.append(legacy_judgment(
        judgment_id="YHZP-ZHENG-YIN-001", system="ZI_PING", school="YUAN_HAI_ZI_PING",
        judgment_type="TEN_GOD", match_mode="CONDITION",
        conditions=[MatchCondition("ZP.DAY_BRANCH_MAIN_TEN_GOD", "EQ", "正印")],
        feature_requirements=["ZP.DAY_BRANCH_MAIN_TEN_GOD"], specificity=15,
        classical="正印坐日支，仁慈宽厚，学识渊博，贵人扶持。",
        semantic_keys=["RESOURCE", "WISDOM", "KINDNESS", "SUPPORT", "LEARNING"],
        book="渊海子平", chapter="论十神", section="正印",
        source_locator="渊海子平/论十神/正印",
    ))

    judgments.append(legacy_judgment(
        judgment_id="YHZP-SHANG-GUAN-001", system="ZI_PING", school="YUAN_HAI_ZI_PING",
        judgment_type="TEN_GOD", match_mode="CONDITION",
        conditions=[MatchCondition("ZP.DAY_BRANCH_MAIN_TEN_GOD", "EQ", "伤官")],
        feature_requirements=["ZP.DAY_BRANCH_MAIN_TEN_GOD"], specificity=15,
        classical="伤官坐日支，聪明伶俐，才华横溢，傲气凌人。",
        semantic_keys=["EXPRESSION", "CREATIVITY", "INTELLIGENCE", "PRIDE", "AUTONOMY"],
        book="渊海子平", chapter="论十神", section="伤官",
        source_locator="渊海子平/论十神/伤官",
    ))

    # SET (3条)
    judgments.append(legacy_judgment(
        judgment_id="YHZP-THREE-SEALS-001", system="ZI_PING", school="YUAN_HAI_ZI_PING",
        judgment_type="TEN_GOD_STRUCTURE", match_mode="SET",
        conditions=[
            MatchCondition("ZP.YEAR_STEM", "IN", ["REN", "GUI"]),
            MatchCondition("ZP.MONTH_STEM", "IN", ["REN", "GUI"]),
            MatchCondition("ZP.HOUR_STEM", "IN", ["REN", "GUI"]),
        ],
        feature_requirements=["ZP.YEAR_STEM", "ZP.MONTH_STEM", "ZP.HOUR_STEM"],
        specificity=30,
        classical="三印并透，学识过人，文章盖世，惟恐印多身弱，反成迂腐。",
        semantic_keys=["RESOURCE", "LEARNING", "WISDOM", "EXCESS", "BALANCE"],
        book="渊海子平", chapter="论印绶", section="三印并透",
        source_locator="渊海子平/论印绶/三印并透",
    ))

    judgments.append(legacy_judgment(
        judgment_id="YHZP-WEALTH-OFFICER-001", system="ZI_PING", school="YUAN_HAI_ZI_PING",
        judgment_type="TEN_GOD_STRUCTURE", match_mode="SET",
        conditions=[
            MatchCondition("ZP.MONTH_BRANCH", "IN", ["XU", "WEI", "CHOU", "CHEN"]),
            MatchCondition("ZP.HOUR_BRANCH", "IN", ["SHEN", "YOU"]),
        ],
        feature_requirements=["ZP.MONTH_BRANCH", "ZP.HOUR_BRANCH"],
        specificity=25,
        classical="财官双美，月令财星，时支官星，财生官旺，功名可许。",
        semantic_keys=["WEALTH", "AUTHORITY", "FAME", "HARMONY", "SUCCESS"],
        book="渊海子平", chapter="论财官", section="财官双美",
        source_locator="渊海子平/论财官/财官双美",
    ))

    judgments.append(legacy_judgment(
        judgment_id="YHZP-FOOD-WEALTH-001", system="ZI_PING", school="YUAN_HAI_ZI_PING",
        judgment_type="TEN_GOD_STRUCTURE", match_mode="SET",
        conditions=[
            MatchCondition("ZP.HOUR_BRANCH", "IN", ["SI", "WU"]),
            MatchCondition("ZP.MONTH_BRANCH", "IN", ["XU", "WEI", "CHOU", "CHEN"]),
        ],
        feature_requirements=["ZP.HOUR_BRANCH", "ZP.MONTH_BRANCH"],
        specificity=25,
        classical="食神生财，时支食伤，月令财星，财源广进，衣食丰足。",
        semantic_keys=["EXPRESSION", "WEALTH", "ABUNDANCE", "SUSTAINABILITY", "COMFORT"],
        book="渊海子平", chapter="论食神", section="食神生财",
        source_locator="渊海子平/论食神/食神生财",
    ))

    # PATTERN_BASIC (3条)
    judgments.append(legacy_judgment(
        judgment_id="YHZP-ZHENG-CAI-PATTERN-001", system="ZI_PING", school="YUAN_HAI_ZI_PING",
        judgment_type="PATTERN_BASIC", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "XU"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH"],
        specificity=20,
        classical="乙木生戌月，戊土司令，为正财格。正财者，乃我克之阳干，见之则财禄丰盈。",
        semantic_keys=["PATTERN", "WEALTH", "EARTH", "PROSPERITY", "STABILITY"],
        book="渊海子平", chapter="论格局", section="正财格",
        source_locator="渊海子平/论格局/正财格",
    ))

    judgments.append(legacy_judgment(
        judgment_id="YHZP-PIAN-CAI-PATTERN-001", system="ZI_PING", school="YUAN_HAI_ZI_PING",
        judgment_type="PATTERN_BASIC", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "WEI"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH"],
        specificity=20,
        classical="乙木生未月，己土司令，为偏财格。偏财者，乃我克之阴干，见之则横财易发。",
        semantic_keys=["PATTERN", "WEALTH", "EARTH", "OPPORTUNITY", "FLEXIBILITY"],
        book="渊海子平", chapter="论格局", section="偏财格",
        source_locator="渊海子平/论格局/偏财格",
    ))

    judgments.append(legacy_judgment(
        judgment_id="YHZP-ZHENG-GUAN-PATTERN-001", system="ZI_PING", school="YUAN_HAI_ZI_PING",
        judgment_type="PATTERN_BASIC", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "SHEN"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH"],
        specificity=20,
        classical="乙木生申月，庚金司令，为正官格。正官者，乃克我之阳干，见之则功名显达。",
        semantic_keys=["PATTERN", "AUTHORITY", "METAL", "FAME", "DISCIPLINE"],
        book="渊海子平", chapter="论格局", section="正官格",
        source_locator="渊海子平/论格局/正官格",
    ))

    # ========================================================================
    # 三命通会 (10条): 8 EXACT DAY_TIME + 2 COMPOSITE
    # ========================================================================

    # EXACT DAY_TIME (8条)
    judgments.append(legacy_judgment(
        judgment_id="SMTH-YIWEI-RENWU-001", system="ZI_PING", school="SAN_MING_TONG_HUI",
        judgment_type="DAY_TIME", match_mode="EXACT",
        conditions=[
            MatchCondition("ZP.DAY_PILLAR", "EQ", "YI_WEI"),
            MatchCondition("ZP.HOUR_PILLAR", "EQ", "REN_WU"),
        ],
        feature_requirements=["ZP.DAY_PILLAR", "ZP.HOUR_PILLAR"],
        specificity=40,
        classical="六乙日壬午时断：乙日壬午时，印绶带食神，丁己庚辛俱不见，名利有成。",
        semantic_keys=["CAREER", "STATUS", "RESOURCE", "OUTPUT", "SUCCESS"],
        book="三命通会", chapter="卷三", section="六乙日壬午时断",
        source_locator="三命通会/卷三/六乙日壬午时断",
    ))

    judgments.append(legacy_judgment(
        judgment_id="SMTH-YIWEI-GUIWU-001", system="ZI_PING", school="SAN_MING_TONG_HUI",
        judgment_type="DAY_TIME", match_mode="EXACT",
        conditions=[
            MatchCondition("ZP.DAY_PILLAR", "EQ", "YI_WEI"),
            MatchCondition("ZP.HOUR_PILLAR", "EQ", "GUI_WU"),
        ],
        feature_requirements=["ZP.DAY_PILLAR", "ZP.HOUR_PILLAR"],
        specificity=40,
        classical="六乙日癸未时断：乙日癸未时，偏印带偏财，身旺遇此，财禄丰足。",
        semantic_keys=["WEALTH", "RESOURCE", "ABUNDANCE", "STABILITY", "COMFORT"],
        book="三命通会", chapter="卷三", section="六乙日癸未时断",
        source_locator="三命通会/卷三/六乙日癸未时断",
    ))

    judgments.append(legacy_judgment(
        judgment_id="SMTH-YIHAI-RENWU-001", system="ZI_PING", school="SAN_MING_TONG_HUI",
        judgment_type="DAY_TIME", match_mode="EXACT",
        conditions=[
            MatchCondition("ZP.DAY_PILLAR", "EQ", "YI_HAI"),
            MatchCondition("ZP.HOUR_PILLAR", "EQ", "REN_WU"),
        ],
        feature_requirements=["ZP.DAY_PILLAR", "ZP.HOUR_PILLAR"],
        specificity=40,
        classical="六乙日壬午时断（乙亥日）：乙亥壬午时，木火通明，文章秀发，名利双收。",
        semantic_keys=["EXPRESSION", "BRILLIANCE", "FAME", "SUCCESS", "CREATIVITY"],
        book="三命通会", chapter="卷三", section="六乙日壬午时断/乙亥",
        source_locator="三命通会/卷三/六乙日壬午时断/乙亥日",
    ))

    judgments.append(legacy_judgment(
        judgment_id="SMTH-YISI-RENWU-001", system="ZI_PING", school="SAN_MING_TONG_HUI",
        judgment_type="DAY_TIME", match_mode="EXACT",
        conditions=[
            MatchCondition("ZP.DAY_PILLAR", "EQ", "YI_SI"),
            MatchCondition("ZP.HOUR_PILLAR", "EQ", "REN_WU"),
        ],
        feature_requirements=["ZP.DAY_PILLAR", "ZP.HOUR_PILLAR"],
        specificity=40,
        classical="六乙日壬午时断（乙巳日）：乙巳壬午时，伤官佩印，聪明机巧，技艺过人。",
        semantic_keys=["EXPRESSION", "INTELLIGENCE", "SKILL", "CREATIVITY", "AUTONOMY"],
        book="三命通会", chapter="卷三", section="六乙日壬午时断/乙巳",
        source_locator="三命通会/卷三/六乙日壬午时断/乙巳日",
    ))

    judgments.append(legacy_judgment(
        judgment_id="SMTH-YIMAOW-001", system="ZI_PING", school="SAN_MING_TONG_HUI",
        judgment_type="DAY_TIME", match_mode="EXACT",
        conditions=[
            MatchCondition("ZP.DAY_PILLAR", "EQ", "YI_MAO"),
            MatchCondition("ZP.HOUR_PILLAR", "EQ", "REN_WU"),
        ],
        feature_requirements=["ZP.DAY_PILLAR", "ZP.HOUR_PILLAR"],
        specificity=40,
        classical="六乙日壬午时断（乙卯日）：乙卯壬午时，建禄带印，身旺用财，富贵双全。",
        semantic_keys=["WEALTH", "AUTHORITY", "BALANCE", "SUCCESS", "PROSPERITY"],
        book="三命通会", chapter="卷三", section="六乙日壬午时断/乙卯",
        source_locator="三命通会/卷三/六乙日壬午时断/乙卯日",
    ))

    judgments.append(legacy_judgment(
        judgment_id="SMTH-YIYOU-RENWU-001", system="ZI_PING", school="SAN_MING_TONG_HUI",
        judgment_type="DAY_TIME", match_mode="EXACT",
        conditions=[
            MatchCondition("ZP.DAY_PILLAR", "EQ", "YI_YOU"),
            MatchCondition("ZP.HOUR_PILLAR", "EQ", "REN_WU"),
        ],
        feature_requirements=["ZP.DAY_PILLAR", "ZP.HOUR_PILLAR"],
        specificity=40,
        classical="六乙日壬午时断（乙酉日）：乙酉壬午时，七杀化印，武职显达，威权万里。",
        semantic_keys=["AUTHORITY", "POWER", "PRESSURE", "TRANSFORMATION", "MILITARY"],
        book="三命通会", chapter="卷三", section="六乙日壬午时断/乙酉",
        source_locator="三命通会/卷三/六乙日壬午时断/乙酉日",
    ))

    judgments.append(legacy_judgment(
        judgment_id="SMTH-YISHEN-RENWU-001", system="ZI_PING", school="SAN_MING_TONG_HUI",
        judgment_type="DAY_TIME", match_mode="EXACT",
        conditions=[
            MatchCondition("ZP.DAY_PILLAR", "EQ", "YI_SHEN"),
            MatchCondition("ZP.HOUR_PILLAR", "EQ", "REN_WU"),
        ],
        feature_requirements=["ZP.DAY_PILLAR", "ZP.HOUR_PILLAR"],
        specificity=40,
        classical="六乙日壬午时断（甲申日）：甲申壬午时，正官佩印，文职清贵，声名远播。",
        semantic_keys=["AUTHORITY", "FAME", "CIVIL_SERVICE", "DIGNITY", "REPUTATION"],
        book="三命通会", chapter="卷三", section="六乙日壬午时断/甲申",
        source_locator="三命通会/卷三/六乙日壬午时断/甲申日",
    ))

    judgments.append(legacy_judgment(
        judgment_id="SMTH-YICHEN-RENWU-001", system="ZI_PING", school="SAN_MING_TONG_HUI",
        judgment_type="DAY_TIME", match_mode="EXACT",
        conditions=[
            MatchCondition("ZP.DAY_PILLAR", "EQ", "YI_CHEN"),
            MatchCondition("ZP.HOUR_PILLAR", "EQ", "REN_WU"),
        ],
        feature_requirements=["ZP.DAY_PILLAR", "ZP.HOUR_PILLAR"],
        specificity=40,
        classical="六乙日壬午时断（甲辰日）：甲辰壬午时，余气带印，温和敦厚，福禄绵长。",
        semantic_keys=["HARMONY", "STABILITY", "KINDNESS", "BLESSING", "LONGEVITY"],
        book="三命通会", chapter="卷三", section="六乙日壬午时断/甲辰",
        source_locator="三命通会/卷三/六乙日壬午时断/甲辰日",
    ))

    # COMPOSITE (2条)
    judgments.append(legacy_judgment(
        judgment_id="SMTH-YIWEI-RENWU-XU-001", system="ZI_PING", school="SAN_MING_TONG_HUI",
        judgment_type="DAY_TIME_COMBO", match_mode="COMPOSITE",
        conditions=[
            MatchCondition("ZP.DAY_PILLAR", "EQ", "YI_WEI"),
            MatchCondition("ZP.HOUR_PILLAR", "EQ", "REN_WU"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "XU"),
        ],
        feature_requirements=["ZP.DAY_PILLAR", "ZP.HOUR_PILLAR", "ZP.MONTH_BRANCH"],
        specificity=50,
        classical="乙未日壬午时，戌月生，财官印全，三奇得位，富贵双全之命。",
        semantic_keys=["WEALTH", "AUTHORITY", "RESOURCE", "COMPLETENESS", "PROSPERITY"],
        book="三命通会", chapter="卷三", section="六乙日壬午时断/戌月",
        source_locator="三命通会/卷三/六乙日壬午时断/戌月",
    ))

    judgments.append(legacy_judgment(
        judgment_id="SMTH-YIWEI-RENWU-HAI-001", system="ZI_PING", school="SAN_MING_TONG_HUI",
        judgment_type="DAY_TIME_COMBO", match_mode="COMPOSITE",
        conditions=[
            MatchCondition("ZP.DAY_PILLAR", "EQ", "YI_WEI"),
            MatchCondition("ZP.HOUR_PILLAR", "EQ", "REN_WU"),
            MatchCondition("ZP.YEAR_BRANCH", "EQ", "HAI"),
        ],
        feature_requirements=["ZP.DAY_PILLAR", "ZP.HOUR_PILLAR", "ZP.YEAR_BRANCH"],
        specificity=50,
        classical="乙未日壬午时，亥年生，亥未拱木，暗助日主，印绶得根，文秀之命。",
        semantic_keys=["RESOURCE", "ROOT", "HARMONY", "EXPRESSION", "WISDOM"],
        book="三命通会", chapter="卷三", section="六乙日壬午时断/亥年",
        source_locator="三命通会/卷三/六乙日壬午时断/亥年",
    ))

    # 添加所有断言到库
    for j in judgments:
        library.add(j)

    return library


if __name__ == "__main__":
    print("=" * 70)
    print("P6-C-3C-2 50条五经典Vertical Slice断言库")
    print("=" * 70)

    library = build_vertical_slice_library()
    stats = library.stats()
    print(f"\n断言总数: {stats['total']}")
    print(f"\n按school分布:")
    for school, count in stats['by_school'].items():
        print(f"  {school}: {count}")

    # 按经典统计
    from tongshu.judgment_architecture.system_school_contract import ZIPING_SCHOOL_NAMES, ZiPingSchool
    print(f"\n按经典名称统计:")
    for school_key, count in stats['by_school'].items():
        if school_key.startswith("ZI_PING:"):
            school_name = school_key.split(":", 1)[1]
            zh_name = ZIPING_SCHOOL_NAMES.get(ZiPingSchool(school_name), school_name)
            print(f"  {zh_name} ({school_name}): {count}")

    print("\n" + "=" * 70)
    print("50条五经典Vertical Slice断言库建立完成")
    print("=" * 70)
