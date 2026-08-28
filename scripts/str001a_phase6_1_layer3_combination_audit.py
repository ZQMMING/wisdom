"""
STR-001A Phase 6.1 Layer 3 — 组合关系层审计

执行边界:
- 先审原典，不先写Resolver
- 每条组合关系拆成: L1 Facts → Relations → Combination → Effect → Conclusion
- 严格区分5种结果分类
- 禁止把"党众""助寡"自动数值化
- 禁止默认: 党众=强、助寡=弱——必须由原典证明
- C3(党众/助寡→强/弱)作为最高风险项特别处理

4组关系:
C1: 比劫＋印绶＋通根 → 党众
C2: 比劫/印绶/通根不足 → 助寡
C3: 党众/助寡 → 强/弱 (最高风险项)
C4: 生扶组合＋克泄耗组合 → 最终强弱
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
class CombinationAudit:
    """组合关系审计模板: L1 Facts → Relations → Combination → Effect → Conclusion"""
    relation_id: str
    source_text: str
    source_book: str
    source_location: str
    l1_facts: List[str]           # L1 Facts
    relations: List[str]          # Relations (来自Layer 2的已授权关系)
    combination: str              # Combination (组合条件)
    effect: str                   # Effect (作用效果)
    conclusion: str               # Conclusion (结论)
    condition: str                # 成立条件
    qualifier: str                # 限定/修饰
    counterexample: str           # 反例
    result_class: ResultClass     # 结果分类
    canonical_authorization: str  # Canonical授权状态
    risk_level: str = ""          # 风险级别
    key_finding: str = ""         # 关键发现

    def to_dict(self):
        return {
            "RELATION_ID": self.relation_id,
            "SOURCE_TEXT": self.source_text,
            "SOURCE_BOOK": self.source_book,
            "SOURCE_LOCATION": self.source_location,
            "L1_FACTS": self.l1_facts,
            "RELATIONS": self.relations,
            "COMBINATION": self.combination,
            "EFFECT": self.effect,
            "CONCLUSION": self.conclusion,
            "CONDITION": self.condition,
            "QUALIFIER": self.qualifier,
            "COUNTEREXAMPLE": self.counterexample,
            "RESULT_CLASS": self.result_class.value,
            "CANONICAL_AUTHORIZATION": self.canonical_authorization,
            "RISK_LEVEL": self.risk_level,
            "KEY_FINDING": self.key_finding,
        }


audits: List[CombinationAudit] = []


# ============================================================
# C1: 比劫＋印绶＋通根 → 党众
# ============================================================

audits.append(CombinationAudit(
    relation_id="C1",
    source_text="春木夏火秋金冬水为得时，比劫印绶通根扶助为党众。",
    source_book="子平真诠",
    source_location="第六章 论十干得时不旺失时不弱",
    l1_facts=[
        "day_master (日主)",
        "companion_stems (比劫: 比肩/劫财)",
        "resource_stems (印绶: 正印/偏印)",
        "branch_hidden_stems (地支藏干)",
        "tonggen_status (通根状态)",
    ],
    relations=[
        "R1-4: 比劫→扶助 (已授权)",
        "R1-5: 印→生扶 (已授权, 带水多木漂qualifier)",
        "R1-1: 藏干→通根 (已授权)",
        "R1-2: 十二长生→根 (已授权, 带阴长生qualifier)",
        "R1-3: 根→根之重/根之轻 (已授权, 带质性优先级)",
    ],
    combination="比劫(扶助) + 印绶(生扶) + 通根(根之重/根之轻) → 三者共同构成'党众'。原典表述为'比劫印绶通根扶助为党众'。",
    effect="党众是强弱维度的结构状态，表示日主在四柱中有充分的生扶和根基。",
    conclusion="原典明确定义'比劫印绶通根扶助为党众'。这是定义性授权，不是因果推理。党众的成立需要三个要素同时存在：比劫扶助、印绶生扶、通根。但'扶助'和'生扶'的具体数量/质量标准原典未明确数值化。",
    condition="(1)存在比劫(比肩/劫财)；(2)存在印绶(正印/偏印)；(3)日主在地支有通根；(4)三者构成'扶助'关系。注意：通根必须是实际有效的(藏干中有日主同类五行)，不是名义上的。原典举例：'得一比肩，不如得支中一墓库，如甲逢未、丙逢戌之类。乙逢戌、丁逢丑、不作此论，以戌中无藏木，丑中无藏火也。'",
    qualifier="(1)党众的定义包含三个要素，但原典未明确每个要素的最低数量/质量标准；(2)'扶助'和'生扶'不是数值概念，不能简单count；(3)通根的质量有层级(根之重/根之轻)，影响党众的'程度'但原典未明确党众的程度分级；(4)印过旺可能反作用(水多木漂)，但这是否影响'党众'的定义需要进一步分析——原典'比劫印绶通根扶助为党众'中的印绶应该是适度生扶，过旺反作用可能不属于'扶助'。",
    counterexample="乙逢戌不作通根论(戌中无藏木)——名义上的通根不算，必须实际藏干中有同类五行。印过旺反作用(水多木漂)可能不属于'扶助'范畴。",
    result_class=ResultClass.SOURCE_SUPPORTED,
    canonical_authorization="AUTHORIZED: '比劫印绶通根扶助为党众'被原典明确定义。这是定义性授权，不是因果推理。党众的成立需要比劫+印绶+通根三个要素。但每个要素的具体数量/质量标准原典未数值化，需要在Resolver中按质性标准(而非数值阈值)判断。禁止：把党众数值化(如比劫count>=2 AND 印count>=1 AND 通根count>=1)。",
    risk_level="LOW",
    key_finding="党众的定义被原典明确授权。关键是'比劫印绶通根扶助'三个要素，不是数值阈值。通根必须实际有效(藏干中有同类五行)，乙逢戌不作通根论。",
))


# ============================================================
# C2: 比劫/印绶/通根不足 → 助寡
# ============================================================

audits.append(CombinationAudit(
    relation_id="C2",
    source_text="大致得时为旺，失时为衰；党众为强，助寡为弱。",
    source_book="子平真诠",
    source_location="第六章 论十干得时不旺失时不弱",
    l1_facts=[
        "day_master (日主)",
        "companion_stems (比劫)",
        "resource_stems (印绶)",
        "tonggen_status (通根状态)",
    ],
    relations=[
        "R1-4: 比劫→扶助",
        "R1-5: 印→生扶",
        "R1-1: 藏干→通根",
        "C1: 比劫+印绶+通根→党众",
    ],
    combination="助寡是党众的反面：比劫/印绶/通根三者不足或缺失，导致日主缺乏充分的生扶和根基。",
    effect="助寡是强弱维度的结构状态，表示日主在四柱中缺乏充分的生扶和根基。",
    conclusion="原典将'助寡'与'党众'对举：'党众为强，助寡为弱'。但原典只明确定义了党众('比劫印绶通根扶助为党众')，没有明确定义助寡的具体组合条件。助寡只能从党众的反面推导：比劫/印绶/通根不足。但'不足'的具体标准原典未明确。",
    condition="(1)比劫不足或缺失；(2)印绶不足或缺失；(3)通根不足或缺失；(4)三者整体构成'扶助不足'。但'不足'的具体标准原典未明确数值化。",
    qualifier="(1)助寡的定义是从党众反面推导的，原典未直接定义助寡的组合条件；(2)'不足'的具体标准(比劫少于几个？印绶少于几个？通根质量低于什么？)原典未明确；(3)助寡不是简单的'比劫count<2 OR 印count<1 OR 无通根'，需要质性判断；(4)部分缺失(如只有比劫但无印绶，或有印绶但无通根)是否构成助寡，原典未明确；(5)助寡的'程度'分级原典未明确。",
    counterexample="原典未明确给出助寡的具体反例。但'虽衰而强'(失时但党众)说明失时不等于助寡，助寡是生扶/根基不足，不是月令失时。",
    result_class=ResultClass.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authorization="AUTHORIZED_WITH_QUALIFIER: 助寡作为党众的反面被原典提及('党众为强，助寡为弱')，但助寡的具体组合条件原典未明确定义，只能从党众反面推导。'不足'的具体标准需要在Resolver中按质性标准判断，不能数值化。禁止：助寡=比劫count<X OR 印count<Y OR 无通根(简单数值映射不成立)。",
    risk_level="MEDIUM",
    key_finding="助寡的概念被原典提及，但具体组合条件不如党众明确。助寡是党众的反面，但'不足'的标准需要质性判断，不能数值化。",
))


# ============================================================
# C3: 党众/助寡 → 强/弱 (最高风险项)
# ============================================================

audits.append(CombinationAudit(
    relation_id="C3",
    source_text="旺衰强弱四字，昔人论命，每笼统互用，不知须分别看也。大致得时为旺，失时为衰；党众为强，助寡为弱。故有虽旺而弱者，亦有虽衰而强者，分别观之，其理自明。",
    source_book="子平真诠",
    source_location="第六章 论十干得时不旺失时不弱",
    l1_facts=[
        "day_master (日主)",
        "dangzhong_status (党众状态, 来自C1)",
        "zhugua_status (助寡状态, 来自C2)",
        "wangshuai_baseline (旺衰基线, 来自Layer 1)",
    ],
    relations=[
        "C1: 比劫+印绶+通根→党众",
        "C2: 比劫/印绶/通根不足→助寡",
        "Layer1: 月令→得时/失时→旺/衰",
    ],
    combination="党众→强，助寡→弱。这是强弱维度的核心关系，与旺衰维度(得时→旺，失时→衰)并行。",
    effect="党众导致日主为强，助寡导致日主为弱。强弱与旺衰是两个独立维度，可以组合出四种状态：得时+党众=旺而强，得时+助寡=旺而弱(虽旺而弱)，失时+党众=衰而强(虽衰而强)，失时+助寡=衰而弱。",
    conclusion="原典明确说'党众为强，助寡为弱'，并且用'虽旺而弱、虽衰而强'的例子证明了强弱与旺衰的分离——这实际上证明了党众→强、助寡→弱的关系(虽衰而强=失时+党众=强)。但是！原典用了'大致'这个限定词：'大致得时为旺，失时为衰；党众为强，助寡为弱'。'大致'意味着这是一般规律，不是绝对规则。可能存在例外情况：(1)克泄耗过重可能修正强弱(但原典在本章未详细讨论，需C4另行审计)；(2)特殊格局(从格/专旺/化格)可能不适用普通强弱模型；(3)印过旺反作用(水多木漂)可能影响'党众'的构成(过旺的印可能不属于'扶助')。",
    condition="(1)党众状态成立(来自C1)→强；(2)助寡状态成立(来自C2)→弱；(3)这是一般规律('大致')，可能存在例外；(4)特殊格局可能不适用。",
    qualifier="(1)【最重要】原典用了'大致'：'大致党众为强，助寡为弱'——这是一般规律，不是绝对规则；(2)党众→强、助寡→弱是强弱维度的定义性陈述，不是从党众到强的因果推理——党众本身就是强的定义性条件；(3)'虽旺而弱、虽衰而强'证明了强弱与旺衰的分离，但也证明了党众→强、助寡→弱的关系(虽衰而强=失时+党众=强)；(4)克泄耗过重是否能使党众变为不强，原典在本章未讨论，需C4另行审计；(5)特殊格局(从格/专旺/化格)不适用普通强弱模型；(6)印过旺反作用(水多木漂)可能影响党众的构成，但这是C1的问题，不是C3的问题。",
    counterexample="(1)'虽旺而弱'=得时(旺)+助寡(弱)——这不是党众但弱的反例，是得时但助寡；(2)'虽衰而强'=失时(衰)+党众(强)——这证明了党众→强；(3)原典在本章未明确给出'党众但不强'的直接反例；(4)但'大致'这个限定词暗示可能存在例外，具体例外需要在其他章节或C4中查找。",
    result_class=ResultClass.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authorization="AUTHORIZED_WITH_QUALIFIER: '党众为强，助寡为弱'被原典明确授权，且'虽衰而强'的例子证明了党众→强的关系。但必须带严格qualifier：(1)原典用了'大致'，是一般规律不是绝对规则；(2)这是强弱维度的定义性陈述，不是因果推理；(3)克泄耗过重的修正作用需C4另行审计；(4)特殊格局不适用；(5)禁止：党众=强(无条件绝对映射)。正确表述：党众一般为强，助寡一般为弱，但需检查例外条件(克泄耗过重、特殊格局等)。【风险评估】这不是SOURCE_MAPPED_NON_PROOF，因为原典明确说了'党众为强，助寡为弱'；但也不是绝对的SOURCE_SUPPORTED，因为用了'大致'且可能存在例外。",
    risk_level="HIGH (最高风险项)",
    key_finding="【关键发现】原典明确说'党众为强，助寡为弱'，用了'大致'限定。'虽衰而强'证明了党众→强。这是定义性授权，不是因果推理。但'大致'意味着一般规律，可能存在例外(克泄耗过重、特殊格局)。C3不是INSUFFICIENT_SOURCE，也不是绝对SOURCE_SUPPORTED，是SOURCE_SUPPORTED_WITH_QUALIFIER。",
))


# ============================================================
# C4: 生扶组合＋克泄耗组合 → 最终强弱
# ============================================================

audits.append(CombinationAudit(
    relation_id="C4",
    source_text="（子平真诠论印绶：印绶喜其生身...故身旺印强，不愁太过，只要官星清纯...有印多而用财者，印重身强，透财以抑太过...身强印重而透煞破格——身强何劳印生，印重何劳煞生。）",
    source_book="子平真诠 / 滴天髓",
    source_location="论印绶 / 论用神成败救应 / 滴天髓全局气势",
    l1_facts=[
        "day_master (日主)",
        "support_relations (生扶组合: 比劫+印绶+通根, 来自C1/C2)",
        "opposition_relations (克泄耗组合: 官杀+食伤+财, 来自Layer 2B R3)",
        "wangshuai_baseline (旺衰基线)",
        "special_pattern (特殊格局检测)",
    ],
    relations=[
        "C1/C2: 党众/助寡 (生扶组合)",
        "C3: 党众/助寡→强/弱 (一般规律)",
        "R3-1: 官杀→克/制 (已授权, 作用关系≠身弱结果)",
        "R3-2: 食伤→泄/盗气 (已授权, 需过重条件)",
        "R3-3: 财→耗 (SOURCE_MAPPED_NON_PROOF, 因果链不授权)",
        "R4/R5: 合冲刑会/空亡 (结构关系/有效性修正)",
    ],
    combination="生扶组合(党众/助寡) + 克泄耗组合(官杀/食伤/财) → 最终强弱。需要判断克泄耗是否修正/覆盖/反作用于C3的一般规律。",
    effect="克泄耗可能修正强弱：官杀过重可能压制日主，食伤过重可能泄身，财过多可能耗身。但原典未明确给出系统的组合规则来计算最终强弱。",
    conclusion="原典没有明确授权'生扶组合+克泄耗组合→最终强弱'的系统组合规则。原典有个案描述(如'身强印重而透煞破格'、'杀重身轻终身有损'、'财多身弱富屋贫人')，但这些是特定格局/条件下的描述，不是系统的组合规则。克泄耗在Layer 2B中已授权为关系变量(官杀制我、食伤泄我、财耗我)，但它们如何组合影响最终强弱，原典没有给出可计算的系统规则。特别是：(1)官杀/食伤/财的'过重'标准原典未数值化；(2)生扶与克泄耗的'比较'规则原典未明确(不是简单的count对比)；(3)制化(食神制杀、印化杀、通关)如何影响最终结果需要单独审计；(4)特殊格局(从杀/从财/从儿)可能完全反转普通强弱逻辑。",
    condition="(1)生扶组合状态(党众/助寡)已确定；(2)克泄耗组合状态已确定；(3)需要判断克泄耗是否修正C3的一般规律。但原典未明确系统的组合规则。",
    qualifier="(1)原典没有系统的'生扶+克泄耗→最终强弱'组合规则，只有个案描述；(2)克泄耗的'过重'标准未数值化；(3)生扶与克泄耗的比较规则未明确(不是count对比)；(4)制化关系(食神制杀、印化杀、通关)需单独审计；(5)特殊格局可能反转普通强弱逻辑；(6)不能简单地做'support_count - opposition_count = final_strength'；(7)不能做加权评分。",
    counterexample="(1)'身强印重而透煞'破格——身强但透煞反而破格，说明克泄耗(煞)在特定条件下可以改变结果；(2)'杀重身轻终身有损'——官杀过重+身轻=有害，但这是描述不是规则；(3)'财多身健方为贵'——财多但身健=为贵，说明财多不必然导致身弱；(4)'食神制杀'——食伤可以制化官杀，改变克泄耗的影响。",
    result_class=ResultClass.INSUFFICIENT_SOURCE,
    canonical_authorization="NOT_AUTHORIZED: 原典没有明确授权'生扶组合+克泄耗组合→最终强弱'的系统组合规则。原典有个案描述，但没有可计算的系统规则。在Canonical State Resolver中，最终强弱的判断不能依赖C4的系统组合规则。当前可行的做法：(1)C3的一般规律(党众→强，助寡→弱)作为基线；(2)克泄耗作为QUALIFIER/COUNTER_RELATION标记，不直接计算最终强弱；(3)制化关系(食神制杀、印化杀)需后续单独审计；(4)特殊格局需单独检测，可能反转普通逻辑；(5)最终强弱在克泄耗过重或特殊格局时标记为'需人工判断'或'UNRESOLVED'，而不是强行计算。禁止：support_score - opposition_score = final_strength(数值评分不被授权)。",
    risk_level="HIGH",
    key_finding="【关键发现】C4是INSUFFICIENT_SOURCE。原典没有系统的生扶+克泄耗组合规则，只有个案描述。这意味着Canonical State Resolver不能依赖系统组合规则计算最终强弱。可行做法：C3一般规律作基线，克泄耗作QUALIFIER标记，制化/特殊格局单独审计，复杂情况标UNRESOLVED。这不是失败，是正确的审计结果——宁愿少一个自动结论，也不能制造不存在于原典的因果规则。",
))


# ============================================================
# 主执行
# ============================================================

def main():
    print("=" * 100)
    print("STR-001A Phase 6.1 Layer 3 — 组合关系层审计")
    print("=" * 100)
    print()
    print("执行边界:")
    print("  - 先审原典，不先写Resolver")
    print("  - 每条组合关系拆成: L1 Facts → Relations → Combination → Effect → Conclusion")
    print("  - 严格区分5种结果分类")
    print("  - 禁止把'党众''助寡'自动数值化")
    print("  - 禁止默认: 党众=强、助寡=弱——必须由原典证明")
    print("  - C3(党众/助寡→强/弱)作为最高风险项特别处理")
    print()

    for audit in audits:
        print(f"\n{'='*100}")
        print(f"【{audit.relation_id}】{audit.combination[:60]}...")
        print(f"风险级别: {audit.risk_level}")
        print(f"{'='*100}")
        print(f"  SOURCE_BOOK: {audit.source_book}")
        print(f"  SOURCE_LOCATION: {audit.source_location}")
        print(f"  SOURCE_TEXT: {audit.source_text[:200]}{'...' if len(audit.source_text) > 200 else ''}")
        print(f"  L1_FACTS: {', '.join(audit.l1_facts)}")
        print(f"  RELATIONS: {', '.join(audit.relations)}")
        print(f"  COMBINATION: {audit.combination}")
        print(f"  EFFECT: {audit.effect}")
        print(f"  CONCLUSION: {audit.conclusion}")
        print(f"  CONDITION: {audit.condition}")
        print(f"  QUALIFIER: {audit.qualifier}")
        print(f"  COUNTEREXAMPLE: {audit.counterexample}")
        print(f"  RESULT_CLASS: {audit.result_class.value}")
        print(f"  CANONICAL_AUTHORIZATION: {audit.canonical_authorization}")
        print(f"  KEY_FINDING: {audit.key_finding}")

    # 汇总
    print("\n" + "=" * 100)
    print("Layer 3 审计汇总")
    print("=" * 100)
    print(f"\n  {'关系ID':<8} {'组合关系':<35} {'结果分类':<35} {'风险':<10}")
    print(f"  {'─'*8} {'─'*35} {'─'*35} {'─'*10}")
    for audit in audits:
        print(f"  {audit.relation_id:<8} {audit.combination[:33]:<35} {audit.result_class.value:<35} {audit.risk_level[:8]:<10}")

    print(f"\n  统计:")
    for rc in ResultClass:
        count = sum(1 for a in audits if a.result_class == rc)
        print(f"    {rc.value}: {count}")
    print(f"    总计: {len(audits)}组")

    print(f"\n  关键结论:")
    print(f"    C1 党众定义: SOURCE_SUPPORTED (原典明确定义'比劫印绶通根扶助为党众')")
    print(f"    C2 助寡定义: SOURCE_SUPPORTED_WITH_QUALIFIER (从党众反面推导, '不足'标准未数值化)")
    print(f"    C3 党众/助寡→强/弱: SOURCE_SUPPORTED_WITH_QUALIFIER (最高风险项)")
    print(f"       - 原典明确说'党众为强，助寡为弱'，用了'大致'限定")
    print(f"       - '虽衰而强'证明了党众→强")
    print(f"       - 这是定义性授权，不是因果推理")
    print(f"       - 但'大致'意味着一般规律，可能存在例外(克泄耗过重、特殊格局)")
    print(f"       - 不是INSUFFICIENT_SOURCE，也不是绝对SOURCE_SUPPORTED")
    print(f"    C4 生扶+克泄耗→最终强弱: INSUFFICIENT_SOURCE")
    print(f"       - 原典没有系统的组合规则，只有个案描述")
    print(f"       - 这不是失败，是正确的审计结果")
    print(f"       - 宁愿少一个自动结论，也不能制造不存在于原典的因果规则")
    print(f"       - 可行做法: C3一般规律作基线，克泄耗作QUALIFIER，复杂情况标UNRESOLVED")

    print(f"\n  对Canonical State Resolver的影响:")
    print(f"    1. 党众/助寡的判断可以按C1/C2的质性标准实现(不数值化)")
    print(f"    2. 强弱的一般规律可以按C3实现(党众→强，助寡→弱)，但必须带'大致'的qualifier")
    print(f"    3. 克泄耗不能直接参与强弱计算(C4=INSUFFICIENT_SOURCE)，只能作QUALIFIER标记")
    print(f"    4. 制化关系(食神制杀、印化杀)和特殊格局需后续单独审计")
    print(f"    5. 复杂情况(克泄耗过重、特殊格局)应标UNRESOLVED，不强行计算")

    print("\n" + "=" * 100)
    print("Layer 3 组合关系层审计完成。")
    print("下一步: Layer 4 修正覆盖层(月令+全局→旺衰修正、全局气势→修正月令、调候独立维度、特殊格局覆盖)")
    print("=" * 100)


if __name__ == "__main__":
    main()
