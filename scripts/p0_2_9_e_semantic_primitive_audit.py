"""
P0-2.9-E Classical Semantic Primitive Audit

基于 74e3b1a 的 🟢 PASS 裁决（特殊 PASS：证明不能假装自己已经拥有综合算法），
改变方向：不要马上继续研究 A AND B AND C，
而是先把五部经典里的核心辨证概念逐个拆出来。

核心原则：
- 原典没有提供完整的现代 Boolean / 数学公式，但提供了大量"辨证原则、观察维度、条件关系、优先级、特殊切换规则"
- 我们的工作是：原典原则 ↓ 拆成可验证的语义组件 ↓ 保留原典授权边界 ↓ 工程化表达 ↓ 验证工程化表达是否忠实
- 不是：经典 → 找公式
- 而是：经典 → 建立可验证的辨证模型
- "有气"目前没有独立 Evidence，是当前最大的缺口
- "势大于数"是最重要的发现，辨证不是 Presence Engine
- 算层完整性（P6-CALC）仍是最高优先级，FROZEN ≠ PROVEN CORRECT

对每个 Primitive 回答 8 个问题：
① 它在原典是什么意思？
② 它依赖哪些 Canonical Facts？
③ 它与哪些 Evidence 不同？
④ 它能否形式化？
⑤ 如果能，形式化到什么程度？
⑥ 哪部分是原典明确？
⑦ 哪部分是工程推导？
⑧ 它是事实、状态、关系、Qualifier 还是判断？

第一阶段：滴天髓 8 个核心旺衰概念
- 得令（DE_LING）
- 得地（DE_DI）
- 有根（YOU_GEN）
- 有气（YOU_QI）— 当前缺失，重点研究
- 党众（DANG_ZHONG）
- 生扶（SHENG_FU）
- 制化（ZHI_HUA）
- 气势（QI_SHI）— 重点研究"势大于数"

数据来源：D:\shuntian\docs\五部经典整理\（本地优先）
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import json


# ============================================================================
# 标准数据结构
# ============================================================================

class PrimitiveType(Enum):
    """Primitive 类型：事实、状态、关系、Qualifier、判断"""
    FACT = "FACT"                    # 事实（算出来的客观结果）
    STATE = "STATE"                  # 状态（基于事实的语义状态）
    RELATION = "RELATION"            # 关系（两个实体之间的关系）
    QUALIFIER = "QUALIFIER"          # Qualifier（对其他状态的限定/修饰）
    JUDGMENT = "JUDGMENT"            # 判断（综合判断结果）


class FormalizationLevel(Enum):
    """形式化程度"""
    FULLY_FORMALIZABLE = "FULLY_FORMALIZABLE"      # 完全可形式化
    PARTIALLY_FORMALIZABLE = "PARTIALLY_FORMALIZABLE"  # 部分可形式化
    PRINCIPLE_ONLY = "PRINCIPLE_ONLY"              # 只有原则，无法精确形式化
    NOT_YET_CLEAR = "NOT_YET_CLEAR"                # 尚不明确


@dataclass(frozen=True)
class ClassicalSemanticPrimitive:
    """
    古典语义原语 — 五部经典中的核心辨证概念

    对每个 Primitive 回答 8 个问题
    """
    primitive_id: str
    name: str                       # 中文名称
    pinyin: str                     # 拼音
    classic: str                    # 主要来源经典
    domain: str                     # 领域（旺衰/格局/调候/气势/生克制化）

    # 8 个问题的回答
    q1_original_meaning: str       # ① 它在原典是什么意思？
    q2_canonical_facts: List[str]  # ② 它依赖哪些 Canonical Facts？
    q3_evidence_difference: str    # ③ 它与哪些 Evidence 不同？
    q4_formalizable: bool           # ④ 它能否形式化？
    q5_formalization_level: FormalizationLevel  # ⑤ 如果能，形式化到什么程度？
    q6_classical_explicit: str     # ⑥ 哪部分是原典明确？
    q7_engineering_derived: str    # ⑦ 哪部分是工程推导？
    q8_primitive_type: PrimitiveType  # ⑧ 它是事实、状态、关系、Qualifier 还是判断？

    # 工程状态
    current_evidence_mapping: str   # 当前工程中的 Evidence 映射（如果有）
    current_implementation_status: str  # 当前实现状态
    gaps: List[str]                 # 当前缺口
    recommendations: List[str]      # 建议

    # 原典引用
    original_texts: List[str]       # 原典原文引用
    local_file: str                  # 本地文件路径

    notes: str = ""


# ============================================================================
# 滴天髓 8 个核心旺衰概念
# ============================================================================

class DitiansuiPrimitives:
    """滴天髓 8 个核心旺衰概念"""

    @staticmethod
    def get_de_ling() -> ClassicalSemanticPrimitive:
        """得令"""
        return ClassicalSemanticPrimitive(
            primitive_id="DTS-PRIM-001",
            name="得令",
            pinyin="de_ling",
            classic="滴天髓",
            domain="旺衰",
            q1_original_meaning=(
                "日主五行与月令五行相同或得到月令生扶，即'得时'。"
                "《滴天髓》：'得时俱为旺论'，但同时强调'虽是至理，亦死法也'。"
                "得令是旺衰判断的首要观察点，但不是唯一决定因素。"
            ),
            q2_canonical_facts=[
                "DayMaster（日主天干）",
                "MonthBranch（月令地支）",
                "MonthBranchHiddenStems（月令藏干）",
                "MonthBranchMainQi（月令本气）",
                "FiveElementRelationship（五行关系：同/生/克）",
                "TwelveGrowthStages（十二长生状态）",
            ],
            q3_evidence_difference=(
                "得令 ≠ 得地（得地是地支有根）"
                "得令 ≠ 有气（有气是更宽泛的力量状态）"
                "得令 ≠ 身强（得令只是旺衰的必要条件之一）"
                "当前工程 SEASONAL_STATE 只表达了 seasonal_alignment（IN_SEASON/NOT_IN_SEASON），"
                "没有区分本气得令、中气得令、余气得令，也没有结合十二长生。"
            ),
            q4_formalizable=True,
            q5_formalization_level=FormalizationLevel.PARTIALLY_FORMALIZABLE,
            q6_classical_explicit=(
                "原典明确：'得时俱为旺论'，得令是旺衰判断的首要观察点。"
                "原典明确：月令是全局提纲，影响力最大。"
            ),
            q7_engineering_derived=(
                "工程推导：将得令简化为 IN_SEASON/NOT_IN_SEASON 的二元状态。"
                "工程推导：没有区分本气得令、中气得令、余气得令的不同权重。"
                "工程推导：没有结合十二长生（临官/帝旺 vs 长生/沐浴）。"
                "工程推导：得令 AND 得地 = required 是工程化的组合规则，原典没有明确给出。"
            ),
            q8_primitive_type=PrimitiveType.STATE,
            current_evidence_mapping="SEASONAL_STATE（seasonal_alignment = IN_SEASON）",
            current_implementation_status="部分实现：只表达了 IN_SEASON/NOT_IN_SEASON 二元状态",
            gaps=[
                "没有区分本气得令、中气得令、余气得令",
                "没有结合十二长生状态",
                "没有表达月令被合/被冲时得令状态的变化",
                "得令的'程度'（强得令 vs 弱得令）没有表达",
            ],
            recommendations=[
                "扩展 SEASONAL_STATE，增加 main_qi / middle_qi / residual_qi 区分",
                "结合十二长生（临官/帝旺 = 强得令，长生/沐浴 = 弱得令）",
                "增加月令被合/被冲时的限定条件",
                "得令应该是 STATE，不是简单的 Boolean Fact",
            ],
            original_texts=[
                "得时俱为旺论，失令便作衰看，虽是至理，亦死法也。",
                "月令是全局提纲统领四季气场影响力最大但绝对不能一锤定音",
            ],
            local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
            notes="得令是当前工程中实现相对完整的概念，但仍有重要缺口。",
        )

    @staticmethod
    def get_you_qi() -> ClassicalSemanticPrimitive:
        """有气 — 当前缺失的独立 Evidence，重点研究"""
        return ClassicalSemanticPrimitive(
            primitive_id="DTS-PRIM-004",
            name="有气",
            pinyin="you_qi",
            classic="滴天髓",
            domain="旺衰",
            q1_original_meaning=(
                "'有气'是滴天髓旺衰判断的核心概念之一，与'得令、得地、有根'并列。"
                "《滴天髓》：'真正的旺是得令得地有根有气是真旺'。"
                "但'有气'的具体含义在原典中没有明确定义，需要从上下文推断："
                "- 可能指天干有同类五行（比劫）透出"
                "- 可能指有印星生扶"
                "- 可能指虽然失令，但有生扶，所以仍有气"
                "- 可能指五行在全局中的'气势'（浓度、方向、连贯性）"
                "'有气'与'得令、得地、有根'不同，它更偏向于全局的力量状态，"
                "而不是某个具体位置的事实。"
            ),
            q2_canonical_facts=[
                "AllStems（全部天干）",
                "AllBranches（全部地支）",
                "AllHiddenStems（全部藏干）",
                "FiveElementCount（五行数量统计）",
                "FiveElementDistribution（五行分布）",
                "StemBranchRelationships（干支关系）",
                "CombinationsAndClashes（合冲关系）",
                "SeasonalState（季节状态）",
                "RootState（根气状态）",
            ],
            q3_evidence_difference=(
                "有气 ≠ 得令（得令是月令关系，有气是全局状态）"
                "有气 ≠ 得地/有根（得地是地支有根，有气更宽泛）"
                "有气 ≠ 印生（印生只是有气的可能来源之一）"
                "有气 ≠ 比劫帮（比劫帮只是有气的可能来源之一）"
                "有气 ≠ 五行数量多（'势大于数'，数量多不等于有气）"
                "当前工程中没有独立的 HAS_QI Evidence，这是最大的缺口。"
            ),
            q4_formalizable=True,
            q5_formalization_level=FormalizationLevel.NOT_YET_CLEAR,
            q6_classical_explicit=(
                "原典明确：'得令得地有根有气是真旺'，有气是真旺的四个条件之一。"
                "原典明确：'势大于数'，有气不等于数量多。"
            ),
            q7_engineering_derived=(
                "工程推导：当前工程完全没有实现'有气'这个概念。"
                "工程推导：如果要实现，可能需要综合五行分布、位置、合冲、方向等多个因素，"
                "但具体的形式化规则原典没有给出，需要深入研究。"
                "工程推导：'有气'可能是一个 QUALIFIER（对得令/得地的限定），"
                "也可能是一个独立的 STATE，需要进一步研究。"
            ),
            q8_primitive_type=PrimitiveType.STATE,
            current_evidence_mapping="❌ 无（当前工程中没有独立的 HAS_QI Evidence）",
            current_implementation_status="未实现：这是当前工程最大的概念缺口",
            gaps=[
                "完全没有实现'有气'这个概念",
                "'有气'的具体含义原典没有明确定义，需要从上下文推断",
                "'有气'与得令、得地、有根的边界不清晰",
                "'有气'的形式化规则尚不明确",
                "'有气'可能需要综合全局信息，不是简单的 presence 判断",
            ],
            recommendations=[
                "优先研究'有气'的原典含义，从滴天髓全文中搜索相关上下文",
                "建立 HAS_QI 的初步定义（可能是：天干有同类/印星透出 + 五行分布有一定集中度）",
                "明确'有气'与得令、得地、有根的边界",
                "'有气'应该是 STATE 或 QUALIFIER，不是简单的 Fact",
                "在'有气'没有明确定义之前，不能把'得令 AND 得地'当成真旺的完整条件",
            ],
            original_texts=[
                "真正的旺是得令得地有根有气是真旺，天干堆叠一堆五行地之无根无气只是虚旺假旺",
                "势大于数哪怕只有一个五行只要占据关键位置掌控全局气势就能制衡全局，五行数量再多杂乱无章互相牵制也成不了气候",
            ],
            local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
            notes=(
                "【重点研究】'有气'是当前工程最大的概念缺口。"
                "原典将'有气'列为真旺的四个条件之一，但当前工程完全没有实现这个概念。"
                "在'有气'没有明确定义之前，DTS-STRENGTH-001 的 required_evidence（得令 AND 得地）"
                "是不完整的，因为原典说的是'得令得地有根有气'四个条件。"
            ),
        )

    @staticmethod
    def get_qi_shi() -> ClassicalSemanticPrimitive:
        """气势 — 重点研究'势大于数'"""
        return ClassicalSemanticPrimitive(
            primitive_id="DTS-PRIM-008",
            name="气势",
            pinyin="qi_shi",
            classic="滴天髓",
            domain="气势",
            q1_original_meaning=(
                "'气势'是滴天髓的核心概念，强调'势大于数'。"
                "《滴天髓》第三十二章重寡：'势大于数哪怕只有一个五行只要占据关键位置掌控全局气势就能制衡全局，"
                "五行数量再多杂乱无章互相牵制也成不了气候'。"
                "气势不是简单的五行数量，而是："
                "- 位置（关键位置 vs 普通位置）"
                "- 集中度（一个五行掌控全局 vs 多个五行互相牵制）"
                "- 方向（五行的生克方向是否一致）"
                "- 连贯性（五行是否形成流通）"
                "气势是比'得令、得地、有根、有气'更高层次的概念，"
                "它关注的是全局的力量结构，而不是某个具体位置的事实。"
            ),
            q2_canonical_facts=[
                "AllStemsAndBranches（全部干支）",
                "FiveElementDistribution（五行分布）",
                "FiveElementConcentration（五行集中度）",
                "KeyPositions（关键位置：月令、日支、时干等）",
                "StemBranchRelationships（干支关系）",
                "CombinationsAndClashes（合冲关系）",
                "GenerationDirection（生克方向）",
                "FlowContinuity（流通连贯性）",
                "SeasonalState（季节状态）",
            ],
            q3_evidence_difference=(
                "气势 ≠ 五行数量多（'势大于数'，数量多不等于气势强）"
                "气势 ≠ 得令（得令只是月令关系，气势是全局结构）"
                "气势 ≠ 有根（有根只是地支关系，气势是全局力量分布）"
                "气势 ≠ 印生+比劫帮（presence 级别的判断，气势需要位置/集中度/方向）"
                "当前工程中没有独立的 QI_SHI Evidence，所有判断都是 presence 级别。"
            ),
            q4_formalizable=True,
            q5_formalization_level=FormalizationLevel.PRINCIPLE_ONLY,
            q6_classical_explicit=(
                "原典明确：'势大于数'，气势比数量更重要。"
                "原典明确：'占据关键位置掌控全局气势就能制衡全局'。"
                "原典明确：'五行数量再多杂乱无章互相牵制也成不了气候'。"
            ),
            q7_engineering_derived=(
                "工程推导：当前工程完全没有实现'气势'这个概念。"
                "工程推导：所有当前判断都是 presence 级别（有没有印、有没有比劫），"
                "没有考虑位置、集中度、方向、连贯性。"
                "工程推导：'气势'的形式化非常复杂，可能需要："
                "  - 关键位置权重（月令 > 日支 > 其他）"
                "  - 五行集中度（一个五行占比多少算'掌控全局'）"
                "  - 生克方向一致性"
                "  - 流通连贯性"
                "但这些具体的形式化规则原典没有给出，需要深入研究。"
            ),
            q8_primitive_type=PrimitiveType.STATE,
            current_evidence_mapping="❌ 无（当前工程中没有独立的 QI_SHI Evidence）",
            current_implementation_status="未实现：当前所有判断都是 presence 级别，没有气势判断",
            gaps=[
                "完全没有实现'气势'这个概念",
                "当前所有判断都是 presence 级别（有没有 X），没有位置/集中度/方向判断",
                "'气势'的形式化规则非常复杂，原典只给了原则",
                "关键位置的权重定义不明确",
                "五行集中度的阈值定义不明确",
                "生克方向一致性和流通连贯性的判断规则不明确",
            ],
            recommendations=[
                "优先研究'气势'的原典含义，从滴天髓全文中搜索相关上下文",
                "建立 QI_SHI 的初步定义框架（位置 + 集中度 + 方向 + 连贯性）",
                "明确'气势'与 presence 级别 Evidence 的关系",
                "'气势'应该是 STATE，是比单个 Evidence 更高层次的综合状态",
                "在'气势'没有初步实现之前，DTS-STRENGTH-001 的判断是不完整的",
                "这是当前工程从'presence engine'升级到真正的'辨证 engine'的关键",
            ],
            original_texts=[
                "势大于数哪怕只有一个五行只要占据关键位置掌控全局气势就能制衡全局，五行数量再多杂乱无章互相牵制也成不了气候",
            ],
            local_file=r"D:\shuntian\docs\五部经典整理\字幕原始\空空道人哲学42344190118\S1-四大古籍\滴天髓.md",
            notes=(
                "【最重要发现】'势大于数'是滴天髓的核心原则，"
                "它明确指出辨证不是简单的 presence 判断（有没有 X），"
                "而是需要考虑位置、集中度、方向、连贯性等全局因素。"
                "当前工程完全没有实现'气势'，所有判断都是 presence 级别，"
                "这是当前工程最大的架构性缺口。"
                "实现'气势'是从'presence engine'升级到真正的'辨证 engine'的关键。"
            ),
        )

    @classmethod
    def get_all(cls) -> List[ClassicalSemanticPrimitive]:
        return [
            cls.get_de_ling(),
            cls.get_you_qi(),      # 重点研究
            cls.get_qi_shi(),       # 重点研究
        ]


# ============================================================================
# 输出 Primitive 审计报告
# ============================================================================

def print_primitive_report(primitives: List[ClassicalSemanticPrimitive]):
    print("=" * 80)
    print("P0-2.9-E Classical Semantic Primitive Audit — 报告")
    print("=" * 80)

    print("\n【核心原则】")
    print("  1. 原典没有提供完整的现代 Boolean / 数学公式，但提供了大量'辨证原则、观察维度、条件关系、优先级、特殊切换规则'")
    print("  2. 我们的工作是：原典原则 ↓ 拆成可验证的语义组件 ↓ 保留原典授权边界 ↓ 工程化表达 ↓ 验证工程化表达是否忠实")
    print("  3. 不是：经典 → 找公式；而是：经典 → 建立可验证的辨证模型")
    print("  4. '有气'目前没有独立 Evidence，是当前最大的缺口")
    print("  5. '势大于数'是最重要的发现，辨证不是 Presence Engine")
    print("  6. 算层完整性（P6-CALC）仍是最高优先级，FROZEN ≠ PROVEN CORRECT")

    print(f"\n【审计范围】第一阶段：滴天髓核心旺衰概念，共 {len(primitives)} 个 Primitive")
    print("  （注：本报告重点展示 3 个关键概念：得令、有气、气势；完整 8 个概念待后续补充）")

    # 按实现状态分类
    implemented = [p for p in primitives if "部分实现" in p.current_implementation_status or "已实现" in p.current_implementation_status]
    not_implemented = [p for p in primitives if "未实现" in p.current_implementation_status]

    print(f"\n【实现状态统计】")
    print(f"  已实现/部分实现: {len(implemented)}")
    print(f"  未实现: {len(not_implemented)}")

    # 逐个输出
    print("\n" + "=" * 80)
    print("【Primitive 详细审计】")
    print("=" * 80)

    for p in primitives:
        print(f"\n{'='*60}")
        print(f"  {p.primitive_id}: {p.name}（{p.pinyin}）")
        print(f"  经典: {p.classic} | 领域: {p.domain}")
        print(f"  类型: {p.q8_primitive_type.value}")
        print(f"  形式化程度: {p.q5_formalization_level.value}")
        print(f"  当前实现: {p.current_implementation_status}")
        print(f"{'='*60}")

        print(f"\n  ① 原典含义: {p.q1_original_meaning[:120]}...")
        print(f"\n  ② 依赖 Canonical Facts:")
        for f in p.q2_canonical_facts:
            print(f"     - {f}")
        print(f"\n  ③ 与 Evidence 的区别: {p.q3_evidence_difference[:120]}...")
        print(f"\n  ④ 能否形式化: {p.q4_formalizable}")
        print(f"  ⑤ 形式化程度: {p.q5_formalization_level.value}")
        print(f"\n  ⑥ 原典明确部分: {p.q6_classical_explicit[:100]}...")
        print(f"\n  ⑦ 工程推导部分: {p.q7_engineering_derived[:120]}...")
        print(f"\n  ⑧ Primitive 类型: {p.q8_primitive_type.value}")

        print(f"\n  当前 Evidence 映射: {p.current_evidence_mapping}")

        print(f"\n  缺口:")
        for g in p.gaps:
            print(f"    ❌ {g}")

        print(f"\n  建议:")
        for r in p.recommendations:
            print(f"    ✅ {r}")

        print(f"\n  原典引用:")
        for t in p.original_texts:
            print(f"    「{t[:80]}...」")

        if p.notes:
            print(f"\n  备注: {p.notes[:120]}...")

    # 核心发现
    print("\n" + "=" * 80)
    print("【核心发现】")
    print("=" * 80)

    print("""
  1. 【最大缺口】'有气'完全没有实现
     - 原典将'有气'列为真旺的四个条件之一（得令得地有根有气）
     - 当前工程只有 SEASONAL_STATE（得令）和 ROOT_PRESENT（得地/有根）
     - '有气'没有独立 Evidence，这意味着 DTS-STRENGTH-001 的 required_evidence 是不完整的
     - '有气'的具体含义原典没有明确定义，需要深入研究

  2. 【最重要发现】'气势'完全没有实现，辨证不是 Presence Engine
     - 滴天髓明确说'势大于数'，一个关键位置的五行比多个普通位置的五行更重要
     - 当前工程所有判断都是 presence 级别（有没有印、有没有比劫、有没有官杀）
     - 没有考虑位置、集中度、方向、连贯性等全局因素
     - 实现'气势'是从'presence engine'升级到真正的'辨证 engine'的关键

  3. 得令的实现相对完整，但仍有重要缺口
     - 当前只表达了 IN_SEASON/NOT_IN_SEASON 二元状态
     - 没有区分本气得令、中气得令、余气得令
     - 没有结合十二长生状态
     - 得令应该是 STATE，不是简单的 Boolean Fact

  4. 原典概念 → Evidence 的映射是当前最关键的工程任务
     - 在 Primitive 没有明确定义之前，继续写 AND/OR 组合规则是没有意义的
     - 必须先把'有气'、'气势'等核心概念拆清楚，才能建立正确的 Evidence
     - 然后才能谈 Evidence 之间的组合逻辑

  5. 算层完整性（P6-CALC）仍是最高优先级
     - FROZEN ≠ PROVEN CORRECT
     - 辨证施工不能被理解为算层已经证明正确
     - 二者可以并行，但辨不能反过来修改算
""")

    # 下一步
    print("\n" + "=" * 80)
    print("【下一步建议】")
    print("=" * 80)

    print("""
  P0-2.9-E 第一阶段已完成 3 个关键概念的深度审计（得令、有气、气势）。

  下一步 P0-2.9-E 第二阶段：
  1. 补充剩余 5 个概念的审计：得地、有根、党众、生扶、制化
  2. 优先深入研究'有气'的原典含义，从滴天髓全文中搜索相关上下文
  3. 建立'有气'的初步定义和 Evidence 映射
  4. 建立'气势'的初步定义框架（位置 + 集中度 + 方向 + 连贯性）
  5. 明确每个 Primitive 是 Fact / State / Relation / Qualifier / Judgment
  6. 在 Primitive 没有明确定义之前，不继续扩展 Combination Rule

  优先级：
  1. 【最高】'有气'概念研究和 Evidence 实现（当前最大缺口）
  2. 【最高】'气势'概念研究和初步框架（当前最重要的架构性缺口）
  3. 【高】补充剩余 5 个概念的审计
  4. 【中】得令概念的扩展（本气/中气/余气、十二长生）
  5. 【低】Combination Rule 的扩展（在 Primitive 没有明确定义之前不做）
""")


if __name__ == "__main__":
    primitives = DitiansuiPrimitives.get_all()
    print_primitive_report(primitives)
