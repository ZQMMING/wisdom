"""
P0-2.9-E Phase 2: Deep Definition of Three Core Ditiansui Primitives

基于 9b7a241 的 🟢 PASS 裁决（"发现问题"的 PASS），
深入定义《滴天髓》的三个核心 Primitive：
  得令 → 有气 → 气势

核心原则：
- 不要继续研究 A+B+C
- 先把三个 Primitive 彻底定义清楚
- 有气 ≠ 有根（禁止画等号）
- 气势 ≠ 五行数量（禁止量化）
- 气势 ≠ strength_score（禁止评分）
- 得令 + 有根 ≠ 身强（禁止直接结论）
- 气势应该首先是结构状态，不是数字
- 算层完整性（P6-CALC）仍是最高优先级，FROZEN ≠ PROVEN CORRECT

三个 Primitive 的核心问题：
1. 得令 ↓ Canonical Facts 是什么？
2. 有气 ↓ 与得令、有根到底是什么关系？
3. 气势 ↓ 哪些结构性事实构成"势"？↓ "势大于数"工程上如何表达？↓ 是否可以结构化，而不量化？

数据来源：D:\shuntian\docs\五部经典整理\（本地优先，已读取滴天髓全文）
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import json


# ============================================================================
# 标准数据结构
# ============================================================================

class PrimitiveLayer(Enum):
    """Primitive 层级"""
    FACT = "FACT"                    # 事实层（算出来的客观结果）
    RELATION = "RELATION"            # 关系层（实体之间的关系）
    STATE = "STATE"                  # 状态层（基于事实和关系的语义状态）
    STRUCTURE = "STRUCTURE"          # 结构层（多个状态形成的结构）
    QUALIFIER = "QUALIFIER"          # 限定层（对其他状态的限定）
    JUDGMENT = "JUDGMENT"            # 判断层（综合判断结果）


class CanonicalFact:
    """Canonical Fact 定义"""
    def __init__(self, fact_id: str, name: str, description: str, source: str, deterministic: bool = True):
        self.fact_id = fact_id
        self.name = name
        self.description = description
        self.source = source
        self.deterministic = deterministic


@dataclass(frozen=True)
class PrimitiveRelation:
    """Primitive 之间的关系"""
    source_primitive: str
    target_primitive: str
    relation_type: str               # SUBSET / SUPERSET / OVERLAP / INDEPENDENT / DERIVED
    description: str
    classical_basis: str
    engineering_mapping: str
    is_proven: bool                  # 原典是否明确支持这个关系


@dataclass(frozen=True)
class StructuralComponent:
    """气势的结构性组成部分"""
    component_id: str
    name: str
    description: str
    canonical_facts: List[str]
    formalization_level: str         # EXACT / STRUCTURED / PARTIAL / QUALITATIVE
    classical_basis: str
    engineering_notes: str


@dataclass(frozen=True)
class PrimitiveDeepDefinition:
    """Primitive 深度定义"""
    primitive_id: str
    name: str
    pinyin: str
    classic: str
    layer: PrimitiveLayer

    # 核心定义
    core_definition: str             # 这个 Primitive 到底是什么
    classical_meaning: str           # 原典中的含义
    canonical_facts: List[CanonicalFact]  # 依赖的 Canonical Facts
    relations_to_other_primitives: List[PrimitiveRelation]  # 与其他 Primitive 的关系

    # 工程化
    formalization_level: str         # EXACT / STRUCTURED / PARTIAL / QUALITATIVE / NOT_YET
    engineering_mapping: str         # 当前工程中的映射（如果有）
    engineering_gaps: List[str]      # 工程缺口
    engineering_recommendations: List[str]  # 工程建议

    # 原典依据
    original_texts: List[str]
    local_file: str

    # 禁区
    forbidden_mappings: List[str]    # 禁止的映射（如 有气=有根）

    notes: str = ""


# ============================================================================
# 得令（DE_LING）深度定义
# ============================================================================

def define_de_ling() -> PrimitiveDeepDefinition:
    """得令深度定义"""

    canonical_facts = [
        CanonicalFact("F-DM", "日主天干", "八字中的日柱天干，代表命主自身", "bazi_engine.day_master", True),
        CanonicalFact("F-MB", "月令地支", "八字中的月柱地支，代表出生月份的地支", "bazi_engine.month_branch", True),
        CanonicalFact("F-MB-HIDDEN", "月令藏干", "月令地支中藏的天干（本气/中气/余气）", "bazi_engine.month_branch_hidden_stems", True),
        CanonicalFact("F-MB-MAIN-QI", "月令本气", "月令藏干中的本气（占比最大的五行）", "bazi_engine.month_branch_main_qi", True),
        CanonicalFact("F-WX-REL", "五行关系", "日主五行与月令五行的关系（同/生/克）", "relations.wuxing_relation", True),
        CanonicalFact("F-TGS", "十二长生", "日主在月令的十二长生状态（长生/沐浴/临官/帝旺等）", "bazi_engine.twelve_growth_stages", True),
        CanonicalFact("F-SEASON", "四季", "月令所属的季节（春/夏/秋/冬）", "calendar.season", True),
    ]

    relations = [
        PrimitiveRelation(
            source_primitive="DE_LING",
            target_primitive="YOU_GEN",
            relation_type="INDEPENDENT",
            description="得令与有根是独立的概念。得令是日主与月令的关系，有根是日主与地支藏干的关系。两者可以同时成立，也可以只有一个成立。",
            classical_basis="原文将'得令'和'得地有根'并列为真旺的不同条件，说明它们是独立的观察维度。",
            engineering_mapping="当前工程中 SEASONAL_STATE 和 ROOT_PRESENT 是独立的 Evidence，这个映射是正确的。",
            is_proven=True,
        ),
        PrimitiveRelation(
            source_primitive="DE_LING",
            target_primitive="YOU_QI",
            relation_type="OVERLAP",
            description="得令与有气有重叠但不等同。得令可能是有气的来源之一，但有气还可能来自其他来源（生扶、同党、流通等）。",
            classical_basis="原文将'得令'和'有气'并列为真旺的条件，说明它们相关但不等同。",
            engineering_mapping="当前工程中没有独立的 YOU_QI Evidence，需要建立。得令应该是有气的可能来源之一，但不是唯一来源。",
            is_proven=False,  # 原典没有明确说明两者的精确关系
        ),
    ]

    return PrimitiveDeepDefinition(
        primitive_id="PRIM-DE-LING",
        name="得令",
        pinyin="de_ling",
        classic="滴天髓",
        layer=PrimitiveLayer.STATE,
        core_definition=(
            "得令是日主五行与月令五行之间的关系状态。"
            "当日主五行与月令本气五行相同，或得到月令五行生扶时，称为得令。"
            "得令是旺衰判断的首要观察点，但不是唯一决定因素。"
            "得令应该是一个结构化的 STATE，包含：本气得令/中气得令/余气得令、十二长生状态、季节状态等维度，"
            "而不是简单的 IN_SEASON/NOT_IN_SEASON 二元判断。"
        ),
        classical_meaning=(
            "《滴天髓》：'得时俱为旺论，失令便作衰看，虽是至理，亦死法也。'"
            "'月令是全局提纲统领四季气场影响力最大但绝对不能一锤定音'。"
            "得令在原典中是旺衰的首要观察维度，但原典明确反对机械判断，强调需要综合其他条件。"
        ),
        canonical_facts=canonical_facts,
        relations_to_other_primitives=relations,
        formalization_level="STRUCTURED",  # 可以结构化，但当前实现只是二元
        engineering_mapping=(
            "当前工程：SEASONAL_STATE（seasonal_alignment = IN_SEASON / NOT_IN_SEASON）"
            "这个映射过于简化，只表达了二元状态，没有区分本气/中气/余气得令，也没有结合十二长生。"
        ),
        engineering_gaps=[
            "没有区分本气得令、中气得令、余气得令",
            "没有结合十二长生状态（临官/帝旺 = 强得令，长生/沐浴 = 弱得令）",
            "没有表达月令被合/被冲时得令状态的变化",
            "得令的'程度'（强得令 vs 弱得令）没有表达",
            "得令应该是 STATE，不是简单的 Boolean Fact",
        ],
        engineering_recommendations=[
            "扩展 SEASONAL_STATE，增加 main_qi / middle_qi / residual_qi 区分",
            "结合十二长生（临官/帝旺 = 强得令，长生/沐浴 = 弱得令）",
            "增加月令被合/被冲时的限定条件",
            "将得令从 Boolean Fact 升级为结构化 STATE",
            "得令是有气的可能来源之一，但不是唯一来源",
        ],
        original_texts=[
            "得时俱为旺论，失令便作衰看，虽是至理，亦死法也。须察支中党众，干上生扶，方可定其真衰真旺。",
            "月令是全局提纲统领四季气场影响力最大但绝对不能一锤定音不要学死板的唯月令论",
        ],
        local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
        forbidden_mappings=[
            "得令 = 身强（禁止：得令只是旺衰的必要条件之一，不是充分条件）",
            "得令 = 有气（禁止：得令可能是有气的来源之一，但有气还可能来自其他来源）",
            "得令 AND 有根 = 身强（禁止：原典说的是'得令得地有根有气'四个条件，不是两个）",
        ],
        notes=(
            "得令是当前工程中实现相对完整的概念，但仍有重要缺口。"
            "得令应该是结构化的 STATE，包含多个维度，而不是简单的二元判断。"
            "得令与有气的关系是 OVERLAP（有重叠但不等同），这个关系原典没有明确说明，需要进一步研究。"
        ),
    )


# ============================================================================
# 有气（YOU_QI）深度定义
# ============================================================================

def define_you_qi() -> PrimitiveDeepDefinition:
    """有气深度定义 — 当前最大的缺口，重点研究"""

    canonical_facts = [
        CanonicalFact("F-ALL-STEMS", "全部天干", "八字中的四个天干（年干/月干/日干/时干）", "bazi_engine.all_stems", True),
        CanonicalFact("F-ALL-BRANCHES", "全部地支", "八字中的四个地支（年支/月支/日支/时支）", "bazi_engine.all_branches", True),
        CanonicalFact("F-ALL-HIDDEN", "全部藏干", "四个地支中藏的所有天干", "bazi_engine.all_hidden_stems", True),
        CanonicalFact("F-WX-COUNT", "五行数量统计", "全局中每个五行的出现次数（天干+地支+藏干）", "calculation.five_element_count", True),
        CanonicalFact("F-WX-DIST", "五行分布", "五行在天干/地支/藏干中的分布情况", "calculation.five_element_distribution", True),
        CanonicalFact("F-STEM-REL", "天干关系", "天干之间的生克关系", "relations.stem_relations", True),
        CanonicalFact("F-COMB-CLASH", "合冲关系", "干支之间的合、冲、刑、害关系", "relations.combinations_and_clashes", True),
        CanonicalFact("F-SEASONAL", "季节状态", "日主与月令的关系（得令/失令）", "state.seasonal_state", True),
        CanonicalFact("F-ROOT", "根气状态", "日主在地支藏干中的根气情况", "state.root_state", True),
        CanonicalFact("F-FLOW", "流通状态", "五行之间的生克流通情况", "state.flow_continuity", False),  # 尚未实现
    ]

    relations = [
        PrimitiveRelation(
            source_primitive="YOU_QI",
            target_primitive="DE_LING",
            relation_type="OVERLAP",
            description="有气与得令有重叠但不等同。得令可能是有气的来源之一，但有气还可能来自生扶、同党、流通等其他来源。",
            classical_basis="原文将'得令'和'有气'并列为真旺的条件，说明它们相关但不等同。",
            engineering_mapping="当前工程中没有独立的 YOU_QI Evidence。得令应该是有气的可能来源之一，但不是唯一来源。",
            is_proven=False,
        ),
        PrimitiveRelation(
            source_primitive="YOU_QI",
            target_primitive="YOU_GEN",
            relation_type="OVERLAP",
            description="有气与有根有重叠但不等同。有根可能是有气的来源之一（根气是气的依托），但有气还可能来自得令、生扶、同党等其他来源。有根 ⊂ 有气 是一个可能的关系，但需要原典证明。",
            classical_basis="原文将'有根'和'有气'并列为真旺的条件，说明它们相关但不等同。'根'强调依托，'气'可能涉及更广泛的力量状态。",
            engineering_mapping="当前工程中 ROOT_PRESENT 已经实现，但没有独立的 YOU_QI Evidence。需要明确两者的边界：有根是地支藏干关系，有气是更广泛的力量状态。",
            is_proven=False,  # 原典没有明确说明两者的精确关系
        ),
        PrimitiveRelation(
            source_primitive="YOU_QI",
            target_primitive="QI_SHI",
            relation_type="SUPERSET",
            description="有气可能是气势的基础组成部分之一。气势是更高层次的结构状态，有气只是其中一个维度。但这个关系需要进一步研究。",
            classical_basis="原文中'有气'和'气势'都与'气'相关，但'气势'更强调全局的力量结构（势大于数）。",
            engineering_mapping="当前工程中两者都没有实现。需要先定义有气，再定义气势，最后明确两者的关系。",
            is_proven=False,
        ),
    ]

    return PrimitiveDeepDefinition(
        primitive_id="PRIM-YOU-QI",
        name="有气",
        pinyin="you_qi",
        classic="滴天髓",
        layer=PrimitiveLayer.STATE,
        core_definition=(
            "有气是日主在全局中的力量状态，是一个比'得令'、'有根'更广泛的概念。"
            "有气可能包括（但不限于）以下来源："
            "  1. 得令：日主与月令五行相同或得月令生扶"
            "  2. 有根：日主在地支藏干中有同五行的根"
            "  3. 生扶：天干有印星生扶日主"
            "  4. 同党：天干或地支有比劫帮身"
            "  5. 流通：五行之间形成连续的生克流通，日主处于流通的有利位置"
            "  6. 时势：日主在当前大运/流年中得到生扶（但这属于运的层面，可能不属于原局有气）"
            "有气不是简单的'有没有'，而是一个结构化的状态，需要考虑气的来源、强度、位置、连贯性等。"
            "有气与得令、有根的关系是 OVERLAP（有重叠但不等同），这个关系原典没有明确说明，需要进一步研究。"
        ),
        classical_meaning=(
            "《滴天髓》：'真正的旺是得令得地有根有气是真旺，天干堆叠一堆五行地之无根无气只是虚旺假旺'。"
            "原典将'有气'列为真旺的四个条件之一，但没有明确定义'有气'的具体含义。"
            "从上下文推断，'有气'与'无根无气'相对，强调的是日主有实际的力量支撑，而不是虚浮的天干堆叠。"
            "'有气'可能涉及得令、有根、生扶、同党、流通等多个维度，是一个综合性的力量状态。"
        ),
        canonical_facts=canonical_facts,
        relations_to_other_primitives=relations,
        formalization_level="PARTIAL",  # 部分可形式化，但核心定义尚不明确
        engineering_mapping=(
            "当前工程：❌ 无（没有独立的 YOU_QI Evidence）"
            "这是当前工程最大的概念缺口。原典将'有气'列为真旺的四个条件之一，但当前工程完全没有实现这个概念。"
        ),
        engineering_gaps=[
            "完全没有实现'有气'这个概念",
            "'有气'的具体含义原典没有明确定义，需要从上下文推断",
            "'有气'与得令、有根的精确关系不明确（OVERLAP? SUBSET? SUPERSET?）",
            "'有气'的形式化规则尚不明确",
            "'有气'可能需要综合全局信息，不是简单的 presence 判断",
            "'有气'的来源（得令/有根/生扶/同党/流通）各自的权重和组合规则不明确",
            "在'有气'没有明确定义之前，DTS-STRENGTH-001 的 required_evidence 是不完整的",
        ],
        engineering_recommendations=[
            "【最高优先级】优先研究'有气'的原典含义，从滴天髓全文中搜索'气'相关上下文",
            "建立'有气'的初步定义框架：来源（得令/有根/生扶/同党/流通）+ 强度 + 位置 + 连贯性",
            "明确'有气'与得令、有根的边界：得令是月令关系，有根是藏干关系，有气是更广泛的力量状态",
            "建立 YOU_QI 的初步 Evidence 映射，但明确标注为 PARTIAL / NEEDS_RESEARCH",
            "在'有气'没有明确定义之前，不继续扩展 Combination Rule",
            "有气应该是 STATE，不是简单的 Fact，也不是 Boolean",
        ],
        original_texts=[
            "真正的旺是得令得地有根有气是真旺，天干堆叠一堆五行地之无根无气只是虚旺假旺",
        ],
        local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
        forbidden_mappings=[
            "有气 = 有根（禁止：有根可能是有气的来源之一，但有气还可能来自其他来源，两者不等同）",
            "有气 = 得令（禁止：得令可能是有气的来源之一，但有气还可能来自其他来源，两者不等同）",
            "有气 = 五行数量多（禁止：'势大于数'，数量多不等于有气）",
            "有气 = strength_score（禁止：有气应该是结构化状态，不是数字评分）",
            "有根 → 有气（禁止：这个推导关系原典没有明确支持，需要进一步研究）",
        ],
        notes=(
            "【最大缺口】'有气'是当前工程最大的概念缺口。"
            "原典将'有气'列为真旺的四个条件之一（得令得地有根有气），但当前工程完全没有实现这个概念。"
            "'有气'的具体含义原典没有明确定义，需要从上下文推断。"
            "'有气'与得令、有根的关系是 OVERLAP（有重叠但不等同），这个关系原典没有明确说明。"
            "在'有气'没有明确定义之前，DTS-STRENGTH-001 的 required_evidence（得令 AND 得地）是不完整的，"
            "因为原典说的是'得令得地有根有气'四个条件。"
            "优先研究'有气'是当前最重要的工程任务。"
        ),
    )


# ============================================================================
# 气势（QI_SHI）深度定义
# ============================================================================

def define_qi_shi() -> PrimitiveDeepDefinition:
    """气势深度定义 — 最重要的架构性缺口，重点研究'势大于数'"""

    canonical_facts = [
        CanonicalFact("F-ALL-GANZHI", "全部干支", "八字中的四个天干和四个地支", "bazi_engine.all_ganzhi", True),
        CanonicalFact("F-WX-DIST", "五行分布", "五行在天干/地支/藏干中的分布情况", "calculation.five_element_distribution", True),
        CanonicalFact("F-WX-CONC", "五行集中度", "某个五行在全局中的占比和集中程度", "calculation.five_element_concentration", False),  # 尚未实现
        CanonicalFact("F-KEY-POS", "关键位置", "月令、日支、时干等关键位置的五行", "state.key_positions", False),
        CanonicalFact("F-STEM-REL", "天干关系", "天干之间的生克关系", "relations.stem_relations", True),
        CanonicalFact("F-BRANCH-REL", "地支关系", "地支之间的合冲刑害关系", "relations.branch_relations", True),
        CanonicalFact("F-COMB-CLASH", "合冲关系", "干支之间的合、冲、刑、害关系", "relations.combinations_and_clashes", True),
        CanonicalFact("F-GEN-DIR", "生克方向", "五行生克的方向是否一致", "state.generation_direction", False),
        CanonicalFact("F-FLOW", "流通连贯性", "五行之间的生克流通是否连贯", "state.flow_continuity", False),
        CanonicalFact("F-SEASONAL", "季节状态", "日主与月令的关系", "state.seasonal_state", True),
        CanonicalFact("F-ROOT", "根气状态", "日主在地支藏干中的根气情况", "state.root_state", True),
    ]

    # 气势的结构性组成部分
    structural_components = [
        StructuralComponent(
            component_id="SC-POSITION",
            name="位置",
            description="五行所处的位置（月令/日支/时干/年干等），关键位置的五行比普通位置的五行更有影响力。",
            canonical_facts=["F-KEY-POS", "F-ALL-GANZHI"],
            formalization_level="STRUCTURED",
            classical_basis="原文：'占据关键位置掌控全局气势就能制衡全局'。",
            engineering_notes="当前工程没有实现关键位置权重。需要定义哪些位置是'关键位置'，以及不同位置的权重。",
        ),
        StructuralComponent(
            component_id="SC-CONCENTRATION",
            name="集中度",
            description="某个五行在全局中的集中程度。一个五行高度集中（掌控全局）比多个五行分散（互相牵制）更有气势。",
            canonical_facts=["F-WX-CONC", "F-WX-DIST"],
            formalization_level="PARTIAL",
            classical_basis="原文：'五行数量再多杂乱无章互相牵制也成不了气候'。",
            engineering_notes="集中度的阈值定义不明确。什么算'掌控全局'？什么算'互相牵制'？需要进一步研究。",
        ),
        StructuralComponent(
            component_id="SC-DIRECTION",
            name="方向",
            description="五行生克的方向是否一致。如果五行之间的生克方向形成一致的流向（如连续相生），则气势更强；如果方向混乱（互相克战），则气势减弱。",
            canonical_facts=["F-GEN-DIR", "F-STEM-REL", "F-BRANCH-REL"],
            formalization_level="QUALITATIVE",
            classical_basis="原文没有直接讨论'方向'，但'势'的概念隐含了方向一致性。",
            engineering_notes="方向是最难形式化的部分。需要定义什么是'方向一致'，什么是'方向混乱'。",
        ),
        StructuralComponent(
            component_id="SC-CONTINUITY",
            name="连贯性",
            description="五行之间的生克流通是否连贯。如果五行形成连续的流通（如木→火→土→金→水），则气势更强；如果流通中断，则气势减弱。",
            canonical_facts=["F-FLOW", "F-COMB-CLASH"],
            formalization_level="QUALITATIVE",
            classical_basis="滴天髓有'流通'的概念，但'气势'中的连贯性需要进一步研究。",
            engineering_notes="连贯性的判断规则不明确。什么算'流通连贯'？什么算'流通中断'？需要进一步研究。",
        ),
        StructuralComponent(
            component_id="SC-TRANSFORMATION",
            name="转化",
            description="合冲刑害等关系对五行气势的转化作用。合局、冲局等会改变五行的气势结构。",
            canonical_facts=["F-COMB-CLASH"],
            formalization_level="PARTIAL",
            classical_basis="三命通会和滴天髓都讨论了合冲刑害对五行力量的影响。",
            engineering_notes="合冲刑害的具体转化规则需要进一步研究和实现。",
        ),
    ]

    relations = [
        PrimitiveRelation(
            source_primitive="QI_SHI",
            target_primitive="YOU_QI",
            relation_type="SUPERSET",
            description="气势是比有气更高层次的结构状态。有气只是气势的一个组成部分（日主是否有力量支撑），气势还包括位置、集中度、方向、连贯性等更广泛的全局结构。",
            classical_basis="原文中'有气'是真旺的条件之一，而'气势'（势大于数）是更高层次的判断原则。",
            engineering_mapping="当前工程中两者都没有实现。需要先定义有气，再定义气势，最后明确两者的关系。",
            is_proven=False,
        ),
        PrimitiveRelation(
            source_primitive="QI_SHI",
            target_primitive="DE_LING",
            relation_type="INDEPENDENT",
            description="气势与得令是独立的概念。得令是日主与月令的关系，气势是全局的力量结构。一个命局可以得令但气势散乱，也可以失令但气势集中。",
            classical_basis="原文'势大于数'明确指出气势比数量（包括得令这种单一维度）更重要。",
            engineering_mapping="当前工程中 SEASONAL_STATE 已实现，但 QI_SHI 未实现。两者应该是独立的 STATE。",
            is_proven=True,
        ),
    ]

    return PrimitiveDeepDefinition(
        primitive_id="PRIM-QI-SHI",
        name="气势",
        pinyin="qi_shi",
        classic="滴天髓",
        layer=PrimitiveLayer.STRUCTURE,  # 气势是结构层，比普通 State 更高
        core_definition=(
            "气势是全局五行力量的结构性状态，是比'得令'、'有根'、'有气'更高层次的概念。"
            "气势的核心原则是'势大于数'：一个关键位置的五行、或一个高度集中的五行，"
            "比多个普通位置的、分散的五行更有影响力。"
            "气势不是简单的五行数量，而是由多个结构性维度组成："
            "  1. 位置：五行所处的位置（月令/日支/时干等），关键位置的五行更有影响力"
            "  2. 集中度：某个五行在全局中的集中程度，高度集中比分散更有气势"
            "  3. 方向：五行生克的方向是否一致，一致的流向比混乱的克战更有气势"
            "  4. 连贯性：五行之间的生克流通是否连贯，连续流通比中断更有气势"
            "  5. 转化：合冲刑害等关系对五行气势的转化作用"
            "气势应该首先是结构状态，不是数字。禁止用 score 表达气势。"
            "气势的形式化非常复杂，原典只给了原则（势大于数），没有给出具体的判断规则。"
        ),
        classical_meaning=(
            "《滴天髓》第三十二章重寡：'势大于数哪怕只有一个五行只要占据关键位置掌控全局气势就能制衡全局，"
            "五行数量再多杂乱无章互相牵制也成不了气候'。"
            "气势在原典中是一个核心原则，明确反对简单的数量计数判断。"
            "气势强调的是全局的力量结构（位置、集中度、方向、连贯性），而不是单一维度的数量。"
        ),
        canonical_facts=canonical_facts,
        relations_to_other_primitives=relations,
        formalization_level="QUALITATIVE",  # 只能定性描述，难以精确形式化
        engineering_mapping=(
            "当前工程：❌ 无（没有独立的 QI_SHI Evidence / State）"
            "当前所有判断都是 presence 级别（有没有印、有没有比劫、有没有官杀），"
            "没有考虑位置、集中度、方向、连贯性等全局结构因素。"
            "这是当前工程最重要的架构性缺口。"
        ),
        engineering_gaps=[
            "完全没有实现'气势'这个概念",
            "当前所有判断都是 presence 级别，没有位置/集中度/方向/连贯性判断",
            "'势大于数'的具体形式化规则原典没有给出，需要深入研究",
            "关键位置的权重定义不明确（哪些位置算'关键位置'？权重多少？）",
            "五行集中度的阈值定义不明确（什么算'掌控全局'？什么算'互相牵制'？）",
            "生克方向一致性的判断规则不明确",
            "流通连贯性的判断规则不明确",
            "合冲刑害对气势的转化规则不明确",
            "气势是 STRUCTURE 层，比普通 State 更高，需要特殊的工程实现",
        ],
        engineering_recommendations=[
            "【最高优先级】建立'气势'的初步定义框架：位置 + 集中度 + 方向 + 连贯性 + 转化",
            "先实现最简单的部分：关键位置识别（月令/日支/时干）",
            "再实现五行集中度的初步计算（某个五行的占比）",
            "方向和连贯性是最难的部分，可以先标记为 QUALITATIVE / NOT_YET",
            "气势应该是 STRUCTURE 层的 State，不是简单的 Evidence，也不是 Boolean",
            "气势的表达应该是结构化的（如：{position: STRONG, concentration: HIGH, direction: UNCLEAR, continuity: UNCLEAR}），不是数字",
            "在气势没有初步实现之前，DTS-STRENGTH-001 的判断是不完整的，因为它只考虑了 presence，没有考虑气势",
            "实现气势是从'presence engine'升级到真正的'辨证 engine'的关键",
        ],
        original_texts=[
            "势大于数哪怕只有一个五行只要占据关键位置掌控全局气势就能制衡全局，五行数量再多杂乱无章互相牵制也成不了气候",
        ],
        local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
        forbidden_mappings=[
            "气势 = 五行数量（禁止：'势大于数'明确反对数量判断）",
            "气势 = strength_score（禁止：气势应该是结构状态，不是数字评分）",
            "气势 = 得令 + 有根 + 印 + 比劫（禁止：这只是 presence 级别的简单相加，不是气势）",
            "气势 = 有气（禁止：有气只是气势的一个组成部分，气势是更高层次的结构状态）",
            "气势 = qi_shi_score = 位置×权重 + 集中度×权重 + ...（禁止：这会重新掉回评分模型）",
        ],
        notes=(
            "【最重要的架构性缺口】'气势'是当前工程最重要的架构性缺口。"
            "滴天髓明确说'势大于数'，但当前工程所有判断都是 presence 级别，没有考虑气势。"
            "气势是 STRUCTURE 层的概念，比普通 State 更高，需要特殊的工程实现。"
            "气势的形式化非常复杂，原典只给了原则，没有给出具体的判断规则。"
            "实现气势是从'presence engine'升级到真正的'辨证 engine'的关键。"
            "气势应该首先是结构状态，不是数字。绝对禁止用 score 表达气势。"
        ),
    )


# ============================================================================
# 输出深度定义报告
# ============================================================================

def print_deep_definition_report(primitives: List[PrimitiveDeepDefinition]):
    print("=" * 80)
    print("P0-2.9-E Phase 2: Deep Definition of Three Core Ditiansui Primitives")
    print("=" * 80)

    print("\n【核心原则】")
    print("  1. 不要继续研究 A+B+C，先把三个 Primitive 彻底定义清楚")
    print("  2. 有气 ≠ 有根（禁止画等号）")
    print("  3. 气势 ≠ 五行数量（禁止量化）")
    print("  4. 气势 ≠ strength_score（禁止评分）")
    print("  5. 得令 + 有根 ≠ 身强（禁止直接结论）")
    print("  6. 气势应该首先是结构状态，不是数字")
    print("  7. 算层完整性（P6-CALC）仍是最高优先级，FROZEN ≠ PROVEN CORRECT")

    print(f"\n【审计范围】滴天髓三个核心 Primitive：得令 → 有气 → 气势")

    # 逐个输出
    for p in primitives:
        print(f"\n{'='*70}")
        print(f"  {p.primitive_id}: {p.name}（{p.pinyin}）")
        print(f"  层级: {p.layer.value} | 形式化程度: {p.formalization_level}")
        print(f"{'='*70}")

        print(f"\n  【核心定义】")
        print(f"    {p.core_definition[:200]}...")

        print(f"\n  【原典含义】")
        print(f"    {p.classical_meaning[:150]}...")

        print(f"\n  【依赖 Canonical Facts】({len(p.canonical_facts)} 个)")
        for f in p.canonical_facts:
            status = "✅" if f.deterministic else "❌"
            print(f"    {status} {f.fact_id}: {f.name} — {f.description[:60]}")

        print(f"\n  【与其他 Primitive 的关系】")
        for r in p.relations_to_other_primitives:
            proven = "✅ 原典支持" if r.is_proven else "⚠️ 需进一步研究"
            print(f"    {r.source_primitive} ↔ {r.target_primitive}: {r.relation_type} ({proven})")
            print(f"      {r.description[:80]}...")

        print(f"\n  【当前工程映射】")
        print(f"    {p.engineering_mapping[:120]}...")

        print(f"\n  【工程缺口】({len(p.engineering_gaps)} 个)")
        for g in p.engineering_gaps:
            print(f"    ❌ {g}")

        print(f"\n  【工程建议】({len(p.engineering_recommendations)} 个)")
        for r in p.engineering_recommendations:
            print(f"    ✅ {r}")

        print(f"\n  【禁止映射】({len(p.forbidden_mappings)} 个)")
        for f in p.forbidden_mappings:
            print(f"    🚫 {f}")

        if p.notes:
            print(f"\n  【备注】")
            print(f"    {p.notes[:150]}...")

    # 三个 Primitive 的关系总结
    print("\n" + "=" * 80)
    print("【三个 Primitive 的关系总结】")
    print("=" * 80)

    print("""
  得令（DE_LING）
    │
    ├── 层级: STATE
    ├── 形式化程度: STRUCTURED（可结构化，但当前实现只是二元）
    ├── 与有气: OVERLAP（有重叠但不等同，得令可能是有气的来源之一）
    ├── 与气势: INDEPENDENT（独立概念，气势比得令更高层次）
    └── 当前状态: 部分实现，需要扩展

  有气（YOU_QI）⚠️ 最大缺口
    │
    ├── 层级: STATE
    ├── 形式化程度: PARTIAL（部分可形式化，核心定义尚不明确）
    ├── 与得令: OVERLAP（有重叠但不等同）
    ├── 与有根: OVERLAP（有重叠但不等同，有根可能是有气的来源之一）
    ├── 与气势: SUPERSET（有气可能是气势的基础组成部分之一）
    └── 当前状态: ❌ 完全未实现，是当前最大的概念缺口

  气势（QI_SHI）⚠️ 最重要的架构性缺口
    │
    ├── 层级: STRUCTURE（比普通 State 更高）
    ├── 形式化程度: QUALITATIVE（只能定性描述，难以精确形式化）
    ├── 组成部分: 位置 + 集中度 + 方向 + 连贯性 + 转化
    ├── 与得令: INDEPENDENT（独立概念）
    ├── 与有气: SUPERSET（气势是比有气更高层次的结构状态）
    └── 当前状态: ❌ 完全未实现，是当前最重要的架构性缺口

  核心关系:
    得令 ≠ 有气 ≠ 气势（三者不等同）
    得令 ⊂ 有气?（可能，得令可能是有气的来源之一，但需原典证明）
    有根 ⊂ 有气?（可能，有根可能是有气的来源之一，但需原典证明）
    有气 ⊂ 气势?（可能，有气可能是气势的基础组成部分，但需原典证明）
""")

    # 工程禁区总结
    print("\n" + "=" * 80)
    print("【工程禁区总结】")
    print("=" * 80)

    print("""
  🚫 有气 = 有根（禁止：两者不等同）
  🚫 有气 = 得令（禁止：两者不等同）
  🚫 有气 = 五行数量多（禁止：势大于数）
  🚫 有气 = strength_score（禁止：有气应该是结构化状态）
  🚫 有根 → 有气（禁止：这个推导关系原典没有明确支持）

  🚫 气势 = 五行数量（禁止：势大于数明确反对数量判断）
  🚫 气势 = strength_score（禁止：气势应该是结构状态，不是数字）
  🚫 气势 = 得令 + 有根 + 印 + 比劫（禁止：这只是 presence 级别简单相加）
  🚫 气势 = 有气（禁止：有气只是气势的一个组成部分）
  🚫 气势 = qi_shi_score = 位置×权重 + 集中度×权重 + ...（禁止：重新掉回评分模型）

  🚫 得令 = 身强（禁止：得令只是旺衰的必要条件之一）
  🚫 得令 AND 有根 = 身强（禁止：原典说的是四个条件，不是两个）
  🚫 五部经典各算一个 strength → 投票（禁止：互补不比较）
  🚫 断言结果 → 反推气势（禁止：解不能反推算）
""")

    # 下一步
    print("\n" + "=" * 80)
    print("【下一步建议】")
    print("=" * 80)

    print("""
  P0-2.9-E Phase 2 已完成三个核心 Primitive 的深度定义。

  下一步 P0-2.9-E Phase 3:
  1. 【最高优先级】深入研究'有气'的原典含义
     - 从滴天髓全文中搜索'气'相关上下文
     - 建立'有气'的初步定义和 Evidence 映射
     - 明确'有气'与得令、有根的精确关系

  2. 【最高优先级】建立'气势'的初步定义框架
     - 先实现最简单的部分：关键位置识别
     - 再实现五行集中度的初步计算
     - 方向和连贯性标记为 QUALITATIVE / NOT_YET
     - 气势的表达应该是结构化的，不是数字

  3. 【高优先级】补充剩余 Primitive 的审计
     - 得地、有根、党众、生扶、制化

  4. 【中优先级】得令概念的扩展
     - 本气/中气/余气得令的区分
     - 结合十二长生状态

  5. 【低优先级】Combination Rule 的扩展
     - 在 Primitive 没有明确定义之前，不继续扩展 Combination Rule

  6. 算层完整性（P6-CALC）继续并行推进
     - FROZEN ≠ PROVEN CORRECT
""")


if __name__ == "__main__":
    primitives = [
        define_de_ling(),
        define_you_qi(),      # 最大缺口
        define_qi_shi(),       # 最重要的架构性缺口
    ]
    print_deep_definition_report(primitives)
