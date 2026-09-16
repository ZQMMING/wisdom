# -*- coding: utf-8 -*-
"""盲派 Assertion Registry V3.2
基线 commit: 899c0e49
Rule 负责"结构是否成立"；Assertion 负责"把成立的结构声明出来"。
禁止: Judgment泄漏/跨层推断/评分/Case直接产生Assertion
"""
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class AssertionDef:
    """单条 Assertion 定义（只读）"""
    assertion_id: str
    rule_id: str
    evidence_id: str
    assertion_type: str     # STRUCTURAL / TIMING / RELATION
    subject: str
    relation: str
    object: str
    conditions: str
    provenance: str


# ═══════════════════════════════════════════════════════════
# L1 STRUCTURE → STRUCTURAL_ASSERTION
# ═══════════════════════════════════════════════════════════

A_PJ_001 = AssertionDef(
    assertion_id="A-PJ-ZHENG", rule_id="R-PJ-001", evidence_id="EVD-PJ-001",
    assertion_type="STRUCTURAL",
    subject="命局", relation="局型=正局", object="ZHENG",
    conditions="DM_direction==original OR DB_direction==original",
    provenance="R-PJ-001 → EVD-PJ-001 → 盲派中级第01章",
)

A_PJ_002 = AssertionDef(
    assertion_id="A-PJ-FAN", rule_id="R-PJ-002", evidence_id="EVD-PJ-002",
    assertion_type="STRUCTURAL",
    subject="命局", relation="局型=反局", object="FAN",
    conditions="DM/DB方向与原局相反 OR DM与DB方向相反",
    provenance="R-PJ-002 → EVD-PJ-002 → 盲派中级第01章",
)

A_PJ_003 = AssertionDef(
    assertion_id="A-PJ-FANJULU", rule_id="R-PJ-003", evidence_id="EVD-PJ-003",
    assertion_type="TIMING",
    subject="岁运", relation="冲合反局激活", object="FAN_JU_ACTIVE",
    conditions="原局CHONG AND 岁运HE",
    provenance="R-PJ-003 → EVD-PJ-003 → 第01章岁运反局",
)

A_ZB_001 = AssertionDef(
    assertion_id="A-ZB-ROBBER_CATCHER", rule_id="R-ZB-001", evidence_id="EVD-ZB-001",
    assertion_type="STRUCTURAL",
    subject="主位", relation="贼捕结构成立", object="catcher=主位,robber=宾位",
    conditions="主>宾 AND 主克宾 AND 宾无根",
    provenance="R-ZB-001 → EVD-ZB-001 → 盲派八字体系第5章",
)

A_GF_001 = AssertionDef(
    assertion_id="A-GF-GONGSHEN", rule_id="R-GF-001", evidence_id="EVD-GF-001",
    assertion_type="STRUCTURAL",
    subject="参与做功字", relation="角色=", object="功神/废神",
    conditions="branch∈working OR target=GONG_SHEN",
    provenance="R-GF-001 → EVD-GF-001 → 第3章功神废神",
)

A_BZ_001 = AssertionDef(
    assertion_id="A-BZ-MAINGUEST", rule_id="R-BZ-001", evidence_id="EVD-BZ-001",
    assertion_type="RELATION",
    subject="四柱", relation="宾主定位", object="day/hour=MAIN; year/month=GUEST",
    conditions="pillar_position",
    provenance="R-BZ-001 → EVD-BZ-001 → 第1章宾主",
)

A_TY_001 = AssertionDef(
    assertion_id="A-TY-TIYONG", rule_id="R-TY-001", evidence_id="EVD-TY-001",
    assertion_type="RELATION",
    subject="十神", relation="体用定位", object="TI/YONG/NEUTRAL",
    conditions="ten_god",
    provenance="R-TY-001 → EVD-TY-001 → 第2章体用",
)

# ═══════════════════════════════════════════════════════════
# L2 SYMBOL → STRUCTURAL_ASSERTION
# ═══════════════════════════════════════════════════════════

A_SX_001 = AssertionDef(
    assertion_id="A-SX-GONGSYMBOLS", rule_id="R-SX-001", evidence_id="EVD-SX-001",
    assertion_type="STRUCTURAL",
    subject="干支", relation="共象成立", object="intersection_meaning",
    conditions="overlapping_xiang>=2",
    provenance="R-SX-001 → EVD-SX-001 → 象的应用·共象",
)

A_SX_002 = AssertionDef(
    assertion_id="A-SX-HESYMBOLS", rule_id="R-SX-002", evidence_id="EVD-SX-002",
    assertion_type="STRUCTURAL",
    subject="合绊双方", relation="互取象", object="A+B复合象",
    conditions="合绊成立",
    provenance="R-SX-002 → EVD-SX-002 → 象的应用·合象",
)

A_SX_003 = AssertionDef(
    assertion_id="A-SX-HUASYMBOLS", rule_id="R-SX-003", evidence_id="EVD-SX-003",
    assertion_type="STRUCTURAL",
    subject="生化关系", relation="转化象", object="纺织/家具/化工",
    conditions="阴木→火/阳木→火/辰→子",
    provenance="R-SX-003 → EVD-SX-003 → 象的应用·化象",
)

A_SX_004 = AssertionDef(
    assertion_id="A-SX-MUSYMBOLS", rule_id="R-SX-004", evidence_id="EVD-SX-004",
    assertion_type="STRUCTURAL",
    subject="墓库", relation="墓象", object="军队/学校/地产",
    conditions="七杀入刃墓/食伤入墓/财入墓",
    provenance="R-SX-004 → EVD-SX-004 → 象的应用·墓象",
)

A_SX_005 = AssertionDef(
    assertion_id="A-SX-ZHISYMBOLS", rule_id="R-SX-005", evidence_id="EVD-SX-005",
    assertion_type="STRUCTURAL",
    subject="制法", relation="制象", object="资本运作/地产",
    conditions="财库制劫财印库/丑未冲制印库",
    provenance="R-SX-005 → EVD-SX-005 → 象的应用·制象",
)

A_SX_006 = AssertionDef(
    assertion_id="A-SX-DAISYMBOLS", rule_id="R-SX-006", evidence_id="EVD-SX-006",
    assertion_type="STRUCTURAL",
    subject="单柱", relation="带象", object="公家财/管财官/权力/薪水",
    conditions="十神同柱组合",
    provenance="R-SX-006 → EVD-SX-006 → 象的应用·带象",
)

A_SX_007 = AssertionDef(
    assertion_id="A-SX-JIESYMBOLS", rule_id="R-SX-007", evidence_id="EVD-SX-007",
    assertion_type="RELATION",
    subject="A↔B", relation="借象关系成立", object="BORROWED",
    conditions="通禄 OR 同五行阴阳不同",
    provenance="R-SX-007 → EVD-SX-007 → 第7章借象",
)

# ═══════════════════════════════════════════════════════════
# L3 WEALTH → STRUCTURAL_ASSERTION（只出结构，不出财富等级）
# ═══════════════════════════════════════════════════════════

A_WEALTH_001 = AssertionDef(
    assertion_id="A-WEALTH-LUASCASH", rule_id="R-WEALTH-001", evidence_id="EVD-WEALTH-001",
    assertion_type="STRUCTURAL",
    subject="禄神", relation="当财候选", object="LU_AS_CASH",
    conditions="有禄AND无伤食泄 OR 无财AND有禄",
    provenance="R-WEALTH-001 → EVD-WEALTH-001 → 第8章禄神当财",
)

# ═══════════════════════════════════════════════════════════
# L4 MARRIAGE → TIMING_ASSERTION
# ═══════════════════════════════════════════════════════════

A_MARRIAGE_001 = AssertionDef(
    assertion_id="A-MARRIAGE-TIMING", rule_id="R-MARRIAGE-001", evidence_id="EVD-MARRIAGE-001",
    assertion_type="TIMING",
    subject="岁运", relation="结婚应期候选", object="MARRIAGE_CANDIDATE",
    conditions="配偶星合入宫/星五合/宫星刑冲",
    provenance="R-MARRIAGE-001 → EVD-MARRIAGE-001 → 第10章结婚应期",
)

A_MARRIAGE_002 = AssertionDef(
    assertion_id="A-DIVORCE-TIMING", rule_id="R-MARRIAGE-002", evidence_id="EVD-MARRIAGE-002",
    assertion_type="TIMING",
    subject="岁运", relation="离婚应期候选", object="DIVORCE_CANDIDATE",
    conditions="原局宫星结构 AND 岁运对抗 AND 对抗平衡",
    provenance="R-MARRIAGE-002 → EVD-MARRIAGE-002 → 第10章离婚应期",
)

# ═══════════════════════════════════════════════════════════
# L5 BODY/DISASTER
# ═══════════════════════════════════════════════════════════

A_BODY_001 = AssertionDef(
    assertion_id="A-BODY-GONGWEI", rule_id="R-BODY-001", evidence_id="EVD-BODY-001",
    assertion_type="STRUCTURAL",
    subject="宫位", relation="身体部位映射", object="年腿/月躯干/日内脏/时头面",
    conditions="pillar_position",
    provenance="R-BODY-001 → EVD-BODY-001 → 第3章宫位身体",
)

A_BODY_002 = AssertionDef(
    assertion_id="A-BODY-GAN", rule_id="R-BODY-002", evidence_id="EVD-BODY-002",
    assertion_type="STRUCTURAL",
    subject="十干", relation="身体类象集合", object="body_symbols",
    conditions="stem lookup",
    provenance="R-BODY-002 → EVD-BODY-002 → 第3章十干类象",
)

A_BODY_003 = AssertionDef(
    assertion_id="A-BODY-ZHI", rule_id="R-BODY-003", evidence_id="EVD-BODY-003",
    assertion_type="STRUCTURAL",
    subject="十二支", relation="身体类象集合", object="body_symbols",
    conditions="branch lookup",
    provenance="R-BODY-003 → EVD-BODY-003 → 第3章十二支类象",
)

A_DISASTER_001 = AssertionDef(
    assertion_id="A-DISASTER-PRISON", rule_id="R-DISASTER-001", evidence_id="EVD-DISASTER-001",
    assertion_type="STRUCTURAL",
    subject="原局结构", relation="牢狱/失自由风险", object="PRISON_RISK",
    conditions="5条灾厄结构任一命中",
    provenance="R-DISASTER-001 → EVD-DISASTER-001 → 第12章牢狱",
)

# ═══════════════════════════════════════════════════════════
# L6 SHENCHA
# ═══════════════════════════════════════════════════════════

A_SHEN_001 = AssertionDef(
    assertion_id="A-SHEN-LU", rule_id="R-SHEN-001", evidence_id="EVD-SHEN-001",
    assertion_type="STRUCTURAL",
    subject="禄神", relation="象=临官之地", object="LU_SYMBOL",
    conditions="stem临官",
    provenance="R-SHEN-001 → EVD-SHEN-001 → 第4章神煞",
)

A_SHEN_002 = AssertionDef(
    assertion_id="A-SHEN-YANGREN", rule_id="R-SHEN-002", evidence_id="EVD-SHEN-002",
    assertion_type="STRUCTURAL",
    subject="羊刃", relation="象=帝旺之地", object="YANGREN_SYMBOL",
    conditions="stem帝旺",
    provenance="R-SHEN-002 → EVD-SHEN-002 → 第4章神煞",
)

A_SHEN_003 = AssertionDef(
    assertion_id="A-SHEN-MUKU", rule_id="R-SHEN-003", evidence_id="EVD-SHEN-003",
    assertion_type="STRUCTURAL",
    subject="墓库", relation="象=收藏控制", object="MUKU_SYMBOL",
    conditions="辰戌丑未",
    provenance="R-SHEN-003 → EVD-SHEN-003 → 第4章神煞",
)

A_SHEN_004 = AssertionDef(
    assertion_id="A-SHEN-YIMA", rule_id="R-SHEN-004", evidence_id="EVD-SHEN-004",
    assertion_type="STRUCTURAL",
    subject="驿马", relation="象=迁移奔波", object="YIMA_SYMBOL",
    conditions="日支三合→对宫",
    provenance="R-SHEN-004 → EVD-SHEN-004 → 第4章神煞",
)

A_SHEN_005 = AssertionDef(
    assertion_id="A-SHEN-KONGWANG", rule_id="R-SHEN-005", evidence_id="EVD-SHEN-005",
    assertion_type="STRUCTURAL",
    subject="空亡", relation="象=虚不实减半", object="KONGWANG_SYMBOL",
    conditions="日柱旬空",
    provenance="R-SHEN-005 → EVD-SHEN-005 → 第4章神煞",
)

# ═══════════════════════════════════════════════════════════
# L7 MUKU（关键边界：MUKU_OPENED≠WEALTH_GAIN）
# ═══════════════════════════════════════════════════════════

A_MUKU_001 = AssertionDef(
    assertion_id="A-MUKU-IDENTIFIED", rule_id="R-MUKU-001", evidence_id="EVD-MUKU-001",
    assertion_type="STRUCTURAL",
    subject="辰戌丑未", relation="墓库识别", object="MUKU_PRESENT/STATE/TYPE/OWNER",
    conditions="branch∈四库",
    provenance="R-MUKU-001 → EVD-MUKU-001 → 初级第4章墓库",
)

A_MUKU_002 = AssertionDef(
    assertion_id="A-MUKU-OPENED", rule_id="R-MUKU-002", evidence_id="EVD-MUKU-002",
    assertion_type="STRUCTURAL",
    subject="墓库", relation="刑冲开库", object="MUKU_OPENED",
    conditions="MUKU_PRESENT AND (冲 OR 刑)",
    provenance="R-MUKU-002 → EVD-MUKU-002 → 初级第4章墓库",
)

A_MUKU_003 = AssertionDef(
    assertion_id="A-MUKU-TRIGGERED", rule_id="R-MUKU-003", evidence_id="EVD-MUKU-003",
    assertion_type="TIMING",
    subject="岁运", relation="引动墓库", object="MUKU_OPENED_TIMING",
    conditions="原局墓库 AND 岁运刑冲命中",
    provenance="R-MUKU-003 → EVD-MUKU-003 → 高级应期论",
)

# ═══════════════════════════════════════════════════════════
# Assertion Registry
# ═══════════════════════════════════════════════════════════

ASSERTION_REGISTRY: Dict[str, AssertionDef] = {a.assertion_id: a for a in [
    A_PJ_001, A_PJ_002, A_PJ_003, A_ZB_001, A_GF_001, A_BZ_001, A_TY_001,
    A_SX_001, A_SX_002, A_SX_003, A_SX_004, A_SX_005, A_SX_006, A_SX_007,
    A_WEALTH_001,
    A_MARRIAGE_001, A_MARRIAGE_002,
    A_BODY_001, A_BODY_002, A_BODY_003, A_DISASTER_001,
    A_SHEN_001, A_SHEN_002, A_SHEN_003, A_SHEN_004, A_SHEN_005,
    A_MUKU_001, A_MUKU_002, A_MUKU_003,
]}

# 禁止的跨层 Assertion（Judgment 泄漏）
FORBIDDEN_ASSERTIONS = {
    "A-WEALTH-GAIN": "MUKU_OPENED≠WEALTH_GAIN，禁止",
    "A-WEALTH-LEVEL": "财富等级未ESTABLISHED，禁止",
    "A-MARRIAGE-MARRIED": "结婚应期≠已结婚，禁止",
    "A-DIVORCE-Divorced": "离婚应期≠已离婚，禁止",
    "A-DISEASE": "身体类象≠疾病，禁止",
    "A-PRISEN-DEFINITE": "牢狱风险≠必坐牢，禁止",
}


def get_assertion_stats() -> Dict[str, int]:
    return {
        "total": len(ASSERTION_REGISTRY),
        "structural": sum(1 for a in ASSERTION_REGISTRY.values() if a.assertion_type == "STRUCTURAL"),
        "timing": sum(1 for a in ASSERTION_REGISTRY.values() if a.assertion_type == "TIMING"),
        "relation": sum(1 for a in ASSERTION_REGISTRY.values() if a.assertion_type == "RELATION"),
        "forbidden": len(FORBIDDEN_ASSERTIONS),
    }
