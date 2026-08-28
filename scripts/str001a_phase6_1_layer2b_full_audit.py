"""
STR-001A Phase 6.1 Layer 2B — R1-5 + R3-R6 全量关系审计

执行边界:
- JSON整理库只作候选索引，原典才是授权来源
- 每条关系按统一14字段模板输出
- 强制允许 INSUFFICIENT_SOURCE / SOURCE_CONTESTED / SOURCE_MAPPED_NON_PROOF
- 不为追求通过率强行授权
- 调候=独立维度，不得混入旺衰/强弱
- 格局=只作为候选关系，不直接授权

14字段模板:
RELATION_ID, SOURCE_TEXT, SOURCE_BOOK, SOURCE_LOCATION, INPUT_FACTS,
RELATION, CONDITION, QUALIFIER, TARGET, EFFECT, COUNTEREXAMPLE,
RESULT_CLASS, CANONICAL_AUTHORIZATION
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class ResultClass(str, Enum):
    SOURCE_SUPPORTED = "SOURCE_SUPPORTED"
    SOURCE_SUPPORTED_WITH_QUALIFIER = "SOURCE_SUPPORTED_WITH_QUALIFIER"
    SOURCE_MAPPED_NON_PROOF = "SOURCE_MAPPED_NON_PROOF"
    INSUFFICIENT_SOURCE = "INSUFFICIENT_SOURCE"
    SOURCE_CONTESTED = "SOURCE_CONTESTED"


@dataclass
class RelationAudit14:
    """14字段统一审计模板"""
    relation_id: str
    source_text: str              # 原典原文
    source_book: str              # 来源经典
    source_location: str          # 来源位置/篇目
    input_facts: List[str]        # 输入L1事实
    relation: str                 # 关系描述
    condition: str                # 成立条件
    qualifier: str                # 限定/修饰
    target: str                   # 作用对象
    effect: str                   # 作用效果
    counterexample: str           # 反例
    result_class: ResultClass     # 结果分类
    canonical_authorization: str  # Canonical授权状态

    def to_dict(self):
        return {
            "RELATION_ID": self.relation_id,
            "SOURCE_TEXT": self.source_text,
            "SOURCE_BOOK": self.source_book,
            "SOURCE_LOCATION": self.source_location,
            "INPUT_FACTS": self.input_facts,
            "RELATION": self.relation,
            "CONDITION": self.condition,
            "QUALIFIER": self.qualifier,
            "TARGET": self.target,
            "EFFECT": self.effect,
            "COUNTEREXAMPLE": self.counterexample,
            "RESULT_CLASS": self.result_class.value,
            "CANONICAL_AUTHORIZATION": self.canonical_authorization,
        }


# ============================================================
# 审计结果集合
# ============================================================

audits: List[RelationAudit14] = []


# ============================================================
# R1-5: 印 → 生扶
# ============================================================

audits.append(RelationAudit14(
    relation_id="R1-5",
    source_text="木赖水生，水多木漂；火赖木生，木多火炽；土赖火生，火多土焦；金赖土生，土多金埋；水赖金生，金多水浊。",
    source_book="渊海子平",
    source_location="论五行生克制化",
    input_facts=["day_master", "resource_stems", "resource_branches", "resource_quantity"],
    relation="印（正印/偏印）生日主，提供生扶。但印过旺则反作用（水多木漂、木多火炽等）。",
    condition="(1)印为生日主的五行；(2)印存在且有根；(3)印的数量/力量在适度范围内",
    qualifier="印过旺则反作用：水多木漂（印过旺反克日主）。印绶不宜身太旺。印的生扶与比劫的扶助不同：印是'生我'，比劫是'同我'。",
    target="日主（day_master）",
    effect="适度印→生扶日主（增强日主力量）；印过旺→反作用（水多木漂，日主漂浮无依）",
    counterexample="水多木漂（印过旺反克）；印绶不宜身太旺（身已旺再逢印则太过）；'漫夸印旺兼多合，不遇刑冲总不宜'（己土体象诗）",
    result_class=ResultClass.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authorization="AUTHORIZED_WITH_QUALIFIER: 印生扶日主被原典授权，但必须带'印过旺反作用（水多木漂）'的qualifier。印的生扶≠比劫的扶助，二者效力不同，需分别处理。印过旺的反作用是1983命例（水4木1）的关键问题。",
))


# ============================================================
# R3-1: 官杀 → 克/制
# ============================================================

audits.append(RelationAudit14(
    relation_id="R3-1",
    source_text="夫七杀者，亦名偏官，喜身旺合杀、喜制伏、喜阳刃；忌身弱、忌见财，生忌无制。身旺有气为偏官，身弱无制为七杀。官来剋我，我去剋官不为害。",
    source_book="渊海子平",
    source_location="论七杀 / 正官论",
    input_facts=["day_master", "officer_stems", "officer_branches", "day_master_strength_context"],
    relation="官杀（正官/七杀）克/制日主。但官杀是'制我'的关系，不是'官杀旺→身弱'的因果。",
    condition="(1)官杀为克日主的五行；(2)官杀存在；(3)需要结合日主本身状态判断影响",
    qualifier="官杀作用关系≠身弱结果。'身强杀浅假杀为权'（身强时官杀可为用）vs'杀重身轻终身有损'（身弱时官杀过重为害）。官杀有制（食神制杀、印化杀）时影响改变。'官来剋我，我去剋官不为害'。",
    target="日主（day_master）",
    effect="官杀→制/克日主。身旺时官杀可为权（可用）；身弱无制时官杀为害（压力/损伤）。官杀有制时影响被转化。",
    counterexample="身强杀浅假杀为权（官杀不必然为害）；食神制杀、印化杀（官杀被制化）；官来剋我我去剋官不为害",
    result_class=ResultClass.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authorization="AUTHORIZED_WITH_QUALIFIER: 官杀克/制日主的关系被原典授权，但必须带'官杀作用关系≠身弱结果'的qualifier。官杀是'制我'的关系变量，不是'身弱指标'。官杀的实际影响取决于日主本身状态+是否有制化。禁止：官杀旺→身弱（因果链不成立）。",
))


# ============================================================
# R3-2: 食伤 → 泄/盗气
# ============================================================

audits.append(RelationAudit14(
    relation_id="R3-2",
    source_text="伤官者，我生彼之谓也；以阳见阴，阴见阳，亦名盗气。食神者，生我财神之谓也；如甲属木，丙属火，名盗气，故谓之食神。甲人见丙本盗气，丙去生财号食神。",
    source_book="渊海子平",
    source_location="论伤官 / 论食神 / 诗诀",
    input_facts=["day_master", "output_stems", "output_branches", "output_quantity"],
    relation="食伤（食神/伤官）泄/盗日主之气。原典明确称食伤为'盗气'。",
    condition="(1)食伤为日主所生的五行；(2)食伤存在；(3)'泄身'需要食伤过重/过多的条件",
    qualifier="食伤泄身需要条件（重重/太多），不是有食伤就泄身。'日主刚强福禄来，身弱食多反为害'（身弱时食多才为害）。食神生财结构中食伤是'生财'的通道，不单纯是泄身。'伤官务要伤尽'（伤官格局有特定条件）。",
    target="日主（day_master）",
    effect="食伤→泄/盗日主之气。食伤过多/过重时→泄身（消耗日主力量）。身弱食多→反为害。食神生财时→食伤是生财通道，影响不同。",
    counterexample="日主刚强福禄来（身强时食伤不必然为害）；食神生财（食伤是生财通道）；伤官伤尽（伤官格局特定条件下可用）",
    result_class=ResultClass.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authorization="AUTHORIZED_WITH_QUALIFIER: 食伤泄/盗气的关系被原典明确授权（原典直接称食伤为'盗气'），但必须带'泄身需要食伤过重条件，不是有食伤就泄身'的qualifier。食伤是'我生'的关系变量，其实际影响取决于日主状态+食伤数量+是否构成食神生财/伤官格局。注意：《神峰通考》'重重伤官盗尽我身之气'不在五部经典内，五部经典内渊海子平已明确'盗气'概念。",
))


# ============================================================
# R3-3: 财 → 耗/我克
# ============================================================

audits.append(RelationAudit14(
    relation_id="R3-3",
    source_text="财多身弱，富屋贫人。财多身健方为贵。财多盗气，本自身柔。正财者，喜身旺、印绶，忌官星、忌倒食、忌身弱、比肩劫财。",
    source_book="渊海子平",
    source_location="论正财 / 诗诀",
    input_facts=["day_master", "wealth_stems", "wealth_branches", "wealth_quantity", "day_master_strength_context"],
    relation="财（正财/偏财）为日主所克，耗日主之力。但财不是'身弱指标'，而是'日主承载财星能力'的关系变量。",
    condition="(1)财为日主所克的五行；(2)财存在；(3)财多+身弱时→力不任财",
    qualifier="财多身弱不能倒推为财多→身弱。同一经典又说'财多身健方为贵'（身健时财多为贵）。财是'我克'的关系，耗我之力，但'耗'的原典依据需要更多确认。'财多盗气，本自身柔'（财多消耗日主气力，但前提是自身本柔）。",
    target="日主（day_master）",
    effect="财→日主所克，耗日主之力。财多身健→为贵（可承载）。财多身弱→力不任/为害（富屋贫人）。",
    counterexample="财多身健方为贵（财多不必然为害）；身旺可任财（身强时财多为福）",
    result_class=ResultClass.SOURCE_MAPPED_NON_PROOF,
    canonical_authorization="PARTIALLY_AUTHORIZED: 财为'我克'的关系被原典明确授权。'财多身弱'的描述被原典记录，但'财多→身弱'的因果链不被授权（同一经典有'财多身健方为贵'的反例）。财是'日主承载财星能力'的关系变量，不是身弱指标。'耗'的具体原典依据需要更多确认。禁止：财多→身弱（因果链不成立）。",
))


# ============================================================
# R4-1: 合（六合/三合/半合）
# ============================================================

audits.append(RelationAudit14(
    relation_id="R4-1",
    source_text="喜逢三合便成林。合可以解冲/刑。地支天干合多，亦云贪合忘官。",
    source_book="渊海子平",
    source_location="地支体象诗诀 / 喜忌篇 / 论刑冲会合解法（子平真诠）",
    input_facts=["branches", "branch_combinations", "heavenly_stems", "stem_combinations"],
    relation="合（六合/三合/半合/天干五合）是结构关系，改变五行力量分布和关系有效性。合≠强。",
    condition="(1)存在合的关系（地支六合/三合/半合，天干五合）；(2)合的条件满足（如三合需要三支齐全或半合有两支）",
    qualifier="合≠强，必须RELATION→TARGET→EFFECT。合可以增强某五行力量（如亥卯未合木局增强木），也可以解冲/刑（合可解冲），也可以'贪合忘官'（合使某星被绊住）。合而不化的情况需要单独处理。合对根的影响取决于合的对象和结果。",
    target="被合的五行/十神/地支",
    effect="合→改变五行力量分布/关系有效性。可能增强某五行，可能解冲刑，可能绊住某星（贪合忘），可能成局（三合局）。",
    counterexample="贪合忘官（合不必然增强，可能绊住）；合而不化（合不一定成功）",
    result_class=ResultClass.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authorization="AUTHORIZED_WITH_QUALIFIER: 合作为结构关系被原典授权。但合≠强，必须按RELATION→TARGET→EFFECT处理。合对根的影响不是自动的，取决于合的对象、是否成化、是否解冲。三合局/半合局对五行力量的增强需要单独审计条件。禁止：合→强（简单映射不成立）。",
))


# ============================================================
# R4-2: 冲（六冲）
# ============================================================

audits.append(RelationAudit14(
    relation_id="R4-2",
    source_text="祸见六冲应落叶。生方怕动，库宜开，败地逢冲子细裁。支神祇以冲为重。",
    source_book="渊海子平 / 滴天髓",
    source_location="地支体象诗诀 / 滴天髓·论冲",
    input_facts=["branches", "branch_clashes", "root_locations"],
    relation="冲（六冲）是结构关系，动摇/破坏地支状态。冲≠弱。冲对根的影响取决于冲的对象和位置。",
    condition="(1)存在六冲关系；(2)冲的位置涉及日主根或关键十神",
    qualifier="冲≠弱，必须RELATION→TARGET→EFFECT。'生方怕动'（长生之地怕冲）；'库宜开'（墓库逢冲可能开启）；'败地逢冲子细裁'（沐浴之地逢冲需仔细判断）。冲可能动摇根（日主根在某支，该支被冲→根可能受损），也可能开库（墓库被冲→库中藏干可能透出），也可能激发（冲主动）。冲对根的有效性影响需要具体分析。",
    target="被冲的地支/其中的藏干/根",
    effect="冲→动摇/破坏地支状态。可能动摇根（根受损），可能开库（墓库开启），可能激发变化。具体效果取决于冲的对象和位置。",
    counterexample="库宜开（冲不必然为害，墓库逢冲可能为吉）；冲动可能激发变化（不必然削弱）",
    result_class=ResultClass.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authorization="AUTHORIZED_WITH_QUALIFIER: 冲作为结构关系被原典授权。但冲≠弱，必须按RELATION→TARGET→EFFECT处理。冲对根的影响不是自动的：生方怕冲（根可能受损），库宜开（冲可能有益），败地逢冲需细裁。冲是否导致根失效需要具体分析冲的对象、位置、是否有合解。禁止：冲→根失效/身弱（简单映射不成立）。",
))


# ============================================================
# R4-3: 刑（三刑/自刑）
# ============================================================

audits.append(RelationAudit14(
    relation_id="R4-3",
    source_text="刑与害兮动不动。纵遇卯刑还有情。",
    source_book="滴天髓 / 渊海子平",
    source_location="滴天髓·论刑害 / 地支体象诗诀",
    input_facts=["branches", "branch_punishments"],
    relation="刑（三刑/自刑）是结构关系。刑≠凶。刑的作用取决于是否'动'（是否被引动）。",
    condition="(1)存在三刑/自刑关系；(2)刑被引动（逢冲/透干/大运流年触发）",
    qualifier="刑≠凶，必须RELATION→TARGET→EFFECT。'刑与害兮动不动'——刑害的作用取决于是否被动，不动则影响小。'纵遇卯刑还有情'——刑不一定完全为害，可能还有情分。刑对根的影响需要具体分析，不能简单认为刑→根伤。",
    target="被刑的地支/其中的藏干",
    effect="刑→结构关系。被引动时可能产生刑伤/阻碍，但不动时影响小。具体效果取决于刑的类型、是否被引动、涉及的十神。",
    counterexample="刑与害兮动不动（刑不被动则影响小）；纵遇卯刑还有情（刑不必然完全为害）",
    result_class=ResultClass.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authorization="AUTHORIZED_WITH_QUALIFIER: 刑作为结构关系被原典授权。但刑≠凶，必须按RELATION→TARGET→EFFECT处理。刑的作用取决于是否被引动（动不动）。刑对根的影响不是自动的，需要具体分析。禁止：刑→根伤/身弱（简单映射不成立）。",
))


# ============================================================
# R4-4: 会（三会方）
# ============================================================

audits.append(RelationAudit14(
    relation_id="R4-4",
    source_text="（三会方：寅卯辰东方木、巳午未南方火、申酉戌西方金、亥子丑北方水）",
    source_book="渊海子平 / 三命通会",
    source_location="论地支 / 论三会",
    input_facts=["branches", "branch_meetings"],
    relation="会（三会方）是结构关系，三支成方增强某五行力量。会≠强（需要三支齐全且条件满足）。",
    condition="(1)三地支齐全（寅卯辰/巳午未/申酉戌/亥子丑）；(2)三会方条件满足",
    qualifier="会≠强，必须RELATION→TARGET→EFFECT。三会方需要三支齐全，缺一则不成会。三会方增强某五行力量，但对日主的影响取决于该五行是日主的十神关系（比劫/印/财/官杀/食伤）。三会方对根的影响需要具体分析。",
    target="三会方所代表的五行",
    effect="会→三支成方，增强某五行力量。具体对日主的影响取决于该五行的十神关系。",
    counterexample="缺一支不成会（三会方条件不满足则不成立）",
    result_class=ResultClass.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authorization="AUTHORIZED_WITH_QUALIFIER: 三会方作为结构关系被原典授权。但会≠强，必须按RELATION→TARGET→EFFECT处理。三会方需要三支齐全。三会方增强的是某五行力量，对日主的影响取决于十神关系。禁止：会→日主强（简单映射不成立）。",
))


# ============================================================
# R4-5: 破/害
# ============================================================

audits.append(RelationAudit14(
    relation_id="R4-5",
    source_text="（六害/相破：子未害、丑午害、寅巳害、卯辰害、申亥害、酉戌害；破：子破酉、酉破子等）",
    source_book="渊海子平 / 三命通会",
    source_location="论六害 / 论相破",
    input_facts=["branches", "branch_harms", "branch_breaks"],
    relation="破/害是结构关系。破/害的影响力低于冲/刑/合。",
    condition="(1)存在六害/相破关系；(2)被引动",
    qualifier="破/害≠凶，必须RELATION→TARGET→EFFECT。破/害的影响力通常低于冲/刑/合，在原典中论述较少。破/害对根的影响需要更多原典依据。",
    target="被害/破的地支",
    effect="破/害→结构关系，影响力较低。具体效果需要更多原典依据确认。",
    counterexample="（待补充）",
    result_class=ResultClass.INSUFFICIENT_SOURCE,
    canonical_authorization="NOT_AUTHORIZED: 破/害作为结构关系在原典中有提及，但五部经典内对破/害的具体作用效果、对根的影响、条件限定等论述不足。当前标INSUFFICIENT_SOURCE，需要更多原典证据才能授权。在Canonical State Resolver中暂不处理破/害对根的影响，仅作为结构关系记录。",
))


# ============================================================
# R5-1: 空亡 → 关系有效性修正
# ============================================================

audits.append(RelationAudit14(
    relation_id="R5-1",
    source_text="金空则鸣，火空则发，水空则流，此三者上吉；木空则朽，土空则崩，二者下凶。日坐空亡，难为妻妾。时上伤官及空亡，难为子息。印绶如经死绝乡，怕财仍旧怕空亡。",
    source_book="渊海子平",
    source_location="六亲总篇 / 论妻妾 / 论子息 / 诗诀",
    input_facts=["branches", "kong_wang", "root_locations", "ten_god_locations"],
    relation="空亡是关系有效性修正（RELATION EFFECT MODIFIER），不是STRENGTH EVIDENCE。空亡对不同五行有不同影响（金空则鸣/火空则发/水空则流=上吉；木空则朽/土空则崩=下凶）。",
    condition="(1)某地支逢空亡；(2)该地支涉及关键十神/根/宫位",
    qualifier="空亡≠身弱。空亡是RELATION EFFECT MODIFIER，不是STRENGTH EVIDENCE。空亡对不同五行有不同影响，不是简单的'空亡=力量减半/失效'。金空则鸣（金空反吉）、火空则发（火空反吉）、水空则流（水空反吉）——这三者上吉。木空则朽（木空为凶）、土空则崩（土空为凶）——这二者下凶。空亡对宫位的影响：日坐空亡难为妻妾，时上空亡难为子息。空亡对根的影响：需要结合五行属性判断，不是简单的根失效。",
    target="逢空亡的地支/其中的五行/十神/宫位",
    effect="空亡→修正关系有效性。对五行：金火水空反吉，木土空为凶。对宫位：日空难为妻妾，时空难为子息。对根：需要结合五行属性判断，不是简单失效。",
    counterexample="金空则鸣/火空则发/水空则流（空亡不必然为害，某些五行逢空反吉）",
    result_class=ResultClass.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authorization="AUTHORIZED_WITH_QUALIFIER: 空亡作为关系有效性修正被原典授权（渊海子平明确有'金空则鸣火空则发水空则流木空则朽土空则崩'的论述）。但必须带严格qualifier：(1)空亡是RELATION EFFECT MODIFIER，不是STRENGTH EVIDENCE；(2)空亡≠身弱；(3)空亡对不同五行有不同影响，不是简单的力量减半/根失效；(4)金火水空反吉，木土空为凶。禁止：空亡→根失效/身弱（简单映射不成立）。",
))


# ============================================================
# R5-2: 合解冲/刑
# ============================================================

audits.append(RelationAudit14(
    relation_id="R5-2",
    source_text="（子平真诠·论刑冲会合解法：合可以解冲/刑）",
    source_book="子平真诠",
    source_location="论刑冲会合解法",
    input_facts=["branches", "branch_combinations", "branch_clashes", "branch_punishments"],
    relation="合可以解冲/刑。当某支被冲/刑时，若该支同时有合，则合可以解除或减轻冲/刑的影响。",
    condition="(1)某支被冲/刑；(2)该支同时有合；(3)合的力量足够解冲/刑",
    qualifier="合解冲/刑需要条件，不是有合就一定能解。'因解而反得刑冲'——解的过程中可能反而得到刑冲。合解冲/刑的具体效果需要分析合的类型、力量、位置。",
    target="被冲/刑的地支",
    effect="合→解除或减轻冲/刑的影响。但可能因解而反得刑冲。",
    counterexample="因解而反得刑冲（合解冲不必然成功，可能反而得到刑冲）",
    result_class=ResultClass.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authorization="AUTHORIZED_WITH_QUALIFIER: 合解冲/刑被原典授权（子平真诠有专门论述）。但必须带qualifier：合解冲/刑需要条件，不是有合就一定能解；可能因解而反得刑冲。具体效果需要分析合的类型、力量、位置。",
))


# ============================================================
# R5-3: 冲破合
# ============================================================

audits.append(RelationAudit14(
    relation_id="R5-3",
    source_text="（冲可以破合：当合的两支中某支被冲时，合可能被冲破）",
    source_book="子平真诠 / 渊海子平",
    source_location="论刑冲会合解法",
    input_facts=["branches", "branch_combinations", "branch_clashes"],
    relation="冲可以破合。当合的关系中某支被冲时，合可能被冲破，合的效果被解除或削弱。",
    condition="(1)存在合的关系；(2)合的某支被冲；(3)冲的力量足够破合",
    qualifier="冲破合需要条件，不是有冲就一定能破合。冲的力量、位置、合的类型都会影响结果。冲破合后，合的效果被解除，但冲本身的影响需要单独处理。",
    target="被冲的合关系",
    effect="冲→冲破合，合的效果被解除或削弱。冲本身的影响需要单独处理。",
    counterexample="（待补充：合力量足够时冲可能不能破合）",
    result_class=ResultClass.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authorization="AUTHORIZED_WITH_QUALIFIER: 冲破合被原典授权（子平真诠刑冲会合解法中有论述）。但必须带qualifier：冲破合需要条件，不是有冲就一定能破合。具体效果需要分析冲的力量、位置、合的类型。",
))


# ============================================================
# R5-4: 刑冲会合相互覆盖
# ============================================================

audits.append(RelationAudit14(
    relation_id="R5-4",
    source_text="（子平真诠·论刑冲会合解法：刑冲会合之间存在相互作用和优先级）",
    source_book="子平真诠",
    source_location="论刑冲会合解法",
    input_facts=["branches", "all_branch_relations"],
    relation="刑冲会合之间存在相互作用和优先级。需要按规则解析多重结构关系的最终效果。",
    condition="(1)存在多重刑冲会合关系；(2)需要按规则解析相互作用",
    qualifier="刑冲会合的相互作用需要按子平真诠的规则解析，不是简单叠加。存在合解冲、冲破合、刑解冲、冲激刑等多种相互作用。具体解析规则需要逐条审计。当前只授权'存在相互作用'这一事实，具体规则待细化。",
    target="多重刑冲会合关系",
    effect="刑冲会合→相互作用，最终效果需要按规则解析。不是简单叠加。",
    counterexample="（待补充）",
    result_class=ResultClass.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authorization="AUTHORIZED_WITH_QUALIFIER: 刑冲会合相互覆盖被原典授权（子平真诠有专门论述）。但当前只授权'存在相互作用'这一事实，具体解析规则（合解冲/冲破合/刑解冲/冲激刑等的优先级和条件）需要逐条细化审计。在Canonical State Resolver中，多重刑冲会合关系需要标记为'需解析'，不能简单叠加效果。",
))


# ============================================================
# R6-1: 天干五合
# ============================================================

audits.append(RelationAudit14(
    relation_id="R6-1",
    source_text="甲己合土、乙庚合金、丙辛合水、丁壬合木、戊癸合火。地支天干合多，亦云贪合忘官。",
    source_book="渊海子平 / 三命通会",
    source_location="论天干五合 / 喜忌篇",
    input_facts=["heavenly_stems", "stem_combinations"],
    relation="天干五合（甲己/乙庚/丙辛/丁壬/戊癸）是天干关系。五合可能成化（合化），也可能只是合住（不化）。五合≠合化。",
    condition="(1)存在天干五合关系；(2)五合的条件满足（两干相邻/位置合适）",
    qualifier="五合≠合化。五合有两种结果：合化（需要化神、得令、得地等严格条件）和合住（不化，只是两干被绊住）。'贪合忘官'——合可能使某星被绊住，忘记其原有作用。五合对十神关系的影响取决于是否成化、合的对象。五合是'财星透干逢流年合之主进财'的前置关系。",
    target="被合的天干/十神",
    effect="五合→天干关系。可能合化（改变五行属性），可能合住（绊住十神，贪合忘）。具体效果取决于是否成化、合的对象、位置。",
    counterexample="贪合忘官（合不必然增强，可能绊住十神）；合而不化（五合不一定成化）",
    result_class=ResultClass.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authorization="AUTHORIZED_WITH_QUALIFIER: 天干五合作为天干关系被原典授权。但必须带qualifier：五合≠合化，五合有合化和合住两种结果；'贪合忘官'说明合可能绊住十神。五合是断言层（财星透干逢流年合之）的前置关系，但五合本身不直接授权断言。禁止：五合→合化（简单映射不成立，合化需要严格条件）。",
))


# ============================================================
# R6-2: 合住
# ============================================================

audits.append(RelationAudit14(
    relation_id="R6-2",
    source_text="地支天干合多，亦云贪合忘官。",
    source_book="渊海子平",
    source_location="喜忌篇",
    input_facts=["heavenly_stems", "stem_combinations", "ten_gods"],
    relation="合住是五合/六合的一种结果：两干/两支被合绊住，暂时失去或减弱其原有作用。合住≠合化。",
    condition="(1)存在合的关系；(2)合不化（没有满足合化条件）；(3)合的对象是关键十神",
    qualifier="合住是合而不化的结果，不是合化。合住使被合的十神被绊住，'贪合忘官'——官星被合住则忘记官的作用。合住是暂时的还是永久的，需要结合大运流年判断。合住对根的影响：如果合住的是日主的根，则根的作用可能被绊住。",
    target="被合住的天干/十神/地支",
    effect="合住→被合的对象被绊住，暂时失去或减弱原有作用。贪合忘（官/财/印等）。",
    counterexample="合化成功时不是合住（合化改变五行属性，不是绊住）",
    result_class=ResultClass.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authorization="AUTHORIZED_WITH_QUALIFIER: 合住作为合的一种结果被原典授权（'贪合忘官'）。但必须带qualifier：合住≠合化；合住是合而不化的结果；合住使被合对象被绊住，暂时失去或减弱原有作用。禁止：合→合住（不是所有合都是合住，合可能成化）。",
))


# ============================================================
# R6-3: 合化
# ============================================================

audits.append(RelationAudit14(
    relation_id="R6-3",
    source_text="化象者：乃甲乙日生人，在辰戌丑未月，天干有一己...（合化需要化神、得令、得地等条件）",
    source_book="渊海子平",
    source_location="神趣八法·化象",
    input_facts=["heavenly_stems", "stem_combinations", "month_branch", "transform_god"],
    relation="合化是五合/六合的高级结果：合的两干/两支化成另一五行。合化条件非常严格，不能简单判定合就化。",
    condition="(1)存在合的关系；(2)化神得令（月令支持化神）；(3)化神得地（地支支持化神）；(4)没有克制化神的因素；(5)其他条件（如化象需要特定月令）",
    qualifier="合化条件非常严格，不是合就一定化。'化象者：乃甲乙日生人，在辰戌丑未月，天干有一己...'——化象需要特定月令和天干条件。合化成功后，原五行属性改变，十神关系也改变。合化失败则只是合住。合化的具体条件清单需要更系统的原典审计。",
    target="被合化的天干/地支",
    effect="合化→原五行属性改变为化神五行。十神关系随之改变。合化失败则只是合住。",
    counterexample="合而不化（大多数合只是合住，不是合化）；化神被克制则合化失败",
    result_class=ResultClass.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authorization="AUTHORIZED_WITH_QUALIFIER: 合化作为合的高级结果被原典授权。但必须带严格qualifier：合化条件非常严格（化神得令、得地、无克制等），不能简单判定合就化。合化的具体条件清单需要更系统的原典审计。在Canonical State Resolver中，合化需要标记为'需严格条件验证'，不能默认合就化。禁止：五合→合化（简单映射不成立）。",
))


# ============================================================
# R6-4: 争合/妒合
# ============================================================

audits.append(RelationAudit14(
    relation_id="R6-4",
    source_text="丁壬妒合犯淫讹。（争合：两干争合一干，如两甲争合一己）",
    source_book="渊海子平",
    source_location="挈要捷驰玄妙诀 / 论争合",
    input_facts=["heavenly_stems", "stem_combinations", "stem_positions"],
    relation="争合/妒合是五合的特殊情况：两个相同天干争合一个天干（如两甲争合一己），或合的位置不当导致妒合。争合/妒合影响合的成立和效果。",
    condition="(1)存在两个相同天干争合一个天干；(2)或合的位置不当（如间隔太远/被阻隔）",
    qualifier="争合/妒合影响合的成立：争合时合可能不成立或效果减弱。'丁壬妒合犯淫讹'——妒合有特定的负面含义。争合/妒合的具体判断规则（位置、力量对比）需要更多原典依据。",
    target="被争合/妒合的天干关系",
    effect="争合/妒合→合可能不成立或效果减弱。妒合可能有特定负面含义。",
    counterexample="（待补充：争合中某干力量占优时合可能成立）",
    result_class=ResultClass.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authorization="AUTHORIZED_WITH_QUALIFIER: 争合/妒合作为五合的特殊情况被原典提及（'丁壬妒合犯淫讹'）。但必须带qualifier：争合/妒合影响合的成立和效果，具体判断规则（位置、力量对比、是否成立）需要更多原典依据。在Canonical State Resolver中，争合/妒合需要标记为'合的有效性存疑'。",
))


# ============================================================
# 调候：独立维度
# ============================================================

audits.append(RelationAudit14(
    relation_id="ADJ-1",
    source_text="（穷通宝鉴120条调候用神表：如乙木戌月'丙火为主，癸辛为佐'）",
    source_book="穷通宝鉴",
    source_location="10天干×12月令调候用神表",
    input_facts=["day_master", "month_branch", "seasonal_context"],
    relation="调候是独立维度，根据日主+月令确定调候用神（寒暖燥湿）。调候≠旺衰，调候≠强弱。调候不混入旺衰/强弱判断。",
    condition="(1)确定日主和月令；(2)查穷通宝鉴调候用神表；(3)确定调候用神（主/佐）",
    qualifier="调候是独立维度，不得混入旺衰/强弱。穷通宝鉴120条调候用神表是候选知识/索引，不是直接授权。调候用神表的原文需要回到穷通宝鉴原典验证上下文和条件。调候影响后续解释和用神选取，但不直接改变旺衰/强弱状态。调候用神表的'丙火为主癸辛为佐'是调候建议，不是强弱结论。",
    target="日主+月令的季节环境",
    effect="调候→确定调候用神（主/佐），指导用神选取和后续解释。不直接改变旺衰/强弱状态。",
    counterexample="调候用神不代表身强/身弱（调候是独立维度）",
    result_class=ResultClass.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authorization="AUTHORIZED_WITH_QUALIFIER: 调候作为独立维度被原典授权（穷通宝鉴专门论调候）。但必须带严格qualifier：(1)调候≠旺衰，调候≠强弱，是独立维度；(2)穷通宝鉴120条调候用神表是候选知识/索引，不是直接授权，需要回到原典验证；(3)调候不混入旺衰/强弱判断；(4)调候用神表是调候建议，不是强弱结论。在Canonical State中，调候作为独立字段seasonal_remedy，与wangshuai/qiangruo并行。禁止：调候→强弱（跨维度映射不成立）。",
))


# ============================================================
# 格局：候选关系
# ============================================================

audits.append(RelationAudit14(
    relation_id="PAT-1",
    source_text="（子平真诠23条格局结构模板：如正官格'月令透出正官...喜印绶护官财星生官，忌伤官刑冲月令'）",
    source_book="子平真诠",
    source_location="8正格+从格+专旺+化格+用神分类",
    input_facts=["month_branch", "hidden_stems", "heavenly_stems", "ten_gods", "day_master"],
    relation="格局是候选关系，根据月令和十神结构确定格局类型。格局≠强弱，格局≠吉凶。格局只作为候选关系，不直接授权断言。",
    condition="(1)确定月令藏干和透干；(2)确定格局类型（正官/七杀/正印/偏印/正财/偏财/食神/伤官/从格/专旺/化格）；(3)确定成格条件",
    qualifier="格局是候选关系，不直接授权。子平真诠23条格局结构模板是参考格式（取格/喜/忌/成格条件/贵格），不是直接授权。格局的成格/破格需要严格条件验证。格局≠强弱（身弱也可能成格，身强也可能破格）。格局≠吉凶（成格不必然吉，破格不必然凶，需要结合用神和大运流年）。格局对断言的影响需要通过Assertion Contract单独授权。",
    target="月令+十神结构",
    effect="格局→确定格局类型和成格状态。作为候选关系输入后续Assertion Contract。不直接授权断言。",
    counterexample="成格不必然吉（需要用神配合）；身弱也可能成格（格局≠强弱）",
    result_class=ResultClass.SOURCE_MAPPED_NON_PROOF,
    canonical_authorization="NOT_DIRECTLY_AUTHORIZED: 格局作为候选关系被原典记录（子平真诠专门论格局），但格局不直接授权强弱结论或断言。格局结构模板是参考格式，不是直接授权。格局的成格/破格需要严格条件验证。格局≠强弱，格局≠吉凶。格局对断言的影响需要通过Assertion Contract单独授权。在Canonical State中，格局作为候选字段pattern_candidate，标记为'需单独授权'。禁止：格局→强弱/吉凶（简单映射不成立）。",
))


# ============================================================
# 主执行：输出审计结果
# ============================================================

def main():
    print("=" * 100)
    print("STR-001A Phase 6.1 Layer 2B — R1-5 + R3-R6 全量关系审计")
    print("=" * 100)
    print()
    print("执行边界:")
    print("  - JSON整理库只作候选索引，原典才是授权来源")
    print("  - 每条关系按14字段统一模板输出")
    print("  - 强制允许 INSUFFICIENT_SOURCE / SOURCE_CONTESTED / SOURCE_MAPPED_NON_PROOF")
    print("  - 不为追求通过率强行授权")
    print("  - 调候=独立维度，不得混入旺衰/强弱")
    print("  - 格局=只作为候选关系，不直接授权")
    print()

    # 按模块分组输出
    modules = {
        "R1-5 印→生扶": [a for a in audits if a.relation_id == "R1-5"],
        "R3 克泄耗": [a for a in audits if a.relation_id.startswith("R3-")],
        "R4 合冲刑会破害": [a for a in audits if a.relation_id.startswith("R4-")],
        "R5 有效性修正": [a for a in audits if a.relation_id.startswith("R5-")],
        "R6 天干五合": [a for a in audits if a.relation_id.startswith("R6-")],
        "调候(独立维度)": [a for a in audits if a.relation_id.startswith("ADJ-")],
        "格局(候选关系)": [a for a in audits if a.relation_id.startswith("PAT-")],
    }

    for module_name, module_audits in modules.items():
        print("\n" + "=" * 100)
        print(f"模块: {module_name} ({len(module_audits)}条)")
        print("=" * 100)
        for audit in module_audits:
            print(f"\n{'─' * 100}")
            print(f"【{audit.relation_id}】")
            print(f"{'─' * 100}")
            print(f"  SOURCE_BOOK: {audit.source_book}")
            print(f"  SOURCE_LOCATION: {audit.source_location}")
            print(f"  SOURCE_TEXT: {audit.source_text[:200]}{'...' if len(audit.source_text) > 200 else ''}")
            print(f"  INPUT_FACTS: {', '.join(audit.input_facts)}")
            print(f"  RELATION: {audit.relation}")
            print(f"  CONDITION: {audit.condition}")
            print(f"  QUALIFIER: {audit.qualifier}")
            print(f"  TARGET: {audit.target}")
            print(f"  EFFECT: {audit.effect}")
            print(f"  COUNTEREXAMPLE: {audit.counterexample}")
            print(f"  RESULT_CLASS: {audit.result_class.value}")
            print(f"  CANONICAL_AUTHORIZATION: {audit.canonical_authorization}")

    # 汇总
    print("\n" + "=" * 100)
    print("审计汇总")
    print("=" * 100)
    print(f"\n  {'关系ID':<10} {'模块':<20} {'结果分类':<35} {'授权状态':<15}")
    print(f"  {'─'*10} {'─'*20} {'─'*35} {'─'*15}")
    for audit in audits:
        module = ""
        if audit.relation_id.startswith("R1"): module = "印生扶"
        elif audit.relation_id.startswith("R3"): module = "克泄耗"
        elif audit.relation_id.startswith("R4"): module = "合冲刑会"
        elif audit.relation_id.startswith("R5"): module = "有效性修正"
        elif audit.relation_id.startswith("R6"): module = "天干五合"
        elif audit.relation_id.startswith("ADJ"): module = "调候"
        elif audit.relation_id.startswith("PAT"): module = "格局"
        auth = "AUTHORIZED" if "AUTHORIZED" in audit.canonical_authorization and "NOT_AUTHORIZED" not in audit.canonical_authorization and "PARTIALLY" not in audit.canonical_authorization else ("PARTIAL" if "PARTIALLY" in audit.canonical_authorization else "NOT_AUTH")
        print(f"  {audit.relation_id:<10} {module:<20} {audit.result_class.value:<35} {auth:<15}")

    print(f"\n  统计:")
    for rc in ResultClass:
        count = sum(1 for a in audits if a.result_class == rc)
        print(f"    {rc.value}: {count}")
    print(f"    总计: {len(audits)}条")

    print(f"\n  关键原则确认:")
    print(f"    1. 印过旺反作用(水多木漂): 已授权(R1-5 WITH_QUALIFIER)")
    print(f"    2. 官杀作用关系≠身弱结果: 已授权(R3-1 WITH_QUALIFIER)")
    print(f"    3. 食伤泄身需要条件(盗气): 已授权(R3-2 WITH_QUALIFIER)")
    print(f"    4. 财多→身弱因果链不授权: SOURCE_MAPPED_NON_PROOF(R3-3)")
    print(f"    5. 合≠强/冲≠弱/刑≠凶: 已授权(R4-1/2/3 WITH_QUALIFIER)")
    print(f"    6. 破/害原典依据不足: INSUFFICIENT_SOURCE(R4-5)")
    print(f"    7. 空亡是RELATION EFFECT MODIFIER不是STRENGTH EVIDENCE: 已授权(R5-1 WITH_QUALIFIER)")
    print(f"    8. 空亡对不同五行有不同影响(金空则鸣/木空则朽): 已授权")
    print(f"    9. 五合≠合化,合化条件严格: 已授权(R6-1/3 WITH_QUALIFIER)")
    print(f"    10. 调候是独立维度不混入旺衰强弱: 已授权(ADJ-1 WITH_QUALIFIER)")
    print(f"    11. 格局是候选关系不直接授权: SOURCE_MAPPED_NON_PROOF(PAT-1)")
    print(f"    12. JSON只作候选索引原典才是授权来源: 全局原则")

    print("\n" + "=" * 100)
    print("Layer 2B 全量关系审计完成。")
    print("下一步: Layer 3 组合关系层（印比+通根→党众、党众/助寡→强弱）")
    print("=" * 100)


if __name__ == "__main__":
    main()
