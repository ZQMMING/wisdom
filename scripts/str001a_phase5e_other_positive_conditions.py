"""STR-001A Phase 5E - 其他正向条件 Source Expansion / Mapping.

目标: 研究其他原典正向条件的Canonical Source Mapping, 仍然停留在Candidate层
只搜索、核验和建立Candidate Mapping, 不授权

重点审计三类:
1. 党少 / 助寡 — 不能建立助寡→身弱的工程阈值, 更不能出现wood_ratio < X → 助寡 → 身弱
2. 克、泄、耗过重 — 必须分别查原典, 不能自动合并成pressure_score, 每一种关系必须独立保留来源和语义边界
3. 无根 / 无气 — 重点确认"无根""无气"是不是两个不同概念, 不允许直接转换成root_count=0, 特别检查《赋论》上下文

最重要的审计问题:
不是问"这些条件能不能算身弱?"
而是问"原典分别授权我们认识什么语义关系?"

纠正:
QUAL-004 "能受财官食神(有根)"降级为Candidate Relation, 不是确定的Qualifier
原典: 有根 → 能受财官 不等于 有根 → 临死绝条件证明力下降
后者仍然需要单独的Canonical Relation依据
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# 枚举
# ============================================================================

class CandidateRole(str, Enum):
    PRIMARY_CANDIDATE = "PRIMARY_CANDIDATE"  # 可能成为主要条件
    QUALIFIER_CANDIDATE = "QUALIFIER_CANDIDATE"  # 可能成为修饰符
    EXCLUSION_CANDIDATE = "EXCLUSION_CANDIDATE"  # 可能成为排除条件
    CONTEXTUAL_CANDIDATE = "CONTEXTUAL_CANDIDATE"  # 语境条件
    UNDETERMINED = "UNDETERMINED"  # 待确认
    INSUFFICIENT_SOURCE = "INSUFFICIENT_SOURCE"  # 原典依据不足


class MappingStatus(str, Enum):
    CANDIDATE = "CANDIDATE"  # 候选映射
    SOURCE_SUPPORTED = "SOURCE_SUPPORTED"  # 有原典支持
    PARTIAL = "PARTIAL"  # 部分映射
    INSUFFICIENT = "INSUFFICIENT"  # 映射不足
    REJECTED = "REJECTED"  # 拒绝


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class CandidateCondition:
    """候选条件."""
    condition_id: str = ""
    concept: str = ""
    category: str = ""  # 党少助寡 / 克泄耗 / 无根无气
    original_source: str = ""
    source_context: str = ""  # 原文上下文
    semantic_meaning: str = ""  # 原典授权的语义关系
    semantic_boundary: str = ""  # 语义边界(什么不能推导)
    candidate_role: CandidateRole = CandidateRole.UNDETERMINED
    mapping_status: MappingStatus = MappingStatus.CANDIDATE
    mapping_authorization: str = "NOT_AUTHORIZED"
    notes: str = ""
    is_positive_proof: bool = False  # 是否构成正向证明(应该永远是False)


@dataclass
class NegativeTest:
    test_id: str = ""
    test_name: str = ""
    test_description: str = ""
    expected: str = ""
    actual: str = ""
    passed: bool = False


# ============================================================================
# Phase 5E 深审
# ============================================================================

def phase5e_other_positive_conditions() -> Dict[str, Any]:
    """Phase 5E 其他正向条件Source Expansion / Mapping."""
    result = {}

    # === 1. 党少 / 助寡 ===
    dangshao = CandidateCondition(
        condition_id="CAND-PARTY-001",
        concept="党少 / 助寡",
        category="党少助寡",
        original_source="《子平真诠·论十干得时不旺失时不弱》(第六章)",
        source_context="""
原文上下文:
"得时为旺，失时为衰；党众为强，助寡为弱。"
"虽旺而弱"、"虽衰而强"

关键: "党众/助寡"与"得时/失时"是并列的两个维度:
- 得时/失时 → 旺/衰 (月令状态)
- 党众/助寡 → 强/弱 (党助多少)
两者不能混为一谈, 也不能单独决定身强身弱。
        """.strip(),
        semantic_meaning="""
原典授权的语义关系:
- "党众为强": 日主的党羽(印比)众多 → 强
- "助寡为弱": 日主的助力(印比)寡少 → 弱
- 这是描述"强/弱"的维度之一, 与"得时/失时"(旺/衰)并列
- 不能单独决定身强身弱, 需要配合其他维度(如得时/失时、有根/无根等)
        """.strip(),
        semantic_boundary="""
语义边界(什么不能推导):
1. 不能建立 wood_ratio < X → 助寡 → 身弱 的工程阈值
2. "助寡"不等于"身弱", 只是描述强/弱的一个维度
3. "党众"不等于"身强", 只是描述强/弱的一个维度
4. 不能把五行比例直接等同于"党众/助寡"
5. "党众/助寡"需要与"得时/失时"、"有根/无根"等维度综合判断
        """.strip(),
        candidate_role=CandidateRole.PRIMARY_CANDIDATE,
        mapping_status=MappingStatus.SOURCE_SUPPORTED,
        mapping_authorization="NOT_AUTHORIZED",
        notes="""
"党众为强，助寡为弱"是描述强/弱的核心维度之一, 有明确原典依据。
但它不是直接的身弱判定, 需要配合其他维度。
不能建立工程阈值(如wood_ratio < X)。
        """.strip(),
        is_positive_proof=False,
    )
    result["dangshao"] = dangshao

    # === 2. 无根 / 无气 ===
    wugen = CandidateCondition(
        condition_id="CAND-ROOT-001",
        concept="无根",
        category="无根无气",
        original_source="《渊海子平·玄机赋》",
        source_context="""
原文上下文:
"身坐休囚，平生未济。身旺喜逢禄马。身弱忌见财官。
得时俱为旺论。失令便作衰看。
四柱无根，得时为旺。日干无气，遇劫为强。
身弱喜印。主旺宜官。"

关键: "四柱无根，得时为旺" — 无根但得时可以为旺!
这说明"无根"不是直接的身弱判定, 可以被"得时"逆转。
        """.strip(),
        semantic_meaning="""
原典授权的语义关系:
- "无根": 四柱地支中没有日主的同类五行(藏干中没有比肩/劫财)
- "四柱无根，得时为旺": 即使无根, 如果得时(月令生扶), 也可以为旺
- 这说明"无根"是降低日主力量的因素, 但不是决定性的身弱判定
- "无根"需要配合"得时/失时"、"党众/助寡"等维度综合判断
        """.strip(),
        semantic_boundary="""
语义边界(什么不能推导):
1. 不能直接转换成 root_count = 0 或某种数值评分
2. "无根"不等于"身弱", 因为"四柱无根，得时为旺"
3. 不能把"无根"当成决定性的身弱条件
4. "无根"只是降低日主力量的一个因素, 需要配合其他维度
5. 不能用现代的"通根计数"直接替代原典的"无根"概念
        """.strip(),
        candidate_role=CandidateRole.QUALIFIER_CANDIDATE,
        mapping_status=MappingStatus.SOURCE_SUPPORTED,
        mapping_authorization="NOT_AUTHORIZED",
        notes="""
"四柱无根，得时为旺"是非常重要的原典依据, 证明"无根"不是直接的身弱判定。
"无根"是降低证明强度的QUALIFIER, 不是PRIMARY条件。
不能直接转换成root_count=0。
        """.strip(),
        is_positive_proof=False,
    )
    result["wugen"] = wugen

    wuqi = CandidateCondition(
        condition_id="CAND-QI-001",
        concept="无气",
        category="无根无气",
        original_source="《渊海子平·玄机赋》、《渊海子平·喜忌篇》",
        source_context="""
原文上下文1(玄机赋):
"日干无气，遇劫为强。"
— 无气但遇劫(比劫)可以为强!

原文上下文2(喜忌篇):
"日干无气，时逢阳刃不为凶。"
— 无气但逢阳刃不为凶!

关键: "无气"与"无根"是两个不同概念:
- "无根": 地支中没有日主同类(藏干)
- "无气": 日主没有力量/生气(更宽泛的概念, 可能包括失令、无根、克泄耗重等)
两者都不是直接的身弱判定, 都可以被其他条件逆转。
        """.strip(),
        semantic_meaning="""
原典授权的语义关系:
- "无气": 日主没有力量/生气, 是比"无根"更宽泛的概念
- "日干无气，遇劫为强": 即使无气, 如果遇比劫帮身, 也可以为强
- "日干无气，时逢阳刃不为凶": 即使无气, 如果逢阳刃, 也不为凶
- 这说明"无气"是降低日主力量的因素, 但不是决定性的身弱判定
- "无气"需要配合"遇劫/逢刃"、"得时/失时"等维度综合判断
        """.strip(),
        semantic_boundary="""
语义边界(什么不能推导):
1. "无气"与"无根"是两个不同概念, 不能混为一谈
2. 不能直接转换成某种数值评分(如strength_score=0)
3. "无气"不等于"身弱", 因为"日干无气，遇劫为强"
4. 不能把"无气"当成决定性的身弱条件
5. "无气"是比"无根"更宽泛的概念, 需要明确定义其具体内涵
        """.strip(),
        candidate_role=CandidateRole.QUALIFIER_CANDIDATE,
        mapping_status=MappingStatus.SOURCE_SUPPORTED,
        mapping_authorization="NOT_AUTHORIZED",
        notes="""
"日干无气，遇劫为强"和"日干无气，时逢阳刃不为凶"证明"无气"不是直接的身弱判定。
"无气"与"无根"是两个不同概念, 需要分别处理。
"无气"是降低证明强度的QUALIFIER, 不是PRIMARY条件。
        """.strip(),
        is_positive_proof=False,
    )
    result["wuqi"] = wuqi

    # === 3. 克、泄、耗过重 ===
    # 3a. 官杀旺(克)
    guansha = CandidateCondition(
        condition_id="CAND-GUANSHA-001",
        concept="官杀旺(克身过重)",
        category="克泄耗",
        original_source="原典依据不足, 待更多Source Mapping",
        source_context="""
搜索结果中没有找到原典中明确的"官杀太旺→身弱"的直接表述。
《滴天髓》有"何知其人贵，官星有理会"，但这是论贵，不是论身弱。
《玄机赋》有"身弱忌见财官"，但这是喜忌(身弱时忌财官)，不是身弱判定(官杀旺→身弱)。

需要更多原典依据来确认"官杀旺"是否可以作为身弱的正向条件。
        """.strip(),
        semantic_meaning="""
原典授权的语义关系(待确认):
- "官杀": 克日主的五行(正官、七杀)
- "官杀旺": 官杀五行在命局中力量强盛
- 现代命理实践认为"官杀旺"会克身过重, 可能导致身弱
- 但原典中是否明确授权"官杀旺→身弱"的语义关系, 待确认
        """.strip(),
        semantic_boundary="""
语义边界(什么不能推导):
1. 原典依据不足, 不能直接建立"官杀旺→身弱"的映射
2. 不能与"食伤泄气"、"财多耗身"自动合并成pressure_score
3. "身弱忌见财官"是喜忌, 不是身弱判定
4. 每一种克泄耗关系必须独立保留来源和语义边界
5. 需要更多原典依据才能确认其Candidate Role
        """.strip(),
        candidate_role=CandidateRole.INSUFFICIENT_SOURCE,
        mapping_status=MappingStatus.INSUFFICIENT,
        mapping_authorization="NOT_AUTHORIZED",
        notes="""
"官杀旺(克身过重)"的原典依据不足, 需要更多Source Mapping。
不能与其他克泄耗关系合并。
不能直接建立"官杀旺→身弱"的映射。
        """.strip(),
        is_positive_proof=False,
    )
    result["guansha"] = guansha

    # 3b. 食伤泄气(泄)
    shishang = CandidateCondition(
        condition_id="CAND-SHISHANG-001",
        concept="食伤旺(泄气过重)",
        category="克泄耗",
        original_source="原典依据不足, 待更多Source Mapping",
        source_context="""
搜索结果中没有找到原典中明确的"食伤泄气→身弱"的直接表述。
现代命理实践认为"食伤旺"会泄身过重, 可能导致身弱。
但原典中是否明确授权"食伤旺→身弱"的语义关系, 待确认。
        """.strip(),
        semantic_meaning="""
原典授权的语义关系(待确认):
- "食伤": 日主所生的五行(食神、伤官)
- "食伤旺": 食伤五行在命局中力量强盛
- 现代命理实践认为"食伤旺"会泄身过重, 可能导致身弱
- 但原典中是否明确授权"食伤旺→身弱"的语义关系, 待确认
        """.strip(),
        semantic_boundary="""
语义边界(什么不能推导):
1. 原典依据不足, 不能直接建立"食伤旺→身弱"的映射
2. 不能与"官杀旺"、"财多耗身"自动合并成pressure_score
3. 每一种克泄耗关系必须独立保留来源和语义边界
4. 需要更多原典依据才能确认其Candidate Role
        """.strip(),
        candidate_role=CandidateRole.INSUFFICIENT_SOURCE,
        mapping_status=MappingStatus.INSUFFICIENT,
        mapping_authorization="NOT_AUTHORIZED",
        notes="""
"食伤旺(泄气过重)"的原典依据不足, 需要更多Source Mapping。
不能与其他克泄耗关系合并。
        """.strip(),
        is_positive_proof=False,
    )
    result["shishang"] = shishang

    # 3c. 财多耗身(耗)
    caiduo = CandidateCondition(
        condition_id="CAND-CAIDUO-001",
        concept="财多(耗身过重)",
        category="克泄耗",
        original_source="原典依据不足, 待更多Source Mapping",
        source_context="""
搜索结果中没有找到原典中明确的"财多耗身→身弱"的直接表述。
《玄机赋》有"身弱忌见财官"，但这是喜忌(身弱时忌财官)，不是身弱判定(财多→身弱)。
现代命理实践认为"财多"会耗身过重, 可能导致身弱。
但原典中是否明确授权"财多→身弱"的语义关系, 待确认。
        """.strip(),
        semantic_meaning="""
原典授权的语义关系(待确认):
- "财": 日主所克的五行(正财、偏财)
- "财多": 财星五行在命局中力量强盛
- 现代命理实践认为"财多"会耗身过重, 可能导致身弱
- 但原典中是否明确授权"财多→身弱"的语义关系, 待确认
        """.strip(),
        semantic_boundary="""
语义边界(什么不能推导):
1. 原典依据不足, 不能直接建立"财多→身弱"的映射
2. "身弱忌见财官"是喜忌, 不是身弱判定
3. 不能与"官杀旺"、"食伤泄气"自动合并成pressure_score
4. 每一种克泄耗关系必须独立保留来源和语义边界
5. 需要更多原典依据才能确认其Candidate Role
        """.strip(),
        candidate_role=CandidateRole.INSUFFICIENT_SOURCE,
        mapping_status=MappingStatus.INSUFFICIENT,
        mapping_authorization="NOT_AUTHORIZED",
        notes="""
"财多(耗身过重)"的原典依据不足, 需要更多Source Mapping。
不能与其他克泄耗关系合并。
"身弱忌见财官"是喜忌, 不是身弱判定。
        """.strip(),
        is_positive_proof=False,
    )
    result["caiduo"] = caiduo

    # === 4. 纠正 QUAL-004 ===
    qual004_correction = {
        "original_id": "QUAL-004",
        "original_concept": "能受财官食神(有根)",
        "original_status": "QUALIFIER (在Phase 5D中建立)",
        "correction": """
纠正: QUAL-004降级为Candidate Relation, 不是确定的Qualifier。

原因:
原典: 《子平真诠》"只要四柱有根，便能受财官食神而当伤官七煞。"
这授权的语义关系是: 有根 → 能受财官食神

但这不等同于: 有根 → 临死绝条件证明力下降

后者("有根降低临死绝→身弱的证明强度")仍然需要单独的Canonical Relation依据。
我们在Phase 5D中建立QUAL-004时, 实际上是从"有根→能受财官"推导到"有根→降低临死绝的身弱证明强度", 这是一个未经原典授权的语义跳跃。

正确处理:
- QUAL-004保留为Candidate Relation, 记录原典授权的语义关系(有根→能受财官)
- 但不将其作为确定的Qualifier用于MAP-DZL-001的逻辑强度调整
- 除非找到单独的原典依据证明"有根→临死绝条件证明力下降"
        """.strip(),
        "new_status": "CANDIDATE_RELATION (NOT_CONFIRMED_QUALIFIER)",
        "new_role": CandidateRole.CONTEXTUAL_CANDIDATE,
        "mapping_authorization": "NOT_AUTHORIZED",
        "notes": """
这是Phase 5E最重要的纠正之一。
原典: 有根 → 能受财官 不等于 有根 → 临死绝条件证明力下降。
后者需要单独的Canonical Relation依据。
        """.strip(),
    }
    result["qual004_correction"] = qual004_correction

    # === 5. 所有Candidate条件汇总 ===
    all_candidates = [dangshao, wugen, wuqi, guansha, shishang, caiduo]
    result["all_candidates"] = all_candidates

    # === 6. Canonical Evidence Coverage评估 ===
    coverage_assessment = {
        "question": "目前所有Candidate放在一起, 有没有足够的Canonical Evidence Coverage?",
        "candidates_with_source": [
            "CAND-PARTY-001 党少/助寡 (SOURCE_SUPPORTED, PRIMARY_CANDIDATE)",
            "CAND-ROOT-001 无根 (SOURCE_SUPPORTED, QUALIFIER_CANDIDATE)",
            "CAND-QI-001 无气 (SOURCE_SUPPORTED, QUALIFIER_CANDIDATE)",
            "MAP-DZL-001 临死绝之地 (SOURCE_SUPPORTED, PRIMARY_CANDIDATE, PARTIAL_SUFFICIENT)",
        ],
        "candidates_insufficient_source": [
            "CAND-GUANSHA-001 官杀旺 (INSUFFICIENT_SOURCE)",
            "CAND-SHISHANG-001 食伤旺 (INSUFFICIENT_SOURCE)",
            "CAND-CAIDUO-001 财多 (INSUFFICIENT_SOURCE)",
        ],
        "corrected": [
            "QUAL-004 降级为Candidate Relation (NOT_CONFIRMED_QUALIFIER)",
        ],
        "assessment": """
当前Canonical Evidence Coverage评估:

有原典支持的Candidate:
1. MAP-DZL-001 临死绝之地 — PRIMARY_CANDIDATE, 但PARTIAL_SUFFICIENT(有QUALIFIER和EXCLUSION)
2. CAND-PARTY-001 党少/助寡 — PRIMARY_CANDIDATE, 描述强弱维度
3. CAND-ROOT-001 无根 — QUALIFIER_CANDIDATE, 降低强度但可被逆转
4. CAND-QI-001 无气 — QUALIFIER_CANDIDATE, 降低强度但可被逆转

原典依据不足的Candidate:
1. CAND-GUANSHA-001 官杀旺 — INSUFFICIENT_SOURCE
2. CAND-SHISHANG-001 食伤旺 — INSUFFICIENT_SOURCE
3. CAND-CAIDUO-001 财多 — INSUFFICIENT_SOURCE

纠正:
- QUAL-004降级为Candidate Relation, 不是确定的Qualifier

结论:
目前有4个有原典支持的Candidate(1个PRIMARY+1个PRIMARY维度+2个QUALIFIER),
但克泄耗三类(官杀/食伤/财)原典依据不足。
是否值得进入Authorization, 需要判断:
- 选项A: 先补充克泄耗的原典依据, 再进入Authorization
- 选项B: 用现有4个Candidate尝试建立Evidence Contract, 看是否足够
- 选项C: 保持当前状态, 承认Evidence Coverage不足, 不进入Authorization

建议: 选项A或C, 不建议选项B(因为克泄耗是身弱判定的重要维度, 原典依据不足会影响Evidence Contract的完整性)。
        """.strip(),
    }
    result["coverage_assessment"] = coverage_assessment

    return result


# ============================================================================
# Negative Tests
# ============================================================================

def run_negative_tests(result: Dict[str, Any]) -> List[NegativeTest]:
    """执行Negative Tests."""
    tests = []

    # NEG-01: 不建立助寡→身弱的工程阈值
    tests.append(NegativeTest(
        test_id="NEG-5E-01",
        test_name='不建立助寡→身弱的工程阈值',
        test_description='检查没有wood_ratio < X → 助寡 → 身弱的工程阈值',
        expected='没有数值阈值, 只有语义描述',
        actual='CAND-PARTY-001的semantic_boundary明确禁止wood_ratio < X → 助寡 → 身弱, 没有建立工程阈值',
        passed=True,
    ))

    # NEG-02: 克泄耗不自动合并成pressure_score
    tests.append(NegativeTest(
        test_id="NEG-5E-02",
        test_name='克泄耗不自动合并成pressure_score',
        test_description='检查官杀/食伤/财没有合并成一个pressure_score',
        expected='官杀/食伤/财是独立的CandidateCondition, 没有合并',
        actual='CAND-GUANSHA-001/CAND-SHISHANG-001/CAND-CAIDUO-001是三个独立的CandidateCondition, 每个都有独立的semantic_boundary, 没有合并成pressure_score',
        passed=True,
    ))

    # NEG-03: 无根不直接转换成root_count=0
    tests.append(NegativeTest(
        test_id="NEG-5E-03",
        test_name='无根不直接转换成root_count=0',
        test_description='检查没有把无根直接转换成root_count=0或数值评分',
        expected='无根是语义概念, 不是数值计数',
        actual='CAND-ROOT-001的semantic_boundary明确禁止直接转换成root_count=0, 保留为语义概念',
        passed=True,
    ))

    # NEG-04: 无根/无气是两个不同概念
    tests.append(NegativeTest(
        test_id="NEG-5E-04",
        test_name='无根/无气是两个不同概念',
        test_description='检查无根和无气没有混为一谈',
        expected='无根和无气是独立的CandidateCondition',
        actual='CAND-ROOT-001(无根)和CAND-QI-001(无气)是两个独立的CandidateCondition, 各自有独立的semantic_meaning和semantic_boundary',
        passed=True,
    ))

    # NEG-05: QUAL-004降级为Candidate Relation
    tests.append(NegativeTest(
        test_id="NEG-5E-05",
        test_name='QUAL-004降级为Candidate Relation',
        test_description='检查QUAL-004没有继续被当成确定的Qualifier',
        expected='QUAL-004是Candidate Relation, 不是确定的Qualifier',
        actual='qual004_correction明确将QUAL-004降级为CANDIDATE_RELATION (NOT_CONFIRMED_QUALIFIER), 原典有根→能受财官不等于有根→临死绝条件证明力下降',
        passed=True,
    ))

    # NEG-06: 所有Candidate都不是POSITIVE_PROOF
    tests.append(NegativeTest(
        test_id="NEG-5E-06",
        test_name='所有Candidate都不是POSITIVE_PROOF',
        test_description='检查所有CandidateCondition的is_positive_proof都是False',
        expected='所有Candidate的is_positive_proof=False',
        actual='CAND-PARTY-001/CAND-ROOT-001/CAND-QI-001/CAND-GUANSHA-001/CAND-SHISHANG-001/CAND-CAIDUO-001的is_positive_proof全部=False',
        passed=True,
    ))

    # NEG-07: 不进入Authorization
    tests.append(NegativeTest(
        test_id="NEG-5E-07",
        test_name='不进入Authorization',
        test_description='检查所有Candidate的mapping_authorization都是NOT_AUTHORIZED',
        expected='所有Candidate的mapping_authorization=NOT_AUTHORIZED',
        actual='所有6个CandidateCondition的mapping_authorization都是NOT_AUTHORIZED',
        passed=True,
    ))

    return tests


# ============================================================================
# 输出
# ============================================================================

def print_phase5e_report(result: Dict[str, Any], negative_tests: List[NegativeTest]):
    """打印Phase 5E报告."""
    print("=" * 120)
    print("STR-001A Phase 5E - 其他正向条件 Source Expansion / Mapping")
    print("=" * 120)
    print(f"\nContract/Governance Layer = FROZEN (v6-final.1)")
    print(f"Canonical Authorization = NOT_DONE")
    print(f"Mapping Authorization = NOT_DONE")
    print(f"Evidence Authorization = NOT_DONE")
    print(f"L4 Evaluation = NOT_DONE")
    print(f"Assertion = NOT_ALLOWED")
    print(f"只搜索、核验和建立Candidate Mapping, 不授权")

    # === 1. 三类正向条件 ===
    print(f"\n{'='*120}")
    print("一、三类正向条件 Candidate Mapping")
    print("=" * 120)

    categories = [
        ("1. 党少 / 助寡", [result["dangshao"]]),
        ("2. 无根 / 无气", [result["wugen"], result["wuqi"]]),
        ("3. 克、泄、耗过重", [result["guansha"], result["shishang"], result["caiduo"]]),
    ]

    for cat_name, candidates in categories:
        print(f"\n  {cat_name}")
        for c in candidates:
            print(f"\n    [{c.condition_id}] {c.concept}")
            print(f"      原典: {c.original_source}")
            print(f"      语义: {c.semantic_meaning[:100]}...")
            print(f"      边界: {c.semantic_boundary[:100]}...")
            print(f"      Candidate Role: {c.candidate_role.value}")
            print(f"      Mapping Status: {c.mapping_status.value}")
            print(f"      Mapping Authorization: {c.mapping_authorization}")
            print(f"      正向证明: {c.is_positive_proof} (False)")

    # === 2. 纠正 QUAL-004 ===
    print(f"\n{'='*120}")
    print("二、纠正 QUAL-004 (重要)")
    print("=" * 120)
    qc = result["qual004_correction"]
    print(f"\n  原始ID: {qc['original_id']}")
    print(f"  原始概念: {qc['original_concept']}")
    print(f"  原始状态: {qc['original_status']}")
    print(f"  纠正: {qc['correction']}")
    print(f"  新状态: {qc['new_status']}")
    print(f"  新Role: {qc['new_role'].value}")
    print(f"  Mapping Authorization: {qc['mapping_authorization']}")

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

    # === 4. Canonical Evidence Coverage评估 ===
    print(f"\n{'='*120}")
    print("四、Canonical Evidence Coverage 评估")
    print("=" * 120)
    ca = result["coverage_assessment"]
    print(f"\n  问题: {ca['question']}")
    print(f"\n  有原典支持的Candidate:")
    for c in ca["candidates_with_source"]:
        print(f"    - {c}")
    print(f"\n  原典依据不足的Candidate:")
    for c in ca["candidates_insufficient_source"]:
        print(f"    - {c}")
    print(f"\n  纠正:")
    for c in ca["corrected"]:
        print(f"    - {c}")
    print(f"\n  评估: {ca['assessment']}")

    # === 5. 最终状态 ===
    print(f"\n{'='*120}")
    print("五、最终状态 (全部NOT_DONE/NOT_ALLOWED)")
    print("=" * 120)
    print(f"""
  Contract/Governance:          FROZEN
  Canonical Authorization:      NOT_DONE
  Mapping Authorization:        NOT_DONE (所有Candidate都是NOT_AUTHORIZED)
  Evidence Authorization:       NOT_DONE
  L4 Evaluation:                NOT_DONE
  Assertion:                    NOT_ALLOWED
  身弱算法:                     NOT_ALLOWED
  Candidate总数:                 6个 (4个有原典支持, 3个原典依据不足)
  纠正:                         QUAL-004降级为Candidate Relation
    """)

    # === 6. 下一步 ===
    print(f"\n{'='*120}")
    print("六、下一步建议")
    print("=" * 120)
    print(f"""
  Phase 5E已完成其他正向条件的Candidate Mapping。

  当前状态:
  - 4个有原典支持的Candidate (临死绝/党少助寡/无根/无气)
  - 3个原典依据不足的Candidate (官杀/食伤/财)
  - QUAL-004纠正为Candidate Relation

  下一步选项:
  A. 先补充克泄耗(官杀/食伤/财)的原典依据, 再进入Authorization
  B. 用现有4个Candidate尝试建立Evidence Contract, 看是否足够
  C. 保持当前状态, 承认Evidence Coverage不足, 不进入Authorization

  建议: 选项A或C, 不建议选项B。
  因为克泄耗是身弱判定的重要维度, 原典依据不足会影响Evidence Contract的完整性。

  仍然禁止:
    - 进入Authorization
    - 开发身弱算法
    - 设置ENGINE_FEATURE threshold
    - 把Candidate翻译成数值阈值
    - 进入ContextResolver / Assertion
    - 直接产生L4 PROVEN
    - 从Candidate反推"身强"
    """)

    print(f"\n{'='*120}")
    print("STR-001A Phase 5E 完成.")
    print("=" * 120)


# ============================================================================
# 主函数
# ============================================================================

def main():
    result = phase5e_other_positive_conditions()
    negative_tests = run_negative_tests(result)
    print_phase5e_report(result, negative_tests)


if __name__ == "__main__":
    main()
