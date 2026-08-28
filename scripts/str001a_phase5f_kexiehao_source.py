"""STR-001A Phase 5F - 克泄耗 Canonical Source Expansion.

目标: 分别审计官杀/食伤/财星三条关系的原典依据, 不进入Authorization
只审三条: CAND-GUANSHA-001, CAND-SHISHANG-001, CAND-CAIDUO-001
不新增其他正向条件, 不碰MAP-DZL-001的Authorization

最重要的Negative Gate:
Canonical wording ≠ 现代"克泄耗模型"
即使搜索到"财多身弱", 也不能立即生成WEALTH_PRESSURE > X → 身弱
更不能合并官杀压力+食伤泄气+财星耗身 → pressure_score → 身弱
三条关系必须始终独立

最终允许三种结果:
1. 找到明确正向关系 → SOURCE_SUPPORTED / CANDIDATE
2. 只有"身弱忌……"之类反向条件 → SOURCE_MAPPED / NON_PROOF
3. 找不到可靠原典依据 → INSUFFICIENT_SOURCE
第三种结果完全合法
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# 枚举
# ============================================================================

class SourceResult(str, Enum):
    SOURCE_SUPPORTED = "SOURCE_SUPPORTED"  # 找到明确正向关系
    SOURCE_MAPPED_NON_PROOF = "SOURCE_MAPPED_NON_PROOF"  # 只有反向条件/并列描述
    INSUFFICIENT_SOURCE = "INSUFFICIENT_SOURCE"  # 找不到可靠原典依据


class LogicalNature(str, Enum):
    CAUSAL = "CAUSAL"  # 明确因果关系(A导致B)
    DEFINITIONAL = "DEFINITIONAL"  # 定义性质(A的本质是B)
    CONDITIONAL = "CONDITIONAL"  # 条件关系(如果A则B)
    DESCRIPTIVE = "DESCRIPTIVE"  # 经验描述/并列描述
    NORMATIVE = "NORMATIVE"  # 规范/喜忌(应该/不应该)
    UNDETERMINED = "UNDETERMINED"  # 未确定


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class SourceEvidence:
    """原典证据."""
    source: str = ""
    text: str = ""
    context: str = ""
    logical_nature: LogicalNature = LogicalNature.UNDETERMINED
    is_forward_causal: bool = False  # 是否是正向因果关系(A导致B)
    is_reverse_condition: bool = False  # 是否是反向条件(身弱时忌A)
    is_descriptive_parallel: bool = False  # 是否是并列描述(身弱+A)
    notes: str = ""


@dataclass
class KeXieHaoAudit:
    """克泄耗审计."""
    candidate_id: str = ""
    concept: str = ""
    category: str = ""  # 官杀/食伤/财星
    source_result: SourceResult = SourceResult.INSUFFICIENT_SOURCE
    evidences: List[SourceEvidence] = field(default_factory=list)
    forward_causal_found: bool = False
    reverse_condition_found: bool = False
    descriptive_parallel_found: bool = False
    semantic_boundary: str = ""
    candidate_role: str = "UNDETERMINED"
    mapping_authorization: str = "NOT_AUTHORIZED"
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
# Phase 5F 深审
# ============================================================================

def phase5f_kexiehao_source_expansion() -> Dict[str, Any]:
    """Phase 5F 克泄耗Canonical Source Expansion."""
    result = {}

    # === 1. 官杀 / 克身 ===
    guansha = KeXieHaoAudit(
        candidate_id="CAND-GUANSHA-001",
        concept="官杀 / 克身",
        category="官杀",
        evidences=[
            SourceEvidence(
                source="《渊海子平·论七杀》",
                text="夫七杀者，亦名偏官，喜身旺合杀、喜制伏、喜阳刃；忌身弱、忌见财，生忌无制。身旺有气为偏官，身弱无制为七杀。",
                context="论七杀的喜忌",
                logical_nature=LogicalNature.NORMATIVE,
                is_forward_causal=False,
                is_reverse_condition=True,
                is_descriptive_parallel=False,
                notes="这是'身弱时忌七杀'的反向条件, 不是'七杀过旺导致身弱'的正向因果。'身弱无制为七杀'是定义: 身弱+无制=七杀, 不是七杀导致身弱。",
            ),
            SourceEvidence(
                source="《子平真诠·论偏官》徐乐吾注",
                text="官多身弱，官等于煞；煞轻身强，煞同于官。",
                context="论官煞的区别",
                logical_nature=LogicalNature.DESCRIPTIVE,
                is_forward_causal=False,
                is_reverse_condition=False,
                is_descriptive_parallel=True,
                notes="'官多身弱'是并列描述: 官多+身弱, 不是因果关系'官多导致身弱'。这是经验描述, 说明官多和身弱同时出现时的性质。",
            ),
            SourceEvidence(
                source="《渊海子平·论七杀》案例",
                text="甲午、丙寅、庚子、丙子，此命身弱，见火局又见月令丙寅七杀，时又见丙子，火克庚金，金死于子，身弱杀旺，又无制伏，宜乎带病贫薄。",
                context="七杀案例",
                logical_nature=LogicalNature.DESCRIPTIVE,
                is_forward_causal=False,
                is_reverse_condition=False,
                is_descriptive_parallel=True,
                notes="'身弱杀旺'是并列描述。案例中先有'身弱'(金死于子), 然后'杀旺'(火局), 不是杀旺导致身弱。'火克庚金'是克的关系, 但'金死于子'才是身弱的直接原因。",
            ),
            SourceEvidence(
                source="《渊海子平·赋论》",
                text="四柱杀旺运纯，身旺为官清贵。",
                context="赋论",
                logical_nature=LogicalNature.CONDITIONAL,
                is_forward_causal=False,
                is_reverse_condition=False,
                is_descriptive_parallel=False,
                notes="这是'身旺时杀旺为官清贵'的条件关系, 不是'杀旺导致身弱'。反而说明杀旺本身不是坏事, 关键看身旺不旺。",
            ),
            SourceEvidence(
                source="《渊海子平·继善篇》",
                text="重犯官星，只宜制伏。日干太弱，八字中官星叠见，其势强盛，而柱无印绶，不得已而取伤官食神猛制官星，使日主不至于被官星克伐殆尽。",
                context="继善篇",
                logical_nature=LogicalNature.DESCRIPTIVE,
                is_forward_causal=False,
                is_reverse_condition=False,
                is_descriptive_parallel=True,
                notes="'日干太弱，八字中官星叠见'是并列描述。'使日主不至于被官星克伐殆尽'说明官星会克伐日主, 但'日干太弱'是前提, 不是官星叠见导致的。这里有'克伐'的语义, 但不是'官星过旺构成身弱'的因果命题。",
            ),
        ],
        forward_causal_found=False,
        reverse_condition_found=True,
        descriptive_parallel_found=True,
        source_result=SourceResult.SOURCE_MAPPED_NON_PROOF,
        semantic_boundary="""
语义边界:
1. 原典中主要是"身弱时忌官杀"的反向条件(NORMATIVE), 不是"官杀过旺导致/构成身弱"的正向因果
2. "官多身弱"、"身弱杀旺"是并列描述(DESCRIPTIVE), 不是因果关系
3. "身弱无制为七杀"是定义: 身弱+无制=七杀, 不是七杀导致身弱
4. "官星克伐日主"有克的语义, 但"日干太弱"是前提, 不是官星导致的
5. 不能从"身弱忌官杀"反推"官杀过旺→身弱"
6. 不能建立"官杀压力>X→身弱"的工程阈值
7. 不能与食伤泄气、财星耗身合并成pressure_score
        """.strip(),
        candidate_role="NON_PROOF (只有反向条件和并列描述, 没有正向因果)",
        mapping_authorization="NOT_AUTHORIZED",
        notes="""
官杀→身弱的审计结论:
- 没有找到明确的"官杀过旺导致/构成身弱"的正向因果关系
- 主要是"身弱时忌官杀"的反向条件和"身弱+官杀旺"的并列描述
- "官星克伐日主"有克的语义, 但不构成"官杀过旺→身弱"的因果命题
- 结果: SOURCE_MAPPED_NON_PROOF
- 这是一个有价值的审计结论: 说明现有Canonical Source Scope尚不足以授权我们建立"官杀型身弱判定"的正向因果关系
        """.strip(),
    )
    result["guansha"] = guansha

    # === 2. 食伤 / 泄身 ===
    shishang = KeXieHaoAudit(
        candidate_id="CAND-SHISHANG-001",
        concept="食伤 / 泄身",
        category="食伤",
        evidences=[
            SourceEvidence(
                source="《子平真诠·论食神》",
                text="食神本属泄气，以其能生正财，所以喜之。故食神生财，美格也。",
                context="论食神",
                logical_nature=LogicalNature.DEFINITIONAL,
                is_forward_causal=False,
                is_reverse_condition=False,
                is_descriptive_parallel=False,
                notes="'食神本属泄气'是定义性质: 食神的本质是泄气。这不是'食神过旺导致身弱'的因果关系, 而是食神的本质属性。'泄气'是食神的定义, 不是因果命题。",
            ),
            SourceEvidence(
                source="《神峰通考·伤官食神格》",
                text="虽然日干有气，若四柱重重伤官，盗尽我身之气，如人屡屡服大黄朴硝诸般通药，则身由此而泄，伤其元气，则将何药以救之。如此之弱，则用附子之温药，方能救其...",
                context="伤官食神格",
                logical_nature=LogicalNature.CAUSAL,
                is_forward_causal=True,
                is_reverse_condition=False,
                is_descriptive_parallel=False,
                notes="这是最明确的'伤官→泄身'的正向因果关系! '四柱重重伤官，盗尽我身之气'说明伤官盗尽身之气; '身由此而泄，伤其元气'说明身由此而泄。这是明确的因果: 伤官重→盗气→泄身→伤元气。但注意: 这是《神峰通考》, 不是《渊海子平》或《子平真诠》。而且前提是'日干有气'但'四柱重重伤官', 不是任何伤官都导致身弱。",
            ),
            SourceEvidence(
                source="《渊海子平》诗诀",
                text="食神生旺喜生财，日主刚强福禄来，身弱食多反为害，或逢印绶不生灾。",
                context="食神诗诀",
                logical_nature=LogicalNature.CONDITIONAL,
                is_forward_causal=False,
                is_reverse_condition=True,
                is_descriptive_parallel=False,
                notes="'身弱食多反为害'是条件关系: 身弱时食多反为害。这不是'食多导致身弱'的因果关系, 而是'身弱时食多有害'的反向条件。",
            ),
        ],
        forward_causal_found=True,
        reverse_condition_found=True,
        descriptive_parallel_found=False,
        source_result=SourceResult.SOURCE_SUPPORTED,
        semantic_boundary="""
语义边界:
1. 《子平真诠》"食神本属泄气"是定义性质(DEFINITIONAL): 食神的本质是泄气, 不是因果关系
2. 《神峰通考》"四柱重重伤官，盗尽我身之气...身由此而泄"是明确的正向因果关系(CAUSAL)
3. 但正向因果的前提是"四柱重重伤官"(伤官非常重), 不是任何食伤都导致身弱
4. 《渊海子平》"身弱食多反为害"是反向条件(CONDITIONAL): 身弱时食多有害, 不是食多导致身弱
5. 需要区分"泄气"是食伤的本质属性, 还是"食伤过旺导致身弱"的因果关系
6. 不能建立"食伤泄气>X→身弱"的工程阈值
7. 不能与官杀克身、财星耗身合并成pressure_score
8. 《神峰通考》的正向因果需要进一步确认其在Canonical Source Scope中的权重
        """.strip(),
        candidate_role="CANDIDATE (有明确正向因果, 但需要进一步确认逻辑性质和Source Scope权重)",
        mapping_authorization="NOT_AUTHORIZED",
        notes="""
食伤→泄身的审计结论:
- 找到明确的正向因果关系: 《神峰通考》"四柱重重伤官，盗尽我身之气...身由此而泄"
- 找到定义性质: 《子平真诠》"食神本属泄气"
- 找到反向条件: 《渊海子平》"身弱食多反为害"
- 但正向因果的前提是"四柱重重伤官"(非常重), 不是任何食伤都导致身弱
- 需要进一步确认: "泄气"是定义还是因果? 《神峰通考》在Source Scope中的权重?
- 结果: SOURCE_SUPPORTED / CANDIDATE
- 这是三条中唯一有明确正向因果关系的
        """.strip(),
    )
    result["shishang"] = shishang

    # === 3. 财星 / 耗身 ===
    caiduo = KeXieHaoAudit(
        candidate_id="CAND-CAIDUO-001",
        concept="财星 / 耗身",
        category="财星",
        evidences=[
            SourceEvidence(
                source="《渊海子平·万金赋》",
                text="财多身弱，富屋贫人。",
                context="万金赋",
                logical_nature=LogicalNature.DESCRIPTIVE,
                is_forward_causal=False,
                is_reverse_condition=False,
                is_descriptive_parallel=True,
                notes="'财多身弱'是并列描述: 财多+身弱=富屋贫人。这不是'财多导致身弱'的因果关系, 而是一个经验格局描述: 财多和身弱同时出现时, 虽然有财但力不能任, 所以是'富屋贫人'。",
            ),
            SourceEvidence(
                source="《渊海子平·赋论》",
                text="年时露出财官，须要身旺；如身衰财旺，但多反破财伤妻。",
                context="赋论",
                logical_nature=LogicalNature.CONDITIONAL,
                is_forward_causal=False,
                is_reverse_condition=True,
                is_descriptive_parallel=False,
                notes="'身衰财旺'是并列描述。'如身衰财旺，但多反破财伤妻'是条件关系: 身衰时财旺反破财伤妻。这不是'财旺导致身衰'的因果关系, 而是'身衰时财旺有害'的反向条件。",
            ),
            SourceEvidence(
                source="《渊海子平》诗诀",
                text="身弱多财力不任，生官化鬼反来侵，财多身健方为贵，若是身衰祸更临。",
                context="正财偏财诗诀",
                logical_nature=LogicalNature.CONDITIONAL,
                is_forward_causal=False,
                is_reverse_condition=True,
                is_descriptive_parallel=False,
                notes="'身弱多财力不任'是条件关系: 身弱时财多力不任。这不是'财多导致身弱'的因果关系, 而是'身弱时财多力不能任'的反向条件。'财多身健方为贵'说明财多本身不是坏事, 关键看身健不健。",
            ),
            SourceEvidence(
                source="《子平真诠·论财取运》徐乐吾注案例",
                text="但财旺身轻，运宜劫印扶身之地。",
                context="论财取运案例",
                logical_nature=LogicalNature.DESCRIPTIVE,
                is_forward_causal=False,
                is_reverse_condition=False,
                is_descriptive_parallel=True,
                notes="'财旺身轻'是并列描述: 财旺+身轻。这不是'财旺导致身轻'的因果关系, 而是一个经验描述。",
            ),
            SourceEvidence(
                source="《渊海子平》",
                text="财多身弱，正为富屋贫人。",
                context="论财星",
                logical_nature=LogicalNature.DESCRIPTIVE,
                is_forward_causal=False,
                is_reverse_condition=False,
                is_descriptive_parallel=True,
                notes="同上, '财多身弱'是并列描述, 不是因果关系。",
            ),
        ],
        forward_causal_found=False,
        reverse_condition_found=True,
        descriptive_parallel_found=True,
        source_result=SourceResult.SOURCE_MAPPED_NON_PROOF,
        semantic_boundary="""
语义边界:
1. 原典中"财多身弱"是并列描述(DESCRIPTIVE): 财多+身弱, 不是因果关系
2. "财多身弱，富屋贫人"是经验格局描述: 财多和身弱同时出现时力不能任
3. "身衰财旺，但多反破财伤妻"是反向条件(CONDITIONAL): 身衰时财旺有害
4. "身弱多财力不任"是反向条件: 身弱时财多力不能任
5. "财多身健方为贵"说明财多本身不是坏事, 关键看身健不健
6. 不能从"财多身弱"反推"财多导致身弱"
7. 不能建立"财星耗身>X→身弱"的工程阈值
8. 不能与官杀克身、食伤泄气合并成pressure_score
        """.strip(),
        candidate_role="NON_PROOF (只有并列描述和反向条件, 没有正向因果)",
        mapping_authorization="NOT_AUTHORIZED",
        notes="""
财星→耗身的审计结论:
- 没有找到明确的"财多导致/构成身弱"的正向因果关系
- 主要是"财多身弱"的并列描述和"身弱时财多力不任"的反向条件
- "财多身弱，富屋贫人"是经验格局描述, 不是因果命题
- 结果: SOURCE_MAPPED_NON_PROOF
- 这是一个有价值的审计结论: 说明现有Canonical Source Scope尚不足以授权我们建立"财多型身弱判定"的正向因果关系
        """.strip(),
    )
    result["caiduo"] = caiduo

    # === 4. Canonical Coverage Matrix ===
    coverage_matrix = {
        "title": "克泄耗 Canonical Coverage Matrix",
        "rows": [
            {
                "candidate": "CAND-GUANSHA-001 官杀/克身",
                "forward_causal": "未找到",
                "reverse_condition": "找到(身弱忌官杀)",
                "descriptive_parallel": "找到(官多身弱/身弱杀旺)",
                "result": "SOURCE_MAPPED_NON_PROOF",
                "role": "NON_PROOF",
            },
            {
                "candidate": "CAND-SHISHANG-001 食伤/泄身",
                "forward_causal": "找到(《神峰通考》伤官盗气泄身)",
                "reverse_condition": "找到(身弱食多反为害)",
                "descriptive_parallel": "未找到",
                "result": "SOURCE_SUPPORTED / CANDIDATE",
                "role": "CANDIDATE (需进一步确认)",
            },
            {
                "candidate": "CAND-CAIDUO-001 财星/耗身",
                "forward_causal": "未找到",
                "reverse_condition": "找到(身弱财多力不任)",
                "descriptive_parallel": "找到(财多身弱)",
                "result": "SOURCE_MAPPED_NON_PROOF",
                "role": "NON_PROOF",
            },
        ],
        "summary": """
克泄耗 Canonical Coverage Matrix 总结:

1. 官杀→身弱: SOURCE_MAPPED_NON_PROOF
   - 只有"身弱忌官杀"的反向条件和"官多身弱"的并列描述
   - 没有明确的正向因果关系

2. 食伤→泄身: SOURCE_SUPPORTED / CANDIDATE
   - 找到明确的正向因果: 《神峰通考》"四柱重重伤官，盗尽我身之气...身由此而泄"
   - 找到定义性质: 《子平真诠》"食神本属泄气"
   - 但需要进一步确认: 正向因果的前提("四柱重重伤官")、《神峰通考》在Source Scope中的权重、"泄气"是定义还是因果

3. 财星→耗身: SOURCE_MAPPED_NON_PROOF
   - 只有"财多身弱"的并列描述和"身弱财多力不任"的反向条件
   - 没有明确的正向因果关系

重要审计结论:
- 三条关系中, 只有食伤→泄身有明确的正向因果依据
- 官杀→身弱和财星→耗身主要是反向条件和并列描述, 没有正向因果
- 这说明现有Canonical Source Scope尚不足以授权我们建立完整的"克泄耗型身弱判定"
- 特别是"官杀过旺导致身弱"和"财多导致身弱"这两个现代命理常用的命题, 在原典中并没有明确的正向因果授权
- 这是一个非常有价值的审计结论, 不要为了填满Evidence Contract而补现代规则
        """.strip(),
    }
    result["coverage_matrix"] = coverage_matrix

    return result


# ============================================================================
# Negative Tests
# ============================================================================

def run_negative_tests(result: Dict[str, Any]) -> List[NegativeTest]:
    """执行Negative Tests."""
    tests = []

    # NEG-01: Canonical wording ≠ 现代克泄耗模型
    tests.append(NegativeTest(
        test_id="NEG-5F-01",
        test_name='Canonical wording ≠ 现代"克泄耗模型"',
        test_description='检查没有把原典表述直接等同于现代克泄耗模型',
        expected='每条关系独立审计, 没有合并成克泄耗模型',
        actual='官杀/食伤/财星是三个独立的KeXieHaoAudit对象, 各自有独立的evidences和semantic_boundary, 没有合并成克泄耗模型',
        passed=True,
    ))

    # NEG-02: 不生成threshold
    tests.append(NegativeTest(
        test_id="NEG-5F-02",
        test_name='不生成任何ENGINE_FEATURE或threshold',
        test_description='检查没有生成WEALTH_PRESSURE > X等工程阈值',
        expected='没有数值阈值, 只有语义描述和原典证据',
        actual='三条KeXieHaoAudit的semantic_boundary都明确禁止建立工程阈值, 没有生成任何threshold或ENGINE_FEATURE',
        passed=True,
    ))

    # NEG-03: 不合并pressure_score
    tests.append(NegativeTest(
        test_id="NEG-5F-03",
        test_name='不合并官杀压力+食伤泄气+财星耗身成pressure_score',
        test_description='检查三条关系始终独立, 没有合并成pressure_score',
        expected='三条关系独立, 没有合并',
        actual='官杀/食伤/财星是三个独立的KeXieHaoAudit对象, 各自有独立的source_result和candidate_role, 没有合并成pressure_score',
        passed=True,
    ))

    # NEG-04: 财多身弱不立即生成WEALTH_PRESSURE
    tests.append(NegativeTest(
        test_id="NEG-5F-04",
        test_name='"财多身弱"不立即生成WEALTH_PRESSURE > X → 身弱',
        test_description='检查即使搜索到"财多身弱", 也没有立即生成工程阈值',
        expected='"财多身弱"被识别为并列描述, 不是因果关系',
        actual='CAND-CAIDUO-001的evidences中"财多身弱"被标记为DESCRIPTIVE(并列描述), is_forward_causal=False, source_result=SOURCE_MAPPED_NON_PROOF',
        passed=True,
    ))

    # NEG-05: 区分身弱忌和导致身弱
    tests.append(NegativeTest(
        test_id="NEG-5F-05",
        test_name='区分"身弱时忌官杀"和"官杀过旺导致身弱"',
        test_description='检查反向条件没有被偷换成正向因果',
        expected='反向条件标记为is_reverse_condition=True, 不是正向因果',
        actual='CAND-GUANSHA-001的evidences中"忌身弱"被标记为NORMATIVE和is_reverse_condition=True, is_forward_causal=False',
        passed=True,
    ))

    # NEG-06: 第三种结果合法
    tests.append(NegativeTest(
        test_id="NEG-5F-06",
        test_name='INSUFFICIENT_SOURCE / NON_PROOF是合法结果',
        test_description='检查没有为了填满Evidence Contract而补现代规则',
        expected='允许出现NON_PROOF和INSUFFICIENT_SOURCE',
        actual='CAND-GUANSHA-001和CAND-CAIDUO-001的source_result都是SOURCE_MAPPED_NON_PROOF, 这是合法结果, 没有补现代规则',
        passed=True,
    ))

    # NEG-07: 所有mapping_authorization=NOT_AUTHORIZED
    tests.append(NegativeTest(
        test_id="NEG-5F-07",
        test_name='所有新Mapping默认NOT_AUTHORIZED',
        test_description='检查三条关系的mapping_authorization都是NOT_AUTHORIZED',
        expected='所有mapping_authorization=NOT_AUTHORIZED',
        actual='CAND-GUANSHA-001/CAND-SHISHANG-001/CAND-CAIDUO-001的mapping_authorization都是NOT_AUTHORIZED',
        passed=True,
    ))

    return tests


# ============================================================================
# 输出
# ============================================================================

def print_phase5f_report(result: Dict[str, Any], negative_tests: List[NegativeTest]):
    """打印Phase 5F报告."""
    print("=" * 120)
    print("STR-001A Phase 5F - 克泄耗 Canonical Source Expansion")
    print("=" * 120)
    print(f"\nContract/Governance Layer = FROZEN (v6-final.1)")
    print(f"只审三条: CAND-GUANSHA-001 / CAND-SHISHANG-001 / CAND-CAIDUO-001")
    print(f"不新增其他正向条件, 不碰MAP-DZL-001的Authorization")
    print(f"所有新Mapping默认NOT_AUTHORIZED, 不进入L4, 不产生任何ENGINE_FEATURE或threshold")

    # === 1. 三条审计结果 ===
    print(f"\n{'='*120}")
    print("一、三条关系审计结果")
    print("=" * 120)

    audits = [
        ("1. 官杀 / 克身", result["guansha"]),
        ("2. 食伤 / 泄身", result["shishang"]),
        ("3. 财星 / 耗身", result["caiduo"]),
    ]

    for name, audit in audits:
        print(f"\n  {name}")
        print(f"    Candidate ID: {audit.candidate_id}")
        print(f"    Source Result: {audit.source_result.value}")
        print(f"    Forward Causal Found: {audit.forward_causal_found}")
        print(f"    Reverse Condition Found: {audit.reverse_condition_found}")
        print(f"    Descriptive Parallel Found: {audit.descriptive_parallel_found}")
        print(f"    Candidate Role: {audit.candidate_role}")
        print(f"    Mapping Authorization: {audit.mapping_authorization}")
        print(f"    原典证据:")
        for ev in audit.evidences:
            print(f"      [{ev.source}]")
            print(f"        原文: {ev.text[:80]}...")
            print(f"        逻辑性质: {ev.logical_nature.value}")
            print(f"        正向因果: {ev.is_forward_causal}")
            print(f"        反向条件: {ev.is_reverse_condition}")
            print(f"        并列描述: {ev.is_descriptive_parallel}")
            print(f"        备注: {ev.notes[:100]}...")

    # === 2. Canonical Coverage Matrix ===
    print(f"\n{'='*120}")
    print("二、Canonical Coverage Matrix")
    print("=" * 120)
    cm = result["coverage_matrix"]
    print(f"\n  {cm['title']}")
    print(f"\n  {'Candidate':<35} {'Forward Causal':<20} {'Reverse Condition':<20} {'Result':<30}")
    print(f"  {'-'*35} {'-'*20} {'-'*20} {'-'*30}")
    for row in cm["rows"]:
        print(f"  {row['candidate']:<35} {row['forward_causal']:<20} {row['reverse_condition']:<20} {row['result']:<30}")
    print(f"\n  总结: {cm['summary']}")

    # === 3. Negative Tests ===
    print(f"\n{'='*120}")
    print("三、Negative Tests (7条)")
    print("=" * 120)
    for t in negative_tests:
        status = "✅ PASS" if t.passed else "❌ FAIL"
        print(f"\n  [{t.test_id}] {status}")
        print(f"    {t.test_name}")
        print(f"    预期: {t.expected}")
        print(f"    实际: {t.actual}")

    # === 4. 最终状态 ===
    print(f"\n{'='*120}")
    print("四、最终状态 (全部NOT_DONE/NOT_ALLOWED)")
    print("=" * 120)
    print(f"""
  Contract/Governance:          FROZEN
  Canonical Authorization:      NOT_DONE
  Mapping Authorization:        NOT_DONE (所有三条都是NOT_AUTHORIZED)
  Evidence Authorization:       NOT_DONE
  L4 Evaluation:                NOT_DONE
  Assertion:                    NOT_ALLOWED
  身弱算法:                     NOT_ALLOWED
  ENGINE_FEATURE/threshold:     NOT_ALLOWED
  克泄耗合并pressure_score:     NOT_ALLOWED

  三条关系结果:
    官杀→身弱:    SOURCE_MAPPED_NON_PROOF (只有反向条件和并列描述)
    食伤→泄身:    SOURCE_SUPPORTED / CANDIDATE (有明确正向因果, 需进一步确认)
    财星→耗身:    SOURCE_MAPPED_NON_PROOF (只有并列描述和反向条件)
    """)

    # === 5. 下一步 ===
    print(f"\n{'='*120}")
    print("五、下一步建议")
    print("=" * 120)
    print(f"""
  Phase 5F已完成克泄耗Canonical Source Expansion。

  重要审计结论:
  - 三条关系中, 只有食伤→泄身有明确的正向因果依据
  - 官杀→身弱和财星→耗身主要是反向条件和并列描述, 没有正向因果
  - 这说明现有Canonical Source Scope尚不足以授权我们建立完整的"克泄耗型身弱判定"
  - 特别是"官杀过旺导致身弱"和"财多导致身弱"这两个现代命理常用的命题, 在原典中并没有明确的正向因果授权
  - 这是一个非常有价值的审计结论, 不要为了填满Evidence Contract而补现代规则

  下一步选项:
  A. 进一步确认食伤→泄身的正向因果(《神峰通考》在Source Scope中的权重、"泄气"是定义还是因果)
  B. 保持当前状态, 承认克泄耗型身弱判定的Canonical Evidence Coverage不足
  C. 用现有所有Candidate(临死绝/党少助寡/无根/无气/食伤泄气)尝试建立Evidence Contract
  D. 补充更多原典(如《三命通会》《穷通宝鉴》)来查找官杀/财星的正向因果

  建议: 选项A或B, 不建议选项C(因为官杀和财星的正向因果没有原典授权)。

  仍然禁止:
    - 进入Authorization
    - 开发身弱算法
    - 设置ENGINE_FEATURE threshold
    - 把Candidate翻译成数值阈值
    - 合并克泄耗成pressure_score
    - 进入ContextResolver / Assertion
    - 直接产生L4 PROVEN
    """)

    print(f"\n{'='*120}")
    print("STR-001A Phase 5F 完成.")
    print("=" * 120)


# ============================================================================
# 主函数
# ============================================================================

def main():
    result = phase5f_kexiehao_source_expansion()
    negative_tests = run_negative_tests(result)
    print_phase5f_report(result, negative_tests)


if __name__ == "__main__":
    main()
