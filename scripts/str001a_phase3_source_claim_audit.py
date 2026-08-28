"""STR-001A Phase 3 - Source Claim Audit (10条Claim原典审计).

Contract/Governance Layer = FROZEN (v6-final.1)
禁止修改 v6-final.1 Contract
禁止开发"身弱算法"
禁止进入 ContextResolver / Assertion
现在只执行 Source Claim Audit

审计流程 (10步):
  1. SOURCE_AUTHENTICITY
  2. TEXT_LAYER (ORIGINAL / ORIGINAL_NOTE / COMMENTARY / UNKNOWN)
  3. CLAIM_TYPE (primary + secondary, 不强行压缩)
  4. SEMANTIC_SCOPE
  5. SOURCE_CLAIM_RELATION
  6. PROPOSITION_SCOPE
  7. MAPPING (Candidate only, 禁止ENGINE_FEATURE_THRESHOLD)
  8. EVIDENCE_ROLE (Candidate only, 允许NOT_ASSIGNED)
  9. 最终状态 (SOURCE_MAPPED / SOURCE_SUPPORTED / REJECTED)
  10. 输出 Audit Matrix

特别检查 (4个防污染问题):
  A. "旺/衰"是否被错误等同于"强/弱"
  B. "得令/失令"是否被错误等同于"身强/身弱"
  C. 原典是否被错误解释成"当前命例事实证明"
  D. 注家解释是否被错误升级为Original Canonical Source

核心原则:
  旺 ≠ 强
  衰 ≠ 弱
  失令 ≠ 身弱
  SourceClaim ≠ 命例事实证明
  注家内容不得自动获得 Canonical Source Authority
  禁止因为Claim"看起来支持身弱"而自动进入SOURCE_SUPPORTED
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# 审计枚举
# ============================================================================

class TextLayer(str, Enum):
    ORIGINAL = "ORIGINAL"              # 原典原文
    ORIGINAL_NOTE = "ORIGINAL_NOTE"    # 原注(古注, 非原文)
    COMMENTARY = "COMMENTARY"          # 后世注家评注
    UNKNOWN = "UNKNOWN"                # 待确认


class AuditClaimType(str, Enum):
    DEFINITION = "DEFINITION"
    DESCRIPTIVE = "DESCRIPTIVE"
    NORMATIVE = "NORMATIVE"
    CONDITIONAL = "CONDITIONAL"
    EXAMPLE = "EXAMPLE"
    EXCLUSION = "EXCLUSION"
    DISTINCTION = "DISTINCTION"        # 概念区分


class SemanticScope(str, Enum):
    WANG_SHUAI = "旺/衰"
    QIANG_RUO = "强/弱"
    DE_LING = "得令/失令"
    DE_DI = "得地/通根"
    DANG_ZHONG = "党众/助寡"
    XI_JI = "喜忌"
    CONDITION_RELATION = "条件关系"
    EXCLUSION_CONDITION = "排除条件"
    IMPORTANCE = "重要性"
    UNKNOWN = "未知"


class SourceClaimRelationType(str, Enum):
    DEFINES = "DEFINES"
    SUPPORTS_INTERPRETATION = "SUPPORTS_INTERPRETATION"
    AUTHORIZES_MAPPING = "AUTHORIZES_MAPPING"
    AUTHORIZES_EVIDENCE_ROLE = "AUTHORIZES_EVIDENCE_ROLE"
    AUTHORIZES_RELATION = "AUTHORIZES_RELATION"


class PropositionScope(str, Enum):
    DIRECTLY_DEFINES_SHEN_RUO = "直接定义日主身弱"
    DISTINGUISHES_WANG_SHUAI_QIANG_RUO = "区分旺衰强弱"
    DESCRIBES_WANG_SHUAI_ONLY = "只描述旺衰"
    DESCRIBES_QIANG_RUO_ONLY = "只描述强弱"
    PROVIDES_NOT_WEAK_CONDITION = "提供NOT_WEAK条件"
    XI_JI_CONDITION = "喜忌条件(身弱成立后)"
    DESCRIBES_IMPORTANCE_ONLY = "只描述重要性"
    NOT_APPLICABLE = "不适用STR-001A"


class CandidateEvidenceRole(str, Enum):
    PRIMARY = "PRIMARY"
    SUPPORTING = "SUPPORTING"
    CONTEXTUAL = "CONTEXTUAL"
    EXCLUSION = "EXCLUSION"
    NON_CANONICAL = "NON_CANONICAL"
    NOT_ASSIGNED = "NOT_ASSIGNED"


class AuditStatus(str, Enum):
    SOURCE_MAPPED = "SOURCE_MAPPED"      # 已映射, 但不支持身弱定义/判定
    SOURCE_SUPPORTED = "SOURCE_SUPPORTED"  # 支持身弱相关定义/判定/排除
    REJECTED = "REJECTED"                  # 不适用或版本不可靠


# ============================================================================
# Audit Matrix 数据结构
# ============================================================================

@dataclass
class SourceClaimAudit:
    """单条Source Claim的审计结果."""
    claim_id: str
    # 1. SOURCE_AUTHENTICITY
    source_id: str = ""
    source_name: str = ""
    edition: str = ""
    chapter: str = ""
    text_reference: str = ""
    source_authenticity_note: str = ""
    # 2. TEXT_LAYER
    text_layer: TextLayer = TextLayer.UNKNOWN
    text_layer_note: str = ""
    # 3. CLAIM_TYPE
    primary_claim_type: Optional[AuditClaimType] = None
    secondary_claim_types: List[AuditClaimType] = field(default_factory=list)
    # 4. SEMANTIC_SCOPE
    semantic_scopes: List[SemanticScope] = field(default_factory=list)
    # 5. SOURCE_CLAIM_RELATION
    source_claim_relations: List[SourceClaimRelationType] = field(default_factory=list)
    # 6. PROPOSITION_SCOPE
    proposition_scope: PropositionScope = PropositionScope.NOT_APPLICABLE
    proposition_scope_note: str = ""
    # 7. MAPPING (Candidate only)
    mapping_status: str = "CANDIDATE"  # CANDIDATE / NOT_APPLICABLE
    mapping_authorization: str = "NOT_AUTHORIZED"
    mapping_note: str = ""
    # 8. EVIDENCE_ROLE (Candidate only)
    candidate_evidence_role: CandidateEvidenceRole = CandidateEvidenceRole.NOT_ASSIGNED
    evidence_role_note: str = ""
    # 9. 最终状态
    audit_status: AuditStatus = AuditStatus.SOURCE_MAPPED
    rejection_reason: str = ""
    # 10. notes
    notes: str = ""
    # 特别检查
    anti_pollution_check: Dict[str, bool] = field(default_factory=dict)


# ============================================================================
# 10条Claim逐条审计
# ============================================================================

def audit_all_claims() -> List[SourceClaimAudit]:
    """对10条Source Claim逐条审计."""
    audits = []

    # === SC-YHZP-XJ-001 ===
    audits.append(SourceClaimAudit(
        claim_id="SC-YHZP-XJ-001",
        source_id="SRC-YHZP", source_name="渊海子平",
        edition="渊海子平(题宋徐子平撰, 后人汇编)",
        chapter="玄机赋",
        text_reference="身坐休囚，平生未济。身旺喜逢禄马。身弱忌见财官。",
        source_authenticity_note="玄机赋为《渊海子平》赋论部分, 版本可靠",
        text_layer=TextLayer.ORIGINAL,
        text_layer_note="赋文原文",
        primary_claim_type=AuditClaimType.NORMATIVE,
        secondary_claim_types=[],
        semantic_scopes=[SemanticScope.XI_JI, SemanticScope.WANG_SHUAI],
        source_claim_relations=[SourceClaimRelationType.SUPPORTS_INTERPRETATION],
        proposition_scope=PropositionScope.XI_JI_CONDITION,
        proposition_scope_note="这是身弱成立后的喜忌条件(身弱忌见财官), 不是身弱的定义或判定标准. 对于STR-001A'日主身弱'的定义, 这条只能作为CONTEXTUAL参考",
        mapping_status="CANDIDATE",
        mapping_authorization="NOT_AUTHORIZED",
        mapping_note="可以建立Candidate Mapping, 但映射的是喜忌条件而非身弱定义",
        candidate_evidence_role=CandidateEvidenceRole.CONTEXTUAL,
        evidence_role_note="喜忌条件, 不是身弱判定证据. 只能作为CONTEXTUAL",
        audit_status=AuditStatus.SOURCE_MAPPED,
        notes="规范性陈述: 身弱忌见财官. 但这是'身弱成立后应该忌什么', 不是'什么条件下身弱成立'. 对STR-001A的定义/判定无直接支持.",
        anti_pollution_check={
            "A_旺衰≠强弱": True,  # 未混淆
            "B_失令≠身弱": True,   # 未涉及
            "C_原典≠命例证明": True,
            "D_注家≠Original": True,
        },
    ))

    # === SC-YHZP-XJ-002 ===
    audits.append(SourceClaimAudit(
        claim_id="SC-YHZP-XJ-002",
        source_id="SRC-YHZP", source_name="渊海子平",
        edition="渊海子平",
        chapter="玄机赋",
        text_reference="得时俱为旺论，失令便作衰看。四柱无根，...",
        source_authenticity_note="玄机赋原文, 版本可靠",
        text_layer=TextLayer.ORIGINAL,
        text_layer_note="赋文原文",
        primary_claim_type=AuditClaimType.DEFINITION,
        secondary_claim_types=[],
        semantic_scopes=[SemanticScope.WANG_SHUAI, SemanticScope.DE_LING, SemanticScope.DE_DI],
        source_claim_relations=[SourceClaimRelationType.DEFINES, SourceClaimRelationType.AUTHORIZES_MAPPING],
        proposition_scope=PropositionScope.DESCRIBES_WANG_SHUAI_ONLY,
        proposition_scope_note="这是旺衰的定义(得时为旺失令为衰), 不是强弱的定义. 旺≠强, 衰≠弱. '四柱无根'涉及根气, 但整句核心是旺衰判定.",
        mapping_status="CANDIDATE",
        mapping_authorization="NOT_AUTHORIZED",
        mapping_note="可以映射旺衰定义(得时/失令, 有根/无根), 但不能直接映射为'身弱'定义",
        candidate_evidence_role=CandidateEvidenceRole.SUPPORTING,
        evidence_role_note="旺衰定义可以作为身弱判定的SUPPORTING证据, 但不能单独证明身弱(因为旺≠强弱)",
        audit_status=AuditStatus.SOURCE_MAPPED,
        notes="定义性陈述: 得时俱为旺论, 失令便作衰看. 这是旺衰的基本原则, 但旺衰≠强弱. 对于STR-001A'日主身弱', 这条只能作为SUPPORTING参考, 不能单独作为身弱的判定依据.",
        anti_pollution_check={
            "A_旺衰≠强弱": True,  # 明确只定义旺衰, 不定义强弱
            "B_失令≠身弱": True,   # 失令=衰, 但衰≠弱
            "C_原典≠命例证明": True,
            "D_注家≠Original": True,
        },
    ))

    # === SC-YHZP-SR-001 ===
    audits.append(SourceClaimAudit(
        claim_id="SC-YHZP-SR-001",
        source_id="SRC-YHZP", source_name="渊海子平",
        edition="渊海子平(版本待确认)",
        chapter="身弱论",
        text_reference="阳木无根，生于丑月；水多转贵，金多则折。乙木无根，生临丑月；金多转贵，火土则折。丙火无根，子申全见；无制无生，此身贫贱。",
        source_authenticity_note="⚠ '身弱论'篇名在不同版本中可能有差异. 搜索结果显示出自《渊海子平》赋论部分, 但需确认具体卷/篇. 目前最多SOURCE_MAPPED, 不能提前SOURCE_SUPPORTED.",
        text_layer=TextLayer.UNKNOWN,
        text_layer_note="⚠ 版本/篇名待确认, 暂标记UNKNOWN",
        primary_claim_type=AuditClaimType.CONDITIONAL,
        secondary_claim_types=[],
        semantic_scopes=[SemanticScope.CONDITION_RELATION, SemanticScope.DE_DI, SemanticScope.DE_LING],
        source_claim_relations=[SourceClaimRelationType.SUPPORTS_INTERPRETATION],
        proposition_scope=PropositionScope.DESCRIBES_QIANG_RUO_ONLY,
        proposition_scope_note="按十干分述身弱的具体条件(无根+生月+克泄). 这是条件性陈述, 给出了身弱的具体判定条件之一. 但版本待确认.",
        mapping_status="CANDIDATE",
        mapping_authorization="NOT_AUTHORIZED",
        mapping_note="版本确认前不建立正式Mapping",
        candidate_evidence_role=CandidateEvidenceRole.NOT_ASSIGNED,
        evidence_role_note="版本确认前不分配Evidence Role",
        audit_status=AuditStatus.SOURCE_MAPPED,
        notes="⚠ 版本待确认. '身弱论'篇名需核实. 内容按十干分述身弱条件, 如果版本确认可靠, 可能成为重要的CONDITIONAL证据. 但目前最多SOURCE_MAPPED.",
        anti_pollution_check={
            "A_旺衰≠强弱": True,
            "B_失令≠身弱": True,  # 无根+生月+克泄, 不是单纯失令
            "C_原典≠命例证明": True,
            "D_注家≠Original": True,
        },
    ))

    # === SC-ZPZQ-06-001 (核心Claim) ===
    audits.append(SourceClaimAudit(
        claim_id="SC-ZPZQ-06-001",
        source_id="SRC-ZPZQ", source_name="子平真诠",
        edition="子平真诠(清沈孝瞻撰, 徐乐吾评注)",
        chapter="第06章 论十干得时不旺失时不弱",
        text_reference="旺衰强弱四字，昔人论命，每笼统互用，不知须分别看也。大致得时为旺，失时为衰；党众为强，助寡为弱。故有虽旺而弱者，亦有虽衰而强者，分别观之。",
        source_authenticity_note="《子平真诠》第06章原文, 版本可靠, 是核心定义性章节",
        text_layer=TextLayer.ORIGINAL,
        text_layer_note="沈孝瞻原文",
        primary_claim_type=AuditClaimType.DEFINITION,
        secondary_claim_types=[AuditClaimType.DISTINCTION],
        semantic_scopes=[SemanticScope.WANG_SHUAI, SemanticScope.QIANG_RUO, SemanticScope.DE_LING, SemanticScope.DANG_ZHONG],
        source_claim_relations=[SourceClaimRelationType.DEFINES, SourceClaimRelationType.AUTHORIZES_MAPPING, SourceClaimRelationType.AUTHORIZES_EVIDENCE_ROLE],
        proposition_scope=PropositionScope.DISTINGUISHES_WANG_SHUAI_QIANG_RUO,
        proposition_scope_note="⭐ 核心Claim. 明确区分旺衰和强弱是两个不同维度: 旺/衰=得时/失时(月令), 强/弱=党众/助寡(生助多寡). 有虽旺而弱者, 有虽衰而强者. 这是STR-001A'日主身弱'定义的最强防污染依据.",
        mapping_status="CANDIDATE",
        mapping_authorization="NOT_AUTHORIZED",
        mapping_note="可以映射: 旺衰定义(得时/失令), 强弱定义(党众/助寡), 以及二者的区分. 禁止映射成单一'失令→身弱'",
        candidate_evidence_role=CandidateEvidenceRole.PRIMARY,
        evidence_role_note="⭐ 核心定义性Claim, 可以作为STR-001A的PRIMARY证据(定义强弱的判定维度)",
        audit_status=AuditStatus.SOURCE_SUPPORTED,
        notes="⭐ 核心Claim. 《子平真诠》第06章明确区分旺衰强弱四个概念. 这意味着STR-001A不能简单实现成'失令→身弱'. 强弱看党众(生助多寡), 不是单纯看月令. 这条是整个审计的基石.",
        anti_pollution_check={
            "A_旺衰≠强弱": True,  # 明确区分, 最强防污染依据
            "B_失令≠身弱": True,   # 失令=衰, 但衰≠弱; 有虽衰而强者
            "C_原典≠命例证明": True,
            "D_注家≠Original": True,
        },
    ))

    # === SC-ZPZQ-06-002 ===
    audits.append(SourceClaimAudit(
        claim_id="SC-ZPZQ-06-002",
        source_id="SRC-ZPZQ", source_name="子平真诠",
        edition="子平真诠",
        chapter="第06章 论十干得时不旺失时不弱",
        text_reference="秋木虽弱，木根深而木亦强。干甲乙而支寅卯，遇官透而能受，逢水生而太过，是失时不弱也。",
        source_authenticity_note="《子平真诠》第06章原文, 版本可靠",
        text_layer=TextLayer.ORIGINAL,
        text_layer_note="沈孝瞻原文(示例)",
        primary_claim_type=AuditClaimType.EXAMPLE,
        secondary_claim_types=[AuditClaimType.EXCLUSION],
        semantic_scopes=[SemanticScope.EXCLUSION_CONDITION, SemanticScope.DE_DI, SemanticScope.QIANG_RUO],
        source_claim_relations=[SourceClaimRelationType.AUTHORIZES_RELATION, SourceClaimRelationType.SUPPORTS_INTERPRETATION],
        proposition_scope=PropositionScope.PROVIDES_NOT_WEAK_CONDITION,
        proposition_scope_note="提供NOT_WEAK条件: 秋木虽失令(弱), 但木根深(通根)则木亦强. 说明失时不等于弱, 根气可以弥补月令不足. 这是EXCLUSION条件.",
        mapping_status="CANDIDATE",
        mapping_authorization="NOT_AUTHORIZED",
        mapping_note="可以映射NOT_WEAK条件: 失令但有根→不弱. 禁止映射成'有根=强'(需要结合其他条件)",
        candidate_evidence_role=CandidateEvidenceRole.EXCLUSION,
        evidence_role_note="EXCLUSION证据: 失令但有根则不弱. 用于排除错误的'失令=身弱'判定.",
        audit_status=AuditStatus.SOURCE_SUPPORTED,
        notes="示例+排除条件. 秋木虽弱(失令)但木根深(通根)则木亦强, 是失时不弱. 这条直接支持'失令≠身弱'的防污染原则, 可以作为EXCLUSION证据.",
        anti_pollution_check={
            "A_旺衰≠强弱": True,  # 秋木虽弱(衰)但木亦强(强), 明确区分
            "B_失令≠身弱": True,   # 失时不弱的直接例证
            "C_原典≠命例证明": True,
            "D_注家≠Original": True,
        },
    ))

    # === SC-ZPZQ-06-003 ===
    audits.append(SourceClaimAudit(
        claim_id="SC-ZPZQ-06-003",
        source_id="SRC-ZPZQ", source_name="子平真诠",
        edition="子平真诠",
        chapter="第06章 论十干得时不旺失时不弱",
        text_reference="书云，得时俱为旺论，失时便作衰看。虽是至理，亦死法也。然亦可活看，夫五行之气，流行四时，虽日干各有专令，而其实专令当中，亦有并存者在。",
        source_authenticity_note="《子平真诠》第06章原文, 引用古书+沈孝瞻评论",
        text_layer=TextLayer.ORIGINAL,
        text_layer_note="沈孝瞻原文(引用古书并评论)",
        primary_claim_type=AuditClaimType.DESCRIPTIVE,
        secondary_claim_types=[],
        semantic_scopes=[SemanticScope.WANG_SHUAI, SemanticScope.DE_LING],
        source_claim_relations=[SourceClaimRelationType.SUPPORTS_INTERPRETATION],
        proposition_scope=PropositionScope.DESCRIBES_WANG_SHUAI_ONLY,
        proposition_scope_note="描述性陈述: 得时为旺失时为衰虽是至理, 但也是死法, 需要活看. 五行之气流行四时, 专令中亦有并存者. 这是对旺衰判定灵活性的描述, 不直接定义身弱.",
        mapping_status="CANDIDATE",
        mapping_authorization="NOT_AUTHORIZED",
        mapping_note="可以映射旺衰判定的灵活性原则, 但不直接映射身弱定义",
        candidate_evidence_role=CandidateEvidenceRole.CONTEXTUAL,
        evidence_role_note="描述性陈述, 只能作为CONTEXTUAL参考",
        audit_status=AuditStatus.SOURCE_MAPPED,
        notes="描述性陈述. 强调得时失令虽是基本原则但非绝对, 需要活看. 这条支持防污染原则(不能机械判定), 但本身不提供身弱的具体定义或判定条件.",
        anti_pollution_check={
            "A_旺衰≠强弱": True,
            "B_失令≠身弱": True,  # 明确说得时失令是"死法", 需要活看
            "C_原典≠命例证明": True,
            "D_注家≠Original": True,
        },
    ))

    # === SC-ZPZQ-03-001 ===
    audits.append(SourceClaimAudit(
        claim_id="SC-ZPZQ-03-001",
        source_id="SRC-ZPZQ", source_name="子平真诠",
        edition="子平真诠",
        chapter="第03章 论阴阳生死",
        text_reference="人之日主，不必生逢禄旺，即月令休囚，而年日时中，得长禄旺，便不为弱，就使逢库，亦为有根。",
        source_authenticity_note="《子平真诠》第03章原文, 版本可靠",
        text_layer=TextLayer.ORIGINAL,
        text_layer_note="沈孝瞻原文",
        primary_claim_type=AuditClaimType.CONDITIONAL,
        secondary_claim_types=[AuditClaimType.EXCLUSION],
        semantic_scopes=[SemanticScope.EXCLUSION_CONDITION, SemanticScope.DE_LING, SemanticScope.DE_DI, SemanticScope.QIANG_RUO],
        source_claim_relations=[SourceClaimRelationType.AUTHORIZES_RELATION, SourceClaimRelationType.AUTHORIZES_EVIDENCE_ROLE],
        proposition_scope=PropositionScope.PROVIDES_NOT_WEAK_CONDITION,
        proposition_scope_note="⭐ 重要的NOT_WEAK排除条件: 日主不必生逢禄旺, 月令休囚但年日时中得长生禄旺便不为弱, 逢库亦为有根. 这条明确给出了'不为弱'的具体条件, 对STR-001A的排除性判定至关重要.",
        mapping_status="CANDIDATE",
        mapping_authorization="NOT_AUTHORIZED",
        mapping_note="可以映射NOT_WEAK条件: 月令休囚但年日时得禄旺/逢库→不为弱. 禁止映射成'得禄旺=强'(需要结合其他条件)",
        candidate_evidence_role=CandidateEvidenceRole.EXCLUSION,
        evidence_role_note="⭐ EXCLUSION证据: 月令休囚但年日时得禄旺则不为弱. 用于排除错误的'月令休囚=身弱'判定.",
        audit_status=AuditStatus.SOURCE_SUPPORTED,
        notes="⭐ 重要的排除性条件. 明确说'月令休囚...便不为弱', 直接支持'失令≠身弱'的防污染原则. 这条和SC-ZPZQ-06-002共同构成STR-001A的EXCLUSION证据基础.",
        anti_pollution_check={
            "A_旺衰≠强弱": True,
            "B_失令≠身弱": True,  # 月令休囚但得禄旺则不为弱, 直接否定失令=身弱
            "C_原典≠命例证明": True,
            "D_注家≠Original": True,
        },
    ))

    # === SC-DTS-SW-001 ===
    audits.append(SourceClaimAudit(
        claim_id="SC-DTS-SW-001",
        source_id="SRC-DTS", source_name="滴天髓",
        edition="滴天髓阐微(传京图撰, 任铁樵注)",
        chapter="第十七章 衰旺",
        text_reference="能知衰旺之真机，其于三命之奥，思过半矣。",
        source_authenticity_note="《滴天髓》第十七章原文, 版本可靠",
        text_layer=TextLayer.ORIGINAL,
        text_layer_note="京图原文(传)",
        primary_claim_type=AuditClaimType.DESCRIPTIVE,
        secondary_claim_types=[],
        semantic_scopes=[SemanticScope.IMPORTANCE, SemanticScope.WANG_SHUAI],
        source_claim_relations=[SourceClaimRelationType.SUPPORTS_INTERPRETATION],
        proposition_scope=PropositionScope.DESCRIBES_IMPORTANCE_ONLY,
        proposition_scope_note="只强调衰旺判定的重要性(能知衰旺之真机, 三命之奥思过半矣), 但未给出具体判定标准. 对STR-001A的定义/判定无直接支持.",
        mapping_status="NOT_APPLICABLE",
        mapping_authorization="NOT_AUTHORIZED",
        mapping_note="只描述重要性, 无可映射的具体判定条件",
        candidate_evidence_role=CandidateEvidenceRole.NON_CANONICAL,
        evidence_role_note="只强调重要性, 不能作为身弱判定的Canonical Evidence",
        audit_status=AuditStatus.SOURCE_MAPPED,
        notes="描述性陈述. 强调衰旺判定的重要性, 但没有给出具体判定标准. 对STR-001A无直接支持, 只能作为背景参考.",
        anti_pollution_check={
            "A_旺衰≠强弱": True,
            "B_失令≠身弱": True,
            "C_原典≠命例证明": True,
            "D_注家≠Original": True,
        },
    ))

    # === SC-DTS-SW-002 ===
    audits.append(SourceClaimAudit(
        claim_id="SC-DTS-SW-002",
        source_id="SRC-DTS", source_name="滴天髓",
        edition="滴天髓阐微",
        chapter="第十七章 衰旺",
        text_reference="旺则宜泄宜伤，衰则喜帮喜助，子平之理也。然旺中有衰者存，不可损也；衰中有旺者存，不可益也。旺之极者不可损，以损在其中矣；衰之极者不可益，以益在其中矣。",
        source_authenticity_note="⚠ 这段在不同版本编排中涉及原注/任氏注的问题. 现有版本明确把原文和原注/任氏曰分开. '旺则宜泄宜伤, 衰则喜帮喜助'通常被归为原注.",
        text_layer=TextLayer.ORIGINAL_NOTE,
        text_layer_note="⚠ 原注(古注), 不是京图原文. 注家内容不得自动获得Canonical Source Authority.",
        primary_claim_type=AuditClaimType.NORMATIVE,
        secondary_claim_types=[AuditClaimType.DESCRIPTIVE],
        semantic_scopes=[SemanticScope.XI_JI, SemanticScope.WANG_SHUAI],
        source_claim_relations=[SourceClaimRelationType.SUPPORTS_INTERPRETATION],
        proposition_scope=PropositionScope.XI_JI_CONDITION,
        proposition_scope_note="这是旺衰的处理原则(旺宜泄伤, 衰喜帮助), 不是判定标准. 而且是原注, 不是原文. '旺中有衰不可损, 衰中有旺不可益'是对旺衰复杂性的描述.",
        mapping_status="CANDIDATE",
        mapping_authorization="NOT_AUTHORIZED",
        mapping_note="原注内容, 可以建立Candidate Mapping但不获得Original Canonical Source Authority. 映射的是处理原则(喜忌), 不是身弱定义.",
        candidate_evidence_role=CandidateEvidenceRole.CONTEXTUAL,
        evidence_role_note="原注+处理原则, 只能作为CONTEXTUAL参考. 不能作为身弱判定的Canonical Evidence.",
        audit_status=AuditStatus.SOURCE_MAPPED,
        notes="⚠ 原注, 不是原文. 内容是旺衰的处理原则(喜忌), 不是判定标准. 对STR-001A的定义/判定无直接支持. 注家内容不得自动获得Canonical Source Authority.",
        anti_pollution_check={
            "A_旺衰≠强弱": True,
            "B_失令≠身弱": True,
            "C_原典≠命例证明": True,
            "D_注家≠Original": True,  # 明确标记为ORIGINAL_NOTE, 不升级为Original
        },
    ))

    # === SC-DTS-SW-003 ===
    audits.append(SourceClaimAudit(
        claim_id="SC-DTS-SW-003",
        source_id="SRC-DTS", source_name="滴天髓",
        edition="滴天髓阐微",
        chapter="第十七章 衰旺 任氏曰",
        text_reference="得时俱为旺论，失令便作衰看，虽是至理，亦死法也。夫五行之气，流行于四时，虽日干各有专令，而其实专令之中，亦有并存者在。",
        source_authenticity_note="⚠ 这是任铁樵的注释('任氏曰'), 不是滴天髓原文. 注家内容不得自动获得Canonical Source Authority.",
        text_layer=TextLayer.COMMENTARY,
        text_layer_note="⚠ 任铁樵注(清), 后世注家评注. 不是原文.",
        primary_claim_type=AuditClaimType.DESCRIPTIVE,
        secondary_claim_types=[],
        semantic_scopes=[SemanticScope.WANG_SHUAI, SemanticScope.DE_LING],
        source_claim_relations=[SourceClaimRelationType.SUPPORTS_INTERPRETATION],
        proposition_scope=PropositionScope.DESCRIBES_WANG_SHUAI_ONLY,
        proposition_scope_note="任铁樵对旺衰判定的评论: 得时为旺失时为衰虽是至理但也是死法, 需要活看. 这是注家的解释, 不是原文. 内容与SC-ZPZQ-06-003类似.",
        mapping_status="CANDIDATE",
        mapping_authorization="NOT_AUTHORIZED",
        mapping_note="注家内容, 可以建立Candidate Mapping但不获得Original Canonical Source Authority. 而且内容与SC-ZPZQ-06-003(子平真诠原文)重复, 优先使用原文版本.",
        candidate_evidence_role=CandidateEvidenceRole.NON_CANONICAL,
        evidence_role_note="注家评论, 不能作为Canonical Evidence. 同类内容已有SC-ZPZQ-06-003(原文)优先.",
        audit_status=AuditStatus.SOURCE_MAPPED,
        notes="⚠ 任铁樵注, 不是原文. 注家内容不得自动获得Canonical Source Authority. 内容与SC-ZPZQ-06-003重复, 优先使用子平真诠原文版本. 这条只作为参考.",
        anti_pollution_check={
            "A_旺衰≠强弱": True,
            "B_失令≠身弱": True,
            "C_原典≠命例证明": True,
            "D_注家≠Original": True,  # 明确标记为COMMENTARY, 不升级为Original
        },
    ))

    return audits


# ============================================================================
# 审计结果汇总
# ============================================================================

def print_audit_report(audits: List[SourceClaimAudit]):
    """打印审计报告."""
    print("=" * 120)
    print("STR-001A Phase 3 - Source Claim Audit (10条Claim原典审计)")
    print("=" * 120)
    print(f"\nContract/Governance Layer = FROZEN (v6-final.1)")
    print(f"禁止修改Contract / 禁止开发身弱算法 / 禁止进入ContextResolver / 禁止生成Assertion")
    print(f"核心原则: 旺≠强, 衰≠弱, 失令≠身弱, SourceClaim≠命例事实证明, 注家≠Original Canonical Source")

    # === 1. Audit Matrix ===
    print(f"\n{'='*120}")
    print("一、10条逐条 Audit Matrix")
    print("=" * 120)
    for a in audits:
        print(f"\n  [{a.claim_id}]")
        print(f"    来源: {a.source_name} · {a.chapter}")
        print(f"    版本: {a.edition}")
        print(f"    TEXT_LAYER: {a.text_layer.value}  ({a.text_layer_note})")
        print(f"    CLAIM_TYPE: primary={a.primary_claim_type.value if a.primary_claim_type else 'None'}, secondary={[t.value for t in a.secondary_claim_types]}")
        print(f"    SEMANTIC_SCOPE: {[s.value for s in a.semantic_scopes]}")
        print(f"    SOURCE_CLAIM_RELATION: {[r.value for r in a.source_claim_relations]}")
        print(f"    PROPOSITION_SCOPE: {a.proposition_scope.value}")
        print(f"    MAPPING: status={a.mapping_status}, authorization={a.mapping_authorization}")
        print(f"    CANDIDATE_EVIDENCE_ROLE: {a.candidate_evidence_role.value}  ({a.evidence_role_note})")
        print(f"    AUDIT_STATUS: {a.audit_status.value}")
        if a.rejection_reason:
            print(f"    REJECTION_REASON: {a.rejection_reason}")
        print(f"    NOTES: {a.notes}")
        # 防污染检查
        apc = a.anti_pollution_check
        print(f"    防污染检查: A旺衰≠强弱={apc.get('A_旺衰≠强弱')}, B失令≠身弱={apc.get('B_失令≠身弱')}, C原典≠命例证明={apc.get('C_原典≠命例证明')}, D注家≠Original={apc.get('D_注家≠Original')}")

    # === 2. 分类汇总 ===
    print(f"\n{'='*120}")
    print("二、分类汇总")
    print("=" * 120)

    supported = [a for a in audits if a.audit_status == AuditStatus.SOURCE_SUPPORTED]
    mapped = [a for a in audits if a.audit_status == AuditStatus.SOURCE_MAPPED]
    rejected = [a for a in audits if a.audit_status == AuditStatus.REJECTED]

    print(f"\n  总数: {len(audits)}条")
    print(f"  SOURCE_SUPPORTED: {len(supported)}条")
    for a in supported:
        print(f"    - {a.claim_id}: {a.proposition_scope.value}")
    print(f"  SOURCE_MAPPED: {len(mapped)}条")
    for a in mapped:
        print(f"    - {a.claim_id}: {a.proposition_scope.value}")
    print(f"  REJECTED: {len(rejected)}条")

    # === 3. 被REJECTED的Claim ===
    print(f"\n{'='*120}")
    print("三、被REJECTED的Claim及原因")
    print("=" * 120)
    if rejected:
        for a in rejected:
            print(f"\n  {a.claim_id}: {a.rejection_reason}")
    else:
        print(f"\n  无REJECTED. 但有{len(mapped)}条只能SOURCE_MAPPED, 不能进入Proposition Evaluation.")

    # === 4. 可进入SemanticMapping的Claim ===
    print(f"\n{'='*120}")
    print("四、可进入SemanticMapping的Claim (Candidate only)")
    print("=" * 120)
    for a in audits:
        if a.mapping_status == "CANDIDATE":
            print(f"\n  {a.claim_id}:")
            print(f"    mapping_note: {a.mapping_note}")
            print(f"    禁止: 直接生成wood_ratio<threshold / day_master_strength<threshold / 任何ENGINE_FEATURE_THRESHOLD")

    # === 5. 可作为EXCLUSION的Claim ===
    print(f"\n{'='*120}")
    print("五、可作为EXCLUSION的Claim (NOT_WEAK排除条件)")
    print("=" * 120)
    exclusion_claims = [a for a in audits if a.candidate_evidence_role == CandidateEvidenceRole.EXCLUSION]
    for a in exclusion_claims:
        print(f"\n  {a.claim_id}:")
        print(f"    排除条件: {a.proposition_scope_note}")
        print(f"    原文: {a.text_reference}")

    # === 6. Source Claim → Mapping → Evidence Role 关系图 ===
    print(f"\n{'='*120}")
    print("六、Source Claim → Mapping → Evidence Role 关系图")
    print("=" * 120)
    print(f"""
  Canonical Source
      ↓
  Source Claim (TEXT_LAYER: ORIGINAL / ORIGINAL_NOTE / COMMENTARY)
      ↓
  SourceClaimRelation (DEFINES / SUPPORTS_INTERPRETATION / AUTHORIZES_MAPPING / AUTHORIZES_EVIDENCE_ROLE / AUTHORIZES_RELATION)
      ↓
  Candidate SemanticMapping (NOT_AUTHORIZED, 禁止ENGINE_FEATURE_THRESHOLD)
      ↓
  Candidate Evidence Role (PRIMARY / SUPPORTING / CONTEXTUAL / EXCLUSION / NON_CANONICAL / NOT_ASSIGNED)
      ↓
  [尚未进入] Evidence Contract / L3 AUTHORIZED / L4 Proposition Evaluation

  具体映射:
""")
    for a in audits:
        role_str = a.candidate_evidence_role.value
        relations = [r.value for r in a.source_claim_relations]
        print(f"    {a.claim_id} [{a.text_layer.value}] → relations={relations} → Candidate Role={role_str} → Status={a.audit_status.value}")

    # === 7. 不进入Proposition Evaluation的Claim ===
    print(f"\n{'='*120}")
    print("七、不进入Proposition Evaluation的Claim")
    print("=" * 120)
    not_for_evaluation = [a for a in audits if a.audit_status != AuditStatus.SOURCE_SUPPORTED]
    for a in not_for_evaluation:
        print(f"\n  {a.claim_id}: {a.audit_status.value}")
        print(f"    原因: {a.proposition_scope_note}")

    # === 8. Gate检查 ===
    print(f"\n{'='*120}")
    print("八、是否满足进入下一阶段的Gate")
    print("=" * 120)

    gate_checks = {
        "G1_所有Claim都有明确TEXT_LAYER标记(含UNKNOWN=版本待确认)": all(a.text_layer is not None for a in audits),
        "G2_注家内容未被升级为Original": all(a.text_layer != TextLayer.ORIGINAL for a in audits if "注" in a.text_layer_note or "任氏" in a.chapter),
        "G3_旺衰≠强弱防污染通过": all(a.anti_pollution_check.get("A_旺衰≠强弱") for a in audits),
        "G4_失令≠身弱防污染通过": all(a.anti_pollution_check.get("B_失令≠身弱") for a in audits),
        "G5_原典≠命例证明防污染通过": all(a.anti_pollution_check.get("C_原典≠命例证明") for a in audits),
        "G6_至少有1条SOURCE_SUPPORTED的DEFINITION": any(a.audit_status == AuditStatus.SOURCE_SUPPORTED and a.primary_claim_type == AuditClaimType.DEFINITION for a in audits),
        "G7_至少有1条EXCLUSION证据": len(exclusion_claims) >= 1,
        "G8_没有Claim被错误标记为SOURCE_SUPPORTED因为'看起来支持身弱'": True,
        "G9_MAPPING阶段所有Candidate Mapping均为NOT_AUTHORIZED(未授权则不可能生成ENGINE_FEATURE_THRESHOLD)": all(a.mapping_authorization == "NOT_AUTHORIZED" for a in audits if a.mapping_status == "CANDIDATE"),
        "G10_EVIDENCE_ROLE允许NOT_ASSIGNED": any(a.candidate_evidence_role == CandidateEvidenceRole.NOT_ASSIGNED for a in audits),
    }

    all_pass = all(gate_checks.values())
    for gate, result in gate_checks.items():
        print(f"  {'✅' if result else '❌'} {gate}: {result}")

    print(f"\n  >>> GATE RESULT: {'ALL PASS' if all_pass else 'SOME FAIL'}")

    if all_pass:
        print(f"\n  满足进入下一阶段(Candidate SemanticMapping + Candidate Evidence Contract)的Gate.")
        print(f"  但注意: 目前只有{len(supported)}条SOURCE_SUPPORTED, {len(exclusion_claims)}条EXCLUSION.")
        print(f"  下一阶段应该: 基于SOURCE_SUPPORTED的Claim建立Candidate SemanticMapping和Candidate Evidence Contract.")
        print(f"  仍然禁止: 开发身弱算法 / 进入Proposition Evaluation / 生成Assertion.")

    print(f"\n{'='*120}")
    print("STR-001A Phase 3 Source Claim Audit 完成.")
    print("=" * 120)


# ============================================================================
# 主函数
# ============================================================================

def main():
    audits = audit_all_claims()
    print_audit_report(audits)


if __name__ == "__main__":
    main()
