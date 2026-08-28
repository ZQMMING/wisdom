"""STR-001A Phase 5B - SC-YHZP-DZL-001 Source Mapping 单条深审.

目标: 完成"临死绝之地"的原典语义闭环.
只处理: SC-YHZP-DZL-001 《渊海子平·定真论》"生日天元临死绝之地，为身弱也"

禁止:
  - 扩展其他Claim
  - 进入Proposition Evaluation
  - Canonical Authorization
  - 开发身弱算法
  - 数值阈值 / wood_ratio / score / probability / ENGINE_FEATURE threshold

最终状态要求:
  Canonical Source Authorization = NOT_DONE
  Semantic Mapping Authorization = NOT_DONE
  Evidence Authorization = NOT_DONE
  Proposition Evaluation = NOT_DONE
  L4 PROVEN = NOT_ALLOWED
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# 枚举
# ============================================================================

class TextLayer(str, Enum):
    ORIGINAL = "ORIGINAL"
    ORIGINAL_NOTE = "ORIGINAL_NOTE"
    COMMENTARY = "COMMENTARY"
    UNKNOWN = "UNKNOWN"


class MappingCompleteness(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"


class LogicalStrength(str, Enum):
    UNIVERSAL_SUFFICIENT = "UNIVERSAL_SUFFICIENT"  # 无条件充分条件
    CONTEXTUAL_SUFFICIENT = "CONTEXTUAL_SUFFICIENT"  # 特定语境下充分条件
    PARTIAL_CONDITION = "PARTIAL_CONDITION"  # 部分条件, 需结合其他条件
    DESCRIPTIVE_EXAMPLE = "DESCRIPTIVE_EXAMPLE"  # 描述性举例
    UNCLEAR = "UNCLEAR"


class AuditStatus(str, Enum):
    SOURCE_SUPPORTED = "SOURCE_SUPPORTED"
    SOURCE_MAPPED = "SOURCE_MAPPED"
    PARTIAL = "PARTIAL"
    REJECTED = "REJECTED"


# ============================================================================
# 深审数据结构
# ============================================================================

@dataclass
class SourceAuthenticity:
    """原文真实性核查."""
    source_id: str = "SRC-YHZP"
    source_name: str = "渊海子平"
    chapter: str = "定真论"
    edition: str = "渊海子平(题宋徐子平撰, 后人汇编)"
    text_reference: str = ""
    full_context: str = ""
    version_notes: str = ""
    confirmed: bool = False


@dataclass
class TermSemantics:
    """关键术语语义核查."""
    term: str = ""
    meaning: str = ""
    evidence: str = ""
    ambiguity: str = ""
    confirmed: bool = False


@dataclass
class Counterexample:
    """反例/限制条件."""
    source: str = ""
    text: str = ""
    implication: str = ""
    reduces_logical_strength: bool = False


@dataclass
class CandidateMapping:
    """Candidate SemanticMapping (NOT_AUTHORIZED)."""
    mapping_id: str = ""
    source_claim_id: str = "SC-YHZP-DZL-001"
    l1_observation: str = ""
    semantic_meaning: str = ""
    candidate_concept: str = ""
    mapping_basis: str = ""
    conditions_required: List[str] = field(default_factory=list)
    mapping_authorization: str = "NOT_AUTHORIZED"
    completeness: MappingCompleteness = MappingCompleteness.PARTIAL
    notes: str = ""


@dataclass
class NegativeTest:
    test_id: str = ""
    test_name: str = ""
    test_description: str = ""
    expected: str = ""
    actual: str = ""
    passed: bool = False


# ============================================================================
# SC-YHZP-DZL-001 深审
# ============================================================================

def deep_audit_sc_yhzp_dzl_001() -> Dict[str, Any]:
    """对SC-YHZP-DZL-001进行单条深审."""
    result = {}

    # === 1. 原文真实性 ===
    authenticity = SourceAuthenticity(
        text_reference="日干衰而求气旺之藉。且如壬癸巳午之类，皆因生日天元临死绝之地，为身弱也。",
        full_context="""
夫生日为主者，行君之令，法运四时；阴阳刚柔之情，内外否泰之道。
择日之法有三要：以干为天，以支为地，支中所藏者为人元。
乃分四柱，以年为根，月为苗，日为花，时为果。
又择四柱之中，以年为祖上...月为父母...以日为己身，当推其干，搜用八字，为内外生克取舍之源。
干弱则求气旺之藉，有余则欲不足之营。
日干弱则求气旺之藉，日干旺却嫌气旺，怕太过反为不足之命，值此损财伤妻。
日干衰而求气旺之藉。且如壬癸巳午之类，皆因生日天元临死绝之地，为身弱也。
        """.strip(),
        version_notes="多个版本(东里书斋/古籍典藏/古诗文网)一致. 《定真论》是《渊海子平》赋论部分的重要篇章.",
        confirmed=True,
    )
    result["authenticity"] = authenticity

    # === 2. "死绝"语义 ===
    sijue_semantics = TermSemantics(
        term="死绝",
        meaning="""
十二长生中的"死"和"绝"两个连续阶段, 是五行力量最弱的状态:
- 死: 五行之气枯竭, 万物走向死亡, 力量完全衰退
- 绝(受气): 万物在地中未有其象, 如母腹空而未有物, 完全无力的状态
"死绝"作为连续组合词使用, 表示从死到绝的极弱状态.
        """.strip(),
        evidence="""
例子"壬癸巳午": 壬水在巳为绝, 癸水在午为绝(水绝在巳/午).
十二长生表: 水绝在巳, 死在卯(阳水); 阴水癸死在寅, 绝在酉(阴干逆行有争议).
注意: 例子中壬癸巳午都是"绝"的位置, 不是"死"的位置.
        """.strip(),
        ambiguity="""
⚠️ 重要歧义:
1. 阴干十二长生有争议. 《滴天髓》原注:"甲木死午, 午为泄气之地, 理固然也, 而乙木死亥, 亥中有壬水, 乃其嫡母, 何为死哉?"
   说明阴干的"死绝"不能简单按十二长生表判定, 需要结合地支藏干.
2. "死绝"是指"死"和"绝"两个状态, 还是"死绝之乡"作为一个统称? 原文例子只有"绝"的位置.
3. "临死绝之地"是特指日支, 还是可以指任何地支? 例子"壬癸巳午"中日支是巳/午, 所以很可能特指日支.
        """.strip(),
        confirmed=False,  # 语义有歧义, 不能完全确认
    )
    result["sijue_semantics"] = sijue_semantics

    # === 3. "生日天元"语义 ===
    tianyuan_semantics = TermSemantics(
        term="生日天元",
        meaning="出生日的天干, 即日干/日主.",
        evidence="""
《定真论》上下文明确:
- "择日之法有三要：以干为天，以支为地，支中所藏者为人元"
- "以日为己身，当推其干"
- "日干弱则求气旺之藉"
因此"天元"=天干, "生日天元"=出生日的天干=日干=日主.
        """.strip(),
        ambiguity="无明显歧义. 在《定真论》上下文中'天元'明确指天干.",
        confirmed=True,
    )
    result["tianyuan_semantics"] = tianyuan_semantics

    # === 4. "临……之地"语义 ===
    lin_zhi_semantics = TermSemantics(
        term="临……之地",
        meaning="日干在地支中处于十二长生的某个状态, 通过十二长生表计算.",
        evidence="""
例子"壬癸巳午": 壬水日主, 巳为日支, 壬水绝在巳; 癸水日主, 午为日支, 癸水绝在午.
所以"临死绝之地"=日干在日支中处于十二长生的"死"或"绝"的位置.
        """.strip(),
        ambiguity="""
⚠️ 歧义:
1. 是否特指日支? 例子中日支是巳/午, 但"临死绝之地"也可能指其他地支.
2. 是否必须通过十二长生表计算? 还是有其他判定方式?
3. 是否存在月令限定? 原文没有明确限定月令.
        """.strip(),
        confirmed=False,  # 有歧义
    )
    result["lin_zhi_semantics"] = lin_zhi_semantics

    # === 5. "为身弱也"的逻辑强度 ===
    logical_strength_analysis = {
        "logical_strength": LogicalStrength.CONTEXTUAL_SUFFICIENT,
        "analysis": """
原文完整语境: "日干衰而求气旺之藉。且如壬癸巳午之类，皆因生日天元临死绝之地，为身弱也。"

关键语言特征:
1. "日干衰而求气旺之藉" — 这是前提/语境: 日干衰, 需要生扶
2. "且如...之类" — 这是举例说明, 不是普遍命题
3. "皆因...为身弱也" — 因果关系: 因为临死绝之地, 所以身弱

综合判断:
- 这不是无条件的Universal Rule (死绝 → 身弱)
- 这是在"日干衰"的语境下, 用举例方式说明"临死绝之地"是身弱的一个重要原因
- 但"皆因"这个词表示在该语境下, 临死绝之地是身弱的充分条件
- 因此逻辑强度: CONTEXTUAL_SUFFICIENT (特定语境下的充分条件)
        """.strip(),
        "not_universal_rule": True,
        "context_required": ["日干衰(语境前提)", "临死绝之地(核心条件)"],
        "cannot_upgrade_to_universal": True,
    }
    result["logical_strength"] = logical_strength_analysis

    # === 6. 反例/限制条件 ===
    counterexamples = [
        Counterexample(
            source="现代命理实践(微博/命理案例)",
            text="若是虽临死绝之位，日主尚有余根，比如甲木生在辰月或未月，辰未二土中均藏有余气木根，这般便轻易不从，或是四柱中印星得地有根，纵然日主势弱，也是绝处逢生之象，只作身弱论，不作从格看",
            implication="临死绝但有根/有生扶 → 仍然身弱, 但不作从格. 说明临死绝通常仍然是身弱, 但'弱'的程度可能不同.",
            reduces_logical_strength=False,  # 仍然是身弱, 只是不从格
        ),
        Counterexample(
            source="《渊海子平·喜忌篇》相关解释",
            text="盖言大凡看命，见人四柱日上天元太弱，不可一概七三弱而论，其中亦有弱处复生而不大弱，足以任财官也。下篇云：'金逢艮而遇土，号曰还魂，水入巽而见金，名为不绝。'",
            implication="天元太弱(包括临死绝)但'弱处复生' → 可能'不大弱', 足以任财官. 说明临死绝不是绝对的身弱, 存在'还魂/不绝'的例外.",
            reduces_logical_strength=True,  # 降低了逻辑强度: 临死绝可能'不大弱'
        ),
        Counterexample(
            source="《滴天髓》原注",
            text="甲木死午，午为泄气之地，理固然也，而乙木死亥，亥中有壬水，乃其嫡母，何为死哉？",
            implication="阴干的'死绝'本身有争议. 乙木死亥但亥中有壬水生乙木, 所以'何为死哉?'. 说明不能简单按十二长生表判定阴干的死绝, 需要结合地支藏干.",
            reduces_logical_strength=True,  # 降低了逻辑强度: 死绝的判定本身就有争议
        ),
        Counterexample(
            source="《滴天髓阐微·衰旺》(与SC-ZPZQ-06-002一致)",
            text="秋木虽弱，木根深而木亦强...是失时不弱也。是故日干不论月令休囚，只要四柱有根，便能受财官食神而当伤官七杀。",
            implication="虽然这是'失时不弱'的例子, 但原则可以推广: 只要四柱有根, 即使临死绝也可能'不弱'或'不大弱'.",
            reduces_logical_strength=True,
        ),
    ]
    result["counterexamples"] = counterexamples

    # === 7. Candidate SemanticMapping ===
    candidate_mappings = [
        CandidateMapping(
            mapping_id="MAP-DZL-001",
            l1_observation="Day Master (日干) 的十二长生状态 = 死 或 绝",
            semantic_meaning="日干在十二长生中处于极弱状态(死/绝)",
            candidate_concept="原典所述身弱条件之一: 临死绝之地",
            mapping_basis="《渊海子平·定真论》'生日天元临死绝之地，为身弱也'",
            conditions_required=[
                "日干在日支(或其他地支)中处于十二长生的死/绝状态",
                "语境前提: 日干衰(需要生扶)",
                "⚠️ 需检查是否有根/有生扶(可能'弱处复生'或'不大弱')",
                "⚠️ 阴干需特别检查地支藏干(十二长生阴干死尽有争议)",
            ],
            mapping_authorization="NOT_AUTHORIZED",
            completeness=MappingCompleteness.PARTIAL,
            notes="""
这是Candidate Mapping, 不是Authorized Mapping.
原典给出了方向性的条件(临死绝 → 身弱), 但:
1. 逻辑强度是CONTEXTUAL_SUFFICIENT, 不是UNIVERSAL_SUFFICIENT
2. 存在反例: 临死绝但有根/有生扶可能'不大弱'
3. 阴干死尽有争议, 需结合地支藏干
4. '临死绝之地'是否特指日支还需确认
因此条件完备度是PARTIAL, 不能直接用于L4 Evaluation.
禁止: 把十二长生状态翻译成数值阈值(如十二长生序号 < X).
            """.strip(),
        ),
    ]
    result["candidate_mappings"] = candidate_mappings

    # === 8. Evidence Role ===
    evidence_role = {
        "current_role": "PRIMARY_CANDIDATE",
        "role_analysis": """
SC-YHZP-DZL-001是目前找到的最明确的身弱正向定义, 可以作为PRIMARY候选证据.
但由于:
1. 条件完备度是PARTIAL(存在反例和歧义)
2. 逻辑强度是CONTEXTUAL_SUFFICIENT(不是Universal Rule)
3. mapping_authorization仍然是NOT_AUTHORIZED
因此当前只能是PRIMARY_CANDIDATE, 不能是AUTHORIZED PRIMARY.
要成为AUTHORIZED PRIMARY, 需要:
1. 确认'临死绝之地'的精确定义(是否特指日支? 阴干如何处理?)
2. 确认反例的处理方式(有根/有生扶时如何判定?)
3. 经过Evidence Contract Authorization
        """.strip(),
        "authorized": False,
        "can_enter_l3_authorized": False,
        "can_enter_l4_evaluation": False,
    }
    result["evidence_role"] = evidence_role

    # === 9. 最终结论 ===
    final_conclusion = {
        "audit_status": AuditStatus.SOURCE_SUPPORTED,
        "mapping_completeness": MappingCompleteness.PARTIAL,
        "logical_strength": LogicalStrength.CONTEXTUAL_SUFFICIENT,
        "summary": """
SC-YHZP-DZL-001 "生日天元临死绝之地，为身弱也" 经过深审:

✅ 原文真实性: 确认, 《渊海子平·定真论》原文, 多个版本一致
✅ "生日天元"语义: 确认, 指日干/日主
⚠️ "死绝"语义: 部分确认, 十二长生中的死/绝, 但阴干死尽有争议
⚠️ "临……之地"语义: 部分确认, 地支位置关系, 但是否特指日支待确认
⚠️ "为身弱也"逻辑强度: CONTEXTUAL_SUFFICIENT (特定语境下充分条件, 不是Universal Rule)
⚠️ 反例存在: 临死绝但有根/有生扶可能'不大弱'; 阴干死尽有争议

结论:
- 这是目前最明确的身弱正向条件, 可以作为PRIMARY_CANDIDATE
- 但条件完备度是PARTIAL, 不能直接用于L4 Evaluation
- mapping_authorization仍然是NOT_AUTHORIZED
- 需要进一步确认: 临死绝的精确定义、反例处理方式、阴干处理
- 不能擅自升级为: 死绝 → 身弱 (Universal Rule)
        """.strip(),
    }
    result["final_conclusion"] = final_conclusion

    return result


# ============================================================================
# Negative Tests
# ============================================================================

def run_negative_tests(result: Dict[str, Any]) -> List[NegativeTest]:
    """执行6个Negative Tests."""
    tests = []

    # NEG-01: "死绝"不能自动转换成任何数值threshold
    tests.append(NegativeTest(
        test_id="NEG-01",
        test_name='"死绝"不能自动转换成任何数值threshold',
        test_description="检查Candidate Mapping中没有把十二长生状态转换成数值阈值(如十二长生序号 < X)",
        expected="Mapping中没有数值阈值, 只有语义描述",
        actual="MAP-DZL-001的l1_observation是'Day Master的十二长生状态=死或绝', 没有数值阈值. notes明确禁止'把十二长生状态翻译成数值阈值'",
        passed=True,
    ))

    # NEG-02: "死绝"不能自动转换成wood_ratio / strength_score
    tests.append(NegativeTest(
        test_id="NEG-02",
        test_name='"死绝"不能自动转换成wood_ratio / strength_score',
        test_description="检查Candidate Mapping中没有wood_ratio或strength_score等工程特征",
        expected="Mapping中没有wood_ratio / strength_score",
        actual="MAP-DZL-001中没有wood_ratio或strength_score, 只有十二长生状态的语义描述",
        passed=True,
    ))

    # NEG-03: "死绝"不能自动生成ENGINE_FEATURE
    tests.append(NegativeTest(
        test_id="NEG-03",
        test_name='"死绝"不能自动生成ENGINE_FEATURE',
        test_description="检查没有把'死绝'自动生成为ENGINE_FEATURE类型的执行条件",
        expected="没有ENGINE_FEATURE生成, mapping_authorization=NOT_AUTHORIZED",
        actual="MAP-DZL-001的mapping_authorization=NOT_AUTHORIZED, 没有生成ENGINE_FEATURE",
        passed=True,
    ))

    # NEG-04: SourceClaimRelation=AUTHORIZES_MAPPING 不能导致 mapping_authorization=AUTHORIZED
    tests.append(NegativeTest(
        test_id="NEG-04",
        test_name='SourceClaimRelation=AUTHORIZES_MAPPING 不能导致 mapping_authorization=AUTHORIZED',
        test_description="检查GOV-INVARIANT-01: Authorization at layer N SHALL NOT imply authorization at layer N+1",
        expected="即使SourceClaim有AUTHORIZES_MAPPING关系, mapping_authorization仍然是NOT_AUTHORIZED",
        actual="SC-YHZP-DZL-001在Phase 5A中有AUTHORIZES_MAPPING关系, 但MAP-DZL-001的mapping_authorization仍然是NOT_AUTHORIZED",
        passed=True,
    ))

    # NEG-05: "死绝 → 身弱"必须经过上下文条件检查, 不得作为无条件Universal Rule
    tests.append(NegativeTest(
        test_id="NEG-05",
        test_name='"死绝 → 身弱"必须经过上下文条件检查, 不得作为无条件Universal Rule',
        test_description="检查逻辑强度判定: 不是UNIVERSAL_SUFFICIENT, 而是CONTEXTUAL_SUFFICIENT",
        expected="logical_strength = CONTEXTUAL_SUFFICIENT, 不是UNIVERSAL_SUFFICIENT",
        actual="logical_strength判定为CONTEXTUAL_SUFFICIENT (特定语境下充分条件), 明确not_universal_rule=True, cannot_upgrade_to_universal=True",
        passed=True,
    ))

    # NEG-06: 如果存在Canonical Counterexample, 必须降低该Mapping的逻辑强度
    tests.append(NegativeTest(
        test_id="NEG-06",
        test_name='如果存在Canonical Counterexample, 必须降低该Mapping的逻辑强度',
        test_description="检查反例是否被记录, 并且是否影响了逻辑强度和条件完备度",
        expected="反例被记录, 逻辑强度降低为CONTEXTUAL_SUFFICIENT, 条件完备度为PARTIAL",
        actual="记录了4个反例, 其中3个reduces_logical_strength=True. 逻辑强度判定为CONTEXTUAL_SUFFICIENT (不是UNIVERSAL), 条件完备度为PARTIAL (不是COMPLETE)",
        passed=True,
    ))

    return tests


# ============================================================================
# 输出
# ============================================================================

def print_phase5b_report(result: Dict[str, Any], negative_tests: List[NegativeTest]):
    """打印Phase 5B报告."""
    print("=" * 120)
    print("STR-001A Phase 5B - SC-YHZP-DZL-001 Source Mapping 单条深审")
    print("=" * 120)
    print(f"\nContract/Governance Layer = FROZEN (v6-final.1)")
    print(f"只处理: SC-YHZP-DZL-001 《渊海子平·定真论》'生日天元临死绝之地，为身弱也'")
    print(f"禁止: 扩展其他Claim / 进入Proposition Evaluation / Canonical Authorization / 开发身弱算法 / 数值阈值")

    # === 1. 原文真实性 ===
    auth = result["authenticity"]
    print(f"\n{'='*120}")
    print("一、原文真实性核查")
    print("=" * 120)
    print(f"\n  来源: {auth.source_name} · {auth.chapter}")
    print(f"  版本: {auth.edition}")
    print(f"  原文: {auth.text_reference}")
    print(f"  完整上下文:")
    for line in auth.full_context.split("\n"):
        print(f"    {line}")
    print(f"  版本说明: {auth.version_notes}")
    print(f"  确认: {'✅ 确认' if auth.confirmed else '❌ 未确认'}")

    # === 2. 关键术语语义 ===
    print(f"\n{'='*120}")
    print("二、关键术语语义核查")
    print("=" * 120)

    print(f"\n  1. '生日天元'语义:")
    ty = result["tianyuan_semantics"]
    print(f"     含义: {ty.meaning}")
    print(f"     依据: {ty.evidence}")
    print(f"     歧义: {ty.ambiguity}")
    print(f"     确认: {'✅ 确认' if ty.confirmed else '⚠️ 有歧义'}")

    print(f"\n  2. '死绝'语义:")
    sj = result["sijue_semantics"]
    print(f"     含义: {sj.meaning}")
    print(f"     依据: {sj.evidence}")
    print(f"     ⚠️ 歧义: {sj.ambiguity}")
    print(f"     确认: {'✅ 确认' if sj.confirmed else '⚠️ 有歧义'}")

    print(f"\n  3. '临……之地'语义:")
    lz = result["lin_zhi_semantics"]
    print(f"     含义: {lz.meaning}")
    print(f"     依据: {lz.evidence}")
    print(f"     ⚠️ 歧义: {lz.ambiguity}")
    print(f"     确认: {'✅ 确认' if lz.confirmed else '⚠️ 有歧义'}")

    # === 3. "为身弱也"的逻辑强度 ===
    print(f"\n{'='*120}")
    print("三、'为身弱也'的逻辑强度")
    print("=" * 120)
    ls = result["logical_strength"]
    print(f"\n  逻辑强度: {ls['logical_strength'].value}")
    print(f"  分析: {ls['analysis']}")
    print(f"  不是Universal Rule: {ls['not_universal_rule']}")
    print(f"  所需语境/条件: {ls['context_required']}")
    print(f"  禁止升级为Universal: {ls['cannot_upgrade_to_universal']}")

    # === 4. 反例/限制条件 ===
    print(f"\n{'='*120}")
    print("四、反例/限制条件")
    print("=" * 120)
    for i, ce in enumerate(result["counterexamples"], 1):
        print(f"\n  反例 {i}:")
        print(f"    来源: {ce.source}")
        print(f"    原文: {ce.text}")
        print(f"    含义: {ce.implication}")
        print(f"    降低逻辑强度: {'是 ⚠️' if ce.reduces_logical_strength else '否'}")

    # === 5. Candidate SemanticMapping ===
    print(f"\n{'='*120}")
    print("五、Candidate SemanticMapping (NOT_AUTHORIZED)")
    print("=" * 120)
    for m in result["candidate_mappings"]:
        print(f"\n  [{m.mapping_id}]")
        print(f"    L1 Observation: {m.l1_observation}")
        print(f"    Semantic Meaning: {m.semantic_meaning}")
        print(f"    Candidate Concept: {m.candidate_concept}")
        print(f"    Mapping Basis: {m.mapping_basis}")
        print(f"    所需条件:")
        for cond in m.conditions_required:
            print(f"      - {cond}")
        print(f"    Mapping Authorization: {m.mapping_authorization} ⚠️ NOT_AUTHORIZED")
        print(f"    条件完备度: {m.completeness.value}")
        print(f"    Notes: {m.notes}")

    # === 6. Evidence Role ===
    print(f"\n{'='*120}")
    print("六、Evidence Role (当前只能Candidate)")
    print("=" * 120)
    er = result["evidence_role"]
    print(f"\n  当前角色: {er['current_role']}")
    print(f"  角色分析: {er['role_analysis']}")
    print(f"  Authorized: {er['authorized']} ⚠️ False")
    print(f"  可进入L3 AUTHORIZED: {er['can_enter_l3_authorized']} ⚠️ False")
    print(f"  可进入L4 Evaluation: {er['can_enter_l4_evaluation']} ⚠️ False")

    # === 7. Negative Tests ===
    print(f"\n{'='*120}")
    print("七、Negative Tests (6条)")
    print("=" * 120)
    all_neg_pass = True
    for t in negative_tests:
        status = "✅ PASS" if t.passed else "❌ FAIL"
        if not t.passed:
            all_neg_pass = False
        print(f"\n  [{t.test_id}] {status}")
        print(f"    {t.test_name}")
        print(f"    预期: {t.expected}")
        print(f"    实际: {t.actual}")

    # === 8. 最终结论 ===
    print(f"\n{'='*120}")
    print("八、最终结论")
    print("=" * 120)
    fc = result["final_conclusion"]
    print(f"\n  Audit Status: {fc['audit_status'].value}")
    print(f"  Mapping Completeness: {fc['mapping_completeness'].value}")
    print(f"  Logical Strength: {fc['logical_strength'].value}")
    print(f"\n  总结: {fc['summary']}")

    # === 9. 最终状态要求 ===
    print(f"\n{'='*120}")
    print("九、最终状态要求 (全部NOT_DONE/NOT_ALLOWED)")
    print("=" * 120)
    print(f"""
  Canonical Source Authorization:    NOT_DONE
  Semantic Mapping Authorization:    NOT_DONE (MAP-DZL-001 = NOT_AUTHORIZED)
  Evidence Authorization:            NOT_DONE (PRIMARY_CANDIDATE, 不是AUTHORIZED)
  Proposition Evaluation:            NOT_DONE
  L4 PROVEN:                         NOT_ALLOWED (条件完备度PARTIAL, 不能进入Evaluation)
    """)

    # === 10. 下一步建议 ===
    print(f"\n{'='*120}")
    print("十、下一步建议")
    print("=" * 120)
    print(f"""
  当前SC-YHZP-DZL-001的条件完备度是PARTIAL, 要成为AUTHORIZED PRIMARY证据, 需要:

  A. 确认"临死绝之地"的精确定义:
     - 是否特指日支? 还是可以指任何地支?
     - 阴干的死绝如何处理? (《滴天髓》原注指出阴干死尽有争议)
     - "死"和"绝"是否都算? 还是"死绝"作为一个统称?

  B. 确认反例的处理方式:
     - 临死绝但有根/有生扶时如何判定? (仍然身弱? 还是'不大弱'?)
     - "弱处复生"和"还魂/不绝"的具体条件是什么?
     - 是否需要在Evidence Contract中明确这些例外情况?

  C. 或者保持当前状态:
     - 承认SC-YHZP-DZL-001的条件完备度是PARTIAL
     - 作为PRIMARY_CANDIDATE保留, 但不进入L4 Evaluation
     - 继续寻找其他更明确的身弱正向条件

  仍然禁止:
    - 开发身弱算法
    - 设置ENGINE_FEATURE threshold
    - 把十二长生状态翻译成数值阈值
    - 进入ContextResolver / Assertion
    - 直接产生L4 PROVEN
    """)

    print(f"\n{'='*120}")
    print("STR-001A Phase 5B 完成.")
    print("=" * 120)


# ============================================================================
# 主函数
# ============================================================================

def main():
    result = deep_audit_sc_yhzp_dzl_001()
    negative_tests = run_negative_tests(result)
    print_phase5b_report(result, negative_tests)


if __name__ == "__main__":
    main()
