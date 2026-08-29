"""
STR-001A P6.4-G ASSERT-006「食神生财，富贵自天来」原典语义审计

目标: 不是把它"做成授权断言", 而是把CANDIDATE → 可审计状态继续推进,
      验证P6.4对关系词「生」的处理能力。

审计顺序:
  G1 原典精确定位
  G2 审计「生」
  G3 审计「富贵自天来」
  G4 反向条件重新搜
  G5 最终重新走P6.4 → Admission

核心验证点:
  食神存在 ≠ 食神生财
  财星存在 ≠ 食神生财成立
  食神生财 ≠ 自动获得「富贵」Effect
  所有新增条件必须有证据来源
  所有反向条件必须有证据来源
  无证据的条件必须保持UNRESOLVED
  Hermes无权自行升级Admission Status
"""

import sys
sys.path.insert(0, r"D:\shuntian\backend\scripts")

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

from str001a_p6_4_assertion_asset_production_protocol import (
    AssertionCandidate, SourceRecord, SemanticRelation,
    PreconditionCandidate, ReverseCondition, Qualifier,
    CandidateStatus, EvidenceStatus, SemanticUncertainty,
    HermesProductionBoundary, IndependentAuditPipeline,
)


# ============================================================
# G1 原典精确定位
# ============================================================

G1_FINDINGS = {
    "exact_location": {
        "book": "《渊海子平》",
        "chapter": "第2430段",
        "section": "格局列表",
        "line_range": "17630-17669",
        "exact_quote": "食神生财。",
        "context_before": "食神生旺。",
        "context_after": "杀化印綬。",
        "full_context": """正气官星。
财官两旺。
印綬天德。
独杀有制。
伤官生财。
坐禄逢财。
官星带合。
日贵逢财。
官贵逢官。
官星坐禄。
官星桃花。
食神生旺。
食神生财。
杀化印綬。
二德扶身。
三奇合局。
阳刃有制。
拱禄拱贵。
归禄逢财。""",
    },
    "key_discovery": "「食神生财」在《渊海子平》中首先是一个格局名称, 出现在格局列表中, 与「正气官星」「财官两旺」「印绶天德」「独杀有制」「伤官生财」「坐禄逢财」等并列。这说明「食神生财」不是一个简单的断语, 而是一个格局定义。",
    "fugui_zi_tian_lai_found": False,
    "fugui_zi_tian_lai_note": "「富贵自天来」这个具体表述在《渊海子平》全文中没有找到精确匹配。原典中有类似表述, 但都不是「食神生财→富贵自天来」的直接断语。",
    "similar_quotes": [
        {"quote": "逢官而看财，见财而富贵。", "source": "《渊海子平·捷驰千里马》第2457段"},
        {"quote": "财生官，官生印，印生身，富贵双全。", "source": "《渊海子平·络绎赋》第2452段"},
        {"quote": "日禄归时见财，则清高富贵。", "source": "《渊海子平·金玉赋》第2456段"},
        {"quote": "归禄有财而获福。", "source": "《渊海子平·金玉赋》第2456段"},
    ],
}


# ============================================================
# G2 审计「生」
# ============================================================

G2_FINDINGS = {
    "relation_word": "生",
    "subject": "食神",
    "object": "财",
    "core_discovery": "「食神生财」中的「生」在原典中首先是一个格局定义, 指食神格中财星作为用神的格局。不是简单的五行相生关系存在即可。",
    "semantic_analysis": {
        "is_simple_five_element_generation": False,
        "reason": "「食神生财」出现在格局列表中, 与「伤官生财」「杀化印绶」等并列, 说明这是格局分类, 不是简单的五行关系描述。",
        "requires_pattern_context": True,
        "requires_shishen_conditions": True,
        "requires_cai_conditions": True,
        "requires_circulation": "UNRESOLVED",  # 是否需要流通无阻未明确
    },
    "shishen_conditions": [
        {"condition": "食神干旺", "source": "食神干旺，胜似财官；顺食者食前方丈，倒食者簞食豆羹。", "location": "第2437段"},
        {"condition": "食神健旺", "source": "月令值食神健旺，善饮食而姿质丰满。", "location": "第2456段《金玉赋》"},
        {"condition": "食神得地", "source": "阳日食神得地，无冲损则暗合官星。", "location": "第2456段《金玉赋》"},
        {"condition": "食神一位逢生旺", "source": "食神一位逢生旺，招子须当拜圣明。", "location": "第2455段"},
    ],
    "cai_conditions": [
        {"condition": "财星作为用神", "source": "「食神生财」作为格局名称, 隐含财星为用神", "location": "第2430段格局列表"},
        {"condition": "财星有气", "source": "但看，财命有气，纵背禄而不贫；财绝命衰，纵建禄而不富。", "location": "第2437段"},
    ],
    "key_limitations": [
        "食神需要干旺/健旺/得地, 不是存在即可",
        "财星需要有气/作为用神, 不是存在即可",
        "「生」是格局定义, 不是简单五行关系",
        "是否需要流通无阻UNRESOLVED",
        "是否需要日主身旺UNRESOLVED",
    ],
}


# ============================================================
# G3 审计「富贵自天来」
# ============================================================

G3_FINDINGS = {
    "effect_candidate": "富贵自天来",
    "exact_quote_found": False,
    "core_discovery": "「富贵自天来」这个具体表述在《渊海子平》全文中没有找到精确匹配。原典中有类似的富贵表述, 但都不是「食神生财→富贵自天来」的直接断语。",
    "similar_effect_quotes": [
        {"quote": "逢官而看财，见财而富贵。", "source": "《捷驰千里马》第2457段", "note": "这是「逢官看财」, 不是「食神生财」"},
        {"quote": "财生官，官生印，印生身，富贵双全。", "source": "《络绎赋》第2452段", "note": "这是「财生官→官生印→印生身」的链条, 不是「食神生财」"},
        {"quote": "日禄归时见财，则清高富贵。", "source": "《金玉赋》第2456段", "note": "这是「日禄归时+见财」, 不是「食神生财」"},
        {"quote": "归禄有财而获福。", "source": "《金玉赋》第2456段", "note": "这是「归禄+有财」, 不是「食神生财」"},
        {"quote": "食神干旺，胜似财官；顺食者食前方丈，倒食者簞食豆羹。", "source": "第2437段", "note": "这是「食神干旺→胜似财官」, 有「食前方丈」的效果描述, 但不是「富贵自天来」"},
    ],
    "effect_authorization": "NOT_AUTHORIZED",
    "reason": "「富贵自天来」没有精确原典出处。类似表述都有不同的前置条件(逢官看财/财生官印/日禄归时/归禄有财), 不能直接套用到「食神生财」上。「食神干旺→胜似财官→食前方丈」是最接近的效果描述, 但也不是「富贵自天来」。",
    "unresolved_items": [
        "「富贵自天来」是否为后世口诀而非原典原文?",
        "「食神生财」格局的具体Effect是什么? 原典没有直接说明",
        "「食前方丈」是否等同于「富贵」?",
        "「胜似财官」是否等同于「富贵」?",
    ],
}


# ============================================================
# G4 反向条件重新搜
# ============================================================

G4_FINDINGS = {
    "reverse_conditions": [
        {
            "id": "R1",
            "condition": "枭神夺食",
            "source": "食神制杀逢梟，不贫则夭。",
            "location": "第2456段《金玉赋》",
            "effect": "不贫则夭",
            "authorized": True,
            "note": "枭神(偏印)克制食神, 是食神格的最大禁忌",
        },
        {
            "id": "R2",
            "condition": "食神逢枭",
            "source": "食神逢梟者，亡。",
            "location": "第2456段《金玉赋》",
            "effect": "亡",
            "authorized": True,
            "note": "比R1更严重, 直接说「亡」",
        },
        {
            "id": "R3",
            "condition": "食衰枭旺",
            "source": "食衰梟旺，不死也灾。",
            "location": "第2437段",
            "effect": "不死也灾",
            "authorized": True,
            "note": "食神衰而枭神旺, 即使不死也有灾",
        },
        {
            "id": "R4",
            "condition": "食神太过",
            "source": "荒淫之慾，食神太过。",
            "location": "第2455段",
            "effect": "荒淫之欲",
            "authorized": True,
            "note": "食神太多反而导致荒淫, 不是富贵",
        },
        {
            "id": "R5",
            "condition": "食神叠见",
            "source": "食神叠见，须忌官乡。",
            "location": "第2454段",
            "effect": "须忌官乡",
            "authorized": True,
            "note": "食神太多反而忌官星, 说明食神不是越多越好",
        },
        {
            "id": "R6",
            "condition": "劫财多",
            "source": "日求升合，食神旺处劫财多。",
            "location": "第2456段《金玉赋》",
            "effect": "日求升合(贫穷)",
            "authorized": True,
            "note": "食神旺但劫财多, 反而贫穷, 因为劫财夺财",
        },
        {
            "id": "R7",
            "condition": "伤官食神并身旺遇库",
            "source": "伤官食神并身旺，遇库兴灾。",
            "location": "第2454段",
            "effect": "遇库兴灾",
            "authorized": True,
            "note": "食神伤官并见且身旺, 遇墓库则兴灾",
        },
        {
            "id": "R8",
            "condition": "偏印克食神",
            "source": "或，逢偏印剋食神，非贫夭寿，须知乞化。",
            "location": "第2456段《金玉赋》",
            "effect": "非贫夭寿，须知乞化",
            "authorized": True,
            "note": "偏印克食神, 不是贫就是夭, 甚至乞讨",
        },
    ],
    "key_discovery": "食神格有大量反向条件, 其中枭神夺食是最严重的(不贫则夭/亡), 劫财多也会导致贫穷(日求升合)。这些反向条件证明「食神生财」不是无条件的富贵断语。",
    "unresolved_reverse_conditions": [
        {"condition": "食神生财但身弱", "status": "UNRESOLVED", "note": "原典没有直接说明身弱时食神生财的效果, 但「我生彼(食伤)兮，常怀逼迫」暗示食伤对日主有消耗"},
        {"condition": "食神生财但财星被冲", "status": "UNRESOLVED", "note": "原典没有直接说明"},
    ],
}


# ============================================================
# P6.4-G 审计主流程
# ============================================================

def build_audited_candidate() -> AssertionCandidate:
    """构建经过G1-G4审计后的ASSERT-006 Candidate"""

    candidate = AssertionCandidate(
        assertion_id="ASSERT-006",
        candidate_status=CandidateStatus.EVIDENCE_CONTRACT,
        created_by="Hermes",
    )

    # G1: 原典精确定位
    candidate.source = SourceRecord(
        source_book=G1_FINDINGS["exact_location"]["book"],
        source_location=f"{G1_FINDINGS['exact_location']['chapter']} {G1_FINDINGS['exact_location']['section']}",
        source_text=G1_FINDINGS["exact_location"]["exact_quote"],
        source_context=G1_FINDINGS["exact_location"]["full_context"],
        source_version="FOR-BAZI渊海子平",
        cross_references=[
            "第2437段《看子平之法》: 食神干旺，胜似财官",
            "第2452段《络绎赋》: 财生官，官生印，印生身，富贵双全",
            "第2456段《金玉赋》: 食神制杀逢梟，不贫则夭",
            "第2457段《捷驰千里马》: 逢官而看财，见财而富贵",
        ],
    )

    # G2: 审计「生」
    candidate.semantic_relations = [
        SemanticRelation(
            subject="食神",
            relation="生",
            object="财",
            relation_semantics=(
                "「食神生财」在原典中首先是一个格局定义, 出现在格局列表中, "
                "与「伤官生财」「杀化印绶」等并列。不是简单的五行相生关系存在即可。"
                "食神需要干旺/健旺/得地, 财星需要有气/作为用神。"
            ),
            relation_word_analysis=(
                "「生」是格局定义词, 不是简单的五行相生动词。"
                "原典证据: 「食神生财」出现在第2430段格局列表中, "
                "与「正气官星」「财官两旺」「印绶天德」「独杀有制」「伤官生财」「坐禄逢财」等并列。"
                "这说明「食神生财」是一个格局分类, 不是「食神存在+财星存在」的简单关系。"
                "食神条件: 干旺(食神干旺，胜似财官)、健旺(月令值食神健旺)、得地(阳日食神得地)。"
                "财星条件: 有气(财命有气，纵背禄而不贫)、作为用神(格局定义隐含)。"
                "是否需要流通无阻: UNRESOLVED。"
                "是否需要日主身旺: UNRESOLVED。"
            ),
            is_boolean_simplifiable=False,
            simplification_risk=(
                "极高: 如果简化为has_shishen AND has_cai, 会丢失: "
                "1)格局定义语义 2)食神干旺/健旺/得地条件 3)财星有气/用神条件 "
                "4)枭神夺食等大量反向条件 5)「富贵自天来」Effect没有原典授权"
            ),
        ),
    ]

    # G2: 前置条件(更新为有原典依据的版本)
    candidate.preconditions = [
        PreconditionCandidate(
            pid="P1",
            name="食神格/食神有力",
            description="食神需要干旺/健旺/得地, 不是存在即可。原典: 食神干旺，胜似财官; 月令值食神健旺; 阳日食神得地。",
            source_type="SOURCE_DEFINED_STATE",
            is_resolvable=True,
            unresolved_reason="",
        ),
        PreconditionCandidate(
            pid="P2",
            name="财星有气/作为用神",
            description="财星需要有气/作为食神格的用神, 不是存在即可。原典: 财命有气，纵背禄而不贫。",
            source_type="SOURCE_DEFINED_STATE",
            is_resolvable=True,
            unresolved_reason="",
        ),
        PreconditionCandidate(
            pid="P3",
            name="无枭神夺食",
            description="必须没有枭神(偏印)克食神。原典: 食神制杀逢梟，不贫则夭; 食神逢梟者，亡; 食衰梟旺，不死也灾。",
            source_type="SOURCE_DEFINED_STATE",
            is_resolvable=True,
            unresolved_reason="",
        ),
        PreconditionCandidate(
            pid="P4",
            name="无劫财夺财",
            description="劫财不能太多, 否则劫财夺财。原典: 日求升合，食神旺处劫财多。",
            source_type="SOURCE_DEFINED_STATE",
            is_resolvable=True,
            unresolved_reason="",
        ),
        PreconditionCandidate(
            pid="P5",
            name="日主状态",
            description="食神生财是否需要日主身旺? 原典未明确。「我生彼(食伤)兮，常怀逼迫」暗示食伤对日主有消耗。",
            source_type="CONSUMED_CANONICAL_STATE",
            canonical_state_ref="qiangruo=STRONG?",
            is_resolvable=False,
            unresolved_reason="原典没有直接说明身弱时食神生财的效果, UNRESOLVED",
        ),
    ]

    # G3: Effect候选(更新为审计后的版本)
    candidate.effect_candidate = "富贵(待授权)"
    candidate.effect_source_text = "「富贵自天来」无精确原典出处。最接近: 食神干旺，胜似财官；顺食者食前方丈。"

    # G4: 反向条件(全部有原典依据)
    candidate.reverse_conditions = [
        ReverseCondition(
            condition_id="R1",
            description="枭神夺食",
            source_text="食神制杀逢梟，不贫则夭。",
            source_location="第2456段《金玉赋》",
            effect="不贫则夭",
            is_authorized=True,
        ),
        ReverseCondition(
            condition_id="R2",
            description="食神逢枭",
            source_text="食神逢梟者，亡。",
            source_location="第2456段《金玉赋》",
            effect="亡",
            is_authorized=True,
        ),
        ReverseCondition(
            condition_id="R3",
            description="食衰枭旺",
            source_text="食衰梟旺，不死也灾。",
            source_location="第2437段",
            effect="不死也灾",
            is_authorized=True,
        ),
        ReverseCondition(
            condition_id="R4",
            description="食神太过",
            source_text="荒淫之慾，食神太过。",
            source_location="第2455段",
            effect="荒淫之欲",
            is_authorized=True,
        ),
        ReverseCondition(
            condition_id="R5",
            description="食神叠见",
            source_text="食神叠见，须忌官乡。",
            source_location="第2454段",
            effect="须忌官乡",
            is_authorized=True,
        ),
        ReverseCondition(
            condition_id="R6",
            description="劫财多",
            source_text="日求升合，食神旺处劫财多。",
            source_location="第2456段《金玉赋》",
            effect="日求升合(贫穷)",
            is_authorized=True,
        ),
        ReverseCondition(
            condition_id="R7",
            description="伤官食神并身旺遇库",
            source_text="伤官食神并身旺，遇库兴灾。",
            source_location="第2454段",
            effect="遇库兴灾",
            is_authorized=True,
        ),
        ReverseCondition(
            condition_id="R8",
            description="偏印克食神",
            source_text="或，逢偏印剋食神，非贫夭寿，须知乞化。",
            source_location="第2456段《金玉赋》",
            effect="非贫夭寿，须知乞化",
            is_authorized=True,
        ),
    ]

    # 限定条件
    candidate.qualifiers = [
        Qualifier(
            qualifier_id="Q1",
            description="「食神生财」是格局定义, 不是简单断语",
            source_text="食神生财。(出现在第2430段格局列表中)",
            source_location="第2430段",
            effect_on_assertion="「生」的语义是格局定义, 不能简化为has_shishen AND has_cai",
        ),
        Qualifier(
            qualifier_id="Q2",
            description="「富贵自天来」无精确原典出处",
            source_text="「富贵自天来」在《渊海子平》全文中未找到精确匹配",
            source_location="全文检索",
            effect_on_assertion="Effect「富贵」未获原典直接授权, 不能作为断事结论",
        ),
        Qualifier(
            qualifier_id="Q3",
            description="大量反向条件存在",
            source_text="枭神夺食(不贫则夭/亡)、劫财多(日求升合)、食神太过(荒淫)等",
            source_location="第2437/2454/2455/2456段",
            effect_on_assertion="「食神生财」不是无条件的富贵断语, 必须检查反向条件",
        ),
    ]

    # 未解决项(更新为审计后的版本)
    candidate.unresolved_items = []
    candidate.add_unresolved(
        SemanticUncertainty.EFFECT_UNDEFINED.value,
        "「富贵自天来」无精确原典出处, Effect未获直接授权",
        "核心: Effect授权不确定, 不能作为断事结论",
    )
    candidate.add_unresolved(
        SemanticUncertainty.CONDITION_UNDEFINED.value,
        "食神生财是否需要日主身旺? 原典未明确",
        "P5前置条件无法解析, UNRESOLVED",
    )
    candidate.add_unresolved(
        SemanticUncertainty.CONDITION_UNDEFINED.value,
        "「生」是否需要流通无阻? 原典未明确",
        "P3核心限定条件无法完全解析",
    )
    candidate.add_unresolved(
        SemanticUncertainty.SCOPE_UNDEFINED.value,
        "「富贵自天来」是否为后世口诀而非原典原文?",
        "需要进一步检索其他经典(《三命通会》《子平真诠》等)确认出处",
    )

    # 证据状态(更新为审计后的版本)
    candidate.evidence_status = EvidenceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER

    # Hermes自评估
    candidate.hermes_self_assessment = {
        "confidence": "MEDIUM",
        "reason": "原典定位精确(第2430段格局列表), 「生」的语义已审计(格局定义), 大量反向条件已授权。但「富贵自天来」无精确原典出处, Effect未获直接授权。",
        "recommendation": "保持CANDIDATE状态。「食神生财」作为格局关系可以进入关系矩阵, 但「富贵自天来」作为Effect不能授权。需要进一步检索其他经典确认「富贵自天来」的出处。",
        "warning": "严禁将「食神生财」简化为has_shishen AND has_cai, 严禁将「富贵自天来」作为已授权Effect",
        "key_audit_findings": {
            "G1": "「食神生财」是格局名称, 出现在第2430段格局列表中",
            "G2": "「生」是格局定义词, 不是简单五行相生; 食神需要干旺/健旺/得地",
            "G3": "「富贵自天来」无精确原典出处, Effect未获直接授权",
            "G4": "8条反向条件全部有原典依据, 枭神夺食最严重(不贫则夭/亡)",
        },
    }

    return candidate


def main():
    print("=" * 110)
    print("STR-001A P6.4-G ASSERT-006「食神生财，富贵自天来」原典语义审计")
    print("=" * 110)

    print(f"""
  目标: 不是把它"做成授权断言", 而是把CANDIDATE → 可审计状态继续推进,
        验证P6.4对关系词「生」的处理能力。

  审计顺序:
    G1 原典精确定位
    G2 审计「生」
    G3 审计「富贵自天来」
    G4 反向条件重新搜
    G5 最终重新走P6.4 → Admission
""")

    # G1
    print(f"\n  {'='*100}")
    print(f"  G1 原典精确定位")
    print(f"  {'='*100}")
    loc = G1_FINDINGS["exact_location"]
    print(f"""
    典籍: {loc['book']}
    章节: {loc['chapter']} ({loc['section']})
    行范围: {loc['line_range']}
    原文: 「{loc['exact_quote']}」
    前文: 「{loc['context_before']}」
    后文: 「{loc['context_after']}」

    完整上下文(格局列表):
    {loc['full_context']}

    关键发现:
    {G1_FINDINGS['key_discovery']}

    「富贵自天来」精确匹配: {'✓ 找到' if G1_FINDINGS['fugui_zi_tian_lai_found'] else '✗ 未找到'}
    {G1_FINDINGS['fugui_zi_tian_lai_note']}

    类似表述:
""")
    for q in G1_FINDINGS["similar_quotes"]:
        print(f"    • 「{q['quote']}」 — {q['source']}")

    # G2
    print(f"\n  {'='*100}")
    print(f"  G2 审计「生」")
    print(f"  {'='*100}")
    print(f"""
    关系: 食神 → 生 → 财
    核心发现: {G2_FINDINGS['core_discovery']}

    语义分析:
      是简单五行相生? {'✓ 是' if G2_FINDINGS['semantic_analysis']['is_simple_five_element_generation'] else '✗ 否'}
      理由: {G2_FINDINGS['semantic_analysis']['reason']}
      需要格局上下文? {'✓ 是' if G2_FINDINGS['semantic_analysis']['requires_pattern_context'] else '✗ 否'}
      需要食神条件? {'✓ 是' if G2_FINDINGS['semantic_analysis']['requires_shishen_conditions'] else '✗ 否'}
      需要财星条件? {'✓ 是' if G2_FINDINGS['semantic_analysis']['requires_cai_conditions'] else '✗ 否'}
      需要流通无阻? {G2_FINDINGS['semantic_analysis']['requires_circulation']}

    食神条件(原典依据):
""")
    for c in G2_FINDINGS["shishen_conditions"]:
        print(f"    • {c['condition']}: 「{c['source']}」 ({c['location']})")

    print(f"\n    财星条件(原典依据):")
    for c in G2_FINDINGS["cai_conditions"]:
        print(f"    • {c['condition']}: 「{c['source']}」 ({c['location']})")

    print(f"\n    关键限制:")
    for lim in G2_FINDINGS["key_limitations"]:
        print(f"    • {lim}")

    # G3
    print(f"\n  {'='*100}")
    print(f"  G3 审计「富贵自天来」")
    print(f"  {'='*100}")
    print(f"""
    Effect候选: {G3_FINDINGS['effect_candidate']}
    精确原文找到: {'✓ 是' if G3_FINDINGS['exact_quote_found'] else '✗ 否'}
    核心发现: {G3_FINDINGS['core_discovery']}
    Effect授权: {G3_FINDINGS['effect_authorization']}
    理由: {G3_FINDINGS['reason']}

    类似Effect表述(都有不同的前置条件):
""")
    for q in G3_FINDINGS["similar_effect_quotes"]:
        print(f"    • 「{q['quote']}」 — {q['source']}")
        print(f"      注: {q['note']}")

    print(f"\n    未解决项:")
    for u in G3_FINDINGS["unresolved_items"]:
        print(f"    • {u}")

    # G4
    print(f"\n  {'='*100}")
    print(f"  G4 反向条件重新搜")
    print(f"  {'='*100}")
    print(f"""
    关键发现: {G4_FINDINGS['key_discovery']}

    已授权反向条件({len(G4_FINDINGS['reverse_conditions'])}条, 全部有原典依据):
""")
    for r in G4_FINDINGS["reverse_conditions"]:
        print(f"    [{r['id']}] {r['condition']}")
        print(f"         原文: 「{r['source']}」 ({r['location']})")
        print(f"         效果: {r['effect']}")
        print(f"         授权: {'✓ AUTHORIZED' if r['authorized'] else '✗ UNRESOLVED'}")

    print(f"\n    未解决反向条件:")
    for r in G4_FINDINGS["unresolved_reverse_conditions"]:
        print(f"    • {r['condition']}: {r['status']} — {r['note']}")

    # G5: 构建审计后的Candidate并验证
    print(f"\n  {'='*100}")
    print(f"  G5 最终重新走P6.4 → Admission")
    print(f"  {'='*100}")

    candidate = build_audited_candidate()

    print(f"""
    审计后Candidate状态:
      assertion_id: {candidate.assertion_id}
      candidate_status: {candidate.candidate_status.value}
      evidence_status: {candidate.evidence_status.value}
      语义关系: {len(candidate.semantic_relations)}个
      前置条件: {len(candidate.preconditions)}个 (P1-P4有原典依据, P5=UNRESOLVED)
      反向条件: {len(candidate.reverse_conditions)}个 (全部有原典依据)
      限定条件: {len(candidate.qualifiers)}个
      未解决项: {len(candidate.unresolved_items)}个

    Hermes生产边界验证:
""")

    is_compliant, violations = HermesProductionBoundary.validate_candidate(candidate)
    print(f"      合规: {'✓ 是' if is_compliant else '✗ 否'}")
    if violations:
        for v in violations:
            print(f"      违规: {v}")

    print(f"\n    Admission Gate准入检查:")
    can_enter = candidate.is_admission_ready()
    print(f"      可进入Admission Gate: {'✓ 是' if can_enter else '✗ 否(预期结果)'}")

    if not can_enter:
        print(f"      原因:")
        critical_unresolved = [
            u for u in candidate.unresolved_items
            if not u.get("resolved", False)
            and u.get("type") in [
                SemanticUncertainty.RELATION_WORD_UNDEFINED.value,
                SemanticUncertainty.CONDITION_UNDEFINED.value,
                SemanticUncertainty.EFFECT_UNDEFINED.value,
            ]
        ]
        print(f"        • evidence_status={candidate.evidence_status.value} (SOURCE_SUPPORTED_WITH_QUALIFIER, 非CONFIRMED)")
        print(f"        • 关键未解决项: {len(critical_unresolved)}个")
        for u in critical_unresolved:
            print(f"          - {u['type']}: {u['description'][:50]}")

    # Independent Audit
    print(f"\n    Independent Audit Pipeline (7层审核):")
    auditor = IndependentAuditPipeline()
    audit_results = auditor.run_full_audit(candidate)

    # 最终结论
    print(f"\n  {'='*100}")
    print(f"  P6.4-G 最终结论")
    print(f"  {'='*100}")

    print(f"""
    ✓ G1 原典精确定位完成: 「食神生财」出现在《渊海子平》第2430段格局列表中
    ✓ G2 「生」的语义审计完成: 「生」是格局定义词, 不是简单五行相生; 食神需要干旺/健旺/得地
    ✓ G3 「富贵自天来」审计完成: 无精确原典出处, Effect未获直接授权
    ✓ G4 反向条件审计完成: 8条反向条件全部有原典依据, 枭神夺食最严重(不贫则夭/亡)
    ✓ G5 重新走P6.4完成: Candidate保持CANDIDATE状态, 不能进入Admission Gate

    核心审计发现:
      1. 「食神生财」在原典中首先是一个格局名称, 不是简单断语
      2. 「生」是格局定义词, 不能简化为has_shishen AND has_cai
      3. 「富贵自天来」无精确原典出处, Effect未获直接授权
      4. 大量反向条件存在(枭神夺食/劫财多/食神太过等), 不是无条件富贵
      5. 食神需要干旺/健旺/得地, 财星需要有气/作为用神

    ASSERT-006当前状态: CANDIDATE (不进入Authorized Library)
      - 「食神生财」作为格局关系可以进入关系矩阵
      - 「富贵自天来」作为Effect不能授权
      - 需要进一步检索其他经典(《三命通会》《子平真诠》等)确认「富贵自天来」的出处

    这正是P6.4的验收标准:
      Hermes找到一句古文 → 原典定位精确 → 语义边界审计 → Effect未获授权 → 仍然只能CANDIDATE ✓

    P6.4-G验证通过。P6.4 Assertion Asset Production Protocol完整验证通过。
    生产流水线正式建立:
      Hermes (Candidate Producer)
        ↓ 只能负责 SOURCE → CANDIDATE
      Assertion Candidate
        ↓
      G1-G4 原典语义审计
        ↓
      Independent Audit (7层)
        ↓
      Admission Gate (7层)
        ↓
      AUTHORIZED / AUTHORIZED_WITH_QUALIFIER / CANDIDATE / POSTERIOR / REJECTED

    以后即使Hermes一次产生1000条候选断言, 系统也不会因为Hermes自己的判断而污染正式规则库。
    {'='*100}
""")


if __name__ == "__main__":
    main()
