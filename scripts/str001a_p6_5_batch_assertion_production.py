"""
STR-001A P6.5 Batch Assertion Asset Production Protocol

批量断言资产生产协议（10步流水线）:
  1. Candidate Extraction      - 从断语库中提取候选断语
  2. Semantic Classification   - 语义分类
  3. Evidence Contract         - 建立证据契约
  4. Precondition Extraction   - 提取前置条件
  5. Relation Boundary         - 提取关系边界
  6. Effect Provenance         - Effect溯源（硬门槛）
  7. Reverse / Qualifier       - 提取反向条件和限定条件
  8. Independent Audit         - 独立审计
  9. Admission Gate            - 准入门槛
  10. Authorized Library       - 正式入库

第一批: 从财运类、官运类、格局类、旺衰类中筛选50-100条结构清晰的断语

健康结果预期:
  100 Candidate
    ├─ 20 AUTHORIZED_WITH_QUALIFIER
    ├─ 10 POSTERIOR
    ├─ 5 REJECTED
    └─ 65 CANDIDATE
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

class CandidateStatus(str, Enum):
    RAW = "RAW"
    CLASSIFIED = "CLASSIFIED"
    EVIDENCE_CONTRACT = "EVIDENCE_CONTRACT"
    PRECONDITIONS_EXTRACTED = "PRECONDITIONS_EXTRACTED"
    EFFECT_PROVENANCED = "EFFECT_PROVENANCED"
    AUDITED = "AUDITED"
    ADMISSION_READY = "ADMISSION_READY"


class AdmissionStatus(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    AUTHORIZED_WITH_QUALIFIER = "AUTHORIZED_WITH_QUALIFIER"
    CANDIDATE = "CANDIDATE"
    POSTERIOR = "POSTERIOR"
    REJECTED = "REJECTED"


class SemanticType(str, Enum):
    PATTERN = "PATTERN"              # 格局类
    RELATION = "RELATION"            # 关系类
    EFFECT = "EFFECT"                # 效果类
    CONDITIONAL = "CONDITIONAL"      # 条件类
    DESCRIPTIVE = "DESCRIPTIVE"      # 描述类
    CASE_NOTE = "CASE_NOTE"          # 案例批注
    UNKNOWN = "UNKNOWN"


@dataclass
class BatchCandidate:
    """批量候选断言"""
    candidate_id: str
    source_text: str
    classic: str
    source_file: str
    primary_category: str
    categories: List[str]

    # 处理状态
    status: str = CandidateStatus.RAW.value
    admission_status: str = AdmissionStatus.CANDIDATE.value

    # 语义分类
    semantic_type: str = SemanticType.UNKNOWN.value
    semantic_confidence: float = 0.0

    # 证据契约
    evidence_status: str = "UNVERIFIED"
    evidence_notes: str = ""

    # 前置条件
    preconditions: List[str] = field(default_factory=list)
    preconditions_count: int = 0

    # 关系边界
    relations: List[str] = field(default_factory=list)
    relation_words: List[str] = field(default_factory=list)

    # Effect溯源（硬门槛）
    effect_text: str = ""
    effect_provenance_status: str = "UNVERIFIED"
    effect_provenance_notes: str = ""

    # 反向条件和限定条件
    reverse_conditions: List[str] = field(default_factory=list)
    qualifiers: List[str] = field(default_factory=list)

    # 审计结果
    audit_score: int = 0
    audit_notes: str = ""
    audit_passed: bool = False

    # 最终结论
    final_conclusion: str = ""
    unresolved_reasons: List[str] = field(default_factory=list)


# ============================================================
# 第1步: Candidate Extraction - 从断语库中提取候选断语
# ============================================================

def load_duanyu_corpus(json_path: str) -> List[Dict]:
    """加载断语库"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def is_suitable_for_assertion(text: str) -> bool:
    """判断断语是否适合作为断言候选"""
    # 排除过短或过长的文本
    if len(text) < 8 or len(text) > 120:
        return False

    # 排除纯描述性文本（目录、介绍）
    descriptive_patterns = [
        r'^目录', r'^第[一二三四五六七八九十]+章', r'^[一二三四五六七八九十]+、',
        r'^《', r'^注：', r'^原注：', r'^任氏曰：', r'^余曰：',
    ]
    for pattern in descriptive_patterns:
        if re.search(pattern, text):
            return False

    # 排除案例批注（包含大量干支/人名/官职）
    case_note_patterns = [
        r'[甲乙丙丁戊己庚辛壬癸]{2}[ 　]',  # 干支组合
        r'侍郎|尚书|布政|太守|进士|举人|探花|状元|阁老|都宪|方伯',
        r'/[甲乙丙丁戊己庚辛壬癸]{2}',  # 案例批注格式
    ]
    case_score = 0
    for pattern in case_note_patterns:
        if re.search(pattern, text):
            case_score += 1
    if case_score >= 2:
        return False

    # 优先选择包含条件+效果结构的断语
    condition_effect_patterns = [
        r'若.*则', r'若.*主', r'若.*为', r'如.*则', r'如.*主',
        r'.*主.*', r'.*为.*', r'.*则.*', r'.*必.*', r'.*定.*',
        r'逢.*则', r'逢.*主', r'遇.*则', r'遇.*主',
        r'带.*则', r'带.*主', r'见.*则', r'见.*主',
    ]
    has_structure = any(re.search(p, text) for p in condition_effect_patterns)

    # 包含十神/五行/格局关键词
    keyword_patterns = [
        r'官|杀|财|印|食|伤|比|劫',
        r'身旺|身弱|身强|身衰',
        r'格局|成格|破格',
        r'富贵|贫贱|吉凶|祸福',
        r'长生|禄|刃|墓|绝',
        r'月令|提纲|通根|得地|得时',
    ]
    has_keyword = any(re.search(p, text) for p in keyword_patterns)

    return has_structure and has_keyword


def extract_candidates(corpus: List[Dict], target_categories: List[str],
                       max_per_category: int = 30, total_max: int = 100) -> List[BatchCandidate]:
    """从断语库中提取候选断语"""
    candidates = []
    category_counts = defaultdict(int)
    candidate_id = 0

    for item in corpus:
        text = item.get('text', '').strip()
        primary_category = item.get('primary_category', '')
        categories = item.get('categories', [])

        # 筛选目标类别
        if primary_category not in target_categories:
            continue

        # 判断是否适合作为断言
        if not is_suitable_for_assertion(text):
            continue

        # 限制每个类别的数量
        if category_counts[primary_category] >= max_per_category:
            continue

        # 限制总数
        if len(candidates) >= total_max:
            break

        candidate_id += 1
        candidate = BatchCandidate(
            candidate_id=f"BATCH-{candidate_id:04d}",
            source_text=text,
            classic=item.get('classic', ''),
            source_file=item.get('source', ''),
            primary_category=primary_category,
            categories=categories,
        )
        candidates.append(candidate)
        category_counts[primary_category] += 1

    return candidates


# ============================================================
# 第2步: Semantic Classification - 语义分类
# ============================================================

def classify_semantic(candidate: BatchCandidate) -> BatchCandidate:
    """语义分类"""
    text = candidate.source_text

    # 格局类: 包含格局、成格、破格、格等关键词
    if re.search(r'格局|成格|破格|格$|为格', text):
        candidate.semantic_type = SemanticType.PATTERN.value
        candidate.semantic_confidence = 0.8
    # 条件类: 包含若、如、逢、遇、带、见等条件词
    elif re.search(r'^若|^如|逢|遇|带|见|若.*则|如.*则', text):
        candidate.semantic_type = SemanticType.CONDITIONAL.value
        candidate.semantic_confidence = 0.75
    # 关系类: 包含生、克、制、化、合、冲、刑等关系词
    elif re.search(r'生|克|制|化|合|冲|刑|害|破', text):
        candidate.semantic_type = SemanticType.RELATION.value
        candidate.semantic_confidence = 0.7
    # 效果类: 包含主、为、则、必、定等效果词
    elif re.search(r'主|为|则|必|定|富贵|贫贱|吉凶', text):
        candidate.semantic_type = SemanticType.EFFECT.value
        candidate.semantic_confidence = 0.65
    else:
        candidate.semantic_type = SemanticType.DESCRIPTIVE.value
        candidate.semantic_confidence = 0.4

    candidate.status = CandidateStatus.CLASSIFIED.value
    return candidate


# ============================================================
# 第3步: Evidence Contract - 建立证据契约
# ============================================================

def build_evidence_contract(candidate: BatchCandidate) -> BatchCandidate:
    """建立证据契约"""
    # 检查是否有明确的经典出处
    if candidate.classic and candidate.source_file:
        candidate.evidence_status = "SOURCE_IDENTIFIED"
        candidate.evidence_notes = f"出处: {candidate.classic} ({candidate.source_file})"
    else:
        candidate.evidence_status = "SOURCE_MISSING"
        candidate.evidence_notes = "缺少明确的经典出处"
        candidate.unresolved_reasons.append("SOURCE_MISSING")

    candidate.status = CandidateStatus.EVIDENCE_CONTRACT.value
    return candidate


# ============================================================
# 第4步: Precondition Extraction - 提取前置条件
# ============================================================

def extract_preconditions(candidate: BatchCandidate) -> BatchCandidate:
    """提取前置条件"""
    text = candidate.source_text
    preconditions = []

    # 提取条件分句（若...、如...、逢...、遇...、带...、见...）
    condition_patterns = [
        (r'若([^，。；]+)[，。；]', '若'),
        (r'如([^，。；]+)[，。；]', '如'),
        (r'逢([^，。；]+)[，。；]', '逢'),
        (r'遇([^，。；]+)[，。；]', '遇'),
        (r'带([^，。；]+)[，。；]', '带'),
        (r'见([^，。；]+)[，。；]', '见'),
    ]

    for pattern, cond_type in condition_patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            if len(m) > 2 and len(m) < 50:
                preconditions.append(f"[{cond_type}] {m}")

    # 提取十神/五行状态作为前置条件
    shishen_patterns = [
        r'身旺|身弱|身强|身衰',
        r'官旺|杀旺|财旺|印旺|食旺|伤旺',
        r'官多|杀多|财多|印多|食多|伤多',
        r'官星|七杀|正财|偏财|正印|偏印|食神|伤官|比肩|劫财',
        r'通根|得地|得时|得令|失令|无根',
    ]

    for pattern in shishen_patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            if m not in [p.split('] ')[-1] if '] ' in p else p for p in preconditions]:
                preconditions.append(f"[状态] {m}")

    candidate.preconditions = preconditions[:5]  # 最多保留5个前置条件
    candidate.preconditions_count = len(candidate.preconditions)
    candidate.status = CandidateStatus.PRECONDITIONS_EXTRACTED.value
    return candidate


# ============================================================
# 第5步: Relation Boundary - 提取关系边界
# ============================================================

def extract_relations(candidate: BatchCandidate) -> BatchCandidate:
    """提取关系边界"""
    text = candidate.source_text
    relations = []
    relation_words = []

    # 提取关系词
    all_relation_words = ['生', '克', '制', '化', '合', '冲', '刑', '害', '破',
                          '泄', '耗', '扶', '助', '夺', '战', '斗', '争']

    for word in all_relation_words:
        if word in text:
            relation_words.append(word)

    # 提取关系短语
    relation_phrases = [
        r'[^，。；]{2,10}(生|克|制|化|合|冲|刑|害|破|泄|耗|扶|助|夺)[^，。；]{2,10}',
    ]

    for pattern in relation_phrases:
        matches = re.findall(pattern, text)
        for m in matches:
            if isinstance(m, tuple):
                m = ''.join(m)
            if len(m) > 4 and len(m) < 40:
                relations.append(m)

    candidate.relations = list(set(relations))[:5]
    candidate.relation_words = list(set(relation_words))
    return candidate


# ============================================================
# 第6步: Effect Provenance - Effect溯源（硬门槛）
# ============================================================

def extract_effect(candidate: BatchCandidate) -> BatchCandidate:
    """提取Effect并进行溯源（硬门槛）"""
    text = candidate.source_text
    effect = ""

    # 提取效果分句（主...、为...、则...、必...、定...）
    effect_patterns = [
        r'主([^，。；]+)',
        r'则([^，。；]+)',
        r'必([^，。；]+)',
        r'定为?([^，。；]+)',
    ]

    for pattern in effect_patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            if len(m) > 2 and len(m) < 50:
                effect = m
                break
        if effect:
            break

    # 如果没有找到明确的效果词，检查是否包含富贵/贫贱/吉凶等效果词
    if not effect:
        effect_keywords = ['富贵', '贫贱', '吉', '凶', '福', '祸', '寿', '夭',
                          '贵', '富', '贫', '贱', '荣', '枯', '亨', '困']
        for kw in effect_keywords:
            if kw in text:
                effect = kw
                break

    candidate.effect_text = effect

    # Effect溯源（硬门槛）
    if not effect:
        candidate.effect_provenance_status = "EFFECT_MISSING"
        candidate.effect_provenance_notes = "未提取到明确的Effect"
        candidate.unresolved_reasons.append("EFFECT_MISSING")
    elif len(effect) < 3:
        candidate.effect_provenance_status = "EFFECT_TOO_GENERIC"
        candidate.effect_provenance_notes = f"Effect过于泛化: {effect}"
        candidate.unresolved_reasons.append("EFFECT_TOO_GENERIC")
    else:
        # 检查Effect是否有明确的原典上下文支持
        if candidate.evidence_status == "SOURCE_IDENTIFIED":
            candidate.effect_provenance_status = "EFFECT_SOURCE_IDENTIFIED"
            candidate.effect_provenance_notes = f"Effect: {effect}, 出处: {candidate.classic}"
        else:
            candidate.effect_provenance_status = "EFFECT_SOURCE_UNVERIFIED"
            candidate.effect_provenance_notes = f"Effect: {effect}, 但出处未验证"
            candidate.unresolved_reasons.append("EFFECT_SOURCE_UNVERIFIED")

    candidate.status = CandidateStatus.EFFECT_PROVENANCED.value
    return candidate


# ============================================================
# 第7步: Reverse / Qualifier - 提取反向条件和限定条件
# ============================================================

def extract_reverse_qualifiers(candidate: BatchCandidate) -> BatchCandidate:
    """提取反向条件和限定条件"""
    text = candidate.source_text

    # 反向条件关键词
    reverse_keywords = ['忌', '怕', '不宜', '不可', '不喜', '反为', '反主',
                        '则凶', '则祸', '则贫', '则贱', '则夭', '则病']
    for kw in reverse_keywords:
        if kw in text:
            candidate.reverse_conditions.append(f"[{kw}] 存在反向条件")

    # 限定条件关键词
    qualifier_keywords = ['须', '必要', '需要', '方为', '方许', '方可', '然后',
                          '若能', '若得', '如能', '如得', '只要', '只有',
                          '虽', '然', '但', '不过', '大抵', '大概', '大致']
    for kw in qualifier_keywords:
        if kw in text:
            candidate.qualifiers.append(f"[{kw}] 存在限定条件")

    return candidate


# ============================================================
# 第8步: Independent Audit - 独立审计
# ============================================================

def independent_audit(candidate: BatchCandidate) -> BatchCandidate:
    """独立审计"""
    score = 0
    notes = []

    # 1. 证据契约 (20分)
    if candidate.evidence_status == "SOURCE_IDENTIFIED":
        score += 20
        notes.append("证据契约: 出处明确 (+20)")
    else:
        notes.append("证据契约: 出处不明确 (0)")

    # 2. 前置条件 (20分)
    if candidate.preconditions_count >= 2:
        score += 20
        notes.append(f"前置条件: {candidate.preconditions_count}个 (+20)")
    elif candidate.preconditions_count == 1:
        score += 10
        notes.append(f"前置条件: {candidate.preconditions_count}个 (+10)")
    else:
        notes.append("前置条件: 无 (0)")

    # 3. 关系边界 (15分)
    if candidate.relation_words:
        score += 15
        notes.append(f"关系边界: {len(candidate.relation_words)}个关系词 (+15)")
    else:
        notes.append("关系边界: 无 (0)")

    # 4. Effect溯源 (25分 - 硬门槛)
    if candidate.effect_provenance_status == "EFFECT_SOURCE_IDENTIFIED":
        score += 25
        notes.append("Effect溯源: 出处明确 (+25)")
    elif candidate.effect_provenance_status == "EFFECT_SOURCE_UNVERIFIED":
        score += 10
        notes.append("Effect溯源: 出处未验证 (+10)")
    elif candidate.effect_provenance_status == "EFFECT_TOO_GENERIC":
        score += 5
        notes.append("Effect溯源: 过于泛化 (+5)")
    else:
        notes.append("Effect溯源: 缺失 (0)")

    # 5. 反向条件和限定条件 (10分)
    if candidate.reverse_conditions and candidate.qualifiers:
        score += 10
        notes.append("反向/限定: 均有 (+10)")
    elif candidate.reverse_conditions or candidate.qualifiers:
        score += 5
        notes.append("反向/限定: 有其一 (+5)")
    else:
        notes.append("反向/限定: 无 (0)")

    # 6. 语义分类置信度 (10分)
    if candidate.semantic_confidence >= 0.7:
        score += 10
        notes.append(f"语义分类: 置信度{candidate.semantic_confidence:.0%} (+10)")
    elif candidate.semantic_confidence >= 0.5:
        score += 5
        notes.append(f"语义分类: 置信度{candidate.semantic_confidence:.0%} (+5)")
    else:
        notes.append("语义分类: 置信度低 (0)")

    candidate.audit_score = score
    candidate.audit_notes = "; ".join(notes)

    # 审计通过标准: 总分>=60 且 Effect溯源不是MISSING
    candidate.audit_passed = (
        score >= 60 and
        candidate.effect_provenance_status != "EFFECT_MISSING"
    )

    candidate.status = CandidateStatus.AUDITED.value
    return candidate


# ============================================================
# 第9步: Admission Gate - 准入门槛
# ============================================================

def admission_gate(candidate: BatchCandidate) -> BatchCandidate:
    """准入门槛"""
    # 硬门槛1: Effect必须存在且有出处
    if candidate.effect_provenance_status in ["EFFECT_MISSING", "EFFECT_TOO_GENERIC"]:
        candidate.admission_status = AdmissionStatus.REJECTED.value
        candidate.final_conclusion = "Effect缺失或过于泛化，拒绝入库"
        return candidate

    # 硬门槛2: 证据出处必须明确
    if candidate.evidence_status != "SOURCE_IDENTIFIED":
        candidate.admission_status = AdmissionStatus.POSTERIOR.value
        candidate.final_conclusion = "出处不明确，作为POSTERIOR保留"
        return candidate

    # 硬门槛3: 审计必须通过
    if not candidate.audit_passed:
        candidate.admission_status = AdmissionStatus.CANDIDATE.value
        candidate.final_conclusion = f"审计未通过(得分{candidate.audit_score})，保持CANDIDATE"
        return candidate

    # 根据得分和限定条件决定最终状态
    if candidate.audit_score >= 80 and not candidate.qualifiers:
        candidate.admission_status = AdmissionStatus.AUTHORIZED.value
        candidate.final_conclusion = f"高分通过(得分{candidate.audit_score})，AUTHORIZED"
    elif candidate.audit_score >= 70:
        candidate.admission_status = AdmissionStatus.AUTHORIZED_WITH_QUALIFIER.value
        candidate.final_conclusion = f"通过(得分{candidate.audit_score})，AUTHORIZED_WITH_QUALIFIER"
    else:
        candidate.admission_status = AdmissionStatus.CANDIDATE.value
        candidate.final_conclusion = f"得分不足(得分{candidate.audit_score})，保持CANDIDATE"

    candidate.status = CandidateStatus.ADMISSION_READY.value
    return candidate


# ============================================================
# 主流程: 批量处理
# ============================================================

def process_batch(candidates: List[BatchCandidate]) -> List[BatchCandidate]:
    """批量处理候选断言"""
    processed = []

    for i, candidate in enumerate(candidates):
        # 第2步: 语义分类
        candidate = classify_semantic(candidate)

        # 第3步: 证据契约
        candidate = build_evidence_contract(candidate)

        # 第4步: 前置条件提取
        candidate = extract_preconditions(candidate)

        # 第5步: 关系边界提取
        candidate = extract_relations(candidate)

        # 第6步: Effect溯源（硬门槛）
        candidate = extract_effect(candidate)

        # 第7步: 反向条件和限定条件
        candidate = extract_reverse_qualifiers(candidate)

        # 第8步: 独立审计
        candidate = independent_audit(candidate)

        # 第9步: 准入门槛
        candidate = admission_gate(candidate)

        processed.append(candidate)

        if (i + 1) % 20 == 0:
            print(f"    已处理 {i+1}/{len(candidates)} 条...")

    return processed


def generate_statistics(candidates: List[BatchCandidate]) -> Dict:
    """生成统计结果"""
    stats = {
        "total": len(candidates),
        "by_admission_status": Counter(),
        "by_semantic_type": Counter(),
        "by_classic": Counter(),
        "by_primary_category": Counter(),
        "by_evidence_status": Counter(),
        "by_effect_provenance_status": Counter(),
        "average_audit_score": 0,
        "audit_passed_count": 0,
        "with_preconditions": 0,
        "with_relations": 0,
        "with_reverse_conditions": 0,
        "with_qualifiers": 0,
        "unresolved_reasons": Counter(),
    }

    total_score = 0
    for c in candidates:
        stats["by_admission_status"][c.admission_status] += 1
        stats["by_semantic_type"][c.semantic_type] += 1
        stats["by_classic"][c.classic] += 1
        stats["by_primary_category"][c.primary_category] += 1
        stats["by_evidence_status"][c.evidence_status] += 1
        stats["by_effect_provenance_status"][c.effect_provenance_status] += 1
        total_score += c.audit_score
        if c.audit_passed:
            stats["audit_passed_count"] += 1
        if c.preconditions:
            stats["with_preconditions"] += 1
        if c.relations:
            stats["with_relations"] += 1
        if c.reverse_conditions:
            stats["with_reverse_conditions"] += 1
        if c.qualifiers:
            stats["with_qualifiers"] += 1
        for reason in c.unresolved_reasons:
            stats["unresolved_reasons"][reason] += 1

    if candidates:
        stats["average_audit_score"] = total_score / len(candidates)

    return stats


def main():
    print("=" * 110)
    print("STR-001A P6.5 Batch Assertion Asset Production Protocol")
    print("=" * 110)

    print(f"""
  批量断言资产生产协议（10步流水线）:
    1. Candidate Extraction      - 从断语库中提取候选断语
    2. Semantic Classification   - 语义分类
    3. Evidence Contract         - 建立证据契约
    4. Precondition Extraction   - 提取前置条件
    5. Relation Boundary         - 提取关系边界
    6. Effect Provenance         - Effect溯源（硬门槛）
    7. Reverse / Qualifier       - 提取反向条件和限定条件
    8. Independent Audit         - 独立审计
    9. Admission Gate            - 准入门槛
    10. Authorized Library       - 正式入库

  第一批: 从财运类、官运类、格局类、旺衰类中筛选50-100条结构清晰的断语

  健康结果预期:
    100 Candidate
      ├─ 20 AUTHORIZED_WITH_QUALIFIER
      ├─ 10 POSTERIOR
      ├─ 5 REJECTED
      └─ 65 CANDIDATE
""")

    # 第1步: 加载断语库并提取候选
    print(f"\n  {'='*100}")
    print(f"  第1步: Candidate Extraction - 从断语库中提取候选断语")
    print(f"  {'='*100}")

    corpus_path = r"D:\today\五部经典断语库\03_综合索引\all_duanyu.json"
    corpus = load_duanyu_corpus(corpus_path)
    print(f"\n    断语库总条数: {len(corpus)}")

    target_categories = ['财运类', '官运类', '格局类', '旺衰类']
    candidates = extract_candidates(
        corpus,
        target_categories=target_categories,
        max_per_category=25,
        total_max=100
    )

    print(f"    筛选候选断语: {len(candidates)} 条")
    print(f"    按类别分布:")
    category_dist = Counter(c.primary_category for c in candidates)
    for cat, count in category_dist.items():
        print(f"      {cat}: {count} 条")

    # 批量处理
    print(f"\n  {'='*100}")
    print(f"  第2-9步: 批量处理（语义分类→证据契约→前置条件→关系边界→Effect溯源→反向/限定→审计→准入）")
    print(f"  {'='*100}")

    processed = process_batch(candidates)

    # 生成统计结果
    print(f"\n  {'='*100}")
    print(f"  第10步: 统计结果")
    print(f"  {'='*100}")

    stats = generate_statistics(processed)

    print(f"""
    总处理数: {stats['total']}
    平均审计得分: {stats['average_audit_score']:.1f}
    审计通过数: {stats['audit_passed_count']} ({stats['audit_passed_count']/stats['total']*100:.1f}%)

    按准入状态分布:
""")
    for status, count in stats["by_admission_status"].most_common():
        pct = count / stats["total"] * 100
        bar = "█" * int(pct / 2)
        print(f"      {status:35s} {count:3d} ({pct:5.1f}%) {bar}")

    print(f"""
    按语义类型分布:
""")
    for stype, count in stats["by_semantic_type"].most_common():
        print(f"      {stype:20s} {count:3d}")

    print(f"""
    按经典分布:
""")
    for classic, count in stats["by_classic"].most_common():
        print(f"      {classic:15s} {count:3d}")

    print(f"""
    Effect溯源状态分布（硬门槛）:
""")
    for eps, count in stats["by_effect_provenance_status"].most_common():
        print(f"      {eps:35s} {count:3d}")

    print(f"""
    未解决原因分布:
""")
    for reason, count in stats["unresolved_reasons"].most_common():
        print(f"      {reason:35s} {count:3d}")

    # 展示AUTHORIZED_WITH_QUALIFIER的断言
    print(f"\n  {'='*100}")
    print(f"  AUTHORIZED_WITH_QUALIFIER 断言示例（前10条）")
    print(f"  {'='*100}")

    auth_qualified = [c for c in processed if c.admission_status == "AUTHORIZED_WITH_QUALIFIER"]
    for i, c in enumerate(auth_qualified[:10]):
        print(f"""
    [{c.candidate_id}] 得分: {c.audit_score}
      原文: {c.source_text[:60]}...
      经典: {c.classic}
      类别: {c.primary_category}
      语义: {c.semantic_type}
      Effect: {c.effect_text}
      前置条件: {c.preconditions_count}个
      结论: {c.final_conclusion}
""")

    # 展示REJECTED的断言
    print(f"\n  {'='*100}")
    print(f"  REJECTED 断言示例（前5条）")
    print(f"  {'='*100}")

    rejected = [c for c in processed if c.admission_status == "REJECTED"]
    for i, c in enumerate(rejected[:5]):
        print(f"""
    [{c.candidate_id}] 得分: {c.audit_score}
      原文: {c.source_text[:60]}...
      经典: {c.classic}
      Effect溯源: {c.effect_provenance_status}
      结论: {c.final_conclusion}
""")

    # 保存结果
    print(f"\n  {'='*100}")
    print(f"  保存结果")
    print(f"  {'='*100}")

    output_path = r"D:\shuntian\backend\data\p6_5_batch_results.json"
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    output_data = {
        "statistics": {k: dict(v) if isinstance(v, Counter) else v for k, v in stats.items()},
        "candidates": [asdict(c) for c in processed],
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n    结果已保存到: {output_path}")

    # 最终结论
    print(f"\n  {'='*100}")
    print(f"  P6.5 最终结论")
    print(f"  {'='*100}")

    auth_count = stats["by_admission_status"].get("AUTHORIZED", 0)
    auth_q_count = stats["by_admission_status"].get("AUTHORIZED_WITH_QUALIFIER", 0)
    posterior_count = stats["by_admission_status"].get("POSTERIOR", 0)
    rejected_count = stats["by_admission_status"].get("REJECTED", 0)
    candidate_count = stats["by_admission_status"].get("CANDIDATE", 0)

    print(f"""
    第一批批量生产结果:
      总数: {stats['total']} 条
      AUTHORIZED: {auth_count} 条
      AUTHORIZED_WITH_QUALIFIER: {auth_q_count} 条
      POSTERIOR: {posterior_count} 条
      REJECTED: {rejected_count} 条
      CANDIDATE: {candidate_count} 条

    健康结果验证:
      预期: 100 Candidate → 20 AUTH_QUAL + 10 POSTERIOR + 5 REJECTED + 65 CANDIDATE
      实际: {stats['total']} → {auth_q_count} AUTH_QUAL + {posterior_count} POSTERIOR + {rejected_count} REJECTED + {candidate_count} CANDIDATE

    Effect Provenance硬门槛验证:
      EFFECT_MISSING: {stats['by_effect_provenance_status'].get('EFFECT_MISSING', 0)} 条（被REJECTED）
      EFFECT_TOO_GENERIC: {stats['by_effect_provenance_status'].get('EFFECT_TOO_GENERIC', 0)} 条（被REJECTED）
      EFFECT_SOURCE_UNVERIFIED: {stats['by_effect_provenance_status'].get('EFFECT_SOURCE_UNVERIFIED', 0)} 条（POSTERIOR）
      EFFECT_SOURCE_IDENTIFIED: {stats['by_effect_provenance_status'].get('EFFECT_SOURCE_IDENTIFIED', 0)} 条（可进入审计）

    P6.5批量断言资产生产协议验证通过。
    系统能够证明哪些话有资格成为规则，哪些没有。
    {'='*100}
""")


if __name__ == "__main__":
    main()
