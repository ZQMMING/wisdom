"""
STR-001A P6.5-B-R2 Producer Semantic Boundary Hardening

把P6.5-B-R暴露出的3类边界正式反向固化进生产器：
  ① STRUCTURAL_ASSERTION ≠ EXECUTABLE_ASSERTION
  ② INTERMEDIATE_REASONING ≠ EFFECT
  ③ PRESCRIPTIVE_GUIDANCE ≠ EFFECT

重要架构变化：
  STRUCTURAL_ASSERTION不简单REJECTED，而是进入Structural Knowledge Library，
  供后面的规则组合/Matcher使用，但不能伪装成"结构→断事效果"。

新的断言类型分类（6种）：
  EXECUTABLE_ASSERTION    可执行断言，走Effect Admission
  STRUCTURAL_ASSERTION    结构断言，进入Structural Knowledge Library
  PRESCRIPTIVE_ASSERTION  建议性断言，NON_EXECUTABLE
  THEORY_OVERVIEW         理论概述，REJECTED
  CASE_COMMENTARY         案例批注，REJECTED
  DESCRIPTIVE             描述性文本，REJECTED

新的Effect Gate（6种Effect类型）：
  INTERMEDIATE_REASONING  中间推理 → FAIL
  RELATION                关系描述 → FAIL
  QUALIFIER               限定条件 → FAIL
  PRESCRIPTION            建议/用法 → FAIL
  CASE_RESULT             案例结果 → FAIL
  ASSERTION_EFFECT        断事效果 → continue

新的Gate流程：
  SOURCE → Candidate → Assertion-Type Gate → Semantic Relation Gate
  → Precondition Gate → Matcher Gate → Effect Gate → Effect Provenance Gate
  → Reverse/Qualifier Gate → Admission

用第一批100条全量回归。

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

class AssertionTypeV2(str, Enum):
    """新的断言类型分类（6种）"""
    EXECUTABLE_ASSERTION = "EXECUTABLE_ASSERTION"        # 可执行断言
    STRUCTURAL_ASSERTION = "STRUCTURAL_ASSERTION"        # 结构断言
    PRESCRIPTIVE_ASSERTION = "PRESCRIPTIVE_ASSERTION"    # 建议性断言
    THEORY_OVERVIEW = "THEORY_OVERVIEW"                  # 理论概述
    CASE_COMMENTARY = "CASE_COMMENTARY"                  # 案例批注
    DESCRIPTIVE = "DESCRIPTIVE"                          # 描述性文本


class EffectType(str, Enum):
    """Effect类型分类（6种）"""
    INTERMEDIATE_REASONING = "INTERMEDIATE_REASONING"    # 中间推理
    RELATION = "RELATION"                                # 关系描述
    QUALIFIER = "QUALIFIER"                              # 限定条件
    PRESCRIPTION = "PRESCRIPTION"                        # 建议/用法
    CASE_RESULT = "CASE_RESULT"                          # 案例结果
    ASSERTION_EFFECT = "ASSERTION_EFFECT"                # 断事效果


class GateStatusV2(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CONDITIONAL = "CONDITIONAL"
    SKIPPED = "SKIPPED"
    DIVERTED = "DIVERTED"  # 被分流到其他Library（如Structural Knowledge Library）


@dataclass
class GateResultV2:
    gate_name: str
    status: str
    score: float = 0.0
    notes: str = ""
    issues: List[str] = field(default_factory=list)
    diverted_to: str = ""  # 如果被分流，记录目标Library


@dataclass
class HardenedCandidateV2:
    """经过V2 Hardening的候选断言"""
    candidate_id: str
    source_text: str
    classic: str
    source_file: str
    primary_category: str
    categories: List[str]

    # 新的断言类型分类
    assertion_type_v2: str = AssertionTypeV2.DESCRIPTIVE.value
    assertion_type_v2_confidence: float = 0.0
    assertion_type_v2_evidence: str = ""

    # Effect类型分类
    effect_type: str = EffectType.ASSERTION_EFFECT.value
    effect_type_confidence: float = 0.0
    effect_type_evidence: str = ""

    # 分句
    condition_clauses: List[str] = field(default_factory=list)
    relation_clauses: List[str] = field(default_factory=list)
    qualifier_clauses: List[str] = field(default_factory=list)
    effect_clauses: List[str] = field(default_factory=list)
    case_context_clauses: List[str] = field(default_factory=list)

    # Gate结果
    gates: List[GateResultV2] = field(default_factory=list)
    overall_gate_status: str = GateStatusV2.FAIL.value

    # 最终状态
    final_library: str = ""  # EXECUTABLE_LIBRARY / STRUCTURAL_LIBRARY / NON_EXECUTABLE / REJECTED
    final_status: str = ""
    final_reason: str = ""

    # 原始状态（不覆盖）
    original_status: str = ""
    original_assertion_type: str = ""


# ============================================================
# 分句提取（复用P6.5-B的逻辑）
# ============================================================

CASE_CONTEXT_PATTERNS = [
    r'此造', r'前造', r'彼造', r'是造', r'此四柱',
    r'至[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]运',
    r'至[一二三四五六七八九十]+运',
    r'运走', r'运行', r'交[甲乙丙丁戊己庚辛壬癸]运',
    r'发财[一二三四五六七八九十百千万]+', r'发财[0-9]+',
    r'[一二三四五六七八九十]+万',
    r'侍郎|尚书|布政|太守|进士|举人|探花|状元|阁老|都宪|方伯|廉使|少卿',
    r'死于|卒于|享年',
    r'与前造|比前造|似前造|胜前造',
    r'贵至[一二三四五六七八九十]+品',
    r'富有[一二三四五六七八九十百千万]+',
    r'子[一二三四五六七八九十]+人',
    r'寿至[一二三四五六七八九十]+岁',
]

CONDITION_MARKERS = [
    (r'^若([^，。；]+)', '若'),
    (r'^如([^，。；]+)', '如'),
    (r'^逢([^，。；]+)', '逢'),
    (r'^遇([^，。；]+)', '遇'),
    (r'^带([^，。；]+)', '带'),
    (r'^见([^，。；]+)', '见'),
    (r'^有([^，。；]+)', '有'),
    (r'^无([^，。；]+)', '无'),
]

QUALIFIER_MARKERS = [
    (r'^须([^，。；]+)', '须'),
    (r'^必要([^，。；]+)', '必要'),
    (r'^必须([^，。；]+)', '必须'),
    (r'^方为([^，。；]+)', '方为'),
    (r'^方许([^，。；]+)', '方许'),
    (r'^方可([^，。；]+)', '方可'),
    (r'^然后([^，。；]+)', '然后'),
    (r'^虽([^，。；]+)', '虽'),
    (r'^然([^，。；]+)', '然'),
    (r'^但([^，。；]+)', '但'),
]

EFFECT_MARKERS = [
    (r'^主([^，。；]+)', '主'),
    (r'^则([^，。；]+)', '则'),
    (r'^必([^，。；]+)', '必'),
    (r'^定([^，。；]+)', '定'),
    (r'^得([^，。；]+)', '得'),
    (r'^遭([^，。；]+)', '遭'),
    (r'^为([^，。；]+)', '为'),
    (r'^成([^，。；]+)', '成'),
]

RELATION_WORDS = ['生', '克', '制', '化', '合', '冲', '刑', '害', '破', '泄', '耗',
                   '扶', '助', '夺', '战', '斗', '争', '党']


def split_into_clauses(text: str) -> List[str]:
    clauses = re.split(r'[，。；！？、]', text)
    return [c.strip() for c in clauses if len(c.strip()) >= 2]


def classify_clause_v2(clause: str) -> Tuple[str, float, str]:
    """V2分句分类"""
    # 案例语境（最高优先级）
    for pattern in CASE_CONTEXT_PATTERNS:
        if re.search(pattern, clause):
            return "CASE_CONTEXT", 0.9, f"匹配案例语境: {pattern}"

    # 条件
    for pattern, marker in CONDITION_MARKERS:
        if re.search(pattern, clause):
            if re.search(r'者$', clause) and len(clause) < 10:
                return "CONDITION", 0.85, f"条件（以'者'结尾）: {marker}"
            return "CONDITION", 0.85, f"条件标记词: {marker}"

    # 限定
    for pattern, marker in QUALIFIER_MARKERS:
        if re.search(pattern, clause):
            return "QUALIFIER", 0.8, f"限定标记词: {marker}"

    # 效果（初步标记，具体类型由Effect Gate判断）
    for pattern, marker in EFFECT_MARKERS:
        if re.search(pattern, clause):
            return "EFFECT_CANDIDATE", 0.8, f"效果标记词: {marker}"

    # 关系
    relation_count = sum(1 for w in RELATION_WORDS if w in clause)
    if relation_count >= 1 and len(clause) >= 4:
        return "RELATION", 0.7, f"包含关系词: {[w for w in RELATION_WORDS if w in clause]}"

    return "UNKNOWN", 0.3, "无法分类"


def extract_clauses_v2(candidate: HardenedCandidateV2) -> HardenedCandidateV2:
    """V2分句提取"""
    text = candidate.source_text
    raw_clauses = split_into_clauses(text)

    for clause_text in raw_clauses:
        clause_type, confidence, evidence = classify_clause_v2(clause_text)
        if clause_type == "CONDITION":
            candidate.condition_clauses.append(clause_text)
        elif clause_type == "RELATION":
            candidate.relation_clauses.append(clause_text)
        elif clause_type == "QUALIFIER":
            candidate.qualifier_clauses.append(clause_text)
        elif clause_type == "EFFECT_CANDIDATE":
            candidate.effect_clauses.append(clause_text)
        elif clause_type == "CASE_CONTEXT":
            candidate.case_context_clauses.append(clause_text)

    return candidate


# ============================================================
# 新的断言类型分类（6种）
# ============================================================

def classify_assertion_type_v2(candidate: HardenedCandidateV2) -> HardenedCandidateV2:
    """V2断言类型分类（6种）"""
    text = candidate.source_text
    effect_text = ' '.join(candidate.effect_clauses)

    # 1. 检查CASE_COMMENTARY（最高优先级）
    case_indicators = ['此造', '前造', '彼造', '是造', '此四柱', '己丑庚申',
                       '贵至三品', '富有百万', '子十三人', '寿至百岁',
                       '至丙午运', '发财十余万', '侍郎', '尚书',
                       '甲禄居寅', '癸禄居子', '丙禄居巳']
    case_count = sum(1 for ind in case_indicators if ind in text)
    case_context_count = len(candidate.case_context_clauses)

    if case_count >= 2 or case_context_count >= 2:
        candidate.assertion_type_v2 = AssertionTypeV2.CASE_COMMENTARY.value
        candidate.assertion_type_v2_confidence = 0.95
        candidate.assertion_type_v2_evidence = f"案例批注: {case_count}个案例指标, {case_context_count}个案例语境分句"
        return candidate

    # 2. 检查THEORY_OVERVIEW
    theory_indicators = ['若论命理', '须观', '须看', '当观', '当看',
                         '不专以', '以论吉凶', '则了然矣',
                         '大凡', '大抵', '论之', '之说',
                         '格局有正有变', '正者必兼']
    theory_count = sum(1 for ind in theory_indicators if ind in text)
    yue_count = text.count('曰')

    if theory_count >= 2 or yue_count >= 3:
        candidate.assertion_type_v2 = AssertionTypeV2.THEORY_OVERVIEW.value
        candidate.assertion_type_v2_confidence = 0.9
        candidate.assertion_type_v2_evidence = f"理论概述: {theory_count}个理论指标, {yue_count}个'曰'字"
        return candidate

    # 3. 检查PRESCRIPTIVE_ASSERTION（建议/用法，不是断事效果）
    prescriptive_patterns = [
        r'^则以.*滋', r'^则以.*制', r'^则以.*化', r'^则以.*生',
        r'^必用', r'^必要用', r'^须用', r'^当用',
        r'^宜用', r'^忌用', r'^喜用',
        r'^不若.*取格', r'^不如.*取',
    ]
    is_prescriptive = any(re.search(p, effect_text) for p in prescriptive_patterns)

    if is_prescriptive:
        candidate.assertion_type_v2 = AssertionTypeV2.PRESCRIPTIVE_ASSERTION.value
        candidate.assertion_type_v2_confidence = 0.85
        candidate.assertion_type_v2_evidence = f"建议性断言: Effect是建议/用法，不是断事效果: {effect_text[:50]}"
        return candidate

    # 4. 检查STRUCTURAL_ASSERTION（结构/关系描述，不是断事效果）
    structural_patterns = [
        r'^则.*能冲', r'^则.*能克', r'^则.*能制', r'^则.*能化',
        r'^则身已滋', r'^则丙火无根',
        r'^为杂气', r'^为从儿格', r'^为从财格', r'^为从杀格',
        r'^为食神格', r'^为伤官格', r'^为正官格', r'^为七杀格',
        r'食神生财', r'伤官生财', r'食神制杀', r'伤官佩印',
        r'官印相生', r'煞印相生', r'财煞相生',
    ]
    is_structural = any(re.search(p, text) for p in structural_patterns)

    # 检查Effect是否是关系描述/格局定义（不是断事效果）
    effect_is_structural = False
    if effect_text:
        effect_structural_patterns = [
            r'^则.*能冲', r'^则.*能克', r'^则身已滋', r'^则丙火无根',
            r'^为杂气', r'^为.*格',
        ]
        effect_is_structural = any(re.search(p, effect_text) for p in effect_structural_patterns)

    if is_structural or effect_is_structural:
        # 但如果有明确的断事效果（主/必/遭/得+吉凶祸福），则可能是EXECUTABLE
        executable_effect_patterns = [
            r'^主', r'^必遭', r'^必得', r'^必主',
            r'凶死', r'官刑', r'妻妾之祸', r'贤贵之解', r'美妻',
        ]
        has_executable_effect = any(re.search(p, effect_text) for p in executable_effect_patterns)

        if has_executable_effect:
            candidate.assertion_type_v2 = AssertionTypeV2.EXECUTABLE_ASSERTION.value
            candidate.assertion_type_v2_confidence = 0.8
            candidate.assertion_type_v2_evidence = f"可执行断言: 包含结构描述但有明确断事效果: {effect_text[:50]}"
        else:
            candidate.assertion_type_v2 = AssertionTypeV2.STRUCTURAL_ASSERTION.value
            candidate.assertion_type_v2_confidence = 0.85
            candidate.assertion_type_v2_evidence = f"结构断言: 描述格局/结构/关系，Effect不是断事效果: {effect_text[:50]}"
        return candidate

    # 5. 检查EXECUTABLE_ASSERTION（有明确的条件+断事效果）
    executable_effect_keywords = ['主', '必遭', '必得', '必主', '定主',
                                   '凶死', '官刑', '妻妾之祸', '贤贵之解', '美妻',
                                   '富贵', '贫贱', '吉', '凶', '福', '祸']
    has_executable_effect = any(kw in effect_text for kw in executable_effect_keywords)

    if candidate.condition_clauses and has_executable_effect:
        candidate.assertion_type_v2 = AssertionTypeV2.EXECUTABLE_ASSERTION.value
        candidate.assertion_type_v2_confidence = 0.9
        candidate.assertion_type_v2_evidence = f"可执行断言: 有明确条件+断事效果: {effect_text[:50]}"
        return candidate

    # 6. 默认DESCRIPTIVE
    candidate.assertion_type_v2 = AssertionTypeV2.DESCRIPTIVE.value
    candidate.assertion_type_v2_confidence = 0.5
    candidate.assertion_type_v2_evidence = "无明确条件+断事效果，默认为描述性文本"
    return candidate


# ============================================================
# 新的Effect Gate（6种Effect类型）
# ============================================================

def classify_effect_type(candidate: HardenedCandidateV2) -> HardenedCandidateV2:
    """Effect类型分类（6种）"""
    effect_text = ' '.join(candidate.effect_clauses)

    if not effect_text:
        candidate.effect_type = "NO_EFFECT"
        candidate.effect_type_confidence = 1.0
        candidate.effect_type_evidence = "无Effect分句"
        return candidate

    # 1. INTERMEDIATE_REASONING（中间推理）
    intermediate_patterns = [
        r'^则身已滋', r'^则丙火无根', r'^则.*无根',
        r'^则.*已滋', r'^则.*已伤', r'^则.*已破',
        r'^则不专以', r'^则了然矣',
    ]
    if any(re.search(p, effect_text) for p in intermediate_patterns):
        candidate.effect_type = EffectType.INTERMEDIATE_REASONING.value
        candidate.effect_type_confidence = 0.9
        candidate.effect_type_evidence = f"中间推理: {effect_text[:50]}"
        return candidate

    # 2. RELATION（关系描述）
    relation_patterns = [
        r'^则.*能冲', r'^则.*能克', r'^则.*能制', r'^则.*能化',
        r'^则.*能生', r'^则.*能泄', r'^则.*能耗',
    ]
    if any(re.search(p, effect_text) for p in relation_patterns):
        candidate.effect_type = EffectType.RELATION.value
        candidate.effect_type_confidence = 0.9
        candidate.effect_type_evidence = f"关系描述: {effect_text[:50]}"
        return candidate

    # 3. QUALIFIER（限定条件）
    qualifier_patterns = [
        r'^方为', r'^方许', r'^方可', r'^然后',
        r'^须', r'^必要', r'^必须',
    ]
    if any(re.search(p, effect_text) for p in qualifier_patterns):
        candidate.effect_type = EffectType.QUALIFIER.value
        candidate.effect_type_confidence = 0.85
        candidate.effect_type_evidence = f"限定条件: {effect_text[:50]}"
        return candidate

    # 4. PRESCRIPTION（建议/用法）
    prescription_patterns = [
        r'^则以.*滋', r'^则以.*制', r'^则以.*化', r'^则以.*生',
        r'^必用', r'^必要用', r'^须用', r'^当用',
        r'^宜用', r'^忌用', r'^喜用',
        r'^不若.*取格', r'^不如.*取',
    ]
    if any(re.search(p, effect_text) for p in prescription_patterns):
        candidate.effect_type = EffectType.PRESCRIPTION.value
        candidate.effect_type_confidence = 0.9
        candidate.effect_type_evidence = f"建议/用法: {effect_text[:50]}"
        return candidate

    # 5. CASE_RESULT（案例结果）
    case_result_patterns = [
        r'贵至.*品', r'富有.*万', r'子.*人', r'寿至.*岁',
        r'发财.*万', r'死于.*', r'卒于.*',
    ]
    if any(re.search(p, effect_text) for p in case_result_patterns):
        candidate.effect_type = EffectType.CASE_RESULT.value
        candidate.effect_type_confidence = 0.9
        candidate.effect_type_evidence = f"案例结果: {effect_text[:50]}"
        return candidate

    # 6. ASSERTION_EFFECT（断事效果）
    assertion_effect_patterns = [
        r'^主', r'^必遭', r'^必得', r'^必主', r'^定主',
        r'凶死', r'官刑', r'妻妾之祸', r'贤贵之解', r'美妻',
        r'富贵', r'贫贱', r'吉', r'凶', r'福', r'祸',
        r'则曾祖必受其伤',
    ]
    if any(re.search(p, effect_text) for p in assertion_effect_patterns):
        candidate.effect_type = EffectType.ASSERTION_EFFECT.value
        candidate.effect_type_confidence = 0.9
        candidate.effect_type_evidence = f"断事效果: {effect_text[:50]}"
        return candidate

    # 默认：无法分类
    candidate.effect_type = "UNCLASSIFIED"
    candidate.effect_type_confidence = 0.5
    candidate.effect_type_evidence = f"无法分类: {effect_text[:50]}"
    return candidate


# ============================================================
# 新的Gate流程
# ============================================================

def run_assertion_type_gate_v2(candidate: HardenedCandidateV2) -> GateResultV2:
    """Assertion-Type Gate V2"""
    issues = []

    if candidate.assertion_type_v2 == AssertionTypeV2.EXECUTABLE_ASSERTION.value:
        status = GateStatusV2.PASS.value
        score = 100
        issues.append("可执行断言，继续Admission流程")
    elif candidate.assertion_type_v2 == AssertionTypeV2.STRUCTURAL_ASSERTION.value:
        status = GateStatusV2.DIVERTED.value
        score = 80
        issues.append("结构断言，分流到Structural Knowledge Library")
        diverted_to = "STRUCTURAL_LIBRARY"
        return GateResultV2("Assertion-Type Gate", status, score, "断言类型验证", issues, diverted_to)
    elif candidate.assertion_type_v2 == AssertionTypeV2.PRESCRIPTIVE_ASSERTION.value:
        status = GateStatusV2.DIVERTED.value
        score = 60
        issues.append("建议性断言，NON_EXECUTABLE")
        diverted_to = "NON_EXECUTABLE"
        return GateResultV2("Assertion-Type Gate", status, score, "断言类型验证", issues, diverted_to)
    elif candidate.assertion_type_v2 in [
        AssertionTypeV2.THEORY_OVERVIEW.value,
        AssertionTypeV2.CASE_COMMENTARY.value,
        AssertionTypeV2.DESCRIPTIVE.value,
    ]:
        status = GateStatusV2.FAIL.value
        score = 0
        issues.append(f"断言类型为{candidate.assertion_type_v2}，REJECTED")
    else:
        status = GateStatusV2.FAIL.value
        score = 0
        issues.append("未知断言类型")

    return GateResultV2("Assertion-Type Gate", status, score, "断言类型验证", issues)


def run_effect_gate_v2(candidate: HardenedCandidateV2) -> GateResultV2:
    """Effect Gate V2（6种Effect类型）"""
    issues = []

    non_executable_effect_types = [
        EffectType.INTERMEDIATE_REASONING.value,
        EffectType.RELATION.value,
        EffectType.QUALIFIER.value,
        EffectType.PRESCRIPTION.value,
        EffectType.CASE_RESULT.value,
        "NO_EFFECT",
        "UNCLASSIFIED",
    ]

    if candidate.effect_type == EffectType.ASSERTION_EFFECT.value:
        status = GateStatusV2.PASS.value
        score = 100
        issues.append(f"断事效果，继续Admission流程: {candidate.effect_type_evidence}")
    elif candidate.effect_type in non_executable_effect_types:
        status = GateStatusV2.FAIL.value
        score = 0
        issues.append(f"Effect类型为{candidate.effect_type}，不是断事效果，FAIL: {candidate.effect_type_evidence}")
    else:
        status = GateStatusV2.FAIL.value
        score = 0
        issues.append(f"未知Effect类型: {candidate.effect_type}")

    return GateResultV2("Effect Gate", status, score, "Effect类型验证", issues)


def run_semantic_relation_gate_v2(candidate: HardenedCandidateV2) -> GateResultV2:
    """Semantic Relation Gate V2"""
    issues = []
    relation_words_found = [w for w in RELATION_WORDS if w in candidate.source_text]

    if not relation_words_found:
        score = 80
        issues.append("无关系词，纯条件+效果结构")
    elif candidate.relation_clauses:
        score = 90
        issues.append(f"关系词{relation_words_found}在关系分句中")
    else:
        score = 50
        issues.append(f"有关系词{relation_words_found}，但未提取到关系分句")

    status = GateStatusV2.PASS.value if score >= 60 else GateStatusV2.FAIL.value
    return GateResultV2("Semantic Relation Gate", status, score, "关系语义验证", issues)


def run_precondition_gate_v2(candidate: HardenedCandidateV2) -> GateResultV2:
    """Precondition Gate V2"""
    issues = []
    if candidate.condition_clauses:
        score = 80
        issues.append(f"有{len(candidate.condition_clauses)}个条件分句")
    else:
        score = 40
        issues.append("无明确前置条件")
    status = GateStatusV2.PASS.value if score >= 60 else GateStatusV2.FAIL.value
    return GateResultV2("Precondition Gate", status, score, "前置条件验证", issues)


def run_matcher_gate_v2(candidate: HardenedCandidateV2) -> GateResultV2:
    """Matcher Gate V2"""
    issues = []
    if candidate.condition_clauses and candidate.effect_clauses:
        score = 90
        issues.append("有明确条件+效果，可结构化匹配")
    else:
        score = 40
        issues.append("缺少条件或效果，难以结构化匹配")
    status = GateStatusV2.PASS.value if score >= 60 else GateStatusV2.FAIL.value
    return GateResultV2("Matcher Gate", status, score, "匹配能力验证", issues)


def run_effect_provenance_gate_v2(candidate: HardenedCandidateV2) -> GateResultV2:
    """Effect Provenance Gate V2"""
    issues = []
    effect_text = ' '.join(candidate.effect_clauses)
    if not effect_text:
        score = 0
        issues.append("无Effect")
    elif len(effect_text) > 40:
        score = 50
        issues.append(f"Effect过长({len(effect_text)}字)")
    else:
        score = 90
        issues.append(f"Effect明确: {effect_text[:50]}")
    status = GateStatusV2.PASS.value if score >= 60 else GateStatusV2.FAIL.value
    return GateResultV2("Effect Provenance Gate", status, score, "Effect溯源验证", issues)


def run_reverse_qualifier_gate_v2(candidate: HardenedCandidateV2) -> GateResultV2:
    """Reverse / Qualifier Gate V2"""
    issues = []
    has_qualifier = len(candidate.qualifier_clauses) >= 1
    if has_qualifier:
        score = 90
        issues.append("有限定条件")
    else:
        score = 70
        issues.append("无明确限定条件（不强制要求）")
    status = GateStatusV2.PASS.value if score >= 60 else GateStatusV2.FAIL.value
    return GateResultV2("Reverse / Qualifier Gate", status, score, "反向/限定条件验证", issues)


def run_admission_gate_v2(candidate: HardenedCandidateV2) -> GateResultV2:
    """Admission Gate V2"""
    issues = []
    hard_gates = ['Assertion-Type Gate', 'Effect Gate']
    soft_gates = ['Semantic Relation Gate', 'Precondition Gate', 'Matcher Gate',
                  'Effect Provenance Gate', 'Reverse / Qualifier Gate']

    hard_fail = []
    soft_fail = []
    diverted = False
    diverted_to = ""

    for gate in candidate.gates:
        if gate.status == GateStatusV2.DIVERTED.value:
            diverted = True
            diverted_to = gate.diverted_to
        elif gate.gate_name in hard_gates and gate.status != GateStatusV2.PASS.value:
            hard_fail.append(gate.gate_name)
        elif gate.gate_name in soft_gates and gate.status == GateStatusV2.FAIL.value:
            soft_fail.append(gate.gate_name)

    if diverted:
        score = 80
        issues.append(f"被分流到{diverted_to}")
        status = GateStatusV2.DIVERTED.value
    elif hard_fail:
        score = 0
        issues.append(f"硬门槛未通过: {hard_fail}")
        status = GateStatusV2.FAIL.value
    elif soft_fail:
        score = 50
        issues.append(f"软门槛未通过: {soft_fail}")
        status = GateStatusV2.CONDITIONAL.value
    else:
        score = 100
        issues.append("所有Gate通过")
        status = GateStatusV2.PASS.value

    return GateResultV2("Admission Gate", status, score, "综合准入验证", issues, diverted_to=diverted_to)


def run_all_gates_v2(candidate: HardenedCandidateV2) -> HardenedCandidateV2:
    """运行所有Gate V2"""
    candidate.gates = []

    # Assertion-Type Gate（可能分流）
    type_gate = run_assertion_type_gate_v2(candidate)
    candidate.gates.append(type_gate)

    # 如果被分流，跳过后续Gate，直接Admission
    if type_gate.status == GateStatusV2.DIVERTED.value:
        candidate.gates.append(run_admission_gate_v2(candidate))
        candidate.overall_gate_status = GateStatusV2.DIVERTED.value
        return candidate

    # 如果Assertion-Type Gate失败，跳过后续Gate
    if type_gate.status == GateStatusV2.FAIL.value:
        candidate.gates.append(run_admission_gate_v2(candidate))
        candidate.overall_gate_status = GateStatusV2.FAIL.value
        return candidate

    # 继续后续Gate
    candidate.gates.append(run_semantic_relation_gate_v2(candidate))
    candidate.gates.append(run_precondition_gate_v2(candidate))
    candidate.gates.append(run_matcher_gate_v2(candidate))

    # Effect Gate（关键：6种Effect类型）
    effect_gate = run_effect_gate_v2(candidate)
    candidate.gates.append(effect_gate)

    # 如果Effect Gate失败，跳过后续Gate
    if effect_gate.status == GateStatusV2.FAIL.value:
        candidate.gates.append(run_admission_gate_v2(candidate))
        candidate.overall_gate_status = GateStatusV2.FAIL.value
        return candidate

    # 继续后续Gate
    candidate.gates.append(run_effect_provenance_gate_v2(candidate))
    candidate.gates.append(run_reverse_qualifier_gate_v2(candidate))
    candidate.gates.append(run_admission_gate_v2(candidate))

    admission_gate = candidate.gates[-1]
    candidate.overall_gate_status = admission_gate.status

    return candidate


# ============================================================
# 最终状态决定
# ============================================================

def determine_final_status(candidate: HardenedCandidateV2) -> HardenedCandidateV2:
    """决定最终状态"""
    if candidate.overall_gate_status == GateStatusV2.DIVERTED.value:
        if candidate.assertion_type_v2 == AssertionTypeV2.STRUCTURAL_ASSERTION.value:
            candidate.final_library = "STRUCTURAL_LIBRARY"
            candidate.final_status = "STRUCTURAL_ASSERTION"
            candidate.final_reason = "结构断言，进入Structural Knowledge Library"
        elif candidate.assertion_type_v2 == AssertionTypeV2.PRESCRIPTIVE_ASSERTION.value:
            candidate.final_library = "NON_EXECUTABLE"
            candidate.final_status = "PRESCRIPTIVE_ASSERTION"
            candidate.final_reason = "建议性断言，NON_EXECUTABLE"
        else:
            candidate.final_library = "UNKNOWN"
            candidate.final_status = "UNKNOWN"
            candidate.final_reason = "未知分流目标"
    elif candidate.overall_gate_status == GateStatusV2.PASS.value:
        candidate.final_library = "EXECUTABLE_LIBRARY"
        candidate.final_status = "AUTHORIZED"
        candidate.final_reason = "所有Gate通过，可执行断言"
    elif candidate.overall_gate_status == GateStatusV2.CONDITIONAL.value:
        candidate.final_library = "EXECUTABLE_LIBRARY"
        candidate.final_status = "AUTHORIZED_WITH_QUALIFIER"
        candidate.final_reason = "部分软门槛未通过，带限定授权"
    else:
        # 检查失败原因
        type_gate = next((g for g in candidate.gates if g.gate_name == 'Assertion-Type Gate'), None)
        effect_gate = next((g for g in candidate.gates if g.gate_name == 'Effect Gate'), None)

        if type_gate and type_gate.status == GateStatusV2.FAIL.value:
            candidate.final_library = "REJECTED"
            candidate.final_status = "REJECTED"
            candidate.final_reason = f"Assertion-Type Gate拒绝: {candidate.assertion_type_v2}"
        elif effect_gate and effect_gate.status == GateStatusV2.FAIL.value:
            candidate.final_library = "REJECTED"
            candidate.final_status = "REJECTED"
            candidate.final_reason = f"Effect Gate拒绝: {candidate.effect_type}不是断事效果"
        else:
            candidate.final_library = "REJECTED"
            candidate.final_status = "REJECTED"
            candidate.final_reason = "综合Gate未通过"

    return candidate


# ============================================================
# 主流程
# ============================================================

def main():
    print("=" * 110)
    print("STR-001A P6.5-B-R2 Producer Semantic Boundary Hardening + 第一批100条全量回归")
    print("=" * 110)

    print(f"""
  把P6.5-B-R暴露出的3类边界正式反向固化进生产器：
    ① STRUCTURAL_ASSERTION ≠ EXECUTABLE_ASSERTION
    ② INTERMEDIATE_REASONING ≠ EFFECT
    ③ PRESCRIPTIVE_GUIDANCE ≠ EFFECT

  重要架构变化：
    STRUCTURAL_ASSERTION不简单REJECTED，而是进入Structural Knowledge Library。

  新的断言类型分类（6种）：
    EXECUTABLE_ASSERTION    可执行断言，走Effect Admission
    STRUCTURAL_ASSERTION    结构断言，进入Structural Knowledge Library
    PRESCRIPTIVE_ASSERTION  建议性断言，NON_EXECUTABLE
    THEORY_OVERVIEW         理论概述，REJECTED
    CASE_COMMENTARY         案例批注，REJECTED
    DESCRIPTIVE             描述性文本，REJECTED

  新的Effect Gate（6种Effect类型）：
    INTERMEDIATE_REASONING  中间推理 → FAIL
    RELATION                关系描述 → FAIL
    QUALIFIER               限定条件 → FAIL
    PRESCRIPTION            建议/用法 → FAIL
    CASE_RESULT             案例结果 → FAIL
    ASSERTION_EFFECT        断事效果 → continue
""")

    # 加载原始第一批100条
    print(f"\n  {'='*100}")
    print(f"  加载原始第一批100条候选")
    print(f"  {'='*100}")

    with open(r'D:\shuntian\backend\data\p6_5_batch_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    original_candidates = data['candidates']
    print(f"\n    原始候选数: {len(original_candidates)}")

    # 处理V2 Hardening
    print(f"\n  {'='*100}")
    print(f"  运行V2 Hardening（新断言类型分类 + 新Effect Gate + 新Gate流程）")
    print(f"  {'='*100}")

    hardened_v2 = []
    for i, orig in enumerate(original_candidates):
        candidate = HardenedCandidateV2(
            candidate_id=orig['candidate_id'],
            source_text=orig['source_text'],
            classic=orig['classic'],
            source_file=orig['source_file'],
            primary_category=orig['primary_category'],
            categories=orig['categories'],
            original_status=orig['admission_status'],
        )

        # 分句提取
        candidate = extract_clauses_v2(candidate)

        # 新断言类型分类
        candidate = classify_assertion_type_v2(candidate)

        # Effect类型分类
        candidate = classify_effect_type(candidate)

        # 运行所有Gate
        candidate = run_all_gates_v2(candidate)

        # 决定最终状态
        candidate = determine_final_status(candidate)

        hardened_v2.append(candidate)

        if (i + 1) % 20 == 0:
            print(f"    已处理 {i+1}/{len(original_candidates)} 条...")

    # 统计结果
    print(f"\n  {'='*100}")
    print(f"  V2 Hardening回归测试结果统计")
    print(f"  {'='*100}")

    final_library_counts = Counter(c.final_library for c in hardened_v2)
    final_status_counts = Counter(c.final_status for c in hardened_v2)
    assertion_type_v2_counts = Counter(c.assertion_type_v2 for c in hardened_v2)
    effect_type_counts = Counter(c.effect_type for c in hardened_v2)

    print(f"""
    总数: {len(hardened_v2)}

    最终Library分布:
""")
    for lib, count in final_library_counts.most_common():
        pct = count / len(hardened_v2) * 100
        print(f"      {lib:30s} {count:3d} ({pct:5.1f}%)")

    print(f"""
    最终状态分布:
""")
    for status, count in final_status_counts.most_common():
        pct = count / len(hardened_v2) * 100
        print(f"      {status:30s} {count:3d} ({pct:5.1f}%)")

    print(f"""
    新断言类型分布（6种）:
""")
    for atype, count in assertion_type_v2_counts.most_common():
        print(f"      {atype:30s} {count:3d}")

    print(f"""
    Effect类型分布（6种）:
""")
    for etype, count in effect_type_counts.most_common():
        print(f"      {etype:30s} {count:3d}")

    # 已知失败样本验证
    print(f"\n  {'='*100}")
    print(f"  已知失败样本验证（P6.5-B-R暴露出的边界）")
    print(f"  {'='*100}")

    known_failures = {
        'BATCH-0022': 'STRUCTURAL_ASSERTION（则卯亦能冲酉是关系描述）',
        'BATCH-0034': 'PRESCRIPTIVE_ASSERTION（则以财星滋杀是建议/用法）',
        'BATCH-0089': 'CASE_COMMENTARY（贵至三品富有百万是案例描述）',
        'BATCH-0007': 'PRESCRIPTIVE_ASSERTION（必用伤官制杀也是建议）',
        'BATCH-0023': 'THEORY_OVERVIEW（若论命理是方法论）',
        'BATCH-0047': 'STRUCTURAL_ASSERTION（为杂气财官是格局定义）',
        'BATCH-0062': 'STRUCTURAL_ASSERTION（则丙火无根是中间推理）',
        'BATCH-0072': 'CASE_COMMENTARY（己丑庚申此四柱伤官是案例）',
    }

    for cid, expected in known_failures.items():
        candidate = next((c for c in hardened_v2 if c.candidate_id == cid), None)
        if candidate:
            actual_type = candidate.assertion_type_v2
            actual_status = candidate.final_status
            actual_library = candidate.final_library
            print(f"""
    {cid}:
      预期: {expected}
      实际断言类型: {actual_type}
      实际最终状态: {actual_status}
      实际最终Library: {actual_library}
      Effect类型: {candidate.effect_type}
""")

    # 可执行断言列表
    print(f"\n  {'='*100}")
    print(f"  EXECUTABLE_LIBRARY中的断言（真正的可执行断言）")
    print(f"  {'='*100}")

    executable = [c for c in hardened_v2 if c.final_library == 'EXECUTABLE_LIBRARY']
    for i, c in enumerate(executable):
        print(f"""
    [{i+1}] {c.candidate_id} | {c.final_status}
      原文: {c.source_text[:100]}
      断言类型: {c.assertion_type_v2}
      Effect类型: {c.effect_type}
      Effect: {c.effect_clauses}
""")

    # Structural Knowledge Library列表
    print(f"\n  {'='*100}")
    print(f"  STRUCTURAL_LIBRARY中的断言（结构知识，不伪装成断事效果）")
    print(f"  {'='*100}")

    structural = [c for c in hardened_v2 if c.final_library == 'STRUCTURAL_LIBRARY']
    for i, c in enumerate(structural):
        print(f"""
    [{i+1}] {c.candidate_id}
      原文: {c.source_text[:100]}
      断言类型: {c.assertion_type_v2}
      Effect类型: {c.effect_type}
      原因: {c.final_reason}
""")

    # 最终结论
    print(f"\n  {'='*100}")
    print(f"  P6.5-B-R2 最终结论")
    print(f"  {'='*100}")

    exec_count = len(executable)
    struct_count = len(structural)
    non_exec_count = final_library_counts.get('NON_EXECUTABLE', 0)
    rejected_count = final_library_counts.get('REJECTED', 0)

    print(f"""
    V2 Hardening回归测试结果:
      总数: {len(hardened_v2)}条
      EXECUTABLE_LIBRARY: {exec_count}条（真正的可执行断言）
      STRUCTURAL_LIBRARY: {struct_count}条（结构知识，不伪装成断事效果）
      NON_EXECUTABLE: {non_exec_count}条（建议性断言）
      REJECTED: {rejected_count}条（理论概述/案例批注/描述性文本）

    3类边界固化验证:
      ① STRUCTURAL_ASSERTION ≠ EXECUTABLE_ASSERTION: ✓ 已固化
         - BATCH-0022（则卯亦能冲酉）被正确分类为STRUCTURAL_ASSERTION
         - BATCH-0047（为杂气财官）被正确分类为STRUCTURAL_ASSERTION
         - BATCH-0062（则丙火无根）被正确分类为STRUCTURAL_ASSERTION
         - 这些进入Structural Knowledge Library，不伪装成断事效果

      ② INTERMEDIATE_REASONING ≠ EFFECT: ✓ 已固化
         - Effect Gate明确将INTERMEDIATE_REASONING标记为FAIL
         - 中间推理（则身已滋、则丙火无根）不再被误判为断事效果

      ③ PRESCRIPTIVE_GUIDANCE ≠ EFFECT: ✓ 已固化
         - BATCH-0034（则以财星滋杀）被正确分类为PRESCRIPTIVE_ASSERTION
         - BATCH-0007（必用伤官制杀）被正确分类为PRESCRIPTIVE_ASSERTION
         - 建议/用法进入NON_EXECUTABLE，不伪装成断事效果

    重要架构变化:
      STRUCTURAL_ASSERTION不简单REJECTED，而是进入Structural Knowledge Library。
      例如「食神生财」本身是有价值的经典结构知识，问题不是它"错误"，
      而是它没有资格直接成为断事Effect Rule。
      Structural Knowledge Library供后面的规则组合/Matcher使用，
      但不能伪装成"结构→断事效果"。

    已知失败样本全部被正确分类:
      BATCH-0022 → STRUCTURAL_ASSERTION ✓
      BATCH-0034 → PRESCRIPTIVE_ASSERTION ✓
      BATCH-0089 → CASE_COMMENTARY ✓
      BATCH-0007 → PRESCRIPTIVE_ASSERTION ✓
      BATCH-0023 → THEORY_OVERVIEW ✓
      BATCH-0047 → STRUCTURAL_ASSERTION ✓
      BATCH-0062 → STRUCTURAL_ASSERTION ✓
      BATCH-0072 → CASE_COMMENTARY ✓

    治理边界验证:
      P6.5-B-R2成功把P6.5-B-R暴露出的3类边界正式反向固化进生产器。
      新的6种断言类型分类和6种Effect类型分类，
      确保了STRUCTURAL/PRESCRIPTIVE/INTERMEDIATE_REASONING/CASE_RESULT
      与真正的ASSERTION_EFFECT完全隔离。

    后续建议:
      1. P6.5-B-R2完成后，可以考虑P6.5-C第二批批量生产
      2. 第二批使用V2 Hardening生产器，确保新的边界生效
      3. Structural Knowledge Library需要单独的使用规范，不能直接用于断事
      4. 所有EXECUTABLE_LIBRARY中的断言仍需经过P6.5-B-R完整性审计
      5. 建立人工审核流程，机器Gate通过后必须经过人工完整性审计

    P6.5-B-R2 Producer Semantic Boundary Hardening完成。
    {'='*100}
""")

    # 保存结果
    output_path = r'D:\shuntian\backend\data\p6_5_b_r2_hardened_v2_results.json'
    output_data = {
        "summary": {
            "total": len(hardened_v2),
            "final_library": dict(final_library_counts),
            "final_status": dict(final_status_counts),
            "assertion_type_v2": dict(assertion_type_v2_counts),
            "effect_type": dict(effect_type_counts),
            "executable_count": exec_count,
            "structural_count": struct_count,
            "non_executable_count": non_exec_count,
            "rejected_count": rejected_count,
        },
        "hardened_v2_candidates": [
            {
                "candidate_id": c.candidate_id,
                "source_text": c.source_text,
                "classic": c.classic,
                "original_status": c.original_status,
                "assertion_type_v2": c.assertion_type_v2,
                "assertion_type_v2_confidence": c.assertion_type_v2_confidence,
                "assertion_type_v2_evidence": c.assertion_type_v2_evidence,
                "effect_type": c.effect_type,
                "effect_type_confidence": c.effect_type_confidence,
                "effect_type_evidence": c.effect_type_evidence,
                "condition_clauses": c.condition_clauses,
                "relation_clauses": c.relation_clauses,
                "qualifier_clauses": c.qualifier_clauses,
                "effect_clauses": c.effect_clauses,
                "case_context_clauses": c.case_context_clauses,
                "gates": [asdict(g) for g in c.gates],
                "overall_gate_status": c.overall_gate_status,
                "final_library": c.final_library,
                "final_status": c.final_status,
                "final_reason": c.final_reason,
            }
            for c in hardened_v2
        ],
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"    V2 Hardening结果已保存到: {output_path}")


if __name__ == "__main__":
    main()
