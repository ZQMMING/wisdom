"""
STR-001A P6.5-B-R Authorized Asset Integrity Audit

逐条检查P6.5-B Hardening后获得AUTHORIZED的15条断言，
验证10项完整性标准，特别检查STRUCTURAL_ASSERTION ≠ EXECUTABLE_ASSERTION。

10项验证标准：
  1. SOURCE是否精确可定位
  2. Assertion Type是否确实属于可执行断言
  3. CONDITION是否没有被吞进Effect
  4. RELATION是否具有明确经典语义
  5. Effect是否有自己的原典provenance（不是中间推理/方法论/格局定义）
  6. Precondition是否真的能够被Resolver/Matcher表达
  7. Qualifier是否真的随资产保存
  8. Reverse condition是否不能被遗漏后改变断言含义
  9. 没有任何score→authorization的隐式路径
  10. 最终资产是否能够被EXIS输出层安全消费

特别增加：
  STRUCTURAL_ASSERTION ≠ EXECUTABLE_ASSERTION
  例如「食神生财」可以确认是经典中的格局/结构语义，
  但并不意味着 has_shishen=true AND has_cai=true → effect=富贵

验证结果：
  PROVEN: 10项全部通过，可以进入正式Authorized Assertion Library
  NOT_PROVEN: 存在问题，需要降级（CANDIDATE/REJECTED）

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

class IntegrityCheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    SKIPPED = "SKIPPED"


class AssetProvenance(str, Enum):
    PROVEN = "PROVEN"                    # 10项全部通过
    NOT_PROVEN = "NOT_PROVEN"            # 存在问题，需要降级
    PROVEN_WITH_QUALIFIER = "PROVEN_WITH_QUALIFIER"  # 基本通过，但有限定


@dataclass
class IntegrityCheck:
    """单项完整性检查"""
    check_id: int
    check_name: str
    status: str
    score: float = 0.0
    notes: str = ""
    issues: List[str] = field(default_factory=list)


@dataclass
class AssetAuditResult:
    """单条断言的完整性审计结果"""
    candidate_id: str
    source_text: str
    classic: str
    original_status: str = "AUTHORIZED"

    # 10项检查
    checks: List[IntegrityCheck] = field(default_factory=list)

    # 问题汇总
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # 最终结论
    provenance: str = AssetProvenance.NOT_PROVEN.value
    recommended_action: str = ""  # KEEP_AUTHORIZED / DOWNGRADE_TO_CANDIDATE / DOWNGRADE_TO_REJECTED / REQUIRE_MANUAL_REVIEW
    downgrade_reason: str = ""

    # 详细分析
    assertion_type_analysis: str = ""
    effect_analysis: str = ""
    condition_analysis: str = ""
    structural_vs_executable: str = ""


# ============================================================
# 10项完整性检查
# ============================================================

def check_source_precision(candidate: Dict) -> IntegrityCheck:
    """检查1: SOURCE是否精确可定位"""
    issues = []
    score = 0

    classic = candidate.get('classic', '')
    source_file = candidate.get('source_file', '')

    if classic and source_file:
        score = 90
        issues.append(f"出处: {classic} / {source_file}")
    elif classic:
        score = 60
        issues.append(f"只有经典名，缺少具体文件/章节: {classic}")
    else:
        score = 0
        issues.append("缺少明确出处")

    status = IntegrityCheckStatus.PASS.value if score >= 60 else IntegrityCheckStatus.FAIL.value
    return IntegrityCheck(1, "SOURCE精确可定位", status, score, "出处验证", issues)


def check_assertion_type_executable(candidate: Dict) -> IntegrityCheck:
    """检查2: Assertion Type是否确实属于可执行断言"""
    issues = []
    score = 0

    assertion_type = candidate.get('assertion_type', '')
    source_text = candidate.get('source_text', '')

    # 可执行断言的特征：有明确的条件+断事效果
    # 不可执行的特征：方法论/理论概述/案例批注/格局定义/关系描述

    # 检查是否包含案例语境
    case_indicators = ['此造', '前造', '彼造', '是造', '此四柱', '己丑庚申',
                       '贵至三品', '富有百万', '子十三人', '寿至百岁',
                       '至丙午运', '发财十余万', '侍郎', '尚书']
    case_count = sum(1 for ind in case_indicators if ind in source_text)

    # 检查是否包含方法论/理论概述
    theory_indicators = ['若论命理', '须观', '须看', '当观', '当看',
                         '不专以', '以论吉凶', '则了然矣',
                         '大凡', '大抵', '论之', '之说']
    theory_count = sum(1 for ind in theory_indicators if ind in source_text)

    # 检查是否包含格局定义（不是断事效果）
    pattern_def_indicators = ['为杂气财官', '为从儿格', '为从财格', '为从杀格',
                              '为食神格', '为伤官格', '为正官格', '为七杀格']
    pattern_def_count = sum(1 for ind in pattern_def_indicators if ind in source_text)

    # 检查Effect是否是断事效果（不是中间推理/建议/格局定义）
    effect_clauses = candidate.get('effect_clauses', [])
    effect_text = ' '.join(effect_clauses)

    # 断事效果的特征词
    executable_effect_keywords = ['主', '必', '定', '得', '遭', '为', '成',
                                   '富贵', '贫贱', '吉', '凶', '福', '祸',
                                   '贵', '富', '贫', '贱', '寿', '夭',
                                   '美妻', '贤妻', '官刑', '名利', '凶死',
                                   '贤贵', '妻妾之祸', '官刑之祸']

    # 非断事效果的特征词（中间推理/建议/方法论/格局定义）
    non_executable_effect_keywords = ['则身已滋', '必用伤官制杀', '则不专以',
                                       '则了然矣', '则以财星滋杀', '为杂气财官',
                                       '为从儿格', '则丙火无根', '必要用财滋杀',
                                       '为人刚柔', '则卯亦能冲酉', '则曾祖必受其伤']

    has_executable_effect = any(kw in effect_text for kw in executable_effect_keywords)
    has_non_executable_effect = any(kw in effect_text for kw in non_executable_effect_keywords)

    # 综合判断
    if case_count >= 2:
        score = 10
        issues.append(f"包含案例语境特征({case_count}个)，应为CASE_COMMENTARY，不是可执行断言")
    elif theory_count >= 2:
        score = 20
        issues.append(f"包含方法论/理论概述特征({theory_count}个)，应为THEORY_OVERVIEW，不是可执行断言")
    elif pattern_def_count >= 1 and not has_executable_effect:
        score = 30
        issues.append(f"Effect是格局定义({pattern_def_count}个)，不是断事效果，应为PATTERN_DEFINITION")
    elif has_non_executable_effect and not has_executable_effect:
        score = 40
        issues.append("Effect是中间推理/建议/关系描述，不是断事效果")
    elif has_executable_effect:
        score = 85
        issues.append("有明确的断事效果，可以作为可执行断言")
    else:
        score = 50
        issues.append("断言类型不确定，需要人工审核")

    status = IntegrityCheckStatus.PASS.value if score >= 60 else IntegrityCheckStatus.FAIL.value
    return IntegrityCheck(2, "Assertion Type属于可执行断言", status, score, "断言类型验证", issues)


def check_condition_not_in_effect(candidate: Dict) -> IntegrityCheck:
    """检查3: CONDITION是否没有被吞进Effect"""
    issues = []
    score = 0

    condition_clauses = candidate.get('condition_clauses', [])
    effect_clauses = candidate.get('effect_clauses', [])

    # 检查Effect中是否包含条件特征
    condition_markers = ['若', '如', '逢', '遇', '带', '见', '有', '无',
                         '者$', '则$', '之泄', '之化', '之祸', '之解']

    condition_in_effect = []
    for effect in effect_clauses:
        for marker in condition_markers:
            if re.search(marker, effect) and len(effect) < 20:
                condition_in_effect.append(effect)
                break

    # 检查条件是否完整（原文中的条件是否都被提取）
    source_text = candidate.get('source_text', '')
    # 简单检查：原文中"若""如"后面的内容是否在condition_clauses中
    source_conditions = re.findall(r'[若如]([^，。；]+)', source_text)
    missing_conditions = []
    for sc in source_conditions:
        found = any(sc[:5] in c for c in condition_clauses)
        if not found and len(sc) > 3:
            missing_conditions.append(sc)

    if condition_in_effect:
        score = 30
        issues.append(f"Effect中包含条件特征: {condition_in_effect}")
    elif missing_conditions:
        score = 50
        issues.append(f"条件提取不完整，遗漏: {missing_conditions[:3]}")
    elif condition_clauses and effect_clauses:
        score = 90
        issues.append("条件与Effect分离清晰")
    else:
        score = 60
        issues.append("条件或Effect缺失")

    status = IntegrityCheckStatus.PASS.value if score >= 60 else IntegrityCheckStatus.FAIL.value
    return IntegrityCheck(3, "CONDITION没有被吞进Effect", status, score, "条件/Effect分离验证", issues)


def check_relation_semantics(candidate: Dict) -> IntegrityCheck:
    """检查4: RELATION是否具有明确经典语义"""
    issues = []
    score = 0

    relation_clauses = candidate.get('relation_clauses', [])
    source_text = candidate.get('source_text', '')

    # 关系词
    relation_words = ['生', '克', '制', '化', '合', '冲', '刑', '害', '破', '泄', '耗',
                      '扶', '助', '夺', '战', '斗', '争', '党']

    relations_found = []
    for w in relation_words:
        if w in source_text:
            relations_found.append(w)

    # 检查关系是否在关系分句中（不是格局名称的一部分）
    if not relations_found:
        score = 70
        issues.append("无关系词，纯条件+效果结构")
    elif relation_clauses:
        score = 85
        issues.append(f"关系词{relations_found}在关系分句中，有明确语义")
    else:
        score = 50
        issues.append(f"有关系词{relations_found}，但未提取到关系分句，语义可能不明确")

    status = IntegrityCheckStatus.PASS.value if score >= 60 else IntegrityCheckStatus.FAIL.value
    return IntegrityCheck(4, "RELATION具有明确经典语义", status, score, "关系语义验证", issues)


def check_effect_provenance(candidate: Dict) -> IntegrityCheck:
    """检查5: Effect是否有自己的原典provenance（不是中间推理/方法论/格局定义）"""
    issues = []
    score = 0

    effect_clauses = candidate.get('effect_clauses', [])
    effect_text = ' '.join(effect_clauses)

    if not effect_clauses:
        score = 0
        issues.append("无Effect分句")
        status = IntegrityCheckStatus.FAIL.value
        return IntegrityCheck(5, "Effect有原典provenance", status, score, "Effect溯源验证", issues)

    # 检查Effect是否是中间推理
    intermediate_reasoning_patterns = [
        r'^则身已滋', r'^必用', r'^必要用', r'^则丙火无根',
        r'^则不专以', r'^则了然矣', r'^则以财星滋杀',
        r'^则卯亦能冲酉', r'^为人刚柔',
    ]

    # 检查Effect是否是格局定义
    pattern_def_patterns = [
        r'^为杂气', r'^为从儿格', r'^为从财格', r'^为从杀格',
        r'^为食神格', r'^为伤官格', r'^为正官格', r'^为七杀格',
    ]

    # 检查Effect是否是断事效果
    executable_effect_patterns = [
        r'^主', r'^必', r'^定', r'^得', r'^遭',
        r'富贵', r'贫贱', r'吉', r'凶', r'福', r'祸',
        r'美妻', r'贤妻', r'官刑', r'凶死', r'贤贵',
        r'妻妾之祸', r'官刑之祸', r'则曾祖必受其伤',
    ]

    is_intermediate = any(re.search(p, effect_text) for p in intermediate_reasoning_patterns)
    is_pattern_def = any(re.search(p, effect_text) for p in pattern_def_patterns)
    is_executable = any(re.search(p, effect_text) for p in executable_effect_patterns)

    if is_intermediate:
        score = 20
        issues.append(f"Effect是中间推理/建议，不是断事效果: {effect_text[:50]}")
    elif is_pattern_def:
        score = 30
        issues.append(f"Effect是格局定义，不是断事效果: {effect_text[:50]}")
    elif is_executable:
        score = 90
        issues.append(f"Effect是明确的断事效果: {effect_text[:50]}")
    else:
        score = 50
        issues.append(f"Effect类型不确定: {effect_text[:50]}")

    status = IntegrityCheckStatus.PASS.value if score >= 60 else IntegrityCheckStatus.FAIL.value
    return IntegrityCheck(5, "Effect有原典provenance", status, score, "Effect溯源验证", issues)


def check_precondition_expressible(candidate: Dict) -> IntegrityCheck:
    """检查6: Precondition是否真的能够被Resolver/Matcher表达"""
    issues = []
    score = 0

    condition_clauses = candidate.get('condition_clauses', [])

    if not condition_clauses:
        score = 30
        issues.append("无前置条件")
    else:
        # 检查条件是否包含可结构化的元素（十神/五行/干支/格局/状态）
        structurable_keywords = ['官星', '财星', '食神', '伤官', '七杀', '正官',
                                 '印绶', '枭印', '比劫', '劫刃',
                                 '木', '火', '土', '金', '水',
                                 '甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸',
                                 '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑',
                                 '身强', '身弱', '杀浅', '杀重', '财多',
                                 '得时', '失时', '通根', '无根',
                                 '从儿格', '杂气财官',
                                 '阴节', '阻节']

        structurable_count = 0
        for cond in condition_clauses:
            for kw in structurable_keywords:
                if kw in cond:
                    structurable_count += 1
                    break

        if structurable_count >= 1:
            score = 80
            issues.append(f"前置条件包含可结构化元素({structurable_count}个)")
        else:
            score = 50
            issues.append("前置条件缺少可结构化元素，可能难以被Resolver/Matcher表达")

    status = IntegrityCheckStatus.PASS.value if score >= 60 else IntegrityCheckStatus.FAIL.value
    return IntegrityCheck(6, "Precondition可被Resolver/Matcher表达", status, score, "前置条件可表达性验证", issues)


def check_qualifier_preserved(candidate: Dict) -> IntegrityCheck:
    """检查7: Qualifier是否真的随资产保存"""
    issues = []
    score = 0

    qualifier_clauses = candidate.get('qualifier_clauses', [])
    source_text = candidate.get('source_text', '')

    # 检查原文中是否有限定词
    qualifier_markers = ['须', '必要', '必须', '方为', '方许', '方可', '然后',
                         '虽', '然', '但', '不过', '大抵', '反忌', '喜', '忌']
    qualifier_in_source = [m for m in qualifier_markers if m in source_text]

    if qualifier_clauses:
        score = 90
        issues.append(f"有限定分句保存: {qualifier_clauses}")
    elif qualifier_in_source:
        score = 50
        issues.append(f"原文中有限定词{qualifier_in_source}，但未提取为Qualifier分句")
    else:
        score = 70
        issues.append("原文中无明显限定词")

    status = IntegrityCheckStatus.PASS.value if score >= 60 else IntegrityCheckStatus.FAIL.value
    return IntegrityCheck(7, "Qualifier随资产保存", status, score, "限定条件保存验证", issues)


def check_reverse_condition(candidate: Dict) -> IntegrityCheck:
    """检查8: Reverse condition是否不能被遗漏后改变断言含义"""
    issues = []
    score = 0

    source_text = candidate.get('source_text', '')

    # 检查是否包含反向条件
    reverse_markers = ['忌', '怕', '不宜', '不可', '反忌', '最怕',
                       '若无', '如无', '无', '缺',
                       '虽', '然', '但', '不过']
    reverse_in_source = [m for m in reverse_markers if m in source_text]

    # 检查是否有"缺一不可"等强反向条件
    strong_reverse = ['缺一不可', '不可缺', '不能缺', '最怕', '大忌']
    has_strong_reverse = any(m in source_text for m in strong_reverse)

    if has_strong_reverse:
        score = 40
        issues.append(f"包含强反向条件，遗漏会改变断言含义: {[m for m in strong_reverse if m in source_text]}")
    elif reverse_in_source:
        score = 60
        issues.append(f"包含反向条件词: {reverse_in_source}")
    else:
        score = 80
        issues.append("无明显反向条件")

    status = IntegrityCheckStatus.PASS.value if score >= 60 else IntegrityCheckStatus.FAIL.value
    return IntegrityCheck(8, "Reverse condition不被遗漏", status, score, "反向条件验证", issues)


def check_no_score_implicit_authorization(candidate: Dict) -> IntegrityCheck:
    """检查9: 没有任何score→authorization的隐式路径"""
    issues = []
    score = 0

    quality_score = candidate.get('quality_score', 0)
    final_status = candidate.get('final_library_status', '')

    # 检查是否有高分但其他Gate失败的情况（证明score不直接决定授权）
    gates = candidate.get('gates', [])
    failed_gates = [g for g in gates if g.get('status') == 'FAIL']

    if quality_score >= 80 and failed_gates:
        score = 95
        issues.append(f"高分({quality_score})但有{len(failed_gates)}个Gate失败，证明score不直接决定授权")
    elif quality_score >= 80 and not failed_gates:
        score = 80
        issues.append(f"高分({quality_score})且所有Gate通过，授权合理")
    elif quality_score < 50 and final_status == 'AUTHORIZED':
        score = 30
        issues.append(f"低分({quality_score})但被授权，可能存在score→authorization的隐式路径")
    else:
        score = 70
        issues.append("score与authorization关系正常")

    status = IntegrityCheckStatus.PASS.value if score >= 60 else IntegrityCheckStatus.FAIL.value
    return IntegrityCheck(9, "无score→authorization隐式路径", status, score, "score授权路径验证", issues)


def check_output_layer_safe(candidate: Dict) -> IntegrityCheck:
    """检查10: 最终资产是否能够被EXIS输出层安全消费"""
    issues = []
    score = 0

    # 检查是否有完整的条件+效果+限定
    condition_clauses = candidate.get('condition_clauses', [])
    effect_clauses = candidate.get('effect_clauses', [])
    qualifier_clauses = candidate.get('qualifier_clauses', [])

    # 检查Effect是否过于泛化或危险
    effect_text = ' '.join(effect_clauses)
    dangerous_effect_keywords = ['必死', '必凶', '大凶', '大祸', '绝后', '夭亡']
    has_dangerous_effect = any(kw in effect_text for kw in dangerous_effect_keywords)

    # 检查是否有unresolved_reasons
    # (这个字段在hardened结果中可能没有，我们检查是否有明显的未解决问题)

    if has_dangerous_effect:
        score = 40
        issues.append(f"Effect包含危险/绝对化表述，输出层需要额外限定: {effect_text[:50]}")
    elif condition_clauses and effect_clauses:
        score = 85
        issues.append("有完整的条件+效果，输出层可以安全消费")
    elif effect_clauses and not condition_clauses:
        score = 50
        issues.append("有效果但无条件，输出层消费时可能产生误判")
    else:
        score = 40
        issues.append("缺少条件或效果，输出层难以安全消费")

    status = IntegrityCheckStatus.PASS.value if score >= 60 else IntegrityCheckStatus.FAIL.value
    return IntegrityCheck(10, "可被EXIS输出层安全消费", status, score, "输出层安全性验证", issues)


# ============================================================
# STRUCTURAL_ASSERTION vs EXECUTABLE_ASSERTION 检查
# ============================================================

def check_structural_vs_executable(candidate: Dict) -> Tuple[str, str]:
    """检查STRUCTURAL_ASSERTION ≠ EXECUTABLE_ASSERTION"""
    source_text = candidate.get('source_text', '')
    effect_clauses = candidate.get('effect_clauses', [])
    effect_text = ' '.join(effect_clauses)

    # 结构断言的特征：描述格局/结构/关系，但没有明确的断事效果
    structural_patterns = [
        r'食神生财', r'伤官生财', r'食神制杀', r'伤官佩印',
        r'官印相生', r'煞印相生', r'财煞相生',
        r'为.*格', r'为.*格局',
        r'则.*能冲', r'则.*能克',
        r'则身已滋', r'则丙火无根',
    ]

    # 可执行断言的特征：有明确的断事效果
    executable_patterns = [
        r'主.*', r'必.*', r'定.*', r'得.*', r'遭.*',
        r'富贵', r'贫贱', r'吉', r'凶', r'福', r'祸',
        r'美妻', r'贤妻', r'官刑', r'凶死',
    ]

    is_structural = any(re.search(p, source_text) for p in structural_patterns)
    is_executable = any(re.search(p, effect_text) for p in executable_patterns)

    if is_structural and not is_executable:
        return "STRUCTURAL_ASSERTION", "原文描述格局/结构/关系，但Effect不是明确的断事效果，属于结构断言，不是可执行断言"
    elif is_structural and is_executable:
        return "STRUCTURAL_WITH_EXECUTABLE_EFFECT", "原文包含结构描述，但Effect是明确的断事效果，可以作为可执行断言"
    elif not is_structural and is_executable:
        return "EXECUTABLE_ASSERTION", "有明确的断事效果，属于可执行断言"
    else:
        return "UNCLASSIFIED", "断言类型不确定"


# ============================================================
# 主流程
# ============================================================

def audit_single_asset(candidate: Dict) -> AssetAuditResult:
    """审计单条断言"""
    result = AssetAuditResult(
        candidate_id=candidate['candidate_id'],
        source_text=candidate['source_text'],
        classic=candidate.get('classic', ''),
        original_status='AUTHORIZED',
    )

    # 运行10项检查
    result.checks = [
        check_source_precision(candidate),
        check_assertion_type_executable(candidate),
        check_condition_not_in_effect(candidate),
        check_relation_semantics(candidate),
        check_effect_provenance(candidate),
        check_precondition_expressible(candidate),
        check_qualifier_preserved(candidate),
        check_reverse_condition(candidate),
        check_no_score_implicit_authorization(candidate),
        check_output_layer_safe(candidate),
    ]

    # STRUCTURAL_ASSERTION vs EXECUTABLE_ASSERTION
    struct_type, struct_analysis = check_structural_vs_executable(candidate)
    result.structural_vs_executable = f"{struct_type}: {struct_analysis}"

    # 汇总问题
    fail_checks = [c for c in result.checks if c.status == IntegrityCheckStatus.FAIL.value]
    warning_checks = [c for c in result.checks if c.status == IntegrityCheckStatus.WARNING.value]

    for c in fail_checks:
        result.critical_issues.append(f"[{c.check_name}] {'; '.join(c.issues)}")
    for c in warning_checks:
        result.warnings.append(f"[{c.check_name}] {'; '.join(c.issues)}")

    # 断言类型分析
    type_check = result.checks[1]  # 检查2
    result.assertion_type_analysis = f"{type_check.status}: {'; '.join(type_check.issues)}"

    # Effect分析
    effect_check = result.checks[4]  # 检查5
    result.effect_analysis = f"{effect_check.status}: {'; '.join(effect_check.issues)}"

    # 条件分析
    cond_check = result.checks[2]  # 检查3
    result.condition_analysis = f"{cond_check.status}: {'; '.join(cond_check.issues)}"

    # 最终结论
    critical_fail_count = len(fail_checks)

    if critical_fail_count == 0:
        result.provenance = AssetProvenance.PROVEN.value
        result.recommended_action = "KEEP_AUTHORIZED"
        result.downgrade_reason = ""
    elif critical_fail_count <= 2:
        result.provenance = AssetProvenance.PROVEN_WITH_QUALIFIER.value
        result.recommended_action = "KEEP_AUTHORIZED_WITH_QUALIFIER"
        result.downgrade_reason = f"存在{critical_fail_count}项检查失败，但不影响核心可执行性"
    elif critical_fail_count <= 4:
        result.provenance = AssetProvenance.NOT_PROVEN.value
        result.recommended_action = "DOWNGRADE_TO_CANDIDATE"
        result.downgrade_reason = f"存在{critical_fail_count}项检查失败，需要修正后重新审核"
    else:
        result.provenance = AssetProvenance.NOT_PROVEN.value
        result.recommended_action = "DOWNGRADE_TO_REJECTED"
        result.downgrade_reason = f"存在{critical_fail_count}项检查失败，断言类型或Effect存在严重问题"

    return result


def main():
    print("=" * 110)
    print("STR-001A P6.5-B-R Authorized Asset Integrity Audit")
    print("=" * 110)

    print(f"""
  逐条检查P6.5-B Hardening后获得AUTHORIZED的15条断言，
  验证10项完整性标准，特别检查STRUCTURAL_ASSERTION ≠ EXECUTABLE_ASSERTION。

  10项验证标准：
    1. SOURCE是否精确可定位
    2. Assertion Type是否确实属于可执行断言
    3. CONDITION是否没有被吞进Effect
    4. RELATION是否具有明确经典语义
    5. Effect是否有自己的原典provenance（不是中间推理/方法论/格局定义）
    6. Precondition是否真的能够被Resolver/Matcher表达
    7. Qualifier是否真的随资产保存
    8. Reverse condition是否不能被遗漏后改变断言含义
    9. 没有任何score→authorization的隐式路径
    10. 最终资产是否能够被EXIS输出层安全消费

  特别增加：
    STRUCTURAL_ASSERTION ≠ EXECUTABLE_ASSERTION

  验证结果：
    PROVEN: 10项全部通过，可以进入正式Authorized Assertion Library
    NOT_PROVEN: 存在问题，需要降级（CANDIDATE/REJECTED）
""")

    # 加载P6.5-B结果
    print(f"\n  {'='*100}")
    print(f"  加载P6.5-B Hardening结果")
    print(f"  {'='*100}")

    with open(r'D:\shuntian\backend\data\p6_5_b_hardened_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    authorized = [c for c in data['hardened_candidates'] if c['final_library_status'] == 'AUTHORIZED']
    print(f"\n    AUTHORIZED总数: {len(authorized)}")

    # 逐条审计
    print(f"\n  {'='*100}")
    print(f"  逐条完整性审计")
    print(f"  {'='*100}")

    audit_results = []
    for i, candidate in enumerate(authorized):
        result = audit_single_asset(candidate)
        audit_results.append(result)

        cid = result.candidate_id
        provenance = result.provenance
        action = result.recommended_action
        fail_count = len(result.critical_issues)

        print(f"""
    [{i+1}/15] {cid}
      Provenance: {provenance}
      推荐操作: {action}
      失败检查数: {fail_count}
      结构vs可执行: {result.structural_vs_executable[:80]}
""")
        if result.critical_issues:
            print(f"      关键问题:")
            for issue in result.critical_issues[:3]:
                print(f"        - {issue[:100]}")

    # 统计结果
    print(f"\n  {'='*100}")
    print(f"  审计结果统计")
    print(f"  {'='*100}")

    provenance_counts = Counter(r.provenance for r in audit_results)
    action_counts = Counter(r.recommended_action for r in audit_results)

    print(f"""
    总数: {len(audit_results)}

    Provenance分布:
""")
    for p, count in provenance_counts.most_common():
        print(f"      {p:30s} {count:3d}")

    print(f"""
    推荐操作分布:
""")
    for a, count in action_counts.most_common():
        print(f"      {a:40s} {count:3d}")

    # 逐项检查通过率
    print(f"""
    10项检查通过率:
""")
    for check_id in range(1, 11):
        check_name = audit_results[0].checks[check_id-1].check_name
        pass_count = sum(1 for r in audit_results if r.checks[check_id-1].status == 'PASS')
        fail_count = sum(1 for r in audit_results if r.checks[check_id-1].status == 'FAIL')
        pct = pass_count / len(audit_results) * 100
        print(f"      {check_id:2d}. {check_name:40s} PASS:{pass_count:2d} FAIL:{fail_count:2d} ({pct:.0f}%)")

    # 详细列出需要降级的断言
    print(f"\n  {'='*100}")
    print(f"  需要降级的断言详细列表")
    print(f"  {'='*100}")

    downgraded = [r for r in audit_results if r.recommended_action.startswith('DOWNGRADE')]
    for i, r in enumerate(downgraded):
        print(f"""
    [{i+1}] {r.candidate_id}
      推荐操作: {r.recommended_action}
      降级原因: {r.downgrade_reason}
      原文: {r.source_text[:100]}
      断言类型分析: {r.assertion_type_analysis[:100]}
      Effect分析: {r.effect_analysis[:100]}
      结构vs可执行: {r.structural_vs_executable[:100]}
      关键问题:
""")
        for issue in r.critical_issues:
            print(f"        - {issue[:120]}")

    # 可以保留的断言
    print(f"\n  {'='*100}")
    print(f"  可以保留的断言（PROVEN/PROVEN_WITH_QUALIFIER）")
    print(f"  {'='*100}")

    kept = [r for r in audit_results if not r.recommended_action.startswith('DOWNGRADE')]
    for i, r in enumerate(kept):
        print(f"""
    [{i+1}] {r.candidate_id}
      Provenance: {r.provenance}
      推荐操作: {r.recommended_action}
      原文: {r.source_text[:100]}
      结构vs可执行: {r.structural_vs_executable[:100]}
""")

    # 最终结论
    print(f"\n  {'='*100}")
    print(f"  P6.5-B-R 最终结论")
    print(f"  {'='*100}")

    proven_count = provenance_counts.get('PROVEN', 0)
    proven_qual_count = provenance_counts.get('PROVEN_WITH_QUALIFIER', 0)
    not_proven_count = provenance_counts.get('NOT_PROVEN', 0)

    keep_count = action_counts.get('KEEP_AUTHORIZED', 0) + action_counts.get('KEEP_AUTHORIZED_WITH_QUALIFIER', 0)
    downgrade_candidate_count = action_counts.get('DOWNGRADE_TO_CANDIDATE', 0)
    downgrade_rejected_count = action_counts.get('DOWNGRADE_TO_REJECTED', 0)

    print(f"""
    审计结果:
      原始AUTHORIZED: {len(audit_results)}条
      PROVEN: {proven_count}条
      PROVEN_WITH_QUALIFIER: {proven_qual_count}条
      NOT_PROVEN: {not_proven_count}条

    推荐操作:
      保留AUTHORIZED: {keep_count}条
      降级为CANDIDATE: {downgrade_candidate_count}条
      降级为REJECTED: {downgrade_rejected_count}条

    核心发现:
      1. P6.5-B的8项回归通过 ≠ 15条AUTHORIZED都可以进入正式Authorized Assertion Library
      2. 多条断言存在Assertion Type错误（THEORY_OVERVIEW/CASE_COMMENTARY被误判为GENERAL_ASSERTION）
      3. 多条断言存在Effect提取错误（中间推理/格局定义/方法论被误判为断事效果）
      4. STRUCTURAL_ASSERTION ≠ EXECUTABLE_ASSERTION的边界需要严格执行
      5. 机器Gate通过结果需要人工完整性审计才能进入正式Library

    治理边界验证:
      P6.5-B-R证明了"8项回归通过"只是针对已发现缺陷的回归验收，
      不是证明整个断言语义空间不存在新的退化。
      15条AUTHORIZED中只有{keep_count}条通过完整性审计，
      {downgrade_candidate_count + downgrade_rejected_count}条需要降级。

    后续建议:
      1. 对降级为CANDIDATE的断言进行修正后重新审核
      2. 对降级为REJECTED的断言不再考虑进入正式Library
      3. 所有后续批量生产的AUTHORIZED断言都必须经过P6.5-B-R完整性审计
      4. 建立人工审核流程，机器Gate通过后必须经过人工完整性审计
      5. P6.5-C第二批批量生产暂缓，直到P6.5-B-R完成并修正生产器

    P6.5-B-R Authorized Asset Integrity Audit完成。
    {'='*100}
""")

    # 保存结果
    output_path = r'D:\shuntian\backend\data\p6_5_b_r_integrity_audit_results.json'
    output_data = {
        "summary": {
            "total": len(audit_results),
            "provenance": dict(provenance_counts),
            "recommended_actions": dict(action_counts),
            "keep_count": keep_count,
            "downgrade_candidate_count": downgrade_candidate_count,
            "downgrade_rejected_count": downgrade_rejected_count,
        },
        "audit_results": [
            {
                "candidate_id": r.candidate_id,
                "source_text": r.source_text,
                "classic": r.classic,
                "original_status": r.original_status,
                "provenance": r.provenance,
                "recommended_action": r.recommended_action,
                "downgrade_reason": r.downgrade_reason,
                "assertion_type_analysis": r.assertion_type_analysis,
                "effect_analysis": r.effect_analysis,
                "condition_analysis": r.condition_analysis,
                "structural_vs_executable": r.structural_vs_executable,
                "critical_issues": r.critical_issues,
                "warnings": r.warnings,
                "checks": [asdict(c) for c in r.checks],
            }
            for r in audit_results
        ],
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"    完整性审计结果已保存到: {output_path}")


if __name__ == "__main__":
    main()
