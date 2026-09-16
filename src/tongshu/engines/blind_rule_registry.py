# -*- coding: utf-8 -*-
"""盲派 Rule Evidence Registry V3.2
基线 commit: 60a733f8
只实现 28 条 ESTABLISHED Rule。禁止新增/推导/评分/Judgment 泄漏。
所有 Rule 输出必须可追溯到 Rule_ID + Evidence_ID。
"""
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set


@dataclass(frozen=True)
class RuleDef:
    """单条 Rule 定义（只读，不可改）"""
    rule_id: str
    evidence_id: str
    layer: str           # L1_STRUCTURE / L2_SYMBOL / L3_MARRIAGE / L4_BODY / L5_MUKU / L6_TIMING
    rule_type: str       # STRUCTURE / SYMBOL / TIMING
    description: str
    preconditions: str
    inputs: str
    rule_logic: str
    assertion: str
    exclusions: str
    status: str = "ESTABLISHED"


# ═══════════════════════════════════════════════════════════
# L1 STRUCTURE（7条）
# ═══════════════════════════════════════════════════════════

R_PJ_001 = RuleDef(
    rule_id="R-PJ-001", evidence_id="EVD-PJ-001",
    layer="L1_STRUCTURE", rule_type="STRUCTURE",
    description="正局判定",
    preconditions="日主做功或日支做功已识别",
    inputs="day_master_work_direction, day_branch_work_direction, original_structure_direction",
    rule_logic="IF (DM_direction == original_direction) OR (DB_direction == original_direction) THEN ZHENG",
    assertion="局型=ZHENG",
    exclusions="不自动推吉；正局≠富贵，只记结构事实",
)

R_PJ_002 = RuleDef(
    rule_id="R-PJ-002", evidence_id="EVD-PJ-002",
    layer="L1_STRUCTURE", rule_type="STRUCTURE",
    description="反局判定",
    preconditions="日主/日支/原局方向已识别",
    inputs="DM_direction, DB_direction, original_direction",
    rule_logic="IF (DM_direction != original_direction) OR (DB_direction != original_direction) OR (DM_direction != DB_direction AND both_act) THEN FAN",
    assertion="局型=FAN",
    exclusions="不自动推凶事；反局只记结构事实，应期层再引动",
)

R_PJ_003 = RuleDef(
    rule_id="R-PJ-003", evidence_id="EVD-PJ-003",
    layer="L1_STRUCTURE", rule_type="TIMING",
    description="岁运冲合反局",
    preconditions="原局已有明确做功方式",
    inputs="original_work_method, luck_year_method",
    rule_logic="IF original==CHONG AND luck==HE THEN FAN_JU_ACTIVE",
    assertion="岁运反局=TRUE/FALSE",
    exclusions="天干合地支冲不反；原局无明确制不反",
)

R_ZB_001 = RuleDef(
    rule_id="R-ZB-001", evidence_id="EVD-ZB-001",
    layer="L1_STRUCTURE", rule_type="STRUCTURE",
    description="贼神捕神结构",
    preconditions="宾主体用已识别",
    inputs="main_strength, guest_strength, main_kills_guest, guest_rootless",
    rule_logic="IF main>guest AND main_kills_guest AND guest_rootless THEN ZEI_BU",
    assertion="robber_catcher=TRUE, catcher=main, robber=guest",
    exclusions="贼捕≠直接大富贵；需叠加其他Rule才进财富层",
)

R_GF_001 = RuleDef(
    rule_id="R-GF-001", evidence_id="EVD-GF-001",
    layer="L1_STRUCTURE", rule_type="STRUCTURE",
    description="功神/废神划分",
    preconditions="做功方向已识别",
    inputs="working_branches, target_branches",
    rule_logic="IF branch IN working OR target THEN GONG_SHEN ELSE FEI_SHEN",
    assertion="每字=功神/废神",
    exclusions="不直接推富贵",
)

R_BZ_001 = RuleDef(
    rule_id="R-BZ-001", evidence_id="EVD-BZ-001",
    layer="L1_STRUCTURE", rule_type="STRUCTURE",
    description="宾主定位",
    preconditions="四柱已排",
    inputs="pillar_position",
    rule_logic="day/hour=MAIN; year/month=GUEST",
    assertion="每柱=MAIN/GUEST",
    exclusions="—",
)

R_TY_001 = RuleDef(
    rule_id="R-TY-001", evidence_id="EVD-TY-001",
    layer="L1_STRUCTURE", rule_type="STRUCTURE",
    description="体用定位",
    preconditions="十神已排",
    inputs="ten_god",
    rule_logic="DM/印/禄/比劫=TI; 财/官杀=YONG; 食伤=NEUTRAL",
    assertion="每十神=TI/YONG/NEUTRAL",
    exclusions="不替代旺衰",
)

# ═══════════════════════════════════════════════════════════
# L2 SYMBOL（7条）
# ═══════════════════════════════════════════════════════════

R_SX_001 = RuleDef(
    rule_id="R-SX-001", evidence_id="EVD-SX-001",
    layer="L2_SYMBOL", rule_type="SYMBOL",
    description="共象原则",
    preconditions="干支象/宫位象/十神象/神煞象已提取",
    inputs="gan_xiang, gongwei_xiang, tenshen_xiang, shensha_xiang",
    rule_logic="IF COUNT(overlapping_xiang)>=2 THEN 共象成立",
    assertion="该字象=intersection_meaning",
    exclusions="只有一类象=不立",
)

R_SX_002 = RuleDef(
    rule_id="R-SX-002", evidence_id="EVD-SX-002",
    layer="L2_SYMBOL", rule_type="SYMBOL",
    description="合象原则",
    preconditions="原局有合",
    inputs="he_pair",
    rule_logic="IF 合绊成立 THEN 双方互取象",
    assertion="合绊双方象=A+B复合象",
    exclusions="无根之合不立",
)

R_SX_003 = RuleDef(
    rule_id="R-SX-003", evidence_id="EVD-SX-003",
    layer="L2_SYMBOL", rule_type="SYMBOL",
    description="化象原则",
    preconditions="有生/三合/半合",
    inputs="source_element, target_element",
    rule_logic="阴木→火=纺织; 阳木→火=家具; 辰→子=化工",
    assertion="转化象",
    exclusions="—",
)

R_SX_004 = RuleDef(
    rule_id="R-SX-004", evidence_id="EVD-SX-004",
    layer="L2_SYMBOL", rule_type="SYMBOL",
    description="墓象原则",
    preconditions="有墓库",
    inputs="mu_god, mu_branch",
    rule_logic="七杀入羊刃墓=军队; 食伤入墓=学校; 财入墓=地产",
    assertion="墓象",
    exclusions="空库/实库另分",
)

R_SX_005 = RuleDef(
    rule_id="R-SX-005", evidence_id="EVD-SX-005",
    layer="L2_SYMBOL", rule_type="SYMBOL",
    description="制象原则",
    preconditions="有制",
    inputs="controller, controlled, method",
    rule_logic="财库制劫财印库=资本运作; 丑未冲制印库=地产",
    assertion="制象",
    exclusions="—",
)

R_SX_006 = RuleDef(
    rule_id="R-SX-006", evidence_id="EVD-SX-006",
    layer="L2_SYMBOL", rule_type="SYMBOL",
    description="带象原则",
    preconditions="一柱干支同看",
    inputs="upper_gan_ten_god, lower_zhi_ten_god",
    rule_logic="财+官=公家财; 官+财=管财官; 印+官=权力; 印+财=薪水",
    assertion="带象",
    exclusions="—",
)

R_SX_007 = RuleDef(
    rule_id="R-SX-007", evidence_id="EVD-SX-007",
    layer="L2_SYMBOL", rule_type="SYMBOL",
    description="借象原则",
    preconditions="A天干 B通禄 OR 同五行阴阳不同",
    inputs="gan_A, gan_B, tonglu, same_element_diff_yinyang",
    rule_logic="IF (A→B通禄) OR (A/B同五行AND阴阳不同) THEN 借象成立",
    assertion="A↔B symbol_reference=BORROWED",
    exclusions="借象后仍需宫位/十神/做功关系才能定具体象",
)

# ═══════════════════════════════════════════════════════════
# L3 WEALTH（1条）
# ═══════════════════════════════════════════════════════════

R_WEALTH_001 = RuleDef(
    rule_id="R-WEALTH-001", evidence_id="EVD-WEALTH-001",
    layer="L3_WEALTH", rule_type="STRUCTURE",
    description="禄神当财",
    preconditions="命局有禄",
    inputs="lu_present, food_injury_present, wealth_star_present, resource_generates_lu",
    rule_logic="001A: 有禄AND无伤食泄→禄当财; 001B: 无财AND有禄→禄作财富象; 001C: 印生禄→现成之福; 001D: 禄取财AND禄伤→财富受损",
    assertion="禄神=财富候选; 禄伤=财富受损",
    exclusions="喜印忌伤食劫财是结构关系，不得变fortune_score",
)

# ═══════════════════════════════════════════════════════════
# L4 MARRIAGE（2条）
# ═══════════════════════════════════════════════════════════

R_MARRIAGE_001 = RuleDef(
    rule_id="R-MARRIAGE-001", evidence_id="EVD-MARRIAGE-001",
    layer="L4_MARRIAGE", rule_type="TIMING",
    description="结婚应期",
    preconditions="配偶宫/配偶星已定位",
    inputs="spouse_palace, spouse_star, relations",
    rule_logic="001A: 配偶星三合/六合合入配偶宫→婚期候选; 001B: 配偶星天干五合→婚期候选; 001C: 配偶宫↔配偶星刑/冲→婚期候选",
    assertion="MARRIAGE_TIMING_CANDIDATE",
    exclusions="多信号同时出现由Assertion Resolver处理，不直接推结婚",
)

R_MARRIAGE_002 = RuleDef(
    rule_id="R-MARRIAGE-002", evidence_id="EVD-MARRIAGE-002",
    layer="L4_MARRIAGE", rule_type="TIMING",
    description="离婚应期",
    preconditions="原局已有宫星作用结构",
    inputs="palace_controls_star, opposition, balance",
    rule_logic="IF 原局宫→星结构 AND 岁运导致宫星对抗 AND 对抗达平衡 THEN",
    assertion="DIVORCE_TIMING_CANDIDATE",
    exclusions="冲≠离婚充分条件；必须是宫星对抗+平衡",
)

# ═══════════════════════════════════════════════════════════
# L5 BODY/DISASTER（4条）
# ═══════════════════════════════════════════════════════════

R_BODY_001 = RuleDef(
    rule_id="R-BODY-001", evidence_id="EVD-BODY-001",
    layer="L5_BODY", rule_type="SYMBOL",
    description="宫位→身体部位",
    preconditions="—",
    inputs="pillar_position",
    rule_logic="年→腿足; 月→躯干; 日支→内脏; 时→头面",
    assertion="宫位→身体部位映射",
    exclusions="—",
)

R_BODY_002 = RuleDef(
    rule_id="R-BODY-002", evidence_id="EVD-BODY-002",
    layer="L5_BODY", rule_type="SYMBOL",
    description="十干→身体类象",
    preconditions="—",
    inputs="stem",
    rule_logic="LOOKUP: 甲乙丙丁戊已封; 己庚辛壬癸待补",
    assertion="十干→身体部位象集合",
    exclusions="Symbol Assertion≠疾病Assertion; 甲→肝胆≠甲→肝病",
)

R_BODY_003 = RuleDef(
    rule_id="R-BODY-003", evidence_id="EVD-BODY-003",
    layer="L5_BODY", rule_type="SYMBOL",
    description="十二支→身体类象",
    preconditions="—",
    inputs="branch",
    rule_logic="LOOKUP: 子丑午申酉戌亥已封; 寅卯辰巳未待补",
    assertion="十二支→身体部位象集合",
    exclusions="只出象不出病种",
)

R_DISASTER_001 = RuleDef(
    rule_id="R-DISASTER-001", evidence_id="EVD-DISASTER-001",
    layer="L5_BODY", rule_type="STRUCTURE",
    description="牢狱/灾厄结构(拆5条)",
    preconditions="原局结构已识别",
    inputs="harmful_branches, water_level, metal_sinks, yinshou_duoshi, rob_hurt_officer, reverse_structure",
    rule_logic="001A: 亥丑辰+阳性有用之物被坏→牢狱; 001B: 水多金沉→牢狱; 001C: 枭神夺食→失自由; 001D: 劫财+伤官+抗官杀→牢狱; 001E: 反局+辰丑→多数应牢狱(CONDITIONAL)",
    assertion="PRISON_RISK / FREEDOM_LOSS",
    exclusions="001E是CONDITIONAL不是充分条件; assertion_strength=STRONG/CONDITIONAL",
)

# ═══════════════════════════════════════════════════════════
# L6 SHENCHA（5条）
# ═══════════════════════════════════════════════════════════

R_SHEN_001 = RuleDef(
    rule_id="R-SHEN-001", evidence_id="EVD-SHEN-001",
    layer="L6_SHENCHA", rule_type="SYMBOL",
    description="禄神",
    preconditions="—",
    inputs="stem, branch",
    rule_logic="禄=十干临官之地",
    assertion="禄象",
    exclusions="—",
)

R_SHEN_002 = RuleDef(
    rule_id="R-SHEN-002", evidence_id="EVD-SHEN-002",
    layer="L6_SHENCHA", rule_type="SYMBOL",
    description="羊刃",
    preconditions="—",
    inputs="stem, branch",
    rule_logic="刃=十干帝旺之地",
    assertion="刃象",
    exclusions="—",
)

R_SHEN_003 = RuleDef(
    rule_id="R-SHEN-003", evidence_id="EVD-SHEN-003",
    layer="L6_SHENCHA", rule_type="SYMBOL",
    description="墓库",
    preconditions="—",
    inputs="branch",
    rule_logic="辰戌丑未=收藏控制",
    assertion="墓库象",
    exclusions="—",
)

R_SHEN_004 = RuleDef(
    rule_id="R-SHEN-004", evidence_id="EVD-SHEN-004",
    layer="L6_SHENCHA", rule_type="SYMBOL",
    description="驿马",
    preconditions="—",
    inputs="day_branch_sanju",
    rule_logic="申子辰→寅午戌; 寅午戌→申子辰; 巳酉丑→亥卯未; 亥卯未→巳酉丑",
    assertion="驿马象=迁移/奔波",
    exclusions="—",
)

R_SHEN_005 = RuleDef(
    rule_id="R-SHEN-005", evidence_id="EVD-SHEN-005",
    layer="L6_SHENCHA", rule_type="SYMBOL",
    description="空亡",
    preconditions="—",
    inputs="day_pillar_xunkong",
    rule_logic="IF 日柱旬空 THEN 空亡成立",
    assertion="空亡象=虚/不实/减半",
    exclusions="—",
)

# ═══════════════════════════════════════════════════════════
# L7 MUKU（3条）
# ═══════════════════════════════════════════════════════════

R_MUKU_001 = RuleDef(
    rule_id="R-MUKU-001", evidence_id="EVD-MUKU-001",
    layer="L7_MUKU", rule_type="STRUCTURE",
    description="墓库识别",
    preconditions="四柱已排",
    inputs="branch, pillar_position, hidden_stems",
    rule_logic="001A: 辰戌丑未→MUKU_PRESENT; 001B: 未受刑冲=墓(死), 受刑冲=库(活); 001C: 按藏干定类型; 001D: 按宫位定归属",
    assertion="MUKU_PRESENT/MUKU_STATE/MUKU_TYPE/MUKU_OWNER",
    exclusions="墓库≠财库；所有墓库不得统称财库",
)

R_MUKU_002 = RuleDef(
    rule_id="R-MUKU-002", evidence_id="EVD-MUKU-002",
    layer="L7_MUKU", rule_type="STRUCTURE",
    description="刑冲开库",
    preconditions="MUKU_PRESENT",
    inputs="muku_branch, xing_or_chong, muku_owner",
    rule_logic="002A: MUKU+冲/刑→MUKU_OPENED; 002B: OPEN_METHOD∈{冲,刑}; 002C: 冲自己库=取财, 冲宾位库=财可能被冲走",
    assertion="MUKU_OPENED/OPEN_METHOD/OPEN_OWNER",
    exclusions="MUKU_OPENED≠WEALTH_GAIN; 合库=闭库; 穿库不进核心Rule",
)

R_MUKU_003 = RuleDef(
    rule_id="R-MUKU-003", evidence_id="EVD-MUKU-003",
    layer="L7_MUKU", rule_type="TIMING",
    description="岁运引动墓库",
    preconditions="原局MUKU_PRESENT",
    inputs="natal_muku, luck_pillar, year_pillar",
    rule_logic="IF 原局墓库 AND 岁运有效刑/冲 AND 命中原局墓库 THEN",
    assertion="TIMING_ASSERTION=MUKU_OPENED_TIMING",
    exclusions="大运到墓位≠开库(只是墓到位); 必须流年/大运刑冲命中才算",
)

# ═══════════════════════════════════════════════════════════
# Registry（28条 ESTABLISHED）
# ═══════════════════════════════════════════════════════════

RULE_REGISTRY: Dict[str, RuleDef] = {r.rule_id: r for r in [
    R_PJ_001, R_PJ_002, R_PJ_003, R_ZB_001, R_GF_001, R_BZ_001, R_TY_001,  # L1 7
    R_SX_001, R_SX_002, R_SX_003, R_SX_004, R_SX_005, R_SX_006, R_SX_007,  # L2 7
    R_WEALTH_001,  # L3 1
    R_MARRIAGE_001, R_MARRIAGE_002,  # L4 2
    R_BODY_001, R_BODY_002, R_BODY_003, R_DISASTER_001,  # L5 4
    R_SHEN_001, R_SHEN_002, R_SHEN_003, R_SHEN_004, R_SHEN_005,  # L6 5
    R_MUKU_001, R_MUKU_002, R_MUKU_003,  # L7 3
]}

FORBIDDEN_RULES = {
    "WEALTH_GRADE": "财富等级未ESTABLISHED，禁止编码",
    "CHONG_KU=FA_CAI": "冲库≠必发财，禁止",
    "HE_KU=KAI_KU": "合库=闭库，禁止",
    "CHUAN_KU=KAI_KU": "穿库原典证据不足，禁止",
    "ALL_MUKU=CAI_KU": "所有墓库不得统称财库",
}

# 反例测试清单（Counter Examples）
COUNTER_EXAMPLES = [
    ("墓≠库", "原局辰戌丑未未受刑冲=MUKU_STATE=墓(死), 不得判开库"),
    ("库≠已开", "MUKU_STATE=库 不得自动 MUKU_OPENED"),
    ("到墓位≠开库", "大运到墓位只是墓到位, 不得判 MUKU_OPENED"),
    ("开库≠发财", "MUKU_OPENED 不得自动 WEALTH_GAIN"),
    ("冲自己库≠冲宾位库", "冲自己库=取财; 冲宾位库=财可能被冲走, 不得同断言"),
    ("刑/冲≠任意动态", "OPEN_METHOD∈{冲,刑}, 合穿不算"),
    ("合库≠开库", "合=闭库, 不得判开库"),
    ("穿库≠核心规则", "穿库原典证据不足, 不进核心Rule"),
]


def get_registry_stats() -> Dict[str, int]:
    return {
        "total": len(RULE_REGISTRY),
        "established": sum(1 for r in RULE_REGISTRY.values() if r.status == "ESTABLISHED"),
        "forbidden": len(FORBIDDEN_RULES),
        "counter_examples": len(COUNTER_EXAMPLES),
    }
