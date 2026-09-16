# -*- coding: utf-8 -*-
"""盲派 Judgment Registry — 46条ESTABLISHED Judgment Evidence机器化登记。

依据：盲派Judgment_Evidence母表_V1.5（186d942d）
铁律：全布尔/枚举/集合，禁评分/概率/权重；CASE→JUDGMENT RULE禁止；
JUDGMENT→EVENT禁止自动推导；IN_PROGRESS/NOT_ESTABLISHED不进Production；
财富等级NOT_ESTABLISHED，禁止WEALTH_LEVEL输出。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple


class JudgmentStatus(str, Enum):
    ESTABLISHED = "ESTABLISHED"
    IN_PROGRESS = "IN_PROGRESS"
    NOT_ESTABLISHED = "NOT_ESTABLISHED"


class EvidenceLevel(str, Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    CASE_DERIVED = "CASE_DERIVED"
    VERIFY_PRIMARY = "VERIFY_PRIMARY"


class JudgmentDomain(str, Enum):
    WEALTH = "J1"
    OFFICIAL = "J2"
    CAREER = "J3"
    MARRIAGE = "J4"
    KIN = "J5"
    CHILD = "J6"
    HEALTH = "J7"
    TIMING = "J8"
    SPECIAL = "J9"


@dataclass(frozen=True)
class JudgmentClause:
    clause_id: str
    description: str
    condition_expr: str


@dataclass(frozen=True)
class JudgmentRule:
    judgment_id: str
    domain: JudgmentDomain
    assertion_inputs: Tuple[str, ...]
    clauses: Tuple[JudgmentClause, ...]
    judgment_result: str
    evidence_id: str
    source: str
    source_location: str
    evidence_level: EvidenceLevel
    status: JudgmentStatus
    exclusions: Tuple[str, ...] = ()
    note: str = ""


# ── 46条ESTABLISHED Judgment Registry ──────────────────────────────

JUDGMENT_REGISTRY: Dict[str, JudgmentRule] = {
    # ===== 第01章（9条） =====
    "J-WEALTH-003": JudgmentRule(
        judgment_id="J-WEALTH-003",
        domain=JudgmentDomain.WEALTH,
        assertion_inputs=("A-BZ-MAINGUEST",),
        clauses=(
            JudgmentClause("C1", "财根在主位=我家财", "root_in_main_position"),
            JudgmentClause("C2", "财根在宾位=他家财/公家财", "root_in_guest_position"),
            JudgmentClause("C3", "年上财=别人的财/国有财", "wealth_at_year"),
        ),
        judgment_result="WEALTH_OWNERSHIP",
        evidence_id="EVD-J-WEALTH-003",
        source="盲派中级命理学第01章",
        source_location="年上的官星被制为国有企业的官；主位一党，宾位一党，要制宾",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("不估财富金额",),
    ),
    "J-WEALTH-005": JudgmentRule(
        judgment_id="J-WEALTH-005",
        domain=JudgmentDomain.WEALTH,
        assertion_inputs=("A-PJ-FAN",),
        clauses=(JudgmentClause("C1", "反局在财星/财宫位置", "fanju_at_wealth_position"),),
        judgment_result="WEALTH_AUSPICIOUS_BREAK",
        evidence_id="EVD-J-WEALTH-005",
        source="盲派中级命理学第01章",
        source_location="财星反局财大凶，故此人非常穷",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("不估具体金额",),
    ),
    "J-OFFICIAL-002": JudgmentRule(
        judgment_id="J-OFFICIAL-002",
        domain=JudgmentDomain.OFFICIAL,
        assertion_inputs=("A-BZ-MAINGUEST",),
        clauses=(
            JudgmentClause("C1", "年上官=国企/公家单位", "official_at_year"),
            JudgmentClause("C2", "日时官=自己/私企", "official_at_day_or_hour"),
        ),
        judgment_result="OFFICIAL_OWNERSHIP",
        evidence_id="EVD-J-OFFICIAL-002",
        source="盲派中级命理学第01章",
        source_location="年上的官星被制为国有企业的官；官表示国家的单位、大型的单位，不表示官职",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("不估官职级别",),
    ),
    "J-OFFICIAL-003": JudgmentRule(
        judgment_id="J-OFFICIAL-003",
        domain=JudgmentDomain.OFFICIAL,
        assertion_inputs=("A-TY-TIYONG",),
        clauses=(JudgmentClause("C1", "官星透干 AND 官星克日主 AND 无制化", "official_transparent_and_attacking"),),
        judgment_result="OFFICIAL_DISASTER_RISK",
        evidence_id="EVD-J-OFFICIAL-003",
        source="盲派中级命理学第01章",
        source_location="因官星高透克身，故不能当官，当官就会有灾",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("不做官级别判断",),
    ),
    "J-CAREER-001": JudgmentRule(
        judgment_id="J-CAREER-001",
        domain=JudgmentDomain.CAREER,
        assertion_inputs=("A-SX-HESYMBOLS", "A-SX-HUASYMBOLS", "A-SX-MUSYMBOLS", "A-SX-ZHISYMBOLS", "A-SX-DAISYMBOLS"),
        clauses=(
            JudgmentClause("C1", "财原神生财之地=银行", "wealth_source_at_bank"),
            JudgmentClause("C2", "辰拱水=从混浊中提纯=化工/制药", "chen_gong_water"),
        ),
        judgment_result="CAREER_DIRECTION",
        evidence_id="EVD-J-CAREER-001",
        source="盲派中级命理学第01章",
        source_location="卯为食神为财原神，生财之地，为银行；辰是机器，拱了水，辰就成了泥巴，表从混浊中提纯",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("不指定具体职业名", "不扩成通用映射"),
    ),
    "J-SPECIAL-001": JudgmentRule(
        judgment_id="J-SPECIAL-001",
        domain=JudgmentDomain.SPECIAL,
        assertion_inputs=("A-PJ-ZHENG", "A-PJ-FAN"),
        clauses=(
            JudgmentClause("C1", "原局反局=原局凶", "natal_fanju"),
            JudgmentClause("C2", "大运反局=大运凶", "luck_fanju"),
            JudgmentClause("C3", "流年反局=流年凶", "year_fanju"),
        ),
        judgment_result="FANJU_AUSPICIOUS_LEVEL",
        evidence_id="EVD-J-SPECIAL-001",
        source="盲派中级命理学第01章",
        source_location="反局分原局反局、大运反局、流年反局三种，原局反局原局凶，大运反局大运凶，流年反局流年凶",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("正局不自动推吉", "反局只记应凶方向，不记具体事件"),
    ),
    "J-TIMING-002": JudgmentRule(
        judgment_id="J-TIMING-002",
        domain=JudgmentDomain.TIMING,
        assertion_inputs=("A-PJ-FANJULU",),
        clauses=(
            JudgmentClause("C1", "走干运=支为体(静)干为用(动)", "stem_luck_branch_ti"),
            JudgmentClause("C2", "走支运=支为用(动)干为体(静)", "branch_luck_stem_ti"),
        ),
        judgment_result="LUCK_TIYONG_DYNAMIC",
        evidence_id="EVD-J-TIMING-002",
        source="盲派中级命理学第01章大运反局节",
        source_location="走干运是支为体，干为用；走支运是支为用，干为体。体为静，用为动",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("此体用与第02章体用根本不同，不可混用",),
    ),
    "J-DISASTER-002": JudgmentRule(
        judgment_id="J-DISASTER-002",
        domain=JudgmentDomain.HEALTH,
        assertion_inputs=("A-DISASTER-PRISON",),
        clauses=(JudgmentClause("C1", "原局反局 AND 岁运见辰", "natal_fanju_and_chen_in_luck"),),
        judgment_result="PRISON_RISK",
        evidence_id="EVD-J-DISASTER-002",
        source="盲派中级命理学第01章大运反局节",
        source_location="辰为伤官库，伤官入库无自由；辰有牢狱之意",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("辰单独出现不等于牢狱", "必须叠加反局/官灾结构"),
    ),
    "J-HEALTH-002": JudgmentRule(
        judgment_id="J-HEALTH-002",
        domain=JudgmentDomain.HEALTH,
        assertion_inputs=("A-BODY-GONGWEI",),
        clauses=(JudgmentClause("C1", "时柱被穿 AND 岁运引动", "hour_pillar_chuan_and_triggered"),),
        judgment_result="HEALTH_RISK_BLADDER_RECTUM",
        evidence_id="EVD-J-HEALTH-002",
        source="盲派中级命理学第01章",
        source_location="穿了子女宫，所以是膀胱、直肠部分有问题",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("是身体风险信号，不是确诊疾病",),
    ),
    # ===== 第03章（4条） =====
    "J-DISASTER-003": JudgmentRule(
        judgment_id="J-DISASTER-003",
        domain=JudgmentDomain.HEALTH,
        assertion_inputs=("A-DISASTER-PRISON",),
        clauses=(JudgmentClause("C1", "丑酉同现 AND 阴干见阴支入墓", "chou_you_yin_ru_mu"),),
        judgment_result="CRIME_RISK_STRUCTURE",
        evidence_id="EVD-J-DISASTER-003",
        source="盲派中级命理学第03章",
        source_location="丑酉为阴中之阴，太多数丑酉与犯罪、黑社会有关；辛酉日主见丑时为黑社会；辛丑日主不是黑社会，因为浊中见清",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("辛丑日主不成立（浊中见清）", "不直接断必犯罪", "不泛化到所有阴干阴支"),
    ),
    "J-CAREER-003": JudgmentRule(
        judgment_id="J-CAREER-003",
        domain=JudgmentDomain.CAREER,
        assertion_inputs=("A-SX-STEMBRANCH",),
        clauses=(
            JudgmentClause("C1", "木火=文", "wood_fire_wenke"),
            JudgmentClause("C2", "金水=理", "metal_water_like"),
            JudgmentClause("C3", "戌亥=数学/计算", "xu_hai_math"),
            JudgmentClause("C4", "丑=玄学", "chou_xuanxue"),
            JudgmentClause("C5", "申=金融，酉=法律（酉不代表金融）", "shen_finance_you_law"),
        ),
        judgment_result="SUBJECT_DIRECTION",
        evidence_id="EVD-J-CAREER-003",
        source="盲派中级命理学第03章",
        source_location="木火主文，金水主理；戌亥为计算、运算的意思，表数学；申酉为法律，申还代表金融，酉不代表金融",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("只给学科方向，不指定具体专业名",),
    ),
    "J-CAREER-004": JudgmentRule(
        judgment_id="J-CAREER-004",
        domain=JudgmentDomain.CAREER,
        assertion_inputs=("A-SX-STEMBRANCH",),
        clauses=(
            JudgmentClause("C1", "阳木遇火=家具", "yang_wood_fire_furniture"),
            JudgmentClause("C2", "阴木遇火=纺织", "yin_wood_fire_textile"),
            JudgmentClause("C3", "辛金取财=五金行业", "xin_metal_wealth_hardware"),
            JudgmentClause("C4", "火克金=冶炼行业", "fire_attack_metal_smelting"),
        ),
        judgment_result="INDUSTRY_DIRECTION",
        evidence_id="EVD-J-CAREER-004",
        source="盲派中级命理学第03章",
        source_location="阳木遇火为家具，阴木遇火为纺织；辛金取财为五金行业，火克金为冶炼行业",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("只给行业方向，不指定具体单位",),
    ),
    "J-HEALTH-003": JudgmentRule(
        judgment_id="J-HEALTH-003",
        domain=JudgmentDomain.HEALTH,
        assertion_inputs=("A-BODY-STEM",),
        clauses=(
            JudgmentClause("C1", "甲丁同现=头发稀", "jia_ding_hair_thin"),
            JudgmentClause("C2", "甲为头丁为脸，癸冲克丁=面部受损", "jia_head_ding_face_gui_attack"),
        ),
        judgment_result="HEALTH_RISK_HAIR_FACE",
        evidence_id="EVD-J-HEALTH-003",
        source="盲派中级命理学第03章",
        source_location="甲遇丁火头发稀；甲为头，丁为脸，两癸冲克，谓干头反复，主凶",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("是身体风险信号，不是确诊",),
    ),
    # ===== 第04章（6条） =====
    "J-WEALTH-006": JudgmentRule(
        judgment_id="J-WEALTH-006",
        domain=JudgmentDomain.WEALTH,
        assertion_inputs=("A-WEALTH-LUASCASH", "A-SHEN-LU"),
        clauses=(
            JudgmentClause("C1", "禄不配印=辛苦", "lu_no_yin_hard"),
            JudgmentClause("C2", "禄配印(禄印相随)=享受/福气", "lu_with_yin_ease"),
        ),
        judgment_result="WEALTH_EFFORT_LEVEL",
        evidence_id="EVD-J-WEALTH-006",
        source="盲派中级命理学第04章神煞类象",
        source_location="禄不配印为辛苦，禄配印为表示享受之意；禄印相随，表享受",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("不得演化成财富等级", "合到印不算桃花"),
    ),
    "J-OFFICIAL-004": JudgmentRule(
        judgment_id="J-OFFICIAL-004",
        domain=JudgmentDomain.OFFICIAL,
        assertion_inputs=("A-SHEN-YANGREN",),
        clauses=(
            JudgmentClause("C1", "羊刃有制服=正业", "yangren_controlled_orthodox"),
            JudgmentClause("C2", "羊刃无制服=偏业", "yangren_uncontrolled_unorthodox"),
        ),
        judgment_result="CAREER_TYPE_ORTHODOX_UNORTHODOX",
        evidence_id="EVD-J-OFFICIAL-004",
        source="盲派中级命理学第04章",
        source_location="羊刃喜制服，制之得用正……无制服，则用偏",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("只给正/偏业方向", "军警/外科等只能作类象，不能直接当职业标签"),
    ),
    "J-CAREER-002": JudgmentRule(
        judgment_id="J-CAREER-002",
        domain=JudgmentDomain.CAREER,
        assertion_inputs=("A-MUKU-IDENTIFIED", "A-SX-MUSYMBOLS"),
        clauses=(
            JudgmentClause("C1", "羊刃库=军队/警察", "yangren_muku_military"),
            JudgmentClause("C2", "伤官食神库=寺庙/学校", "shangshi_muku_school"),
            JudgmentClause("C3", "财库=银行", "wealth_muku_bank"),
            JudgmentClause("C4", "官杀库=组织部/权力中心", "guansha_muku_org"),
        ),
        judgment_result="INSTITUTION_TYPE",
        evidence_id="EVD-J-CAREER-002",
        source="盲派中级命理学第04章",
        source_location="羊刃库或理解成军团或营地；伤官、食神库可理解成寺庙或学校；财库可理解成银行；官杀库可理解成权力中心或组织部门",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("只给机构方向，不指定具体单位名", "财库不自动推出从事银行"),
    ),
    "J-TIMING-003": JudgmentRule(
        judgment_id="J-TIMING-003",
        domain=JudgmentDomain.TIMING,
        assertion_inputs=("A-SHEN-YIMA",),
        clauses=(
            JudgmentClause("C1", "驿马存在=走动/外出/迁移象", "yima_present"),
            JudgmentClause("C2", "驿马被合=停留不动", "yima_he_stationary"),
        ),
        judgment_result="MOBILITY_SIGNAL",
        evidence_id="EVD-J-TIMING-003",
        source="盲派中级命理学第04章",
        source_location="驿马在命中表示走动、外出、远行、游走、迁移、奔忙等意；驿马逢合，则表示停留、不动之意",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("驿马≠必然搬家/出国/换工作", "只是象"),
    ),
    "J-KIN-002": JudgmentRule(
        judgment_id="J-KIN-002",
        domain=JudgmentDomain.KIN,
        assertion_inputs=("A-SHEN-KONGWANG",),
        clauses=(
            JudgmentClause("C1", "年支空亡=祖业空", "year_kongwang_zu_ye"),
            JudgmentClause("C2", "月支空亡=兄弟无靠", "month_kongwang_brother"),
            JudgmentClause("C3", "日支空亡=夫妻缘薄", "day_kongwang_spouse"),
            JudgmentClause("C4", "时支空亡=子女迟育", "hour_kongwang_children"),
        ),
        judgment_result="KIN_RELATION_QUALITY",
        evidence_id="EVD-J-KIN-002",
        source="盲派中级命理学第04章",
        source_location="年支空亡祖业空；月支空亡兄弟无靠或有伤损；日支空亡……夫妻之缘薄；时支空亡子女迟育",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("空亡≠必然事件", "只表缘薄/迟/空"),
    ),
    "J-MARRIAGE-002": JudgmentRule(
        judgment_id="J-MARRIAGE-002",
        domain=JudgmentDomain.MARRIAGE,
        assertion_inputs=("A-SHEN-LU",),
        clauses=(JudgmentClause("C1", "女命 AND 禄合伤官/官杀/财=禄绊桃花", "female_lu_he_taohua"),),
        judgment_result="TAOHUA_SIGNAL",
        evidence_id="EVD-J-MARRIAGE-002",
        source="盲派中级命理学第04章",
        source_location="女人的禄也是身体，合到伤官，官杀，财为禄绊桃花；合到夫妻宫不为桃花",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("合到夫妻宫不算桃花",),
    ),
    # ===== 第05章（4条） =====
    "J-WEALTH-007": JudgmentRule(
        judgment_id="J-WEALTH-007",
        domain=JudgmentDomain.WEALTH,
        assertion_inputs=("A-BODY-GONGWEI",),
        clauses=(
            JudgmentClause("C1", "时支被生=买车", "hour_branch_sheng_car"),
            JudgmentClause("C2", "时支被破/冲=车有问题/车祸风险", "hour_branch_break_car_risk"),
        ),
        judgment_result="CAR_SIGNAL",
        evidence_id="EVD-J-WEALTH-007",
        source="盲派中级命理学第05章",
        source_location="时支表示车，如买车、车祸均看时支；卯财在时上表车……原局子卯破表车有问题",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("是物品/应期信号，不是必然事件",),
    ),
    "J-HEALTH-005": JudgmentRule(
        judgment_id="J-HEALTH-005",
        domain=JudgmentDomain.HEALTH,
        assertion_inputs=("A-BODY-GONGWEI",),
        clauses=(JudgmentClause("C1", "年支被主位破 AND 比劫破年=腿足残疾风险", "year_break_by_main_bijie"),),
        judgment_result="HEALTH_RISK_LEG_FOOT",
        evidence_id="EVD-J-HEALTH-005",
        source="盲派中级命理学第05章",
        source_location="火旺了，比劫破到年上卯，阴为右，阳为左，表右腿有残疾；必须是主位和他破",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("必须是主位破宾位", "是风险信号不是确诊"),
    ),
    "J-KIN-003": JudgmentRule(
        judgment_id="J-KIN-003",
        domain=JudgmentDomain.KIN,
        assertion_inputs=("A-BODY-GONGWEI",),
        clauses=(JudgmentClause("C1", "年柱 AND 与妻宫关联 AND 印/伤食=丈母娘", "year_related_to_spouse_palace"),),
        judgment_result="MOTHER_IN_LAW_SOURCE",
        evidence_id="EVD-J-KIN-003",
        source="盲派中级命理学第05章",
        source_location="丈母娘在年上找，因年上表外戚，和妻宫发生了关联的印伤食都是丈母娘",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("与妻宫无关则伤可能是奶奶",),
    ),
    "J-MARRIAGE-003": JudgmentRule(
        judgment_id="J-MARRIAGE-003",
        domain=JudgmentDomain.MARRIAGE,
        assertion_inputs=("A-BODY-GONGWEI",),
        clauses=(JudgmentClause("C1", "夫妻星/宫在月柱=同学/同事", "spouse_at_month_schoolmate"),),
        judgment_result="SPOUSE_SOURCE_SCHOOLMATE",
        evidence_id="EVD-J-MARRIAGE-003",
        source="盲派中级命理学第05章",
        source_location="月柱表同学、同事，若夫妻象现在月上可能是同学",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("只给来源方向，不必然",),
    ),
    # ===== 第06章（5条） =====
    "J-WEALTH-008": JudgmentRule(
        judgment_id="J-WEALTH-008",
        domain=JudgmentDomain.WEALTH,
        assertion_inputs=("A-TY-TIYONG",),
        clauses=(JudgmentClause("C1", "年月柱财星旺 AND 女命优先=早辍学", "wealth_strong_at_year_month_female"),),
        judgment_result="EARLY_DROPOUT_TENDENCY",
        evidence_id="EVD-J-WEALTH-008",
        source="盲派中级命理学第06章",
        source_location="年月逢旺的人，尤其是女的，一定很早辍学，诀：财多心乱",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("不必然，只是倾向",),
    ),
    "J-WEALTH-009": JudgmentRule(
        judgment_id="J-WEALTH-009",
        domain=JudgmentDomain.WEALTH,
        assertion_inputs=("A-TY-TIYONG",),
        clauses=(
            JudgmentClause("C1", "财星虚透天干=才华/会来事", "wealth_transparent_talent"),
            JudgmentClause("C2", "财星虚透在时上=爱打扮/时尚", "wealth_transparent_at_hour_fashion"),
        ),
        judgment_result="WEALTH_PRESENTATION",
        evidence_id="EVD-J-WEALTH-009",
        source="盲派中级命理学第06章",
        source_location="财虚透是指才华，表会来事、会交往、会说话；财星虚透在时上为爱打扮，时尚，穿金带银",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("是象，不必然",),
    ),
    "J-CHILD-001": JudgmentRule(
        judgment_id="J-CHILD-001",
        domain=JudgmentDomain.CHILD,
        assertion_inputs=("A-TY-TIYONG",),
        clauses=(
            JudgmentClause("C1", "男命 AND 七杀有财=儿", "male_sha_with_wealth_son"),
            JudgmentClause("C2", "男命 AND 七杀无财=女", "male_sha_no_wealth_daughter"),
            JudgmentClause("C3", "穿倒财=生女", "chuan_wealth_daughter"),
            JudgmentClause("C4", "行伤官大运=生儿", "hurt_official_luck_son"),
        ),
        judgment_result="CHILD_GENDER_TENDENCY",
        evidence_id="EVD-J-CHILD-001",
        source="盲派中级命理学第06章",
        source_location="男命以杀为儿，官为女……杀＋财＝儿，杀无财为女。穿倒财生女；行伤大运，则生儿",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("只是倾向，不是必然",),
    ),
    "J-KIN-004": JudgmentRule(
        judgment_id="J-KIN-004",
        domain=JudgmentDomain.KIN,
        assertion_inputs=("A-TY-TIYONG",),
        clauses=(JudgmentClause("C1", "食神被穿 AND 无救应=母早死风险信号", "shishen_chuan_no_salvation"),),
        judgment_result="MOTHER_HEALTH_RISK",
        evidence_id="EVD-J-KIN-004",
        source="盲派中级命理学第06章",
        source_location="穿倒了食神……母早死；食、伤、禄为母",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("是风险信号，不是必然",),
    ),
    "J-WEALTH-010": JudgmentRule(
        judgment_id="J-WEALTH-010",
        domain=JudgmentDomain.WEALTH,
        assertion_inputs=("A-BODY-GONGWEI",),
        clauses=(JudgmentClause("C1", "时柱被穿=车被盗风险信号", "hour_pillar_chuan_car_theft"),),
        judgment_result="CAR_THEFT_RISK",
        evidence_id="EVD-J-WEALTH-010",
        source="盲派中级命理学第06章末",
        source_location="穿了门口注意车被盗",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("是风险信号，不是必然",),
    ),
    # ===== 第07章（5条，J-KIN-005降VERIFY） =====
    "J-OFFICIAL-005": JudgmentRule(
        judgment_id="J-OFFICIAL-005",
        domain=JudgmentDomain.OFFICIAL,
        assertion_inputs=("A-SX-HESYMBOLS",),
        clauses=(JudgmentClause("C1", "阳字制阴字=公安/刑警组合", "yang_attack_yin_police"),),
        judgment_result="LAW_ENFORCEMENT_DIRECTION",
        evidence_id="EVD-J-OFFICIAL-005",
        source="盲派中级命理学第07章",
        source_location="申辰丑为阴，寅为阳，以阳制阴，公安处长；卯穿了辰阴，为公安！刑警！",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("只给部门方向，不指定级别",),
    ),
    "J-WEALTH-011": JudgmentRule(
        judgment_id="J-WEALTH-011",
        domain=JudgmentDomain.WEALTH,
        assertion_inputs=("A-SX-DAISYMBOLS",),
        clauses=(
            JudgmentClause("C1", "财带官帽=公家之财", "wealth_with_official_cap_public"),
            JudgmentClause("C2", "官带财帽=管理财的官", "official_with_wealth_cap_manager"),
            JudgmentClause("C3", "印带官帽=权力", "yin_with_official_cap_power"),
            JudgmentClause("C4", "印带财帽=薪水/上班领工资", "yin_with_wealth_cap_salary"),
        ),
        judgment_result="WEALTH_NATURE",
        evidence_id="EVD-J-WEALTH-011",
        source="盲派中级命理学第07章带象原则",
        source_location="财带官帽：公家之财。官带财帽：管理财的官。印带官帽：权力。印带财帽：表薪水",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("是象，不必然",),
    ),
    "J-OFFICIAL-006": JudgmentRule(
        judgment_id="J-OFFICIAL-006",
        domain=JudgmentDomain.OFFICIAL,
        assertion_inputs=("A-MUKU-IDENTIFIED",),
        clauses=(JudgmentClause("C1", "七杀入羊刃墓=军队/军团方向", "sha_into_yangren_muku_military"),),
        judgment_result="MILITARY_DIRECTION",
        evidence_id="EVD-J-OFFICIAL-006",
        source="盲派中级命理学第07章墓象原则",
        source_location="七杀入了羊刃墓，表军队，军团",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("不推具体级别（案例少将仅作验证）", "不指定单位"),
    ),
    "J-CAREER-005": JudgmentRule(
        judgment_id="J-CAREER-005",
        domain=JudgmentDomain.CAREER,
        assertion_inputs=("A-SX-HUASYMBOLS",),
        clauses=(JudgmentClause("C1", "辰子同现=化工/制药/提纯", "chen_zi_chemical_pharma"),),
        judgment_result="CHEMICAL_PHARMA_DIRECTION",
        evidence_id="EVD-J-CAREER-005",
        source="盲派中级命理学第07章化象原则",
        source_location="辰---子，化工，制药，提纯",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("只给行业方向",),
    ),
    "J-WEALTH-012": JudgmentRule(
        judgment_id="J-WEALTH-012",
        domain=JudgmentDomain.WEALTH,
        assertion_inputs=("A-MUKU-IDENTIFIED",),
        clauses=(JudgmentClause("C1", "丑未冲 AND 丑为财库=资本运营/资金运作", "chou_wei_chong_capital_operation"),),
        judgment_result="WEALTH_METHOD_CAPITAL",
        evidence_id="EVD-J-WEALTH-012",
        source="盲派中级命理学第07章制象原则",
        source_location="丑是财库，财库制劫财与印库……他取财的手段与方式是资本运营",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("不估金额",),
    ),
    # ===== 第08章（5条） =====
    "J-WEALTH-013": JudgmentRule(
        judgment_id="J-WEALTH-013",
        domain=JudgmentDomain.WEALTH,
        assertion_inputs=("A-WEALTH-LUASCASH",),
        clauses=(
            JudgmentClause("C1", "禄存在 AND (无伤食泄 OR 无财)=禄可当财", "lu_as_wealth_condition"),
            JudgmentClause("C2", "禄当财条件=印生禄", "lu_as_wealth_yin_sheng"),
            JudgmentClause("C3", "以禄取财=辛苦求财", "lu_wealth_hard"),
            JudgmentClause("C4", "禄作用神最怕见劫财=分禄破财", "lu_jiecai_broken"),
        ),
        judgment_result="LU_AS_WEALTH_STRUCTURE",
        evidence_id="EVD-J-WEALTH-013",
        source="盲派中级命理学第08章禄神当财节",
        source_location="命中占禄，无伤食泄时，或八字无财时，禄可以当财看；禄是现成之福，其条件是印生禄；以禄当财，喜印，忌伤食劫财；禄作用神最怕见劫财，劫财有分禄之意",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("不估金额",),
    ),
    "J-WEALTH-014": JudgmentRule(
        judgment_id="J-WEALTH-014",
        domain=JudgmentDomain.WEALTH,
        assertion_inputs=("A-WEALTH-LUASCASH",),
        clauses=(
            JudgmentClause("C1", "八字无财 AND 有伤食=伤食当财富", "no_wealth_shangshi_as_wealth"),
            JudgmentClause("C2", "伤官=谋为/经营之财；食神=思想/脑力之财", "shangshi_wealth_nature"),
            JudgmentClause("C3", "天干食=思想，地支食=企业", "shishen_stem_branch_nature"),
        ),
        judgment_result="SHANGSHI_AS_WEALTH",
        evidence_id="EVD-J-WEALTH-014",
        source="盲派中级命理学第08章伤食当财节",
        source_location="八字无财星，却有伤食星，以伤食当财富看；伤官为谋为、经营之财；食神为思想、脑力之财。天干的食表思想，地支的食表企业",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("有财时伤食是原神/投资财",),
    ),
    "J-WEALTH-015": JudgmentRule(
        judgment_id="J-WEALTH-015",
        domain=JudgmentDomain.WEALTH,
        assertion_inputs=("A-WEALTH-LUASCASH",),
        clauses=(
            JudgmentClause("C1", "官统财/财统官=官杀当财富看", "guan_wealth_unified"),
            JudgmentClause("C2", "官杀有制但制不净=官杀当财富看", "guansha_not_controlled_pure"),
        ),
        judgment_result="GUANSHA_AS_WEALTH",
        evidence_id="EVD-J-WEALTH-015",
        source="盲派中级命理学第08章官杀当财节",
        source_location="官统财或财统官，官杀当财富看；官杀有制，但制服不太好，官杀可以当财富看",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("只论原局，大运出现不算", "不推财富等级/金额"),
    ),
    "J-CAREER-006": JudgmentRule(
        judgment_id="J-CAREER-006",
        domain=JudgmentDomain.CAREER,
        assertion_inputs=("A-SX-HUASYMBOLS",),
        clauses=(
            JudgmentClause("C1", "地支食神做功 AND 食神生财=适合做企业经营", "inner_shishen_business"),
            JudgmentClause("C2", "食神带官象=企业经理人（非本人企业）", "shishen_with_official_manager"),
        ),
        judgment_result="BUSINESS_OPERATION",
        evidence_id="EVD-J-CAREER-006",
        source="盲派中级命理学第08章经营取财节",
        source_location="内食神格（地支食神做功者）适合于做企业经营；食神带官象说明不是他本人的企业，应是企业经理人",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("不指定具体行业",),
    ),
    "J-WEALTH-016": JudgmentRule(
        judgment_id="J-WEALTH-016",
        domain=JudgmentDomain.WEALTH,
        assertion_inputs=("A-BODY-GONGWEI",),
        clauses=(JudgmentClause("C1", "财星在年柱 AND 做功 AND 年主远方 AND 水象配合=远方求财方向", "wealth_at_year_remote_trade"),),
        judgment_result="REMOTE_WEALTH_DIRECTION",
        evidence_id="EVD-J-WEALTH-016",
        source="盲派中级命理学第08章经营取财节",
        source_location="财在年上，局有火土成势，意在制财，冲制，一股一股来财。年主远方，水主海运，故是做海外贸易的",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("不单独推海外贸易", "需完整结构"),
    ),
    # ===== 第10章（4条） =====
    "J-MARRIAGE-004": JudgmentRule(
        judgment_id="J-MARRIAGE-004",
        domain=JudgmentDomain.MARRIAGE,
        assertion_inputs=("A-MARRIAGE-MAINGUEST",),
        clauses=(JudgmentClause("C1", "夫妻宫无破坏 AND 宫制星成立=好婚姻", "spouse_palace_quiet_control"),),
        judgment_result="GOOD_MARRIAGE_STRUCTURE",
        evidence_id="EVD-J-MARRIAGE-004",
        source="盲派中级命理学第10章好婚姻节",
        source_location="夫妻宫位要安静……不能被刑坏、冲破、穿倒；夫妻宫的宫位制去夫妻星的字为好婚姻……如制之不住，反为坏婚姻",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("制之不住=反为坏婚姻",),
    ),
    "J-MARRIAGE-005": JudgmentRule(
        judgment_id="J-MARRIAGE-005",
        domain=JudgmentDomain.MARRIAGE,
        assertion_inputs=("A-MARRIAGE-MAINGUEST",),
        clauses=(
            JudgmentClause("C1", "夫妻宫被刑冲破穿=婚姻不好", "spouse_palace_damaged"),
            JudgmentClause("C2", "破坏较轻=婚姻不好不一定离婚", "damage_light_no_divorce"),
            JudgmentClause("C3", "破坏太重=必离异", "damage_heavy_divorce"),
            JudgmentClause("C4", "比劫争夫/争妻=第三者问题", "bijie_compete_spouse"),
        ),
        judgment_result="BAD_MARRIAGE_STRUCTURE",
        evidence_id="EVD-J-MARRIAGE-005",
        source="盲派中级命理学第10章差婚姻节",
        source_location="夫妻宫位有用，却被刑、冲、破、穿……不好到什么程度，能否离婚，却要看夫妻宫破坏到什么程度；比劫争夫……轻者有第三者问题，重者必离婚",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("不必然离婚，看破坏程度", "不用数学破坏程度分数"),
    ),
    "J-MARRIAGE-006": JudgmentRule(
        judgment_id="J-MARRIAGE-006",
        domain=JudgmentDomain.MARRIAGE,
        assertion_inputs=("A-MARRIAGE-MAINGUEST",),
        clauses=(
            JudgmentClause("C1", "原局配偶宫或星原有合，冲其合为结婚应期", "spouse_he_chong_marriage_timing"),
            JudgmentClause("C2", "配偶星或宫入墓，刑冲其墓流年为婚期", "spouse_ru_mu_chong_marriage_timing"),
        ),
        judgment_result="MARRIAGE_TIMING_WINDOW",
        evidence_id="EVD-J-MARRIAGE-006",
        source="盲派中级命理学第10章结婚应期节",
        source_location="配偶宫或配偶星原有合……应在冲其合为结婚应期；配偶星或配偶宫入墓时，应刑冲其墓的流年而结婚",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("是应期窗口，不是事件坐实",),
    ),
    "J-MARRIAGE-007": JudgmentRule(
        judgment_id="J-MARRIAGE-007",
        domain=JudgmentDomain.MARRIAGE,
        assertion_inputs=("A-TY-TIYONG",),
        clauses=(JudgmentClause("C1", "比劫与夫星有关系=争夫结构", "bijie_with_husband_star_compete"),),
        judgment_result="COMPETE_HUSBAND_TENDENCY",
        evidence_id="EVD-J-MARRIAGE-007",
        source="盲派中级命理学第10章差婚姻节",
        source_location="比肩争夫的几种可能：1、找的老公是离过婚的。2、老公有外遇。3、自己当小的或被包。4、离婚。5、曾经的对象",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("只是可能，不是必然",),
    ),
    # ===== 第12章（4条） =====
    "J-DISASTER-004": JudgmentRule(
        judgment_id="J-DISASTER-004",
        domain=JudgmentDomain.HEALTH,
        assertion_inputs=("A-DISASTER-PRISON",),
        clauses=(
            JudgmentClause("A", "亥/丑/辰牢狱字坏阳性有用之物（阳制阴不算）", "chou_chen_hai_damage_yang_useful"),
            JudgmentClause("B", "水多金沉=牢狱", "water_metal_sink_prison"),
            JudgmentClause("C", "枭神夺食=失去自由", "xiao_shen_duo_shishen_freedom"),
            JudgmentClause("D", "劫财+伤官+与官杀对抗=牢狱", "jiecai_shangshi_attack_official_prison"),
            JudgmentClause("E", "反局+辰/丑=多数应牢狱", "fanju_with_chou_chen_most_prison"),
        ),
        judgment_result="PRISON_STRUCTURE",
        evidence_id="EVD-J-DISASTER-004",
        source="盲派中级命理学第12章",
        source_location="亥水、丑土、辰土……有牢狱象；水多金沉为牢狱；枭神夺食为牢狱……失去自由；劫财、伤官的组合……再与官杀对抗必为牢狱；凡出现反局的情况，有辰、丑等字在局中，多数应牢狱",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("阳制阴不算", "E是多数/倾向不是必然", "不压成单一Boolean"),
    ),
    "J-DISASTER-005": JudgmentRule(
        judgment_id="J-DISASTER-005",
        domain=JudgmentDomain.HEALTH,
        assertion_inputs=("A-DISASTER-PRISON",),
        clauses=(
            JudgmentClause("C1", "日主得禄之年=出狱应期", "day_master_lu_release"),
            JudgmentClause("C2", "日主合出/冲出日主之年=出狱应期", "day_master_he_chong_release"),
            JudgmentClause("C3", "牢狱为库，冲穿坏库=出狱", "prison_muku_chuan_release"),
        ),
        judgment_result="RELEASE_TIMING_WINDOW",
        evidence_id="EVD-J-DISASTER-005",
        source="盲派中级命理学第12章出狱节",
        source_location="当日主得禄之年或日主合出、冲出日主之年出狱；如牢狱为库，冲、穿坏了库为出狱",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("是应期窗口，不是事件坐实",),
    ),
    "J-WEALTH-017": JudgmentRule(
        judgment_id="J-WEALTH-017",
        domain=JudgmentDomain.WEALTH,
        assertion_inputs=("A-TY-TIYONG",),
        clauses=(JudgmentClause("C1", "劫财+官杀在主位=小偷结构", "jiecai_official_at_main_position_thief"),),
        judgment_result="THIEF_STRUCTURE",
        evidence_id="EVD-J-WEALTH-017",
        source="盲派中级命理学第12章",
        source_location="劫财为手，官为盗贼，劫财和官在主位组合时为小偷",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("是结构象，不是必然犯罪",),
    ),
    "J-DISASTER-006": JudgmentRule(
        judgment_id="J-DISASTER-006",
        domain=JudgmentDomain.HEALTH,
        assertion_inputs=("A-MUKU-IDENTIFIED",),
        clauses=(JudgmentClause("C1", "食伤入墓=失去自由/不能和外界联系", "shangshi_ru_muku_freedom_loss"),),
        judgment_result="FREEDOM_LOSS_STRUCTURE",
        evidence_id="EVD-J-DISASTER-006",
        source="盲派中级命理学第12章",
        source_location="食伤也表示自由，入墓为失去自由，不能和外界联系",
        evidence_level=EvidenceLevel.PRIMARY,
        status=JudgmentStatus.ESTABLISHED,
        exclusions=("是结构象，不是必然坐牢",),
    ),
}


# ── Registry Gate 8项硬性检查 ─────────────────────────────────────

def get_production_judgments() -> Dict[str, JudgmentRule]:
    """只返回ESTABLISHED状态的Judgment（可进Production）"""
    return {k: v for k, v in JUDGMENT_REGISTRY.items()
            if v.status == JudgmentStatus.ESTABLISHED}


def validate_registry() -> List[str]:
    """Registry Gate 8项硬性检查"""
    errors = []
    judgments = list(JUDGMENT_REGISTRY.values())

    # 1. Judgment_ID唯一性
    ids = [j.judgment_id for j in judgments]
    if len(ids) != len(set(ids)):
        errors.append("Judgment_ID有重复")

    # 2. Evidence_ID唯一性
    ev_ids = [j.evidence_id for j in judgments]
    if len(ev_ids) != len(set(ev_ids)):
        errors.append("Evidence_ID有重复")

    # 3. 每条都有Source和Source_Location
    for j in judgments:
        if not j.source:
            errors.append(f"{j.judgment_id} 缺Source")
        if not j.source_location:
            errors.append(f"{j.judgment_id} 缺Source_Location")

    # 4. Clause不合并（每条至少1个Clause）
    for j in judgments:
        if len(j.clauses) == 0:
            errors.append(f"{j.judgment_id} 无Clause")

    # 5. Exclusion进约束
    for j in judgments:
        if not j.exclusions:
            errors.append(f"{j.judgment_id} 无Exclusion")

    # 6. CASE-DERIVED不得进ESTABLISHED
    for j in judgments:
        if j.evidence_level == EvidenceLevel.CASE_DERIVED and j.status == JudgmentStatus.ESTABLISHED:
            errors.append(f"{j.judgment_id} CASE-DERIVED标为ESTABLISHED")

    # 7. IN_PROGRESS/NOT_ESTABLISHED不得标ESTABLISHED（Registry里不应有非ESTABLISHED）
    for j in judgments:
        if j.status != JudgmentStatus.ESTABLISHED:
            errors.append(f"{j.judgment_id} 非ESTABLISHED，不应在Registry Production")

    # 8. 财富等级禁止
    for j in judgments:
        if "财富等级" in j.judgment_result or "WEALTH_LEVEL" in j.judgment_result:
            errors.append(f"{j.judgment_id} 出现财富等级判断")

    return errors


if __name__ == "__main__":
    errors = validate_registry()
    print(f"Registry总条数: {len(JUDGMENT_REGISTRY)}")
    print(f"Production ESTABLISHED: {len(get_production_judgments())}")
    if errors:
        print(f"❌ Gate失败 {len(errors)}项:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("✅ Registry Gate PASS")
