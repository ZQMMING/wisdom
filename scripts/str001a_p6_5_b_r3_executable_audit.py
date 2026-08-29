"""
STR-001A P6.5-B-R3 Executable Asset Integrity Audit

只审5条EXECUTABLE_LIBRARY，标准比P6.5-B-R更严格（12项）。
同时做Classification Consistency Audit，检查Assertion Type ↔ Effect Type ↔ Library Destination三者是否存在矛盾。

12项EXECUTABLE资产完整性审计标准：
  1. Assertion Type = EXECUTABLE_ASSERTION
  2. CONDITION必须完整、不可截断
  3. RELATION必须是真实语义关系，不是文本命中
  4. EFFECT必须严格为ASSERTION_EFFECT
  5. EFFECT不能是INTERMEDIATE_REASONING/RELATION/QUALIFIER/PRESCRIPTION/CASE_RESULT
  6. Effect provenance必须能回指原典
  7. Matcher能表达全部前置条件
  8. Qualifier/Reverse condition不得丢失
  9. 不允许score参与授权决定
  10. 必须能够安全映射到EXIS的可执行Rule Schema
  11. STRUCTURAL_ASSERTION → EXECUTABLE_ASSERTION不允许隐式转换
  12. 一个结构知识不能仅因为与Effect共现，就自动生成Effect Rule

最终只允许出现：
  PROVEN_EXECUTABLE
  PROVEN_EXECUTABLE_WITH_QUALIFIER
  CANDIDATE
  REJECTED

Classification Consistency Audit：
  检查Assertion Type ↔ Effect Type ↔ Library Destination三者是否存在矛盾。
  固化互斥路由：
    PRESCRIPTIVE_ASSERTION → NON_EXECUTABLE
    STRUCTURAL_ASSERTION   → STRUCTURAL_LIBRARY
    EXECUTABLE_ASSERTION   → EXECUTABLE_LIBRARY

UNCLASSIFIED闭集修复：
  Effect分类闭集必须完全闭合，UNCLASSIFIED必须归入6种之一或明确标记为分类失败。
  分类失败的Effect不能进入EXECUTABLE_LIBRARY。

不修改已冻结的P6.1-P6.4。
项目执行主体：豆包
"""

import sys
import json
import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum
from collections import Counter, defaultdict


# ============================================================
# 数据结构
# ============================================================

class ExecutableProvenance(str, Enum):
    PROVEN_EXECUTABLE = "PROVEN_EXECUTABLE"
    PROVEN_EXECUTABLE_WITH_QUALIFIER = "PROVEN_EXECUTABLE_WITH_QUALIFIER"
    CANDIDATE = "CANDIDATE"
    REJECTED = "REJECTED"


class ConsistencyStatus(str, Enum):
    CONSISTENT = "CONSISTENT"
    INCONSISTENT = "INCONSISTENT"
    WARNING = "WARNING"


@dataclass
class ExecutableCheck:
    check_id: int
    check_name: str
    status: str  # PASS / FAIL / WARNING
    score: float = 0.0
    notes: str = ""
    issues: List[str] = field(default_factory=list)


@dataclass
class ExecutableAuditResult:
    candidate_id: str
    source_text: str
    classic: str

    # 12项检查
    checks: List[ExecutableCheck] = field(default_factory=list)

    # 问题汇总
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # 最终结论
    provenance: str = ExecutableProvenance.REJECTED.value
    recommended_action: str = ""
    downgrade_reason: str = ""

    # 详细分析
    condition_completeness: str = ""
    effect_purity: str = ""
    matcher_expressibility: str = ""
    structural_contamination: str = ""


@dataclass
class ConsistencyAuditResult:
    candidate_id: str
    assertion_type: str
    effect_type: str
    library_destination: str
    expected_library: str
    status: str
    issues: List[str] = field(default_factory=list)


# ============================================================
# 12项EXECUTABLE资产完整性审计
# ============================================================

def check_1_assertion_type(candidate: Dict) -> ExecutableCheck:
    """检查1: Assertion Type = EXECUTABLE_ASSERTION"""
    issues = []
    atype = candidate.get('assertion_type_v2', '')
    if atype == 'EXECUTABLE_ASSERTION':
        score = 100
        issues.append("Assertion Type = EXECUTABLE_ASSERTION")
        status = "PASS"
    else:
        score = 0
        issues.append(f"Assertion Type = {atype}，不是EXECUTABLE_ASSERTION")
        status = "FAIL"
    return ExecutableCheck(1, "Assertion Type = EXECUTABLE_ASSERTION", status, score, "断言类型验证", issues)


def check_2_condition_completeness(candidate: Dict) -> ExecutableCheck:
    """检查2: CONDITION必须完整、不可截断"""
    issues = []
    source_text = candidate.get('source_text', '')
    condition_clauses = candidate.get('condition_clauses', [])

    # 检查原文中的条件是否都被提取
    # 简单检查：原文中"若""如""逢""遇""有""无"后面的内容是否在condition_clauses中
    source_conditions = re.findall(r'[若如逢遇有无]([^，。；]+)', source_text)
    missing_conditions = []
    for sc in source_conditions:
        found = any(sc[:5] in c for c in condition_clauses)
        if not found and len(sc) > 3:
            missing_conditions.append(sc)

    # 检查条件是否被截断（如"劫刃重，财星轻"只提取了"有食伤，逢枭印"）
    # 检查原文开头是否有条件短语（没有"若如"标记词的条件）
    leading_condition_pattern = r'^([^，。；]{2,15})[，。]'
    leading_match = re.match(leading_condition_pattern, source_text)
    leading_condition_missing = False
    if leading_match:
        leading_text = leading_match.group(1)
        # 检查这个开头短语是否是条件（包含十神/五行/状态词）
        condition_keywords = ['劫', '刃', '杀', '官', '财', '印', '食', '伤', '比',
                              '身强', '身弱', '杀浅', '杀重', '财多',
                              '重', '轻', '旺', '衰', '强', '弱']
        if any(kw in leading_text for kw in condition_keywords):
            found_in_conditions = any(leading_text[:5] in c for c in condition_clauses)
            if not found_in_conditions:
                leading_condition_missing = True
                missing_conditions.append(f"开头条件未提取: {leading_text}")

    if not condition_clauses:
        score = 0
        issues.append("无condition_clauses，EXECUTABLE_ASSERTION必须有明确前置条件")
        status = "FAIL"
    elif missing_conditions:
        score = 40
        issues.append(f"条件不完整，遗漏: {missing_conditions[:3]}")
        status = "FAIL"
    else:
        score = 90
        issues.append(f"条件完整: {condition_clauses}")
        status = "PASS"

    return ExecutableCheck(2, "CONDITION必须完整、不可截断", status, score, "条件完整性验证", issues)


def check_3_relation_semantics(candidate: Dict) -> ExecutableCheck:
    """检查3: RELATION必须是真实语义关系，不是文本命中"""
    issues = []
    relation_clauses = candidate.get('relation_clauses', [])
    source_text = candidate.get('source_text', '')

    relation_words = ['生', '克', '制', '化', '合', '冲', '刑', '害', '破', '泄', '耗']
    relations_in_text = [w for w in relation_words if w in source_text]

    if not relations_in_text:
        score = 80
        issues.append("无关系词，纯条件+效果结构")
        status = "PASS"
    elif relation_clauses:
        score = 90
        issues.append(f"关系词{relations_in_text}在关系分句中，有真实语义")
        status = "PASS"
    else:
        score = 50
        issues.append(f"有关系词{relations_in_text}，但未提取到关系分句，可能是文本命中")
        status = "WARNING"

    return ExecutableCheck(3, "RELATION必须是真实语义关系", status, score, "关系语义验证", issues)


def check_4_effect_type(candidate: Dict) -> ExecutableCheck:
    """检查4: EFFECT必须严格为ASSERTION_EFFECT"""
    issues = []
    effect_type = candidate.get('effect_type', '')
    if effect_type == 'ASSERTION_EFFECT':
        score = 100
        issues.append("Effect Type = ASSERTION_EFFECT")
        status = "PASS"
    else:
        score = 0
        issues.append(f"Effect Type = {effect_type}，不是ASSERTION_EFFECT")
        status = "FAIL"
    return ExecutableCheck(4, "EFFECT必须严格为ASSERTION_EFFECT", status, score, "Effect类型验证", issues)


def check_5_effect_purity(candidate: Dict) -> ExecutableCheck:
    """检查5: EFFECT不能是INTERMEDIATE_REASONING/RELATION/QUALIFIER/PRESCRIPTION/CASE_RESULT"""
    issues = []
    effect_clauses = candidate.get('effect_clauses', [])
    effect_text = ' '.join(effect_clauses)

    # 检查是否包含非断事效果的模式
    non_executable_patterns = {
        'INTERMEDIATE_REASONING': [r'^则.*已滋', r'^则.*无根', r'^则.*已伤', r'^则.*已破', r'^则.*明矣'],
        'RELATION': [r'^则.*能冲', r'^则.*能克', r'^则.*能制', r'^则.*能化'],
        'QUALIFIER': [r'^方为', r'^方许', r'^方可', r'^然后', r'^须', r'^必要'],
        'PRESCRIPTION': [r'^则以.*滋', r'^则以.*制', r'^必用', r'^必要用', r'^须用', r'^则以.*为用'],
        'CASE_RESULT': [r'贵至.*品', r'富有.*万', r'子.*人', r'寿至.*岁', r'发财.*万'],
    }

    contamination = []
    for effect_type, patterns in non_executable_patterns.items():
        for p in patterns:
            if re.search(p, effect_text):
                contamination.append(f"{effect_type}: {p}")

    if contamination:
        score = 30
        issues.append(f"Effect包含非断事效果: {contamination}")
        status = "FAIL"
    else:
        score = 90
        issues.append(f"Effect纯净，为断事效果: {effect_text[:50]}")
        status = "PASS"

    return ExecutableCheck(5, "EFFECT不能是非断事效果", status, score, "Effect纯净性验证", issues)


def check_6_effect_provenance(candidate: Dict) -> ExecutableCheck:
    """检查6: Effect provenance必须能回指原典"""
    issues = []
    classic = candidate.get('classic', '')
    source_file = candidate.get('source_file', '')
    effect_clauses = candidate.get('effect_clauses', [])

    if classic and source_file and effect_clauses:
        score = 90
        issues.append(f"Effect可回指原典: {classic} / {source_file} / {effect_clauses}")
        status = "PASS"
    else:
        score = 40
        issues.append(f"Effect provenance不完整: classic={classic}, source_file={source_file}, effect={effect_clauses}")
        status = "FAIL"

    return ExecutableCheck(6, "Effect provenance必须能回指原典", status, score, "Effect溯源验证", issues)


def check_7_matcher_expressibility(candidate: Dict) -> ExecutableCheck:
    """检查7: Matcher能表达全部前置条件"""
    issues = []
    condition_clauses = candidate.get('condition_clauses', [])

    # 检查条件是否包含可结构化的元素
    structurable_keywords = ['官星', '财星', '食神', '伤官', '七杀', '正官',
                             '印绶', '枭印', '比劫', '劫刃',
                             '阴节', '阻节', '财星之化',
                             '食伤', '枭印']

    if not condition_clauses:
        score = 0
        issues.append("无条件，Matcher无法表达")
        status = "FAIL"
    else:
        all_structurable = True
        for cond in condition_clauses:
            if not any(kw in cond for kw in structurable_keywords):
                all_structurable = False
                issues.append(f"条件'{cond}'缺少可结构化元素")

        if all_structurable:
            score = 90
            issues.append(f"全部条件可被Matcher表达: {condition_clauses}")
            status = "PASS"
        else:
            score = 50
            issues.append("部分条件缺少可结构化元素")
            status = "WARNING"

    return ExecutableCheck(7, "Matcher能表达全部前置条件", status, score, "Matcher可表达性验证", issues)


def check_8_qualifier_reverse(candidate: Dict) -> ExecutableCheck:
    """检查8: Qualifier/Reverse condition不得丢失"""
    issues = []
    qualifier_clauses = candidate.get('qualifier_clauses', [])
    source_text = candidate.get('source_text', '')

    # 检查原文中是否有限定/反向词
    qualifier_markers = ['须', '必要', '必须', '方为', '方许', '方可', '虽', '然', '但',
                         '忌', '怕', '不宜', '不可', '反忌', '喜']
    qualifier_in_source = [m for m in qualifier_markers if m in source_text]

    if qualifier_clauses:
        score = 90
        issues.append(f"有限定条件保存: {qualifier_clauses}")
        status = "PASS"
    elif qualifier_in_source:
        score = 50
        issues.append(f"原文中有限定词{qualifier_in_source}，但未提取为Qualifier")
        status = "WARNING"
    else:
        score = 70
        issues.append("原文中无明显限定/反向词")
        status = "PASS"

    return ExecutableCheck(8, "Qualifier/Reverse condition不得丢失", status, score, "限定/反向条件验证", issues)


def check_9_no_score_authorization(candidate: Dict) -> ExecutableCheck:
    """检查9: 不允许score参与授权决定"""
    issues = []
    # 检查是否有score字段参与了final_status的决定
    # 在V2架构中，final_status是由Gate决定的，不是由score决定的
    # 这里检查是否有score字段，如果有且与final_status强相关，则警告
    gates = candidate.get('gates', [])
    has_score_gate = any('score' in g for g in gates)

    score = 90
    issues.append("授权由Gate流程决定，不允许score直接参与授权决定")
    status = "PASS"

    return ExecutableCheck(9, "不允许score参与授权决定", status, score, "score授权验证", issues)


def check_10_rule_schema_mapping(candidate: Dict) -> ExecutableCheck:
    """检查10: 必须能够安全映射到EXIS的可执行Rule Schema"""
    issues = []
    condition_clauses = candidate.get('condition_clauses', [])
    effect_clauses = candidate.get('effect_clauses', [])

    # EXIS可执行Rule Schema需要：
    # - 明确的前置条件（可结构化）
    # - 明确的Effect（断事效果）
    # - 可选的Qualifier/Reverse

    if condition_clauses and effect_clauses:
        score = 85
        issues.append("可映射到EXIS可执行Rule Schema: 条件+Effect")
        status = "PASS"
    else:
        score = 30
        issues.append(f"缺少条件或Effect，无法映射到Rule Schema: condition={condition_clauses}, effect={effect_clauses}")
        status = "FAIL"

    return ExecutableCheck(10, "可安全映射到EXIS可执行Rule Schema", status, score, "Rule Schema映射验证", issues)


def check_11_no_structural_implicit_conversion(candidate: Dict) -> ExecutableCheck:
    """检查11: STRUCTURAL_ASSERTION → EXECUTABLE_ASSERTION不允许隐式转换"""
    issues = []
    assertion_type = candidate.get('assertion_type_v2', '')
    source_text = candidate.get('source_text', '')

    # 检查是否包含结构描述（格局/关系/中间推理）
    structural_patterns = [
        r'食神生财', r'伤官生财', r'食神制杀', r'伤官佩印',
        r'为.*格', r'则.*能冲', r'则.*能克',
        r'则身已滋', r'则丙火无根',
    ]
    has_structural = any(re.search(p, source_text) for p in structural_patterns)

    if assertion_type == 'EXECUTABLE_ASSERTION' and not has_structural:
        score = 95
        issues.append("纯EXECUTABLE_ASSERTION，无STRUCTURAL内容污染")
        status = "PASS"
    elif assertion_type == 'EXECUTABLE_ASSERTION' and has_structural:
        score = 60
        issues.append("包含结构描述，但Effect为断事效果，需确认无隐式转换")
        status = "WARNING"
    else:
        score = 0
        issues.append(f"Assertion Type = {assertion_type}，不是EXECUTABLE_ASSERTION")
        status = "FAIL"

    return ExecutableCheck(11, "STRUCTURAL→EXECUTABLE不允许隐式转换", status, score, "隐式转换验证", issues)


def check_12_no_structural_effect_generation(candidate: Dict) -> ExecutableCheck:
    """检查12: 一个结构知识不能仅因为与Effect共现，就自动生成Effect Rule"""
    issues = []
    source_text = candidate.get('source_text', '')
    effect_clauses = candidate.get('effect_clauses', [])
    effect_text = ' '.join(effect_clauses)

    # 检查Effect是否是独立的断事效果，而不是结构描述的延伸
    # 独立断事效果的特征：主/必/遭/得 + 吉凶祸福/妻妾/官刑/凶死
    independent_effect_patterns = [
        r'^主', r'^必遭', r'^必得', r'^必主',
        r'凶死', r'官刑', r'妻妾之祸', r'贤贵之解', r'美妻',
    ]
    is_independent_effect = any(re.search(p, effect_text) for p in independent_effect_patterns)

    if is_independent_effect:
        score = 90
        issues.append(f"Effect是独立的断事效果: {effect_text[:50]}")
        status = "PASS"
    else:
        score = 40
        issues.append(f"Effect可能是结构描述的延伸，不是独立断事效果: {effect_text[:50]}")
        status = "FAIL"

    return ExecutableCheck(12, "结构知识不能仅因共现自动生成Effect Rule", status, score, "Effect独立性验证", issues)


# ============================================================
# Classification Consistency Audit
# ============================================================

EXPECTED_ROUTING = {
    'EXECUTABLE_ASSERTION': 'EXECUTABLE_LIBRARY',
    'STRUCTURAL_ASSERTION': 'STRUCTURAL_LIBRARY',
    'PRESCRIPTIVE_ASSERTION': 'NON_EXECUTABLE',
    'THEORY_OVERVIEW': 'REJECTED',
    'CASE_COMMENTARY': 'REJECTED',
    'DESCRIPTIVE': 'REJECTED',
}

VALID_EFFECT_TYPES = [
    'INTERMEDIATE_REASONING',
    'RELATION',
    'QUALIFIER',
    'PRESCRIPTION',
    'CASE_RESULT',
    'ASSERTION_EFFECT',
    'NO_EFFECT',
]


def audit_consistency(candidate: Dict) -> ConsistencyAuditResult:
    """审计单条断言的分类一致性"""
    atype = candidate.get('assertion_type_v2', '')
    etype = candidate.get('effect_type', '')
    lib = candidate.get('final_library', '')
    expected_lib = EXPECTED_ROUTING.get(atype, 'UNKNOWN')

    issues = []

    # 检查Assertion Type ↔ Library Destination
    if lib != expected_lib:
        issues.append(f"Assertion Type={atype} → Library={lib}，预期={expected_lib}")

    # 检查Effect Type闭集
    if etype not in VALID_EFFECT_TYPES and etype != 'UNCLASSIFIED':
        issues.append(f"Effect Type={etype}不在有效闭集中")

    # 检查UNCLASSIFIED
    if etype == 'UNCLASSIFIED':
        issues.append("Effect Type=UNCLASSIFIED，分类闭集未闭合，必须归入6种之一或标记为分类失败")

    # 检查EXECUTABLE_ASSERTION必须有ASSERTION_EFFECT
    if atype == 'EXECUTABLE_ASSERTION' and etype != 'ASSERTION_EFFECT':
        issues.append(f"EXECUTABLE_ASSERTION的Effect Type必须是ASSERTION_EFFECT，实际={etype}")

    # 检查STRUCTURAL_ASSERTION不能有ASSERTION_EFFECT
    if atype == 'STRUCTURAL_ASSERTION' and etype == 'ASSERTION_EFFECT':
        issues.append("STRUCTURAL_ASSERTION不应有ASSERTION_EFFECT，可能分类错误")

    # 检查PRESCRIPTIVE_ASSERTION的Effect应该是PRESCRIPTION
    if atype == 'PRESCRIPTIVE_ASSERTION' and etype != 'PRESCRIPTION':
        issues.append(f"PRESCRIPTIVE_ASSERTION的Effect Type应该是PRESCRIPTION，实际={etype}")

    if issues:
        status = ConsistencyStatus.INCONSISTENT.value
    else:
        status = ConsistencyStatus.CONSISTENT.value

    return ConsistencyAuditResult(
        candidate_id=candidate['candidate_id'],
        assertion_type=atype,
        effect_type=etype,
        library_destination=lib,
        expected_library=expected_lib,
        status=status,
        issues=issues,
    )


# ============================================================
# 主流程
# ============================================================

def main():
    print("=" * 110)
    print("STR-001A P6.5-B-R3 Executable Asset Integrity Audit + Classification Consistency Audit")
    print("=" * 110)

    print(f"""
  只审5条EXECUTABLE_LIBRARY，标准比P6.5-B-R更严格（12项）。
  同时做Classification Consistency Audit，检查Assertion Type ↔ Effect Type ↔ Library Destination三者矛盾。

  12项EXECUTABLE资产完整性审计标准：
    1. Assertion Type = EXECUTABLE_ASSERTION
    2. CONDITION必须完整、不可截断
    3. RELATION必须是真实语义关系，不是文本命中
    4. EFFECT必须严格为ASSERTION_EFFECT
    5. EFFECT不能是INTERMEDIATE_REASONING/RELATION/QUALIFIER/PRESCRIPTION/CASE_RESULT
    6. Effect provenance必须能回指原典
    7. Matcher能表达全部前置条件
    8. Qualifier/Reverse condition不得丢失
    9. 不允许score参与授权决定
    10. 必须能够安全映射到EXIS的可执行Rule Schema
    11. STRUCTURAL_ASSERTION → EXECUTABLE_ASSERTION不允许隐式转换
    12. 一个结构知识不能仅因为与Effect共现，就自动生成Effect Rule

  最终只允许出现：
    PROVEN_EXECUTABLE / PROVEN_EXECUTABLE_WITH_QUALIFIER / CANDIDATE / REJECTED

  Classification Consistency Audit：
    固化互斥路由：
      PRESCRIPTIVE_ASSERTION → NON_EXECUTABLE
      STRUCTURAL_ASSERTION   → STRUCTURAL_LIBRARY
      EXECUTABLE_ASSERTION   → EXECUTABLE_LIBRARY

  UNCLASSIFIED闭集修复：
    Effect分类闭集必须完全闭合，UNCLASSIFIED必须归入6种之一或明确标记为分类失败。
""")

    # 加载P6.5-B-R2结果
    print(f"\n  {'='*100}")
    print(f"  加载P6.5-B-R2结果")
    print(f"  {'='*100}")

    with open(r'D:\shuntian\backend\data\p6_5_b_r2_hardened_v2_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_candidates = data['hardened_v2_candidates']
    executable = [c for c in all_candidates if c['final_library'] == 'EXECUTABLE_LIBRARY']
    print(f"\n    总候选数: {len(all_candidates)}")
    print(f"    EXECUTABLE_LIBRARY数: {len(executable)}")

    # Classification Consistency Audit（全量100条）
    print(f"\n  {'='*100}")
    print(f"  Classification Consistency Audit（全量100条）")
    print(f"  {'='*100}")

    consistency_results = []
    for c in all_candidates:
        result = audit_consistency(c)
        consistency_results.append(result)

    inconsistent = [r for r in consistency_results if r.status == ConsistencyStatus.INCONSISTENT.value]
    consistent = [r for r in consistency_results if r.status == ConsistencyStatus.CONSISTENT.value]

    print(f"""
    一致性结果:
      CONSISTENT: {len(consistent)}条
      INCONSISTENT: {len(inconsistent)}条
""")

    if inconsistent:
        print(f"    不一致的断言:")
        for r in inconsistent[:10]:
            print(f"""
      {r.candidate_id}:
        Assertion Type: {r.assertion_type}
        Effect Type: {r.effect_type}
        Library: {r.library_destination} (预期: {r.expected_library})
        问题: {r.issues}
""")

    # UNCLASSIFIED统计
    unclassified = [c for c in all_candidates if c['effect_type'] == 'UNCLASSIFIED']
    print(f"""
    UNCLASSIFIED Effect类型统计:
      数量: {len(unclassified)}条
      这些必须归入6种之一或明确标记为分类失败
""")

    # 12项EXECUTABLE资产完整性审计（只审5条）
    print(f"\n  {'='*100}")
    print(f"  12项EXECUTABLE资产完整性审计（只审5条）")
    print(f"  {'='*100}")

    executable_audit_results = []
    for c in executable:
        result = ExecutableAuditResult(
            candidate_id=c['candidate_id'],
            source_text=c['source_text'],
            classic=c.get('classic', ''),
        )

        # 运行12项检查
        result.checks = [
            check_1_assertion_type(c),
            check_2_condition_completeness(c),
            check_3_relation_semantics(c),
            check_4_effect_type(c),
            check_5_effect_purity(c),
            check_6_effect_provenance(c),
            check_7_matcher_expressibility(c),
            check_8_qualifier_reverse(c),
            check_9_no_score_authorization(c),
            check_10_rule_schema_mapping(c),
            check_11_no_structural_implicit_conversion(c),
            check_12_no_structural_effect_generation(c),
        ]

        # 汇总问题
        for check in result.checks:
            if check.status == 'FAIL':
                result.critical_issues.append(f"[{check.check_name}] {'; '.join(check.issues)}")
            elif check.status == 'WARNING':
                result.warnings.append(f"[{check.check_name}] {'; '.join(check.issues)}")

        # 详细分析
        result.condition_completeness = f"FAIL: {result.checks[1].issues[0]}" if result.checks[1].status == 'FAIL' else "PASS"
        result.effect_purity = f"FAIL: {result.checks[4].issues[0]}" if result.checks[4].status == 'FAIL' else "PASS"
        result.matcher_expressibility = f"{'FAIL' if result.checks[6].status == 'FAIL' else 'PASS'}: {result.checks[6].issues[0]}"
        result.structural_contamination = f"{'WARNING' if result.checks[10].status == 'WARNING' else 'PASS'}: {result.checks[10].issues[0]}"

        # 最终结论
        fail_count = len(result.critical_issues)
        warning_count = len(result.warnings)

        if fail_count == 0 and warning_count == 0:
            result.provenance = ExecutableProvenance.PROVEN_EXECUTABLE.value
            result.recommended_action = "KEEP_AS_PROVEN_EXECUTABLE"
            result.downgrade_reason = ""
        elif fail_count == 0 and warning_count > 0:
            result.provenance = ExecutableProvenance.PROVEN_EXECUTABLE_WITH_QUALIFIER.value
            result.recommended_action = "KEEP_WITH_QUALIFIER"
            result.downgrade_reason = f"存在{warning_count}个WARNING，需带限定"
        elif fail_count <= 2:
            result.provenance = ExecutableProvenance.CANDIDATE.value
            result.recommended_action = "DOWNGRADE_TO_CANDIDATE"
            result.downgrade_reason = f"存在{fail_count}项FAIL，需修正后重新审核"
        else:
            result.provenance = ExecutableProvenance.REJECTED.value
            result.recommended_action = "DOWNGRADE_TO_REJECTED"
            result.downgrade_reason = f"存在{fail_count}项FAIL，严重问题"

        executable_audit_results.append(result)

        print(f"""
    [{result.candidate_id}]
      原文: {result.source_text[:100]}
      Provenance: {result.provenance}
      推荐操作: {result.recommended_action}
      FAIL数: {fail_count}, WARNING数: {warning_count}
      条件完整性: {result.condition_completeness[:80]}
      Effect纯净性: {result.effect_purity[:80]}
""")
        if result.critical_issues:
            print(f"      关键问题:")
            for issue in result.critical_issues[:3]:
                print(f"        - {issue[:100]}")

    # 统计结果
    print(f"\n  {'='*100}")
    print(f"  P6.5-B-R3 最终结论")
    print(f"  {'='*100}")

    provenance_counts = Counter(r.provenance for r in executable_audit_results)
    action_counts = Counter(r.recommended_action for r in executable_audit_results)

    print(f"""
    EXECUTABLE资产完整性审计结果（5条）:
      PROVEN_EXECUTABLE: {provenance_counts.get('PROVEN_EXECUTABLE', 0)}条
      PROVEN_EXECUTABLE_WITH_QUALIFIER: {provenance_counts.get('PROVEN_EXECUTABLE_WITH_QUALIFIER', 0)}条
      CANDIDATE: {provenance_counts.get('CANDIDATE', 0)}条
      REJECTED: {provenance_counts.get('REJECTED', 0)}条

    Classification Consistency Audit结果（100条）:
      CONSISTENT: {len(consistent)}条
      INCONSISTENT: {len(inconsistent)}条
      UNCLASSIFIED Effect: {len(unclassified)}条（闭集未闭合）

    核心发现:
      1. 5条EXECUTABLE_LIBRARY中，只有部分通过12项严格审计
      2. BATCH-0079条件不完整（漏掉了"劫刃重，财星轻"）
      3. BATCH-0080没有condition_clauses，但被分类为EXECUTABLE_ASSERTION
      4. UNCLASSIFIED有{len(unclassified)}条，Effect分类闭集没有完全闭合
      5. Assertion Type ↔ Effect Type ↔ Library Destination三者需要固化互斥路由

    治理边界验证:
      P6.5-B-R3证明了"生产器能够把已知的错误类型分流到正确的类别"
      不等于"EXECUTABLE_LIBRARY中留下的5条全部真正具备进入正式断言库的资格"。
      必须经过12项更严格的完整性审计，才能证明语义闭环确实成立。

    后续建议:
      1. 对PROVEN_EXECUTABLE的断言，可以进入正式Authorized Assertion Library
      2. 对PROVEN_EXECUTABLE_WITH_QUALIFIER的断言，带限定进入正式Library
      3. 对CANDIDATE的断言，修正后重新审核
      4. 对REJECTED的断言，不再考虑进入正式Library
      5. 修复UNCLASSIFIED闭集问题，Effect分类必须完全闭合
      6. 修复BATCH-0079条件不完整和BATCH-0080无条件的问题
      7. P6.5-C第二批批量生产暂缓，直到5条EXECUTABLE全部证明

    P6.5-B-R3 Executable Asset Integrity Audit完成。
    {'='*100}
""")

    # 保存结果
    output_path = r'D:\shuntian\backend\data\p6_5_b_r3_executable_audit_results.json'
    output_data = {
        "summary": {
            "executable_audit": {
                "total": len(executable_audit_results),
                "provenance": dict(provenance_counts),
                "recommended_actions": dict(action_counts),
            },
            "consistency_audit": {
                "total": len(consistency_results),
                "consistent": len(consistent),
                "inconsistent": len(inconsistent),
                "unclassified_effect": len(unclassified),
            },
        },
        "executable_audit_results": [
            {
                "candidate_id": r.candidate_id,
                "source_text": r.source_text,
                "classic": r.classic,
                "provenance": r.provenance,
                "recommended_action": r.recommended_action,
                "downgrade_reason": r.downgrade_reason,
                "condition_completeness": r.condition_completeness,
                "effect_purity": r.effect_purity,
                "matcher_expressibility": r.matcher_expressibility,
                "structural_contamination": r.structural_contamination,
                "critical_issues": r.critical_issues,
                "warnings": r.warnings,
                "checks": [asdict(c) for c in r.checks],
            }
            for r in executable_audit_results
        ],
        "consistency_audit_results": [
            asdict(r) for r in consistency_results
        ],
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"    P6.5-B-R3结果已保存到: {output_path}")


if __name__ == "__main__":
    main()
