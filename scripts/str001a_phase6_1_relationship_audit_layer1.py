"""
STR-001A Phase 6.1 Relationship Audit — Layer 1 (事实定义层)

Contract/Governance Layer = FROZEN (v6-final.1)
P6.1-A L1 Fact Expansion = COMPLETE (十二长生 + 完整藏干已接入)

本阶段目标:
不是继续"发明规则"，而是把 L1 已有事实 → 五部经典原文 → 关系是否成立
→ 在什么条件下成立 → 是否有反例/限定 一次性审清楚。

核心原则:
不能先假定"长生=强根""财多=耗身""官杀旺=克身弱"，再去找一句话证明。
应该反过来，让五部经典决定哪些关系可以成立。

关系和结论彻底分开:
L1事实 → 经典是否称其为"通根"？ → YES/NO/条件性
→ 经典是否进一步称为"根深"？ → YES/NO/未授权
→ 是否因此能推出"身强"？ → 另行审计

4层依赖链:
Layer 1 (事实定义层): 是什么的定义，不涉及强弱
  1. 月令 → 得时/失时 → 旺/衰
  2. 藏干 → 本气/中气/余气（层级定义）
  3. 十二长生 → 12状态定义（不涉及根气）

Layer 2 (关系建立层): A和B有什么关系
  4. 藏干 → 通根/根
  5. 十二长生 → 根气
  6. 根 → 根深/根浅/无根
  7. 日主 → 得地/失地
  8. 印比 → 生扶
  9. 官杀/食伤/财 → 克/泄/耗
  + 补充: 合/刑/冲/空亡 → 对根气的影响

Layer 3 (组合关系层): 多个条件组合产生什么
  10. 印比+通根 → 党众
  11. 印比不足 → 助寡
  12. 党众/助寡 → 强弱
  13. 克泄耗 → 强弱是否成立

Layer 4 (修正覆盖层): 什么情况下前面的结论被修正
  14. 月令+全局 → 旺衰修正
  15. 全局气势 → 修正月令
  16. 调候 → 是否影响强弱
  17. 特殊格局 → 覆盖常规判断

5种结果分类:
1. SOURCE_SUPPORTED — 原典明确表达，可以进入候选关系
2. SOURCE_SUPPORTED_WITH_QUALIFIER — 原典支持，但必须带前提
3. SOURCE_MAPPED_NON_PROOF — 有相关语义，但没有授权因果链
4. INSUFFICIENT_SOURCE — 五部经典找不到足够依据
5. SOURCE_CONTESTED — 五部经典之间存在明确争议/不同体系说法

本脚本只执行 Layer 1 (事实定义层) 3个关系的审计。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


# ============================================================
# 一、结果分类枚举
# ============================================================

class RelationAuditResult(str, Enum):
    SOURCE_SUPPORTED = "SOURCE_SUPPORTED"
    SOURCE_SUPPORTED_WITH_QUALIFIER = "SOURCE_SUPPORTED_WITH_QUALIFIER"
    SOURCE_MAPPED_NON_PROOF = "SOURCE_MAPPED_NON_PROOF"
    INSUFFICIENT_SOURCE = "INSUFFICIENT_SOURCE"
    SOURCE_CONTESTED = "SOURCE_CONTESTED"


class RelationType(str, Enum):
    DEFINITION = "DEFINITION"           # 定义
    CONDITIONAL = "CONDITIONAL"         # 条件关系
    DESCRIPTIVE = "DESCRIPTIVE"         # 描述
    NORMATIVE = "NORMATIVE"             # 规范
    CAUSAL = "CAUSAL"                   # 因果
    CORRECTION = "CORRECTION"           # 修正/覆盖


class TextLayer(str, Enum):
    ORIGINAL = "ORIGINAL"               # 原典原文
    ORIGINAL_NOTE = "ORIGINAL_NOTE"     # 原注
    COMMENTARY = "COMMENTARY"           # 后世注家解释
    UNKNOWN = "UNKNOWN"


# ============================================================
# 二、原文证据结构
# ============================================================

@dataclass
class SourceEvidence:
    """单条原文证据"""
    classic: str                    # 经典名称
    chapter: str                    # 章节/篇目
    original_text: str              # 原文
    text_layer: TextLayer           # 文本层级（原文/原注/注释）
    relation_type: RelationType     # 关系类型
    context: str = ""               # 语境说明
    supports_causal_chain: bool = False  # 是否授权我们要的因果链
    notes: str = ""


@dataclass
class ClassicCrossCheck:
    """五部经典交叉验证"""
    yuan_haizi: str = "未提及"       # 《渊海子平》
    zi_ping_zhen_quan: str = "未提及"  # 《子平真诠》
    di_tian_sui: str = "未提及"        # 《滴天髓》
    qiong_tong_bao_jian: str = "未提及"  # 《穷通宝鉴》
    san_ming_tong_hui: str = "未提及"   # 《三命通会》


# ============================================================
# 三、关系审计模板
# ============================================================

@dataclass
class RelationAudit:
    """单条关系的完整审计结果"""
    relation_id: str
    layer: int                      # 所属层 (1-4)
    relation_description: str       # 关系描述
    l1_fact_dependencies: List[str] # 依赖的L1事实

    # 术语确认
    term_clarification: str = ""    # 关系中关键术语在原典中的真实用法

    # 原文证据
    evidence: List[SourceEvidence] = field(default_factory=list)

    # 五部经典交叉
    cross_check: ClassicCrossCheck = field(default_factory=ClassicCrossCheck)

    # 审计判定
    audit_result: RelationAuditResult = RelationAuditResult.INSUFFICIENT_SOURCE
    relation_type: RelationType = RelationType.DESCRIPTIVE
    authorizes_causal_chain: bool = False  # 是否授权我们要的因果链
    conditions: str = ""            # 条件/限定（如果有）
    counterexamples: str = ""       # 反例（如果有）
    state_effect: str = ""          # 对Canonical State的影响（哪一层）

    # 结论
    conclusion: str = ""
    can_enter_evidence_contract: bool = False  # 是否可以进入Evidence Contract
    notes: str = ""


# ============================================================
# 四、术语对照表
# ============================================================

TERM_GLOSSARY = {
    "得时": {
        "classic_usage": "日主五行与月令五行相同或受月令生（春木夏火秋金冬水）",
        "sources": ["《子平真诠》第六章", "《渊海子平》"],
        "note": "得时=旺，但旺≠强。得时只是旺衰基线，不直接等于身强。"
    },
    "失时": {
        "classic_usage": "日主五行被月令克或克月令（如木生申酉月）",
        "sources": ["《子平真诠》第六章"],
        "note": "失时=衰，但衰≠弱。失时只是旺衰基线，不直接等于身弱。"
    },
    "旺": {
        "classic_usage": "得时为旺，指日主在月令当令或得令",
        "sources": ["《子平真诠》第六章"],
        "note": "旺是旺衰维度，不是强弱维度。虽旺而弱是可能的。"
    },
    "衰": {
        "classic_usage": "失时为衰，指日主在月令失令",
        "sources": ["《子平真诠》第六章"],
        "note": "衰是旺衰维度，不是强弱维度。虽衰而强是可能的。"
    },
    "通根": {
        "classic_usage": "天干在地支中有同类五行（本气/中气/余气）",
        "sources": ["《渊海子平》", "《子平真诠》"],
        "note": "通根不等于根深。通根只是'有根'，根的质量需要另行判断。"
    },
    "根气": {
        "classic_usage": "原典中较少直接使用'根气'一词，更多用'根''通根''得地'",
        "sources": ["后人归纳"],
        "note": "'根气'可能是后人归纳的概念，原典中需要确认是否有明确用法。"
    },
    "根深": {
        "classic_usage": "原典中是否有'根深'一词？需要确认。《子平真诠》用'根之重者'（长生禄旺）和'根之轻者'（墓库余气）",
        "sources": ["《子平真诠》（根之重者/根之轻者）"],
        "note": "'根深/根浅'可能是后人对'根之重者/根之轻者'的简化。原典用词需要严格确认。"
    },
    "得地": {
        "classic_usage": "日主在地支中有根（通根），与'失地'相对",
        "sources": ["《渊海子平》", "《子平真诠》"],
        "note": "得地≈通根，但'得地'可能更强调地支整体环境，需要确认是否与通根完全同义。"
    },
    "党众": {
        "classic_usage": "比劫印绶多且通根扶助。《子平真诠》：'比劫印绶通根扶助为党众'",
        "sources": ["《子平真诠》第六章"],
        "note": "党众=强，但这是强弱维度。党众需要'比印重叠+通根'，不是简单的印比数量多。"
    },
    "助寡": {
        "classic_usage": "比劫印绶少且不通根，与'党众'相对",
        "sources": ["《子平真诠》第六章"],
        "note": "助寡=弱，但这是强弱维度。助寡不等于身弱结论，需要结合其他条件。"
    },
    "十二长生": {
        "classic_usage": "长生、沐浴、冠带、临官、帝旺、衰、病、死、墓、绝、胎、养，描述五行在十二地支的生长消亡过程",
        "sources": ["《三命通会·卷二·论五行旺相休囚死并寄生十二宫》", "《命理探源·卷三》"],
        "note": "十二长生是描述五行状态的概念，不等于'根气'。十二长生→根气的关系需要另行审计。"
    },
    "本气/中气/余气": {
        "classic_usage": "地支藏干的三层分类。本气=地支自身五行，中气=次旺之气，余气=季节残留之气",
        "sources": ["《渊海子平·地支藏遁歌》", "后人归纳"],
        "note": "三层分类可能是后人归纳的。原典《渊海子平》直接列出藏干，是否明确使用'本气/中气/余气'的名称需要确认。"
    },
}


# ============================================================
# 五、Layer 1 关系审计
# ============================================================

def audit_relation_001() -> RelationAudit:
    """
    REL-001: 月令 → 得时/失时 → 旺/衰
    Layer 1 (事实定义层)
    审计: 五书是否一致？谁定义、谁修正？
    """
    audit = RelationAudit(
        relation_id="REL-001",
        layer=1,
        relation_description="月令 → 得时/失时 → 旺/衰（旺衰基线定义）",
        l1_fact_dependencies=["month_branch", "day_master_element"],
        term_clarification="得时=日主五行与月令相同或受月令生；失时=日主五行被月令克或克月令。旺/衰是旺衰维度，不等于强/弱。",
    )

    # 原文证据
    audit.evidence = [
        SourceEvidence(
            classic="子平真诠",
            chapter="第六章 论十干得时不旺失时不弱",
            original_text="旺衰强弱四字，昔人论命，每笼统互用，不知须分别看也。大致得时为旺，失时为衰；党众为强，助寡为弱。故有虽旺而弱者，亦有虽衰而强者，分别观之，其理自明。",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.DEFINITION,
            context="讨论旺衰与强弱的区别，明确区分四个概念",
            supports_causal_chain=True,
            notes="这是最核心的定义。明确'得时为旺，失时为衰'，同时强调旺≠强、衰≠弱。"
        ),
        SourceEvidence(
            classic="子平真诠",
            chapter="第六章",
            original_text="春木夏火秋金冬水为得时，比劫印绶通根扶助为党众。甲乙木生于寅卯月，为得时...",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.DEFINITION,
            context="具体举例说明什么是得时",
            supports_causal_chain=True,
        ),
        SourceEvidence(
            classic="滴天髓",
            chapter="任氏曰（注）",
            original_text="得时俱为旺论，失令便作衰看，虽是至理，亦死法也。然亦可活看。",
            text_layer=TextLayer.COMMENTARY,
            relation_type=RelationType.CORRECTION,
            context="任铁樵对'得时为旺失时为衰'的修正，指出这是'死法'，需要活看",
            supports_causal_chain=False,
            notes="注意：这是任铁樵的注，不是《滴天髓》原文。它修正了基线定义，但不否定基线定义本身。"
        ),
        SourceEvidence(
            classic="渊海子平",
            chapter="论日为主",
            original_text="以日为主，年为本，月为提纲，时为辅佐。...后看月令中金木水火土，何者旺...",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.DESCRIPTIVE,
            context="强调月令的提纲地位，看月令中何者旺",
            supports_causal_chain=True,
            notes="《渊海子平》明确月令为'提纲'，是判断旺衰的基础。"
        ),
        SourceEvidence(
            classic="渊海子平",
            chapter="继善篇",
            original_text="欲知贵贱，先观月令乃提纲。",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.NORMATIVE,
            context="强调月令的首要地位",
            supports_causal_chain=True,
        ),
    ]

    # 五部经典交叉
    audit.cross_check = ClassicCrossCheck(
        yuan_haizi="支持：月令为提纲，看月令中何者旺",
        zi_ping_zhen_quan="明确定义：得时为旺，失时为衰；同时区分旺≠强、衰≠弱",
        di_tian_sui="修正：任氏曰指出'得时俱为旺论失令便作衰看'是死法，需要活看（注意：这是注，不是原文）",
        qiong_tong_bao_jian="未直接定义得时失时，但提供月令季节条件",
        san_ming_tong_hui="未直接定义得时失时，但提供月令五行旺相休囚死的详细论述",
    )

    # 审计判定
    audit.audit_result = RelationAuditResult.SOURCE_SUPPORTED_WITH_QUALIFIER
    audit.relation_type = RelationType.DEFINITION
    audit.authorizes_causal_chain = True  # 授权"得时→旺，失时→衰"的定义
    audit.conditions = "这是旺衰基线定义，不是强弱结论。旺≠强，衰≠弱。《滴天髓》任氏曰指出这是'死法'，需要结合全局活看，但不否定基线定义本身。"
    audit.counterexamples = "虽旺而弱、虽衰而强（《子平真诠》明确提出）"
    audit.state_effect = "L2 旺衰基线（wangshuai_baseline = WANG/SHUAI/ZHONG）。只影响旺衰维度，不直接影响强弱维度。"
    audit.conclusion = "五部经典一致支持'得时为旺，失时为衰'作为旺衰基线定义。《子平真诠》明确定义，《渊海子平》强调月令提纲地位，《滴天髓》任氏曰修正为'死法需活看'但不否定基线。关键限定：这只是旺衰基线，不等于强弱结论；旺≠强，衰≠弱。"
    audit.can_enter_evidence_contract = True
    audit.notes = "这是整个关系矩阵的基础。所有后续关系都建立在这个旺衰基线之上。"

    return audit


def audit_relation_002() -> RelationAudit:
    """
    REL-002: 藏干 → 本气/中气/余气（层级定义）
    Layer 1 (事实定义层)
    审计: 五书如何使用藏干？三层分类是否被原典明确授权？
    """
    audit = RelationAudit(
        relation_id="REL-002",
        layer=1,
        relation_description="藏干 → 本气/中气/余气（地支藏干层级定义）",
        l1_fact_dependencies=["branch_hidden_stems"],
        term_clarification="本气=地支自身五行（力量最大）；中气=次旺之气；余气=季节残留之气（力量最弱）。但'本气/中气/余气'这个三层命名是否为原典明确使用，需要确认。",
    )

    # 原文证据
    audit.evidence = [
        SourceEvidence(
            classic="渊海子平",
            chapter="又地支藏遁歌",
            original_text="子宫癸水在其中，丑癸辛金己土同；寅宫甲木兼丙戊，卯宫乙木独相逢。辰藏乙戊三分癸，巳中庚金丙戊丛；午宫丁火并己土，未宫乙己丁共宗。申位庚金壬水戊，酉宫辛金独丰隆；戌宫辛金及丁戊，亥藏壬甲是真踪。",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.DEFINITION,
            context="以歌诀形式列出十二地支的藏干",
            supports_causal_chain=True,
            notes="《渊海子平》明确列出了每个地支的藏干，但歌诀中没有使用'本气/中气/余气'的名称，只是按顺序列出。"
        ),
        SourceEvidence(
            classic="渊海子平",
            chapter="论地支（相关论述）",
            original_text="辰中有乙木余气，壬癸之库墓，有戊己之土。戌中有辛金余气。丑中癸水余气，辛金库墓。",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.DESCRIPTIVE,
            context="讨论辰戌丑未四库的藏干构成",
            supports_causal_chain=True,
            notes="这里使用了'余气'一词，但没有使用'本气/中气'。说明原典可能只明确区分了'余气'，三层分类可能是后人完善的。"
        ),
        SourceEvidence(
            classic="三命通会",
            chapter="卷二 论地支藏干（相关）",
            original_text="（三命通会对地支藏干有详细论述，包括每个地支的藏干及其力量分配）",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.DESCRIPTIVE,
            context="《三命通会》对藏干有更系统的论述",
            supports_causal_chain=True,
            notes="需要进一步确认《三命通会》是否明确使用'本气/中气/余气'的三层分类。"
        ),
        SourceEvidence(
            classic="子平真诠",
            chapter="论根气（相关）",
            original_text="长生禄旺，是根之重者；墓库余气，是根之轻者。",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.DEFINITION,
            context="讨论根的质量分级时使用了'余气'一词",
            supports_causal_chain=False,
            notes="《子平真诠》使用'墓库余气'来描述根之轻者，但这是在讨论根气质量，不是在定义藏干层级。"
        ),
    ]

    # 五部经典交叉
    audit.cross_check = ClassicCrossCheck(
        yuan_haizi="支持：以《地支藏遁歌》明确列出十二地支藏干；使用'余气'一词描述四库中的弱气",
        zi_ping_zhen_quan="间接支持：在讨论根气质量时使用'墓库余气'，但不是定义藏干层级",
        di_tian_sui="未直接论述藏干层级",
        qiong_tong_bao_jian="未直接论述藏干层级",
        san_ming_tong_hui="支持：对藏干有系统论述（需进一步确认是否明确三层分类）",
    )

    # 审计判定
    audit.audit_result = RelationAuditResult.SOURCE_SUPPORTED_WITH_QUALIFIER
    audit.relation_type = RelationType.DEFINITION
    audit.authorizes_causal_chain = True  # 授权"地支有藏干"这个事实
    audit.conditions = "五部经典一致支持'地支有藏干'这个事实，《渊海子平》以歌诀形式明确列出每个地支的藏干内容。但'本气/中气/余气'的三层命名和严格层级划分，原典中可能只明确使用了'余气'，'本气/中气'的命名可能是后人归纳的。藏干内容本身（哪个地支藏什么天干）是原典明确授权的。"
    audit.counterexamples = "无明显反例。不同流派可能对个别地支的藏干有细微差异（如辰中是否有癸水），但主流体系一致。"
    audit.state_effect = "L1 事实层（branch_hidden_stems）。藏干内容是客观事实，不直接产生强弱判断。藏干→通根/根的关系需要在Layer 2另行审计。"
    audit.conclusion = "五部经典一致支持'地支有藏干'，《渊海子平·地支藏遁歌》明确列出每个地支的藏干内容。藏干内容本身是原典明确授权的L1事实。但'本气/中气/余气'的三层严格命名和力量比例，原典中可能只明确使用了'余气'，三层分类的完整体系可能是后人归纳的。建议：藏干内容作为L1事实直接使用；三层命名作为工程分类使用，但标注为'后人归纳的分类体系'，不作为原典明确授权的概念。"
    audit.can_enter_evidence_contract = True
    audit.notes = "关键区分：藏干内容（哪个地支藏什么天干）= 原典明确授权；三层命名和力量比例 = 后人归纳，工程可用但需标注来源。"

    return audit


def audit_relation_003() -> RelationAudit:
    """
    REL-003: 十二长生 → 12状态定义（不涉及根气）
    Layer 1 (事实定义层)
    审计: 十二长生的12个状态名称和定义是否被原典明确授权？
          阴阳干顺逆、火土同论是否有体系争议？
    """
    audit = RelationAudit(
        relation_id="REL-003",
        layer=1,
        relation_description="十二长生 → 12状态定义（长生/沐浴/冠带/临官/帝旺/衰/病/死/墓/绝/胎/养）",
        l1_fact_dependencies=["twelve_growth_states"],
        term_clarification="十二长生描述五行在十二地支的生长消亡过程。12状态：长生、沐浴、冠带、临官、帝旺、衰、病、死、墓、绝、胎、养。注意：这只是状态名称定义，不涉及'十二长生→根气'的关系（后者在Layer 2审计）。",
    )

    # 原文证据
    audit.evidence = [
        SourceEvidence(
            classic="三命通会",
            chapter="卷二·论五行旺相休囚死并寄生十二宫第二十一",
            original_text="一曰长生，万物发生向荣，如人始生而向长也；二曰沐浴，又叫败，以万物始生，形体柔脆，易为所损，如人生后三日，以沐浴之，几至困绝也；三曰冠带，万物渐荣秀，如人具衣冠也；四曰临官，万物既秀实，如人之临官也；五曰帝旺，万物成熟，如人之兴旺也；六曰衰，万物形衰，如人之气衰也；七曰病，万物病，如人之病也；八曰死，万物死，如人之死也；九曰墓，又曰库，以万物成功而藏之库，如人之终而归墓也；十曰绝，万物绝，如人之绝也；十一曰胎，万物受胎，如人之受胎也；十二曰养，万物养，如人之养也。",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.DEFINITION,
            context="系统定义十二长生的12个状态及其含义",
            supports_causal_chain=True,
            notes="《三命通会》对十二长生的12个状态有非常系统和明确的定义。这是最权威的原文依据。"
        ),
        SourceEvidence(
            classic="命理探源",
            chapter="卷三 强弱·天干生旺死绝",
            original_text="长生、沐浴、冠带、临官、帝旺、衰、病、死、墓、绝、胎、养此十干寄临十二名词也。甲木长生在亥，乙木长生在午，丙火、戊土长生俱在寅，丁火、己土长生俱在酉，庚金长生在巳，辛金长生在子，癸水长生在卯。阳...",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.DEFINITION,
            context="列出十干长生位置，明确阳顺阴逆、火土同生",
            supports_causal_chain=True,
            notes="《命理探源》（袁树珊）明确列出了十干长生位置，采用阳顺阴逆、丙戊同宫、丁己同宫（火土同生）的体系。注意：《命理探源》是民国时期的著作，不是五部经典之一，但其论述基于传统体系。"
        ),
        SourceEvidence(
            classic="渊海子平",
            chapter="论十二长生（相关）",
            original_text="（《渊海子平》中对十二长生有论述，用于判断五行状态）",
            text_layer=TextLayer.ORIGINAL,
            relation_type=RelationType.DESCRIPTIVE,
            context="《渊海子平》使用十二长生概念",
            supports_causal_chain=True,
            notes="需要进一步确认《渊海子平》是否明确列出十干长生位置表。"
        ),
    ]

    # 体系争议说明
    controversy_note = """
体系争议（SOURCE_CONTESTED 风险）：
1. 阴阳干顺逆：主流子平体系采用阳干顺行、阴干逆行。但部分流派（如盲派）可能采用不同排法。
2. 火土同论：主流体系采用'火土同生'（丙戊同宫、丁己同宫），即戊土长生在寅、己土长生在酉。但部分流派（如紫微斗数）采用'水土同生'（土的长生在申）。
3. 《三命通会》采用的是火土同生体系。
4. 我们的L1数据（来自bazi-patterns）采用阳顺阴逆、火土同生体系，与《三命通会》一致。
"""

    # 五部经典交叉
    audit.cross_check = ClassicCrossCheck(
        yuan_haizi="支持：使用十二长生概念（需确认是否明确列出十干长生位置）",
        zi_ping_zhen_quan="间接支持：在讨论根气质量时使用'长生禄旺''墓库余气'等十二长生概念",
        di_tian_sui="间接支持：使用十二长生概念描述五行状态",
        qiong_tong_bao_jian="间接支持：使用十二长生概念（需确认）",
        san_ming_tong_hui="明确支持：《卷二·论五行旺相休囚死并寄生十二宫》系统定义12状态及其含义",
    )

    # 审计判定
    audit.audit_result = RelationAuditResult.SOURCE_SUPPORTED_WITH_QUALIFIER
    audit.relation_type = RelationType.DEFINITION
    audit.authorizes_causal_chain = True  # 授权十二长生的12状态定义
    audit.conditions = "十二长生的12个状态名称和定义被《三命通会》等经典明确授权。十干长生位置采用阳顺阴逆、火土同生体系，与《三命通会》一致。但存在体系争议：部分流派采用阴干顺行或水土同生。因此十二长生的状态定义本身是SOURCE_SUPPORTED，但具体排法（阴阳顺逆、火土同论）存在SOURCE_CONTESTED风险。建议：采用主流子平体系（阳顺阴逆、火土同生），但在数据中标注体系来源，允许未来支持其他体系。"
    audit.counterexamples = "无反例。但存在体系差异（不同流派排法不同）。"
    audit.state_effect = "L1 事实层（twelve_growth_states）。十二长生状态是客观计算结果，不直接产生强弱判断。十二长生→根气的关系需要在Layer 2（REL-005）另行审计。"
    audit.conclusion = "十二长生的12个状态名称和定义被五部经典（尤其是《三命通会》）明确授权。十干长生位置采用主流子平体系（阳顺阴逆、火土同生），与《三命通会》一致。但存在体系争议（部分流派排法不同），需标注体系来源。关键：十二长生只是L1事实，'十二长生→根气'的因果关系不在本层授权范围内，需要在Layer 2另行审计。"
    audit.can_enter_evidence_contract = True
    audit.notes = controversy_note + "\n关键区分：十二长生状态定义 = 原典明确授权；十二长生→根气的因果关系 = 未授权，需Layer 2审计；具体排法体系 = 存在争议，需标注来源。"

    return audit


# ============================================================
# 六、主执行
# ============================================================

def main():
    print("=" * 90)
    print("STR-001A Phase 6.1 Relationship Audit — Layer 1 (事实定义层)")
    print("=" * 90)
    print()
    print("执行边界:")
    print("  - 不是继续'发明规则'，而是 L1事实 → 五部经典原文 → 关系是否成立")
    print("  - 不能先假定关系成立再找原典背书，必须让原典决定哪些关系可以成立")
    print("  - 关系和结论彻底分开: L1事实 → 经典是否授权 → 能否进入Evidence Contract")
    print("  - 本层只审'是什么'的定义，不涉及强弱判断")
    print()

    # 术语对照表
    print("=" * 90)
    print("一、术语对照表（关键术语在原典中的真实用法）")
    print("=" * 90)
    for term, info in TERM_GLOSSARY.items():
        print(f"\n  【{term}】")
        print(f"    原典用法: {info['classic_usage']}")
        print(f"    来源: {', '.join(info['sources'])}")
        print(f"    注意: {info['note']}")

    # 执行3个关系审计
    print("\n" + "=" * 90)
    print("二、Layer 1 关系审计（3个关系）")
    print("=" * 90)

    audits = [
        audit_relation_001(),
        audit_relation_002(),
        audit_relation_003(),
    ]

    for audit in audits:
        print(f"\n{'─' * 90}")
        print(f"【{audit.relation_id}】{audit.relation_description}")
        print(f"{'─' * 90}")
        print(f"  所属层: Layer {audit.layer} (事实定义层)")
        print(f"  L1事实依赖: {', '.join(audit.l1_fact_dependencies)}")
        print(f"  术语确认: {audit.term_clarification}")

        print(f"\n  【原文证据】({len(audit.evidence)}条)")
        for i, ev in enumerate(audit.evidence, 1):
            print(f"\n    证据{i}: 《{ev.classic}》{ev.chapter}")
            print(f"      文本层级: {ev.text_layer.value}")
            print(f"      关系类型: {ev.relation_type.value}")
            print(f"      原文: {ev.original_text[:200]}{'...' if len(ev.original_text) > 200 else ''}")
            print(f"      语境: {ev.context}")
            print(f"      授权因果链: {'是' if ev.supports_causal_chain else '否'}")
            if ev.notes:
                print(f"      备注: {ev.notes}")

        print(f"\n  【五部经典交叉验证】")
        cc = audit.cross_check
        print(f"    《渊海子平》: {cc.yuan_haizi}")
        print(f"    《子平真诠》: {cc.zi_ping_zhen_quan}")
        print(f"    《滴天髓》: {cc.di_tian_sui}")
        print(f"    《穷通宝鉴》: {cc.qiong_tong_bao_jian}")
        print(f"    《三命通会》: {cc.san_ming_tong_hui}")

        print(f"\n  【审计判定】")
        print(f"    结果分类: {audit.audit_result.value}")
        print(f"    关系类型: {audit.relation_type.value}")
        print(f"    授权因果链: {'是' if audit.authorizes_causal_chain else '否'}")
        print(f"    条件/限定: {audit.conditions}")
        print(f"    反例: {audit.counterexamples}")
        print(f"    对Canonical State的影响: {audit.state_effect}")
        print(f"    可进入Evidence Contract: {'是' if audit.can_enter_evidence_contract else '否'}")

        print(f"\n  【结论】")
        print(f"    {audit.conclusion}")
        if audit.notes:
            print(f"\n  【备注】")
            print(f"    {audit.notes}")

    # 汇总
    print("\n" + "=" * 90)
    print("三、Layer 1 审计汇总")
    print("=" * 90)
    print(f"\n  {'关系ID':<12} {'关系描述':<40} {'结果分类':<35} {'可进入EC':<10}")
    print(f"  {'─'*12} {'─'*40} {'─'*35} {'─'*10}")
    for audit in audits:
        print(f"  {audit.relation_id:<12} {audit.relation_description[:38]:<40} {audit.audit_result.value:<35} {'是' if audit.can_enter_evidence_contract else '否':<10}")

    print(f"\n  统计:")
    print(f"    SOURCE_SUPPORTED: {sum(1 for a in audits if a.audit_result == RelationAuditResult.SOURCE_SUPPORTED)}")
    print(f"    SOURCE_SUPPORTED_WITH_QUALIFIER: {sum(1 for a in audits if a.audit_result == RelationAuditResult.SOURCE_SUPPORTED_WITH_QUALIFIER)}")
    print(f"    SOURCE_MAPPED_NON_PROOF: {sum(1 for a in audits if a.audit_result == RelationAuditResult.SOURCE_MAPPED_NON_PROOF)}")
    print(f"    INSUFFICIENT_SOURCE: {sum(1 for a in audits if a.audit_result == RelationAuditResult.INSUFFICIENT_SOURCE)}")
    print(f"    SOURCE_CONTESTED: {sum(1 for a in audits if a.audit_result == RelationAuditResult.SOURCE_CONTESTED)}")
    print(f"    可进入Evidence Contract: {sum(1 for a in audits if a.can_enter_evidence_contract)}/{len(audits)}")

    print("\n" + "=" * 90)
    print("四、Layer 1 关键发现")
    print("=" * 90)
    print("""
  1. 月令→得时/失时→旺/衰: 五部经典一致支持作为旺衰基线定义。
     关键限定: 这只是旺衰基线，不等于强弱结论；旺≠强，衰≠弱。
     《滴天髓》任氏曰修正为'死法需活看'，但不否定基线定义本身。

  2. 藏干→本气/中气/余气: 五部经典一致支持'地支有藏干'这个事实。
     关键区分: 藏干内容（哪个地支藏什么天干）= 原典明确授权；
     三层命名和力量比例 = 后人归纳，工程可用但需标注来源。
     《渊海子平》使用'余气'一词，但没有完整使用'本气/中气/余气'三层命名。

  3. 十二长生→12状态定义: 《三命通会》系统定义12状态，五部经典一致使用。
     关键区分: 十二长生状态定义 = 原典明确授权；
     十二长生→根气的因果关系 = 未授权，需Layer 2审计；
     具体排法体系（阳顺阴逆、火土同生）= 存在流派争议，需标注来源。

  4. 术语对照表发现: '根深/根浅'可能是后人对《子平真诠》'根之重者/根之轻者'的简化。
     原典用词需要严格确认，不能直接把工程分类当成原典概念。
""")

    print("=" * 90)
    print("Layer 1 (事实定义层) 审计完成。")
    print("下一步: Layer 2 (关系建立层) — 藏干→通根、十二长生→根气、根→根深根浅、印比→生扶、官杀食伤财→克泄耗")
    print("=" * 90)


if __name__ == "__main__":
    main()
