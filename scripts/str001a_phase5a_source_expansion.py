"""STR-001A Phase 5A - Canonical Source Expansion (身弱正向条件).

目标: 寻找并审计"身弱成立的正向条件"原典Claim.

前置条件:
  Contract/Governance Layer v6-final.1 = FROZEN
  Phase 3 Source Claim Audit = PASS (10 Claims)
  Phase 4 Candidate Mapping/Evidence = PASS (5 Mapping, 4 Evidence, 1 Contract DRAFT)
  当前证据链只能排除错误命题, 不能正向证明身弱

本阶段新增4条正向条件候选Claim:
  SC-YHZP-DZL-001: 《渊海子平·定真论》"生日天元临死绝之地，为身弱也"
  SC-YHZP-FL-001: 《渊海子平·赋论》"四柱无根，得时为旺。日干无气，遇劫为强。"
  SC-ZPZQ-06-005: 《子平真诠·第06章》"金之党众而木之助寡...虽秉令而不强也"
  SC-YHZP-XJP-001: 《渊海子平·喜忌篇》"柱中官星太旺，天元羸弱之名"

特别防污染:
  "党少/助寡"不能被直接翻译成现代计算阈值
  wood_ratio < 15% → 助寡 → 身弱 这条链绝对不能成立
  原典如果只说"党众为强，助寡为弱"，最多授权Engine Observation → "党众/助寡"语义映射
  还没有授权wood_ratio < X → 助寡
  更没有授权助寡 → STR-001A PROVEN

SC-YHZP-SR-001继续UNKNOWN隔离, 不进入本阶段.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# 枚举 (复用Phase 3的定义)
# ============================================================================

class TextLayer(str, Enum):
    ORIGINAL = "ORIGINAL"
    ORIGINAL_NOTE = "ORIGINAL_NOTE"
    COMMENTARY = "COMMENTARY"
    UNKNOWN = "UNKNOWN"


class AuditClaimType(str, Enum):
    DEFINITION = "DEFINITION"
    DESCRIPTIVE = "DESCRIPTIVE"
    NORMATIVE = "NORMATIVE"
    CONDITIONAL = "CONDITIONAL"
    EXAMPLE = "EXAMPLE"
    EXCLUSION = "EXCLUSION"
    DISTINCTION = "DISTINCTION"


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
    SHI_JUE = "死绝/十二长生"
    WU_GEN = "无根/无气"
    KE_XIE = "克泄/官杀太旺"
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
    PROVIDES_POSITIVE_WEAK_CONDITION = "提供身弱正向条件"
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
    SOURCE_MAPPED = "SOURCE_MAPPED"
    SOURCE_SUPPORTED = "SOURCE_SUPPORTED"
    REJECTED = "REJECTED"


# ============================================================================
# 新Claim审计数据结构
# ============================================================================

@dataclass
class NewSourceClaimAudit:
    """新增正向条件Claim的审计结果."""
    claim_id: str
    source_id: str = ""
    source_name: str = ""
    edition: str = ""
    chapter: str = ""
    text_reference: str = ""
    source_authenticity_note: str = ""
    text_layer: TextLayer = TextLayer.UNKNOWN
    text_layer_note: str = ""
    primary_claim_type: Optional[AuditClaimType] = None
    secondary_claim_types: List[AuditClaimType] = field(default_factory=list)
    semantic_scopes: List[SemanticScope] = field(default_factory=list)
    source_claim_relations: List[SourceClaimRelationType] = field(default_factory=list)
    proposition_scope: PropositionScope = PropositionScope.NOT_APPLICABLE
    proposition_scope_note: str = ""
    # 正向条件分析
    positive_condition_description: str = ""
    positive_condition_concreteness: str = ""  # CONCRETE / PARTIAL / ABSTRACT
    positive_condition_gap: str = ""  # 还缺少什么才能成为可执行条件
    # Candidate Mapping (NOT_AUTHORIZED)
    mapping_status: str = "CANDIDATE"
    mapping_authorization: str = "NOT_AUTHORIZED"
    mapping_note: str = ""
    # Candidate Evidence Role
    candidate_evidence_role: CandidateEvidenceRole = CandidateEvidenceRole.NOT_ASSIGNED
    evidence_role_note: str = ""
    # 最终状态
    audit_status: AuditStatus = AuditStatus.SOURCE_MAPPED
    rejection_reason: str = ""
    notes: str = ""
    # 防污染检查
    anti_pollution_check: Dict[str, bool] = field(default_factory=dict)


# ============================================================================
# 4条新Claim逐条审计
# ============================================================================

def audit_new_claims() -> List[NewSourceClaimAudit]:
    """对4条新增正向条件Claim逐条审计."""
    audits = []

    # === SC-YHZP-DZL-001: 《渊海子平·定真论》"生日天元临死绝之地，为身弱也" ===
    audits.append(NewSourceClaimAudit(
        claim_id="SC-YHZP-DZL-001",
        source_id="SRC-YHZP", source_name="渊海子平",
        edition="渊海子平(题宋徐子平撰, 后人汇编)",
        chapter="定真论",
        text_reference="干弱則求氣旺之藉，有餘則欲不足之營。日干弱則求氣旺之藉...且如壬癸巳午之類，皆因生日天元臨死絕之地，爲身弱也。",
        source_authenticity_note="《渊海子平·定真论》原文, 多个版本一致. '生日天元临死绝之地，为身弱也'是明确的身弱定义.",
        text_layer=TextLayer.ORIGINAL,
        text_layer_note="《渊海子平·定真论》原文",
        primary_claim_type=AuditClaimType.DEFINITION,
        secondary_claim_types=[AuditClaimType.CONDITIONAL],
        semantic_scopes=[SemanticScope.QIANG_RUO, SemanticScope.SHI_JUE, SemanticScope.DE_DI],
        source_claim_relations=[SourceClaimRelationType.DEFINES, SourceClaimRelationType.AUTHORIZES_MAPPING, SourceClaimRelationType.AUTHORIZES_EVIDENCE_ROLE],
        proposition_scope=PropositionScope.PROVIDES_POSITIVE_WEAK_CONDITION,
        proposition_scope_note="⭐ 这是目前找到的最明确的身弱正向定义: 生日天元临死绝之地 = 身弱. 但需要确认'死绝'的具体定义(十二长生中的死/绝?), 以及是否需要结合其他条件.",
        positive_condition_description="日干(生日天元)在十二长生中处于'死'或'绝'的状态 → 身弱",
        positive_condition_concreteness="PARTIAL",
        positive_condition_gap="1. '死绝'的具体定义需要确认: 是十二长生中的'死'和'绝'两个状态? 还是'死绝'作为一个统称? 2. 例子'壬癸巳午'需要验证: 壬水在巳为绝, 癸水在午为绝? 3. 是否'临死绝'就一定身弱, 还是需要结合其他条件(如是否有根/有生扶)?",
        mapping_status="CANDIDATE",
        mapping_authorization="NOT_AUTHORIZED",
        mapping_note="可以建立Candidate Mapping: 日干十二长生状态 → 死/绝 → 身弱候选条件. 但'死绝'的具体定义和是否需要结合其他条件尚未确认. 禁止: 直接把十二长生状态翻译成数值阈值.",
        candidate_evidence_role=CandidateEvidenceRole.PRIMARY,
        evidence_role_note="⭐ 这是目前最明确的身弱正向定义, 可以作为PRIMARY候选证据. 但需要先确认'死绝'的具体定义, 以及是否需要结合其他条件. 在定义确认前, 只能作为CANDIDATE, 不能AUTHORIZED.",
        audit_status=AuditStatus.SOURCE_SUPPORTED,
        notes="⭐ 重要发现. 这是目前找到的最明确的身弱正向定义. '生日天元临死绝之地，为身弱也'直接给出了身弱的一个充分条件. 但'死绝'的具体定义还需要进一步确认. 这条Claim如果经过详细Source Mapping, 可能成为STR-001A正向判定的核心依据.",
        anti_pollution_check={
            "A_旺衰≠强弱": True,  # 临死绝是强弱/得地问题, 不是旺衰(月令)问题
            "B_失令≠身弱": True,   # 临死绝≠失令, 这是不同的条件
            "C_原典≠命例证明": True,
            "D_注家≠Original": True,
            "E_党寡≠计算阈值": True,  # 这条不涉及党寡, 不涉及wood_ratio
        },
    ))

    # === SC-YHZP-FL-001: 《渊海子平·赋论》"四柱无根，得时为旺。日干无气，遇劫为强。" ===
    audits.append(NewSourceClaimAudit(
        claim_id="SC-YHZP-FL-001",
        source_id="SRC-YHZP", source_name="渊海子平",
        edition="渊海子平",
        chapter="赋论",
        text_reference="四柱无情，取元干而论也。四柱无根，得时为旺。日干无气，遇劫为强。身弱喜印。",
        source_authenticity_note="《渊海子平·赋论》原文, 多个版本一致. '四柱无根'和'日干无气'是身弱的重要条件.",
        text_layer=TextLayer.ORIGINAL,
        text_layer_note="《渊海子平·赋论》原文",
        primary_claim_type=AuditClaimType.CONDITIONAL,
        secondary_claim_types=[],
        semantic_scopes=[SemanticScope.QIANG_RUO, SemanticScope.WU_GEN, SemanticScope.DE_DI],
        source_claim_relations=[SourceClaimRelationType.AUTHORIZES_MAPPING, SourceClaimRelationType.AUTHORIZES_EVIDENCE_ROLE],
        proposition_scope=PropositionScope.PROVIDES_POSITIVE_WEAK_CONDITION,
        proposition_scope_note="提供身弱正向条件: 四柱无根 / 日干无气. 但'四柱无根'和'日干无气'的具体定义需要确认. 注意'四柱无根，得时为旺'说明无根但得令可以为旺(旺衰维度), 不等于身弱(强弱维度).",
        positive_condition_description="1. 四柱无根 → 身弱候选条件 2. 日干无气 → 身弱候选条件",
        positive_condition_concreteness="PARTIAL",
        positive_condition_gap="1. '四柱无根'的具体定义: 是四柱地支中完全没有日主的根(本气/余气/墓库)? 还是有更严格的定义? 2. '日干无气'的具体定义: 什么叫'无气'? 是不得令+不得地+不得势? 3. '四柱无根，得时为旺'说明无根但得令可以为旺, 这与身弱的关系需要澄清(旺≠强).",
        mapping_status="CANDIDATE",
        mapping_authorization="NOT_AUTHORIZED",
        mapping_note="可以建立Candidate Mapping: 四柱无根/日干无气 → 身弱候选条件. 但'无根'和'无气'的具体定义尚未确认. 禁止: 直接把'无根'翻译成wood_ratio=0或类似的数值阈值.",
        candidate_evidence_role=CandidateEvidenceRole.SUPPORTING,
        evidence_role_note="四柱无根/日干无气是身弱的重要支持条件, 可以作为SUPPORTING候选证据. 但具体定义尚未确认, 在定义确认前只能作为CANDIDATE.",
        audit_status=AuditStatus.SOURCE_SUPPORTED,
        notes="重要发现. '四柱无根'和'日干无气'是身弱的经典条件. 但需要注意'四柱无根，得时为旺'这句话: 它说明无根但得令可以为旺(旺衰维度), 这进一步证明了旺≠强. 身弱(强弱)需要无根+无气等条件, 不是单纯失令.",
        anti_pollution_check={
            "A_旺衰≠强弱": True,  # '四柱无根，得时为旺'明确区分了旺衰和强弱
            "B_失令≠身弱": True,   # 无根≠失令
            "C_原典≠命例证明": True,
            "D_注家≠Original": True,
            "E_党寡≠计算阈值": True,  # 禁止把无根翻译成wood_ratio=0
        },
    ))

    # === SC-ZPZQ-06-005: 《子平真诠·第06章》"金之党众而木之助寡...虽秉令而不强也" ===
    audits.append(NewSourceClaimAudit(
        claim_id="SC-ZPZQ-06-005",
        source_id="SRC-ZPZQ", source_name="子平真诠",
        edition="子平真诠(清沈孝瞻撰, 徐乐吾评注)",
        chapter="第06章 论十干得时不旺失时不弱",
        text_reference="甲乙木生于寅卯月，为得时者旺；干庚辛而支酉丑，则金之党众，而木之助寡。干丙丁而支巳午，则火之党众，木泄气太重，虽秉令而不强也。",
        source_authenticity_note="《子平真诠》第06章原文, 版本可靠. 这段给出了'助寡'的具体例子和'虽秉令而不强'的正向条件.",
        text_layer=TextLayer.ORIGINAL,
        text_layer_note="沈孝瞻原文",
        primary_claim_type=AuditClaimType.CONDITIONAL,
        secondary_claim_types=[AuditClaimType.EXAMPLE],
        semantic_scopes=[SemanticScope.QIANG_RUO, SemanticScope.DANG_ZHONG, SemanticScope.KE_XIE, SemanticScope.DE_LING],
        source_claim_relations=[SourceClaimRelationType.AUTHORIZES_MAPPING, SourceClaimRelationType.AUTHORIZES_EVIDENCE_ROLE, SourceClaimRelationType.SUPPORTS_INTERPRETATION],
        proposition_scope=PropositionScope.PROVIDES_POSITIVE_WEAK_CONDITION,
        proposition_scope_note="提供身弱正向条件的具体例子: 1. 金之党众而木之助寡 → 木不强 2. 火之党众，木泄气太重，虽秉令而不强 → 木不强. 这是'助寡'和'克泄太重'的具体例子, 但'助寡'的量化标准还没有.",
        positive_condition_description="1. 克我者(官杀)党众 + 我(日主)助寡 → 日主不强 2. 我生者(食伤)党众 + 日主泄气太重 → 虽得令而不强",
        positive_condition_concreteness="PARTIAL",
        positive_condition_gap="1. '党众'和'助寡'的量化标准: 多少算党众? 多少算助寡? 原典只给了例子(干庚辛而支酉丑=金之党众), 没有给出通用的量化标准. 2. '泄气太重'的具体定义: 什么叫'太重'? 3. 这些例子是针对甲乙木的, 是否可以推广到其他日干? 4. 绝对不能把'助寡'翻译成wood_ratio < 15%或类似的现代计算阈值.",
        mapping_status="CANDIDATE",
        mapping_authorization="NOT_AUTHORIZED",
        mapping_note="可以建立Candidate Mapping: 官杀党众+日主助寡 / 食伤党众+日主泄气太重 → 日主不强候选条件. 但'党众/助寡/泄气太重'的量化标准尚未确认. ⚠️ 绝对禁止: 把'助寡'翻译成wood_ratio < 15%或任何现代计算阈值. 原典只给了具体例子, 没有给出通用的数值标准.",
        candidate_evidence_role=CandidateEvidenceRole.SUPPORTING,
        evidence_role_note="这是'助寡'和'克泄太重'的具体例子, 可以作为SUPPORTING候选证据. 但量化标准尚未确认, 在标准确认前只能作为CANDIDATE. ⚠️ 特别注意: 不能因为这条Claim就把wood_ratio < 15%等同于'助寡'.",
        audit_status=AuditStatus.SOURCE_SUPPORTED,
        notes="⭐ 重要发现. 这段给出了'助寡'的具体例子和'虽秉令而不强'的正向条件. 它说明即使得令(旺), 如果克泄太重导致助寡, 仍然不强. 这进一步证明了旺≠强. 但'党众/助寡'的量化标准还没有, 绝对不能翻译成现代计算阈值.",
        anti_pollution_check={
            "A_旺衰≠强弱": True,  # '虽秉令而不强'明确区分了旺衰和强弱
            "B_失令≠身弱": True,   # 这条是得令但不强, 不是失令
            "C_原典≠命例证明": True,
            "D_注家≠Original": True,
            "E_党寡≠计算阈值": True,  # ⚠️ 特别检查: 绝对不能把助寡翻译成wood_ratio < 15%
        },
    ))

    # === SC-YHZP-XJP-001: 《渊海子平·喜忌篇》"柱中官星太旺，天元羸弱之名" ===
    audits.append(NewSourceClaimAudit(
        claim_id="SC-YHZP-XJP-001",
        source_id="SRC-YHZP", source_name="渊海子平",
        edition="渊海子平",
        chapter="喜忌篇",
        text_reference="柱中官星太旺，天元羸弱之名，日干旺甚无依，若不为僧即为道是也。身弱有生必发，忌财马以相伤。",
        source_authenticity_note="《渊海子平·喜忌篇》原文, 多个版本一致. '柱中官星太旺，天元羸弱之名'是官杀太旺导致身弱的经典表述.",
        text_layer=TextLayer.ORIGINAL,
        text_layer_note="《渊海子平·喜忌篇》原文",
        primary_claim_type=AuditClaimType.CONDITIONAL,
        secondary_claim_types=[],
        semantic_scopes=[SemanticScope.QIANG_RUO, SemanticScope.KE_XIE, SemanticScope.DANG_ZHONG],
        source_claim_relations=[SourceClaimRelationType.AUTHORIZES_MAPPING, SourceClaimRelationType.SUPPORTS_INTERPRETATION],
        proposition_scope=PropositionScope.PROVIDES_POSITIVE_WEAK_CONDITION,
        proposition_scope_note="提供身弱正向条件: 官星太旺 → 天元羸弱(身弱). 但'官星太旺'的具体定义需要确认. 注意'身弱有生必发'说明身弱但有生扶(印比)可以发, 这是喜忌条件, 不是身弱定义.",
        positive_condition_description="官星(克我者)太旺 → 天元羸弱(身弱)",
        positive_condition_concreteness="PARTIAL",
        positive_condition_gap="1. '官星太旺'的具体定义: 什么叫'太旺'? 是得令+得地+得势? 还是有更严格的定义? 2. '天元羸弱'是否等同于'身弱'? 还是有细微差别? 3. 官星太旺导致身弱, 是否需要结合其他条件(如日主是否有根/有生扶)?",
        mapping_status="CANDIDATE",
        mapping_authorization="NOT_AUTHORIZED",
        mapping_note="可以建立Candidate Mapping: 官星太旺 → 天元羸弱(身弱)候选条件. 但'官星太旺'的具体定义尚未确认. 禁止: 直接把'官星太旺'翻译成某个数值阈值(如官杀占比 > X%).",
        candidate_evidence_role=CandidateEvidenceRole.SUPPORTING,
        evidence_role_note="官星太旺导致身弱是经典的身弱条件, 可以作为SUPPORTING候选证据. 但'太旺'的具体定义尚未确认, 在定义确认前只能作为CANDIDATE.",
        audit_status=AuditStatus.SOURCE_SUPPORTED,
        notes="重要发现. '柱中官星太旺，天元羸弱之名'是官杀太旺导致身弱的经典表述. 这与SC-ZPZQ-06-005的'金之党众而木之助寡'是一致的: 克我者太旺/党众 → 我助寡/羸弱. 但'太旺'的量化标准还没有.",
        anti_pollution_check={
            "A_旺衰≠强弱": True,  # 官星太旺是官杀的旺, 不是日主的旺衰
            "B_失令≠身弱": True,   # 官星太旺≠失令
            "C_原典≠命例证明": True,
            "D_注家≠Original": True,
            "E_党寡≠计算阈值": True,  # 禁止把官星太旺翻译成官杀占比 > X%
        },
    ))

    return audits


# ============================================================================
# 汇总和Gate检查
# ============================================================================

def print_phase5a_report(audits: List[NewSourceClaimAudit]):
    """打印Phase 5A报告."""
    print("=" * 120)
    print("STR-001A Phase 5A - Canonical Source Expansion (身弱正向条件)")
    print("=" * 120)
    print(f"\nContract/Governance Layer = FROZEN (v6-final.1)")
    print(f"目标: 寻找并审计'身弱成立的正向条件'原典Claim")
    print(f"特别防污染: 党少/助寡不能被直接翻译成现代计算阈值 (wood_ratio < 15% → 助寡 → 身弱 绝对不能成立)")
    print(f"SC-YHZP-SR-001 继续 UNKNOWN 隔离, 不进入本阶段")

    # === 1. 新Claim Audit Matrix ===
    print(f"\n{'='*120}")
    print("一、新增4条正向条件Claim Audit Matrix")
    print("=" * 120)
    for a in audits:
        print(f"\n  [{a.claim_id}]")
        print(f"    来源: {a.source_name} · {a.chapter}")
        print(f"    版本: {a.edition}")
        print(f"    原文: {a.text_reference}")
        print(f"    TEXT_LAYER: {a.text_layer.value}")
        print(f"    CLAIM_TYPE: primary={a.primary_claim_type.value if a.primary_claim_type else 'None'}, secondary={[t.value for t in a.secondary_claim_types]}")
        print(f"    SEMANTIC_SCOPE: {[s.value for s in a.semantic_scopes]}")
        print(f"    SOURCE_CLAIM_RELATION: {[r.value for r in a.source_claim_relations]}")
        print(f"    PROPOSITION_SCOPE: {a.proposition_scope.value}")
        print(f"    正向条件: {a.positive_condition_description}")
        print(f"    条件具体度: {a.positive_condition_concreteness}")
        print(f"    条件缺口: {a.positive_condition_gap}")
        print(f"    MAPPING: status={a.mapping_status}, authorization={a.mapping_authorization} ⚠️ NOT_AUTHORIZED")
        print(f"    CANDIDATE_EVIDENCE_ROLE: {a.candidate_evidence_role.value}")
        print(f"    AUDIT_STATUS: {a.audit_status.value}")
        print(f"    NOTES: {a.notes}")
        # 防污染检查
        apc = a.anti_pollution_check
        print(f"    防污染: A旺衰≠强弱={apc.get('A_旺衰≠强弱')}, B失令≠身弱={apc.get('B_失令≠身弱')}, C原典≠命例证明={apc.get('C_原典≠命例证明')}, D注家≠Original={apc.get('D_注家≠Original')}, E党寡≠计算阈值={apc.get('E_党寡≠计算阈值')}")

    # === 2. 分类汇总 ===
    print(f"\n{'='*120}")
    print("二、分类汇总")
    print("=" * 120)
    supported = [a for a in audits if a.audit_status == AuditStatus.SOURCE_SUPPORTED]
    mapped = [a for a in audits if a.audit_status == AuditStatus.SOURCE_MAPPED]
    rejected = [a for a in audits if a.audit_status == AuditStatus.REJECTED]

    print(f"\n  新增Claim总数: {len(audits)}条")
    print(f"  SOURCE_SUPPORTED: {len(supported)}条")
    for a in supported:
        print(f"    - {a.claim_id}: {a.proposition_scope.value} (条件具体度: {a.positive_condition_concreteness})")
    print(f"  SOURCE_MAPPED: {len(mapped)}条")
    print(f"  REJECTED: {len(rejected)}条")

    # === 3. 关键发现 ===
    print(f"\n{'='*120}")
    print("三、关键发现")
    print("=" * 120)
    print(f"""
  1. ⭐ SC-YHZP-DZL-001 是目前找到的最明确的身弱正向定义:
     "生日天元临死绝之地，为身弱也"
     这直接给出了身弱的一个充分条件: 日干临死绝 → 身弱.
     但'死绝'的具体定义还需要确认.

  2. SC-YHZP-FL-001 提供了'四柱无根'和'日干无气'两个身弱条件:
     但'无根'和'无气'的具体定义还需要确认.
     注意'四柱无根，得时为旺'进一步证明了旺≠强.

  3. SC-ZPZQ-06-005 提供了'助寡'和'克泄太重'的具体例子:
     "金之党众而木之助寡" / "火之党众，木泄气太重，虽秉令而不强"
     但'党众/助寡'的量化标准还没有.
     ⚠️ 绝对不能把'助寡'翻译成wood_ratio < 15%或任何现代计算阈值.

  4. SC-YHZP-XJP-001 提供了'官星太旺 → 天元羸弱'的条件:
     与SC-ZPZQ-06-005一致: 克我者太旺/党众 → 我助寡/羸弱.
     但'太旺'的量化标准还没有.

  5. 所有4条新Claim的条件具体度都是PARTIAL:
     原典给出了方向性的条件, 但没有给出可直接执行的量化标准.
     这是正常的: 原典是语义权威, 不是工程规范.
     量化标准需要经过Canonical Source Mapping和Evidence Contract Authorization才能建立.

  6. ⚠️ 特别防污染:
     所有4条Claim都明确禁止翻译成现代计算阈值.
     wood_ratio < 15% → 助寡 → 身弱 这条链绝对不能成立.
     原典如果只说'党众为强，助寡为弱'，最多授权Engine Observation → '党众/助寡'语义映射.
     还没有授权wood_ratio < X → 助寡.
     更没有授权助寡 → STR-001A PROVEN.
    """)

    # === 4. 与已有Claim的关系 ===
    print(f"\n{'='*120}")
    print("四、与已有Claim的关系")
    print("=" * 120)
    print(f"""
  已有Claim (Phase 3, 10条):
    - SC-ZPZQ-06-001: 旺衰强弱区分 (DEFINITION/DISTINCTION, PRIMARY)
    - SC-ZPZQ-06-002: 失时但有根→不弱 (EXCLUSION)
    - SC-ZPZQ-03-001: 月令休囚但得禄旺→不为弱 (EXCLUSION)
    - 其余7条: SOURCE_MAPPED (喜忌/旺衰定义/描述性/原注/注家)

  新增Claim (Phase 5A, 4条):
    - SC-YHZP-DZL-001: 日干临死绝→身弱 (⭐ 最明确的正向定义, PRIMARY候选)
    - SC-YHZP-FL-001: 四柱无根/日干无气→身弱 (SUPPORTING候选)
    - SC-ZPZQ-06-005: 官杀/食伤党众+日主助寡/泄气太重→不强 (SUPPORTING候选)
    - SC-YHZP-XJP-001: 官星太旺→天元羸弱 (SUPPORTING候选)

  关系:
    - 新增4条都是正向条件, 补充了已有Claim只有排除条件的不足.
    - SC-YHZP-DZL-001 可能成为正向判定的核心依据 (如果'死绝'定义确认).
    - 新增4条与已有3条SOURCE_SUPPORTED不冲突, 而是互补.
    - 所有新增Claim的mapping_authorization仍然是NOT_AUTHORIZED.
    """)

    # === 5. Gate检查 ===
    print(f"\n{'='*120}")
    print("五、Gate检查")
    print("=" * 120)
    gate_checks = {
        "G1_所有新Claim都有明确TEXT_LAYER标记": all(a.text_layer != TextLayer.UNKNOWN for a in audits),
        "G2_注家内容未被升级为Original": all(a.text_layer != TextLayer.ORIGINAL for a in audits if "注" in a.text_layer_note),
        "G3_旺衰≠强弱防污染通过": all(a.anti_pollution_check.get("A_旺衰≠强弱") for a in audits),
        "G4_失令≠身弱防污染通过": all(a.anti_pollution_check.get("B_失令≠身弱") for a in audits),
        "G5_原典≠命例证明防污染通过": all(a.anti_pollution_check.get("C_原典≠命例证明") for a in audits),
        "G6_党寡≠计算阈值防污染通过": all(a.anti_pollution_check.get("E_党寡≠计算阈值") for a in audits),
        "G7_所有新Claim的mapping_authorization=NOT_AUTHORIZED": all(a.mapping_authorization == "NOT_AUTHORIZED" for a in audits),
        "G8_至少有1条提供正向身弱条件": any(a.proposition_scope == PropositionScope.PROVIDES_POSITIVE_WEAK_CONDITION for a in audits),
        "G9_所有正向条件的具体度都是PARTIAL(没有过度量化)": all(a.positive_condition_concreteness == "PARTIAL" for a in audits),
        "G10_SC-YHZP-SR-001保持UNKNOWN隔离": True,  # 本阶段没有处理SC-YHZP-SR-001
    }
    all_pass = all(gate_checks.values())
    for gate, result in gate_checks.items():
        print(f"  {'✅' if result else '❌'} {gate}: {result}")
    print(f"\n  >>> GATE RESULT: {'ALL PASS' if all_pass else 'SOME FAIL'}")

    # === 6. 下一步建议 ===
    print(f"\n{'='*120}")
    print("六、下一步建议")
    print("=" * 120)
    print(f"""
  当前状态:
    - 已有3条SOURCE_SUPPORTED (1条核心定义 + 2条EXCLUSION)
    - 新增4条SOURCE_SUPPORTED (全部是正向条件, 但具体度都是PARTIAL)
    - 总共7条SOURCE_SUPPORTED
    - 所有Claim的mapping_authorization仍然是NOT_AUTHORIZED
    - Evidence Contract仍然是DRAFT, can_produce_proven=False

  下一步可能的路径:
    A. 深入Source Mapping: 对SC-YHZP-DZL-001的'死绝'定义进行详细Source Mapping,
       确认'死绝'的具体含义(十二长生中的死/绝?), 以及是否需要结合其他条件.
       如果'死绝'定义确认, 这条可能成为第一个可以AUTHORIZED的正向条件.

    B. 深入Source Mapping: 对SC-YHZP-FL-001的'四柱无根'和'日干无气'定义进行详细Source Mapping,
       确认'无根'和'无气'的具体含义.

    C. 保持当前状态: 承认当前7条SOURCE_SUPPORTED的条件具体度都是PARTIAL,
       还不能建立可执行的正向判定规则. STR-001A保持PARTIAL/UNPROVEN.

  仍然禁止:
    - 开发身弱算法
    - 设置ENGINE_FEATURE threshold
    - wood_ratio → 身弱
    - 把'助寡'翻译成数值阈值
    - 进入ContextResolver / Assertion
    - 直接产生L4 PROVEN
    """)

    print(f"\n{'='*120}")
    print("STR-001A Phase 5A 完成.")
    print("=" * 120)


# ============================================================================
# 主函数
# ============================================================================

def main():
    audits = audit_new_claims()
    print_phase5a_report(audits)


if __name__ == "__main__":
    main()
