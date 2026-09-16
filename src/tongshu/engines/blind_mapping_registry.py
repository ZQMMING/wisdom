# -*- coding: utf-8 -*-
"""盲派 Modern Semantic Mapping Registry V1 — 46条静态映射配置表。

Schema:
  mapping_id / judgment_id
  classical_result / classical_meaning  ← 原样保留，不改经典语义
  modern_semantic / modern_domain / modern_expression
  semantic_boundary / avoid_phrases
  source_judgment_id / mapping_version / review_status

铁律：
  - 经典层一字不改
  - Mapping层只做现代语义转义
  - 禁止反向污染经典层
  - 1 Judgment_ID ↔ 1 MappingRule
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class MappingRule:
    """单条MappingRule"""
    mapping_id: str
    judgment_id: str
    # ===== Classical（原样保留） =====
    classical_result: str
    classical_meaning: str
    # ===== Modern Mapping =====
    modern_semantic: str
    modern_domain: str
    modern_expression: str
    # ===== Boundary =====
    semantic_boundary: Tuple[str, ...]
    avoid_phrases: Tuple[str, ...]
    # ===== Provenance =====
    source_judgment_id: str
    mapping_version: str
    # ===== Governance =====
    review_status: str  # PENDING / PASS / FAIL
    review_notes: str = ""


# ═══════════════════════════════════════════════════════════════
# A类：结构类（重点：结构≠事件）
# ═══════════════════════════════════════════════════════════════

_MAP_SPECIAL_001 = MappingRule(
    mapping_id="MAP-J-SPECIAL-001",
    judgment_id="J-SPECIAL-001",
    classical_result="FANJU_LAYERED_JUDGMENT",
    classical_meaning="反局三层：原局反局应重灾、大运反局应转运、流年反局应当年灾",
    modern_semantic="传统命理中，「反局」是指命局结构与做功方向相悖的结构状态；不同层级（原局/大运/流年）的反局对应不同时间尺度上的结构失衡信号",
    modern_domain="结构/格局",
    modern_expression="该命局存在结构失衡的信号，失衡层级不同，影响的时间范围也不同",
    semantic_boundary=("结构信号", "不是事件坐实", "正局不自动推吉"),
    avoid_phrases=("你会有大灾", "必然倒大霉", "命不好"),
    source_judgment_id="J-SPECIAL-001",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_MARRIAGE_004 = MappingRule(
    mapping_id="MAP-J-MARRIAGE-004",
    judgment_id="J-MARRIAGE-004",
    classical_result="GOOD_MARRIAGE_STRUCTURE",
    classical_meaning="夫妻宫安静制星，婚姻结构好",
    modern_semantic="传统命理中，夫妻宫稳定且能制衡配偶星的结构，被认为是婚姻关系较为和谐的结构信号",
    modern_domain="婚姻/感情",
    modern_expression="从传统命理角度看，婚姻关系的结构基础较为稳定",
    semantic_boundary=("结构信号", "不是婚姻已发生", "制之不住则反为坏"),
    avoid_phrases=("你婚姻一定幸福", "肯定不会离婚", "婚姻美满一生"),
    source_judgment_id="J-MARRIAGE-004",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_MARRIAGE_005 = MappingRule(
    mapping_id="MAP-J-MARRIAGE-005",
    judgment_id="J-MARRIAGE-005",
    classical_result="BAD_MARRIAGE_STRUCTURE",
    classical_meaning="夫妻宫被刑冲破穿，婚姻结构不好；破坏轻不离婚，破坏重必离异",
    modern_semantic="传统命理中，夫妻宫受到刑、冲、破、穿等作用的结构，被认为是婚姻关系容易出现波动的信号；波动程度与破坏程度相关",
    modern_domain="婚姻/感情",
    modern_expression="从传统命理角度看，婚姻关系存在波动信号，波动程度需结合具体结构判断",
    semantic_boundary=("结构信号", "不是离婚事件坐实", "破坏程度轻不必然离婚"),
    avoid_phrases=("你会离婚", "肯定要离", "婚姻必破裂"),
    source_judgment_id="J-MARRIAGE-005",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_DISASTER_004 = MappingRule(
    mapping_id="MAP-J-DISASTER-004",
    judgment_id="J-DISASTER-004",
    classical_result="PRISON_STRUCTURE",
    classical_meaning="牢狱五结构：丑辰亥坏阳用、水多金沉、枭神夺食、劫财伤官抗官杀、反局+丑辰",
    modern_semantic="传统命理中，这五种结构被认为与「受限制、约束、行动自由受影响」等情境相关的结构性信号；其中反局+丑辰的判断是「多数应牢狱」的倾向描述",
    modern_domain="限制/约束",
    modern_expression="从传统命理角度看，该命局存在与「受限制、约束」相关的结构性信号，是否应事需结合岁运引动和现实条件综合判断",
    semantic_boundary=("结构信号", "不是事件坐实", "E条是多数/倾向不是必然", "不压成单一Boolean"),
    avoid_phrases=("你会坐牢", "必然入狱", "肯定有牢狱之灾", "犯法坐牢"),
    source_judgment_id="J-DISASTER-004",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_DISASTER_006 = MappingRule(
    mapping_id="MAP-J-DISASTER-006",
    judgment_id="J-DISASTER-006",
    classical_result="FREEDOM_LOSS_STRUCTURE",
    classical_meaning="食伤入墓为失去自由，不能和外界联系",
    modern_semantic="传统命理中，食伤代表自由和对外联系，食伤入墓的结构被认为与「行动受限、与外界联系减少」相关的结构性信号",
    modern_domain="限制/约束",
    modern_expression="从传统命理角度看，该命局存在与「行动受限、对外联系减少」相关的结构性信号",
    semantic_boundary=("结构信号", "不是事件坐实", "不是必然坐牢"),
    avoid_phrases=("你会被关起来", "必然坐牢", "失去自由"),
    source_judgment_id="J-DISASTER-006",
    mapping_version="V1.0",
    review_status="PENDING",
)


# ═══════════════════════════════════════════════════════════════
# B类：健康类（重点：身体象≠医学诊断）
# ═══════════════════════════════════════════════════════════════

_MAP_HEALTH_002 = MappingRule(
    mapping_id="MAP-J-HEALTH-002",
    judgment_id="J-HEALTH-002",
    classical_result="HEALTH_RISK_BLADDER_RECTUM",
    classical_meaning="时柱被穿，膀胱/直肠/下身易有毛病",
    modern_semantic="传统命理中，时柱对应下身和排泄系统，时柱被穿的结构被认为是相关身体部位需要注意养护的传统命理信号",
    modern_domain="健康/身体",
    modern_expression="从传统命理角度看，该命局提示下身、排泄相关部位需要多注意养护",
    semantic_boundary=("风险信号", "不是医学诊断", "不替代专业医疗建议"),
    avoid_phrases=("你会得膀胱癌", "肯定有直肠癌", "下身一定有毛病"),
    source_judgment_id="J-HEALTH-002",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_HEALTH_003 = MappingRule(
    mapping_id="MAP-J-HEALTH-003",
    judgment_id="J-HEALTH-003",
    classical_result="HEALTH_RISK_HAIR_FACE",
    classical_meaning="甲丁同现主头发稀；甲为头丁为面癸冲克主面受损",
    modern_semantic="传统命理中，甲丁相关结构被认为与头部、面部、头发等部位的状态相关的传统命理信号",
    modern_domain="健康/身体",
    modern_expression="从传统命理角度看，该命局提示头部、面部、头发相关部位需要多注意养护",
    semantic_boundary=("风险信号", "不是医学诊断", "不替代专业医疗建议"),
    avoid_phrases=("你头发一定掉光", "脸会毁容", "肯定有面部疾病"),
    source_judgment_id="J-HEALTH-003",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_HEALTH_005 = MappingRule(
    mapping_id="MAP-J-HEALTH-005",
    judgment_id="J-HEALTH-005",
    classical_result="HEALTH_RISK_LEG_FOOT",
    classical_meaning="比劫破到年上卯，主右腿有残疾",
    modern_semantic="传统命理中，年柱对应头部和下肢，年支被主位比劫破坏的结构被认为是下肢部位需要注意的传统命理信号",
    modern_domain="健康/身体",
    modern_expression="从传统命理角度看，该命局提示下肢、腿脚相关部位需要多注意养护",
    semantic_boundary=("风险信号", "不是医学诊断", "必须是主位破宾位", "不替代专业医疗建议"),
    avoid_phrases=("你腿会残疾", "肯定腿有毛病", "腿脚一定有伤"),
    source_judgment_id="J-HEALTH-005",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_KIN_004 = MappingRule(
    mapping_id="MAP-J-KIN-004",
    judgment_id="J-KIN-004",
    classical_result="MOTHER_HEALTH_RISK",
    classical_meaning="食神被穿无救，主母亲有早丧之象",
    modern_semantic="传统命理中，食神代表母亲，食神被穿且无救应的结构被认为是与母亲健康状况相关的传统命理信号",
    modern_domain="六亲/母亲",
    modern_expression="从传统命理角度看，该命局提示母亲的健康状况需要多关注",
    semantic_boundary=("风险信号", "不是必然事件", "不替代专业医疗建议"),
    avoid_phrases=("你妈会早死", "母亲一定短命", "肯定克母"),
    source_judgment_id="J-KIN-004",
    mapping_version="V1.0",
    review_status="PENDING",
)


# ═══════════════════════════════════════════════════════════════
# C类：刑灾/法律类（最严格）
# ═══════════════════════════════════════════════════════════════

_MAP_DISASTER_002 = MappingRule(
    mapping_id="MAP-J-DISASTER-002",
    judgment_id="J-DISASTER-002",
    classical_result="PRISON_RISK",
    classical_meaning="原局反局+辰，辰为伤官库无自由，主牢狱",
    modern_semantic="传统命理中，原局反局叠加辰（伤官库）的结构，被认为与「受限制、约束、自由受限」相关的结构性风险信号",
    modern_domain="限制/约束",
    modern_expression="从传统命理角度看，该命局存在与「受限制、约束」相关的结构性风险信号，需结合岁运引动综合判断",
    semantic_boundary=("风险信号", "不是事件坐实", "辰单独不等于牢狱", "必须叠加反局结构"),
    avoid_phrases=("你会坐牢", "必然入狱", "肯定有牢狱之灾"),
    source_judgment_id="J-DISASTER-002",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_DISASTER_003 = MappingRule(
    mapping_id="MAP-J-DISASTER-003",
    judgment_id="J-DISASTER-003",
    classical_result="CRIME_STRUCTURE_YIN",
    classical_meaning="丑酉为阴中之阴，多数主犯罪",
    modern_semantic="传统命理中，丑酉同现且阴干见阴支入墓的结构，被认为是与「暗昧、暗中行事」相关的结构性信号；原典描述为「多数」的倾向判断",
    modern_domain="结构/倾向",
    modern_expression="从传统命理角度看，该命局存在与「暗中、隐蔽」相关的结构性倾向信号",
    semantic_boundary=("倾向信号", "不是事件坐实", "辛丑日主见丑时不成立", "不泛化所有阴干"),
    avoid_phrases=("你会犯罪", "肯定犯法", "天生就是坏人"),
    source_judgment_id="J-DISASTER-003",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_DISASTER_005 = MappingRule(
    mapping_id="MAP-J-DISASTER-005",
    judgment_id="J-DISASTER-005",
    classical_result="RELEASE_TIMING_WINDOW",
    classical_meaning="出狱应期：日主得禄、日主合冲、冲穿库",
    modern_semantic="传统命理中，出狱应期是指「受限制状态解除」的时间窗口信号；包括日主得禄、日主合冲、冲穿墓库等触发条件",
    modern_domain="时间窗口",
    modern_expression="从传统命理角度看，该命局存在「受限制状态可能解除」的时间窗口信号，具体应事需结合现实条件判断",
    semantic_boundary=("时间窗口", "不是事件坐实", "是信号不是已定事实"),
    avoid_phrases=("你X年出狱", "肯定那时候出来", "出狱时间确定"),
    source_judgment_id="J-DISASTER-005",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_WEALTH_017 = MappingRule(
    mapping_id="MAP-J-WEALTH-017",
    judgment_id="J-WEALTH-017",
    classical_result="THIEF_STRUCTURE",
    classical_meaning="劫财与官杀同在主位，主小偷",
    modern_semantic="传统命理中，劫财与官杀同在主位的结构，被认为是与「财物易被他人侵夺」相关的结构性信号",
    modern_domain="财物/风险",
    modern_expression="从传统命理角度看，该命局存在与「财物易被他人侵夺」相关的结构性信号",
    semantic_boundary=("结构信号", "不是事件坐实", "不是必然犯罪"),
    avoid_phrases=("你是小偷", "肯定偷东西", "天生贼命"),
    source_judgment_id="J-WEALTH-017",
    mapping_version="V1.0",
    review_status="PENDING",
)


# ═══════════════════════════════════════════════════════════════
# D类：财富类（重点：结构≠金额）
# ═══════════════════════════════════════════════════════════════

_MAP_WEALTH_003 = MappingRule(
    mapping_id="MAP-J-WEALTH-003",
    judgment_id="J-WEALTH-003",
    classical_result="WEALTH_OWNERSHIP",
    classical_meaning="财根在主位=我家财；财根在宾位=别人财；年上财=远方财",
    modern_semantic="传统命理中，财星所在的位置（主位/宾位/年柱）被认为与财富的来源方向、归属性质相关的结构信号",
    modern_domain="财富/方向",
    modern_expression="从传统命理角度看，该命局的财富来源方向和归属性质有明确的结构特征",
    semantic_boundary=("结构信号", "不是财富金额", "不估财富等级"),
    avoid_phrases=("你很有钱", "财富等级高", "肯定发大财"),
    source_judgment_id="J-WEALTH-003",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_WEALTH_005 = MappingRule(
    mapping_id="MAP-J-WEALTH-005",
    judgment_id="J-WEALTH-005",
    classical_result="WEALTH_AUSPICIOUS_BREAK",
    classical_meaning="财星反局，主大凶",
    modern_semantic="传统命理中，财星所在位置出现反局结构，被认为是财富方面容易出现波折、动荡的结构性风险信号",
    modern_domain="财富/风险",
    modern_expression="从传统命理角度看，该命局在财富方面存在结构性波动风险信号",
    semantic_boundary=("风险信号", "不是事件坐实", "不估具体金额"),
    avoid_phrases=("你会破产", "肯定破财", "财富大凶"),
    source_judgment_id="J-WEALTH-005",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_WEALTH_006 = MappingRule(
    mapping_id="MAP-J-WEALTH-006",
    judgment_id="J-WEALTH-006",
    classical_result="WEALTH_EASE_OR_HARD",
    classical_meaning="禄不配印主辛苦；禄配印主享受",
    modern_semantic="传统命理中，禄代表现成的福禄，印生禄代表被滋养；禄不配印的结构被认为是求财较辛苦的信号，禄配印则是较为安逸的信号",
    modern_domain="财富/性质",
    modern_expression="从传统命理角度看，该命局在求财的辛苦程度上有明确的结构特征",
    semantic_boundary=("结构信号", "不演化成财富等级", "合夫妻宫不算桃花"),
    avoid_phrases=("你财富等级高", "肯定是有钱人", "富贵命"),
    source_judgment_id="J-WEALTH-006",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_WEALTH_007 = MappingRule(
    mapping_id="MAP-J-WEALTH-007",
    judgment_id="J-WEALTH-007",
    classical_result="CAR_PROPERTY_SIGNAL",
    classical_meaning="时支被生主买车；时支被破主车损",
    modern_semantic="传统命理中，时支代表车辆，时支被生的结构被认为是与车辆添置相关的信号，时支被破则是车辆易有损耗的信号",
    modern_domain="财物/车辆",
    modern_expression="从传统命理角度看，该命局在车辆相关事项上有明确的结构信号",
    semantic_boundary=("信号", "不是事件坐实"),
    avoid_phrases=("你肯定买车", "车一定会坏", "车辆事故"),
    source_judgment_id="J-WEALTH-007",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_WEALTH_008 = MappingRule(
    mapping_id="MAP-J-WEALTH-008",
    judgment_id="J-WEALTH-008",
    classical_result="WEALTH_CAREER_CONFLICT",
    classical_meaning="年月财旺女命，心乱主早辍学",
    modern_semantic="传统命理中，年月财旺的女命结构被认为是心思较早偏向现实事务、学业可能较早中断的传统命理倾向信号",
    modern_domain="学业/倾向",
    modern_expression="从传统命理角度看，该命局在学业与现实事务的权衡上存在较早偏向现实的倾向信号",
    semantic_boundary=("倾向信号", "不是必然事件"),
    avoid_phrases=("你一定辍学", "肯定不上学", "读书读不出来"),
    source_judgment_id="J-WEALTH-008",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_WEALTH_009 = MappingRule(
    mapping_id="MAP-J-WEALTH-009",
    judgment_id="J-WEALTH-009",
    classical_result="WEALTH_TALENT_DIRECTION",
    classical_meaning="财虚透天干主有才华；财虚透时上主时尚",
    modern_semantic="传统命理中，财星虚透天干的结构被认为与外在才华、表达能力相关的信号，财虚透时柱则与时尚、审美等方向相关",
    modern_domain="才华/方向",
    modern_expression="从传统命理角度看，该命局在才华表达、外在形象方面有明确的结构特征",
    semantic_boundary=("结构信号", "不是必然事件"),
    avoid_phrases=("你肯定有才华", "天生时尚达人", "才华横溢"),
    source_judgment_id="J-WEALTH-009",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_WEALTH_010 = MappingRule(
    mapping_id="MAP-J-WEALTH-010",
    judgment_id="J-WEALTH-010",
    classical_result="CAR_THEFT_RISK",
    classical_meaning="时柱被穿（门口被穿），主车被盗",
    modern_semantic="传统命理中，时柱代表门户，时柱被穿的结构被认为是车辆、门户相关财物易有损耗风险的信号",
    modern_domain="财物/风险",
    modern_expression="从传统命理角度看，该命局在车辆、门户相关财物上存在易有损耗的风险信号",
    semantic_boundary=("风险信号", "不是事件坐实"),
    avoid_phrases=("你车肯定被盗", "一定会丢车", "车辆被盗"),
    source_judgment_id="J-WEALTH-010",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_WEALTH_011 = MappingRule(
    mapping_id="MAP-J-WEALTH-011",
    judgment_id="J-WEALTH-011",
    classical_result="WEALTH_NATURE_DIRECTION",
    classical_meaning="带象四法：财带官帽=公家、官带财帽=管理、印带官帽=权力、印带财帽=薪水",
    modern_semantic="传统命理中，干支「带象」是指干生支的结构，不同的带象组合对应不同性质的财富来源方向",
    modern_domain="财富/性质",
    modern_expression="从传统命理角度看，该命局的财富来源性质有明确的结构特征",
    semantic_boundary=("结构信号", "不是必然事件"),
    avoid_phrases=("你肯定进公家单位", "一定当领导", "权力很大"),
    source_judgment_id="J-WEALTH-011",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_WEALTH_012 = MappingRule(
    mapping_id="MAP-J-WEALTH-012",
    judgment_id="J-WEALTH-012",
    classical_result="CAPITAL_OPERATION_DIRECTION",
    classical_meaning="丑未冲财库，主资本运营",
    modern_semantic="传统命理中，丑未相冲打开财库的结构，被认为与资本运作、资金流转方向相关的信号",
    modern_domain="财富/运作",
    modern_expression="从传统命理角度看，该命局在资本运作、资金流转方向上有明确的结构特征",
    semantic_boundary=("结构信号", "不估金额"),
    avoid_phrases=("你肯定做资本运作", "财富几千万", "资本大鳄"),
    source_judgment_id="J-WEALTH-012",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_WEALTH_013 = MappingRule(
    mapping_id="MAP-J-WEALTH-013",
    judgment_id="J-WEALTH-013",
    classical_result="LU_WEALTH_STRUCTURE",
    classical_meaning="禄神当财：禄无伤食泄时可当财；印生禄为现成之福；禄取财主辛苦；禄见劫财主破财",
    modern_semantic="传统命理中，禄代表俸禄和现成的福禄，特定条件下禄可以作为财富来看待；不同的组合对应不同的财富结构性质",
    modern_domain="财富/结构",
    modern_expression="从传统命理角度看，该命局的禄神与财富的关系有明确的结构特征",
    semantic_boundary=("结构信号", "不估金额", "有财时伤食是原神"),
    avoid_phrases=("你财富等级高", "肯定是有钱人", "富贵命"),
    source_judgment_id="J-WEALTH-013",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_WEALTH_014 = MappingRule(
    mapping_id="MAP-J-WEALTH-014",
    judgment_id="J-WEALTH-014",
    classical_result="SHANGSHI_WEALTH_STRUCTURE",
    classical_meaning="无财时伤食当财；伤食为财性质；食干支性质",
    modern_semantic="传统命理中，原局无财星时，伤食可以作为财富来看待；不同的伤食干支对应不同的财富性质方向",
    modern_domain="财富/结构",
    modern_expression="从传统命理角度看，该命局在无财星的情况下，伤食与财富的关系有明确的结构特征",
    semantic_boundary=("结构信号", "有财时伤食是原神"),
    avoid_phrases=("你靠才华发财", "肯定做投资", "财富等级高"),
    source_judgment_id="J-WEALTH-014",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_WEALTH_015 = MappingRule(
    mapping_id="MAP-J-WEALTH-015",
    judgment_id="J-WEALTH-015",
    classical_result="GUAN_WEALTH_STRUCTURE",
    classical_meaning="官统财/财统官；官杀有制但制不净，官杀可当财富看",
    modern_semantic="传统命理中，官星与财星形成统属关系（官统财或财统官）的结构，被认为是官杀与财富关系密切的结构信号",
    modern_domain="财富/结构",
    modern_expression="从传统命理角度看，该命局的官星与财星的关系有明确的结构特征",
    semantic_boundary=("结构信号", "只论原局", "不推财富等级"),
    avoid_phrases=("你财富级别高", "肯定大富", "亿万富翁"),
    source_judgment_id="J-WEALTH-015",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_WEALTH_016 = MappingRule(
    mapping_id="MAP-J-WEALTH-016",
    judgment_id="J-WEALTH-016",
    classical_result="REMOTE_TRADE_DIRECTION",
    classical_meaning="财在年上+年主远方+水主海运，主远方求财/海外贸易",
    modern_semantic="传统命理中，财星在年柱（远方位置）且配合相应象义的结构，被认为与远方求财、跨区域贸易方向相关的信号",
    modern_domain="财富/方向",
    modern_expression="从传统命理角度看，该命局在远方求财、跨区域贸易方向上有明确的结构特征",
    semantic_boundary=("结构信号", "不单独推海外贸易", "需完整结构组合"),
    avoid_phrases=("你肯定做海外贸易", "肯定出国做生意", "外贸专家"),
    source_judgment_id="J-WEALTH-016",
    mapping_version="V1.0",
    review_status="PENDING",
)


# ═══════════════════════════════════════════════════════════════
# E类：事业/行业/婚姻/六亲/子女/时间
# ═══════════════════════════════════════════════════════════════

_MAP_OFFICIAL_002 = MappingRule(
    mapping_id="MAP-J-OFFICIAL-002",
    judgment_id="J-OFFICIAL-002",
    classical_result="OFFICIAL_OWNERSHIP",
    classical_meaning="官在年主国企/公家单位；官在日时主私企/自己干",
    modern_semantic="传统命理中，官星所在的位置（年柱/日时柱）被认为与事业平台的性质方向相关的结构信号",
    modern_domain="事业/平台",
    modern_expression="从传统命理角度看，该命局的事业平台性质有明确的结构特征",
    semantic_boundary=("结构信号", "不估官职级别"),
    avoid_phrases=("你肯定进国企", "一定当大官", "官职很高"),
    source_judgment_id="J-OFFICIAL-002",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_OFFICIAL_003 = MappingRule(
    mapping_id="MAP-J-OFFICIAL-003",
    judgment_id="J-OFFICIAL-003",
    classical_result="OFFICIAL_DISASTER_RISK",
    classical_meaning="官星高透克身无制，主不能当官，当官就有灾",
    modern_semantic="传统命理中，官星高透且直接克身无制化的结构，被认为是事业方面容易有压力、波折的结构性风险信号",
    modern_domain="事业/风险",
    modern_expression="从传统命理角度看，该命局在事业方面存在压力较大、波折较多的结构性风险信号",
    semantic_boundary=("风险信号", "不做官级别判断"),
    avoid_phrases=("你当不了官", "当官就会出事", "事业一败涂地"),
    source_judgment_id="J-OFFICIAL-003",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_OFFICIAL_004 = MappingRule(
    mapping_id="MAP-J-OFFICIAL-004",
    judgment_id="J-OFFICIAL-004",
    classical_result="ORTHODOX_UNORTHODOX_DIRECTION",
    classical_meaning="羊刃有制主正业；羊刃无制主偏业",
    modern_semantic="传统命理中，羊刃代表竞争和魄力，有制化的羊刃被认为适合正规、体制内的事业方向，无制化的羊刃则适合竞争性强、偏门的事业方向",
    modern_domain="事业/性质",
    modern_expression="从传统命理角度看，该命局的事业性质方向有明确的结构特征",
    semantic_boundary=("方向信号", "只给正/偏业方向", "不直接断职业名"),
    avoid_phrases=("你肯定当警察", "一定做外科医生", "职业就是军人"),
    source_judgment_id="J-OFFICIAL-004",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_OFFICIAL_005 = MappingRule(
    mapping_id="MAP-J-OFFICIAL-005",
    judgment_id="J-OFFICIAL-005",
    classical_result="POLICE_DEPARTMENT_DIRECTION",
    classical_meaning="阳字制阴字，主公安/执法部门",
    modern_semantic="传统命理中，阳干制阴支的结构，被认为与执法、监管类部门方向相关的信号",
    modern_domain="事业/部门",
    modern_expression="从传统命理角度看，该命局在执法、监管类部门方向上有明确的结构特征",
    semantic_boundary=("方向信号", "只给部门方向", "不指定级别"),
    avoid_phrases=("你肯定当警察", "一定在公安局", "就是公安系统"),
    source_judgment_id="J-OFFICIAL-005",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_OFFICIAL_006 = MappingRule(
    mapping_id="MAP-J-OFFICIAL-006",
    judgment_id="J-OFFICIAL-006",
    classical_result="MILITARY_DIRECTION",
    classical_meaning="七杀入羊刃墓，主军队/军团方向",
    modern_semantic="传统命理中，七杀入羊刃墓库的结构，被认为与军队、武装力量类机构方向相关的信号",
    modern_domain="事业/行业",
    modern_expression="从传统命理角度看，该命局在军队、武装力量类机构方向上有明确的结构特征",
    semantic_boundary=("方向信号", "不推具体级别", "不推具体单位"),
    avoid_phrases=("你肯定当将军", "一定是军官", "就是少将"),
    source_judgment_id="J-OFFICIAL-006",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_CAREER_001 = MappingRule(
    mapping_id="MAP-J-CAREER-001",
    judgment_id="J-CAREER-001",
    classical_result="CAREER_DIRECTION_BANK",
    classical_meaning="卯为食神为财原神生财之地，主银行；辰拱水主化工/制药",
    modern_semantic="传统命理中，特定干支结构被认为与金融、资金流通类职业方向，以及化工、制药类行业方向相关的信号",
    modern_domain="职业/行业",
    modern_expression="从传统命理角度看，该命局在金融类和化工制药类方向上有明确的结构特征",
    semantic_boundary=("方向信号", "不指定具体职业名", "不泛化通用映射"),
    avoid_phrases=("你适合去银行", "肯定做金融", "职业就是银行"),
    source_judgment_id="J-CAREER-001",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_CAREER_002 = MappingRule(
    mapping_id="MAP-J-CAREER-002",
    judgment_id="J-CAREER-002",
    classical_result="INSTITUTION_DIRECTION",
    classical_meaning="羊刃库主军队；伤食库主学校；财库主银行；官杀库主组织",
    modern_semantic="传统命理中，不同五行的墓库被认为与不同类型的机构方向相关的信号：羊刃库对应军队武装、伤食库对应学校教育、财库对应金融机构、官杀库对应组织单位",
    modern_domain="事业/机构",
    modern_expression="从传统命理角度看，该命局在机构类型方向上有明确的结构特征",
    semantic_boundary=("方向信号", "只给机构方向", "不指定具体单位"),
    avoid_phrases=("你肯定在大学", "一定进银行", "就是军队单位"),
    source_judgment_id="J-CAREER-002",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_CAREER_003 = MappingRule(
    mapping_id="MAP-J-CAREER-003",
    judgment_id="J-CAREER-003",
    classical_result="CAREER_ACADEMIC_DIRECTION",
    classical_meaning="木火主文、金水主理；戌亥主数学计算；丑主玄学；申主金融、酉主法律",
    modern_semantic="传统命理中，不同干支组合被认为与不同的学科方向相关：木火对应文科、金水对应理科、戌亥对应数学计算、丑对应玄学、申对应金融、酉对应法律",
    modern_domain="学业/学科",
    modern_expression="从传统命理角度看，该命局在学科方向上有明确的结构特征",
    semantic_boundary=("方向信号", "只给学科方向", "不指定具体专业"),
    avoid_phrases=("你肯定学文科", "一定读数学", "专业就是金融"),
    source_judgment_id="J-CAREER-003",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_CAREER_004 = MappingRule(
    mapping_id="MAP-J-CAREER-004",
    judgment_id="J-CAREER-004",
    classical_result="CAREER_INDUSTRY_DIRECTION",
    classical_meaning="阳木遇火主家具；阴木遇火主纺织；辛金取财主五金；火克金主冶炼",
    modern_semantic="传统命理中，不同的干支组合被认为与不同的行业方向相关的信号：阳木遇火对应家具业、阴木遇火对应纺织业、辛金取财对应五金业、火克金对应冶炼业",
    modern_domain="事业/行业",
    modern_expression="从传统命理角度看，该命局在行业方向上有明确的结构特征",
    semantic_boundary=("方向信号", "只给行业方向", "不指定具体单位"),
    avoid_phrases=("你肯定做家具", "一定开纺织厂", "就是五金行业"),
    source_judgment_id="J-CAREER-004",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_CAREER_005 = MappingRule(
    mapping_id="MAP-J-CAREER-005",
    judgment_id="J-CAREER-005",
    classical_result="CHEMICAL_PHARMA_DIRECTION",
    classical_meaning="辰拱水主化工/制药行业",
    modern_semantic="传统命理中，辰子同现的结构被认为与化工、制药类行业方向相关的信号",
    modern_domain="事业/行业",
    modern_expression="从传统命理角度看，该命局在化工、制药类行业方向上有明确的结构特征",
    semantic_boundary=("方向信号", "只给行业方向"),
    avoid_phrases=("你肯定做化工", "一定开制药厂", "就是化工行业"),
    source_judgment_id="J-CAREER-005",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_CAREER_006 = MappingRule(
    mapping_id="MAP-J-CAREER-006",
    judgment_id="J-CAREER-006",
    classical_result="BUSINESS_MANAGER_DIRECTION",
    classical_meaning="内食神主企业；食带官主经理人",
    modern_semantic="传统命理中，内食神做功的结构被认为与企业经营方向相关的信号，食带官的结构则与职业经理人方向相关",
    modern_domain="事业/职业",
    modern_expression="从传统命理角度看，该命局在企业经营和职业经理人方向上有明确的结构特征",
    semantic_boundary=("方向信号", "不指定具体行业"),
    avoid_phrases=("你肯定开公司", "一定当老板", "就是职业经理人"),
    source_judgment_id="J-CAREER-006",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_TIMING_002 = MappingRule(
    mapping_id="MAP-J-TIMING-002",
    judgment_id="J-TIMING-002",
    classical_result="LUCK_DYNAMIC_STATIC",
    classical_meaning="走干运支为体主动；走支运干为体主静",
    modern_semantic="传统命理中，大运干支与原局体用的配合关系，被认为是大运动静状态的结构信号",
    modern_domain="时间/动静",
    modern_expression="从传统命理角度看，该命局在大运运行期间的动静状态有明确的结构特征",
    semantic_boundary=("结构信号", "体用不混淆"),
    avoid_phrases=("你这十年肯定动", "一定变动", "大运不好"),
    source_judgment_id="J-TIMING-002",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_TIMING_003 = MappingRule(
    mapping_id="MAP-J-TIMING-003",
    judgment_id="J-TIMING-003",
    classical_result="YIMA_DYNAMIC_OR_STATIONARY",
    classical_meaning="驿马主动；驿马被合主停留",
    modern_semantic="传统命理中，驿马代表走动、迁移，驿马存在的结构被认为是走动多的信号，驿马被合则是停留不动的信号",
    modern_domain="时间/动静",
    modern_expression="从传统命理角度看，该命局在走动、迁移方面有明确的结构特征",
    semantic_boundary=("信号", "驿马≠搬家", "不必然迁移"),
    avoid_phrases=("你肯定搬家", "一定出国", "肯定换工作"),
    source_judgment_id="J-TIMING-003",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_KIN_002 = MappingRule(
    mapping_id="MAP-J-KIN-002",
    judgment_id="J-KIN-002",
    classical_result="KIN_KONGWANG_RELATION",
    classical_meaning="年空亡祖业空；月空亡兄弟无靠；日空亡夫妻缘薄；时空亡子女迟育",
    modern_semantic="传统命理中，空亡对应「虚、不实、缘薄」的状态，不同宫位空亡对应不同六亲方面缘薄、迟、虚的信号",
    modern_domain="六亲/关系",
    modern_expression="从传统命理角度看，该命局在六亲关系的厚薄、迟早上有明确的结构特征",
    semantic_boundary=("信号", "空亡≠必然事件", "不指定具体事件"),
    avoid_phrases=("你肯定克兄弟", "夫妻一定缘薄", "子女迟育"),
    source_judgment_id="J-KIN-002",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_KIN_003 = MappingRule(
    mapping_id="MAP-J-KIN-003",
    judgment_id="J-KIN-003",
    classical_result="MOTHER_IN_LAW_RELATION",
    classical_meaning="年柱与妻宫关联，主丈母娘在年",
    modern_semantic="传统命理中，年柱与配偶宫发生关联的结构，被认为与配偶家庭（尤其是长辈）的关系密切相关的信号",
    modern_domain="六亲/关系",
    modern_expression="从传统命理角度看，该命局与配偶家庭长辈的关系有明确的结构特征",
    semantic_boundary=("信号", "与妻宫无关则伤可能是奶奶"),
    avoid_phrases=("你丈母娘克你", "肯定和丈母娘关系差", "丈母娘不好"),
    source_judgment_id="J-KIN-003",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_CHILD_001 = MappingRule(
    mapping_id="MAP-J-CHILD-001",
    judgment_id="J-CHILD-001",
    classical_result="CHILD_GENDER_TENDENCY",
    classical_meaning="男命杀+财=儿；杀无财=女；穿财=生女；伤官运=生儿",
    modern_semantic="传统命理中，男命以七杀为儿子、正官为女儿，不同的组合结构对应子女性别的倾向信号；原典描述为倾向，不是必然",
    modern_domain="子女/性别",
    modern_expression="从传统命理角度看，该命局在子女性别倾向上有明确的结构特征",
    semantic_boundary=("倾向信号", "不是必然", "性别倾向不绝对"),
    avoid_phrases=("你肯定生儿子", "一定生女儿", "子女性别确定"),
    source_judgment_id="J-CHILD-001",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_MARRIAGE_002 = MappingRule(
    mapping_id="MAP-J-MARRIAGE-002",
    judgment_id="J-MARRIAGE-002",
    classical_result="TAOHUA_MARITAL_RISK",
    classical_meaning="女命禄合桃花，主感情波折",
    modern_semantic="传统命理中，女命禄与桃花相合的结构，被认为是感情方面容易有波折的信号",
    modern_domain="婚姻/感情",
    modern_expression="从传统命理角度看，该命局在感情方面存在容易有波折的信号",
    semantic_boundary=("风险信号", "合夫妻宫不算桃花"),
    avoid_phrases=("你肯定出轨", "婚姻一定有桃花", "感情混乱"),
    source_judgment_id="J-MARRIAGE-002",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_MARRIAGE_003 = MappingRule(
    mapping_id="MAP-J-MARRIAGE-003",
    judgment_id="J-MARRIAGE-003",
    classical_result="SPOUSE_SOURCE_DIRECTION",
    classical_meaning="夫妻象在月柱，主同学/同事来源",
    modern_semantic="传统命理中，夫妻星象在月柱（青年时期位置）的结构，被认为是配偶来源与同学、同事等社交圈相关的信号",
    modern_domain="婚姻/来源",
    modern_expression="从传统命理角度看，该命局的配偶来源方向有明确的结构特征",
    semantic_boundary=("方向信号", "不必然"),
    avoid_phrases=("你肯定找同学", "一定是同事", "配偶就是同学"),
    source_judgment_id="J-MARRIAGE-003",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_MARRIAGE_006 = MappingRule(
    mapping_id="MAP-J-MARRIAGE-006",
    judgment_id="J-MARRIAGE-006",
    classical_result="MARRIAGE_TIMING_WINDOW",
    classical_meaning="冲合夫妻宫/冲墓主结婚应期窗口",
    modern_semantic="传统命理中，结婚应期是指婚姻关系容易发生变化的时间窗口信号；包括冲合夫妻宫、冲开墓库等触发条件",
    modern_domain="时间窗口",
    modern_expression="从传统命理角度看，该命局存在婚姻关系容易发生变化的时间窗口信号，具体应事需结合现实条件判断",
    semantic_boundary=("时间窗口", "不是事件坐实", "是信号不是已定事实"),
    avoid_phrases=("你X年结婚", "肯定那时候结婚", "结婚时间确定"),
    source_judgment_id="J-MARRIAGE-006",
    mapping_version="V1.0",
    review_status="PENDING",
)

_MAP_MARRIAGE_007 = MappingRule(
    mapping_id="MAP-J-MARRIAGE-007",
    judgment_id="J-MARRIAGE-007",
    classical_result="HUSBAND_COMPETE_RISK",
    classical_meaning="比劫与夫星关系，主感情竞争",
    modern_semantic="传统命理中，比劫与夫星发生作用的结构，被认为是感情方面容易有竞争的信号",
    modern_domain="婚姻/竞争",
    modern_expression="从传统命理角度看，该命局在感情方面存在容易有竞争的信号",
    semantic_boundary=("风险信号", "只是可能不是必然"),
    avoid_phrases=("你肯定被抢老公", "一定有第三者", "感情竞争确定"),
    source_judgment_id="J-MARRIAGE-007",
    mapping_version="V1.0",
    review_status="PENDING",
)


# ═══════════════════════════════════════════════════════════════
# Registry
# ═══════════════════════════════════════════════════════════════

MAPPING_REGISTRY: Dict[str, MappingRule] = {
    m.mapping_id: m for m in [
        # A类：结构类
        _MAP_SPECIAL_001,
        _MAP_MARRIAGE_004,
        _MAP_MARRIAGE_005,
        _MAP_DISASTER_004,
        _MAP_DISASTER_006,
        # B类：健康类
        _MAP_HEALTH_002,
        _MAP_HEALTH_003,
        _MAP_HEALTH_005,
        _MAP_KIN_004,
        # C类：刑灾/法律类
        _MAP_DISASTER_002,
        _MAP_DISASTER_003,
        _MAP_DISASTER_005,
        _MAP_WEALTH_017,
        # D类：财富类
        _MAP_WEALTH_003,
        _MAP_WEALTH_005,
        _MAP_WEALTH_006,
        _MAP_WEALTH_007,
        _MAP_WEALTH_008,
        _MAP_WEALTH_009,
        _MAP_WEALTH_010,
        _MAP_WEALTH_011,
        _MAP_WEALTH_012,
        _MAP_WEALTH_013,
        _MAP_WEALTH_014,
        _MAP_WEALTH_015,
        _MAP_WEALTH_016,
        # E类：事业/行业/婚姻/六亲/子女/时间
        _MAP_OFFICIAL_002,
        _MAP_OFFICIAL_003,
        _MAP_OFFICIAL_004,
        _MAP_OFFICIAL_005,
        _MAP_OFFICIAL_006,
        _MAP_CAREER_001,
        _MAP_CAREER_002,
        _MAP_CAREER_003,
        _MAP_CAREER_004,
        _MAP_CAREER_005,
        _MAP_CAREER_006,
        _MAP_TIMING_002,
        _MAP_TIMING_003,
        _MAP_KIN_002,
        _MAP_KIN_003,
        _MAP_CHILD_001,
        _MAP_MARRIAGE_002,
        _MAP_MARRIAGE_003,
        _MAP_MARRIAGE_006,
        _MAP_MARRIAGE_007,
    ]
}


def get_mapping_by_judgment_id(judgment_id: str) -> MappingRule | None:
    """按Judgment_ID查MappingRule"""
    for m in MAPPING_REGISTRY.values():
        if m.judgment_id == judgment_id:
            return m
    return None


if __name__ == "__main__":
    print(f"Mapping Rule总数: {len(MAPPING_REGISTRY)}")
    # 统计
    pending = sum(1 for m in MAPPING_REGISTRY.values() if m.review_status == "PENDING")
    print(f"待审核: {pending}")

    # 验证：每条Judgment_ID都有Mapping
    from tongshu.engines.blind_judgment_registry import get_production_judgments
    prod = get_production_judgments()
    missing = []
    for j_id in prod:
        if get_mapping_by_judgment_id(j_id) is None:
            missing.append(j_id)
    print(f"缺失Mapping的Judgment: {len(missing)}")
    if missing:
        for m in missing:
            print(f"  - {m}")
