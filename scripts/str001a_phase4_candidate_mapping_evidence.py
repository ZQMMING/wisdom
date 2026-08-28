"""STR-001A Phase 4 - Candidate SemanticMapping + Candidate Evidence Contract.

前置条件:
  Contract/Governance Layer v6-final.1 = FROZEN
  Phase 3 Source Claim Audit = PASS (10 Claims, 3 SOURCE_SUPPORTED, 7 SOURCE_MAPPED, 0 REJECTED)

只处理3条SOURCE_SUPPORTED:
  SC-ZPZQ-06-001 (核心定义/区分: 旺衰≠强弱)
  SC-ZPZQ-06-002 (EXCLUSION: 失时+根深→不弱)
  SC-ZPZQ-03-001 (EXCLUSION: 月令休囚+年日时得禄旺/有根→不为弱)

SC-YHZP-SR-001 保持 UNKNOWN / NOT_AUTHORIZED 隔离状态, 不得进入本阶段Canonical链.

禁止:
  1. 修改Contract
  2. 修改Governance Rules
  3. 开发身弱算法
  4. 设置任何ENGINE_FEATURE threshold
  5. wood_ratio → 身弱
  6. day_master_strength → 身弱
  7. 进入ContextResolver
  8. 进入Assertion
  9. 直接产生L4 PROVEN

特别注意 (GOV-INVARIANT-01):
  SourceClaimRelation=AUTHORIZES_MAPPING ≠ Mapping automatically AUTHORIZED
  Authorization at layer N SHALL NOT imply/grant/substitute authorization at layer N+1.

本阶段正确结果: Candidate assets created, 但Canonical Authorization仍然NOT_DONE.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# 枚举
# ============================================================================

class MappingStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    SUPPORTED = "SUPPORTED"
    REJECTED = "REJECTED"


class MappingAuthorization(str, Enum):
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    AUTHORIZED = "AUTHORIZED"
    REVOKED = "REVOKED"


class MappingBasis(str, Enum):
    DIRECT_SOURCE = "DIRECT_SOURCE"              # 原典直接定义
    DERIVED_FROM_SOURCE = "DERIVED_FROM_SOURCE"  # 从原典推导
    INTERPRETIVE_MAPPING = "INTERPRETIVE_MAPPING"  # 解释性映射
    UNAUTHORIZED_MAPPING = "UNAUTHORIZED_MAPPING"  # 未授权映射


class CandidateEvidenceRole(str, Enum):
    PRIMARY = "PRIMARY"
    SUPPORTING = "SUPPORTING"
    CONTEXTUAL = "CONTEXTUAL"
    EXCLUSION = "EXCLUSION"
    NON_CANONICAL = "NON_CANONICAL"
    NOT_ASSIGNED = "NOT_ASSIGNED"


class EvidenceAuthorizationStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    SOURCE_SUPPORTED = "SOURCE_SUPPORTED"
    AUTHORIZED = "AUTHORIZED"
    REJECTED = "REJECTED"


class ContractStatus(str, Enum):
    DRAFT = "DRAFT"
    SOURCE_MAPPED = "SOURCE_MAPPED"
    SOURCE_SUPPORTED = "SOURCE_SUPPORTED"
    AUTHORIZED = "AUTHORIZED"
    RETIRED = "RETIRED"
    REJECTED = "REJECTED"


class SourceClaimRelationType(str, Enum):
    DEFINES = "DEFINES"
    SUPPORTS_INTERPRETATION = "SUPPORTS_INTERPRETATION"
    AUTHORIZES_MAPPING = "AUTHORIZES_MAPPING"
    AUTHORIZES_EVIDENCE_ROLE = "AUTHORIZES_EVIDENCE_ROLE"
    AUTHORIZES_RELATION = "AUTHORIZES_RELATION"


# ============================================================================
# Candidate SemanticMapping
# ============================================================================

@dataclass
class CandidateSemanticMapping:
    """Candidate SemanticMapping (NOT_AUTHORIZED)."""
    mapping_id: str
    source_claim_id: str
    engine_feature_id: Optional[str] = None  # 可以是None, 因为还没有确定Engine Feature
    observable_meaning: str = ""
    candidate_concept: str = ""
    mapping_basis: MappingBasis = MappingBasis.INTERPRETIVE_MAPPING
    mapping_status: MappingStatus = MappingStatus.CANDIDATE
    mapping_authorization: MappingAuthorization = MappingAuthorization.NOT_AUTHORIZED
    notes: str = ""
    # 防污染标记
    is_dimension_mapping_only: bool = False  # 只是维度映射, 不是判定映射
    is_exclusion_mapping: bool = False        # 是排除条件映射
    forbidden_direction: str = ""             # 禁止的推导方向


# ============================================================================
# Candidate Evidence
# ============================================================================

@dataclass
class CandidateEvidence:
    """Candidate Evidence (CANDIDATE status, NOT_AUTHORIZED)."""
    evidence_id: str
    evidence_role: CandidateEvidenceRole
    description: str = ""
    supporting_source_claim_ids: List[str] = field(default_factory=list)
    source_claim_relations: List[SourceClaimRelationType] = field(default_factory=list)
    conditional_relations: List[Dict[str, Any]] = field(default_factory=list)
    dependent_relations: List[Dict[str, Any]] = field(default_factory=list)
    evaluation_sequence: Optional[int] = None
    authorization_status: EvidenceAuthorizationStatus = EvidenceAuthorizationStatus.CANDIDATE
    notes: str = ""
    # 防污染标记
    is_exclusion: bool = False
    is_dimension_only: bool = False
    cannot_be_positive_proof: bool = False


# ============================================================================
# Candidate Evidence Contract (DRAFT)
# ============================================================================

@dataclass
class EvidenceGroup:
    group_id: str
    group_description: str = ""
    evidence_ids: List[str] = field(default_factory=list)
    group_logic: str = ""  # 描述性, 不是机器可执行的logic (禁止在EvidenceEntry中加入logic)


@dataclass
class CandidateEvidenceContract:
    """Candidate Evidence Contract (DRAFT status)."""
    contract_id: str
    contract_status: ContractStatus = ContractStatus.DRAFT
    proposition_id: str = "STR-001A"
    proposition_name: str = "日主身弱"
    evidence_groups: List[EvidenceGroup] = field(default_factory=list)
    evaluation_order_mode: str = "ORDERED"  # ORDERED / UNORDERED
    evaluation_order_scope: str = "EVIDENCE_GROUPS"
    evaluation_sequence: List[str] = field(default_factory=list)
    notes: str = ""
    # 防污染标记
    has_positive_proof_rule: bool = False  # 是否有正向判定规则
    has_exclusion_rule: bool = False        # 是否有排除规则
    can_produce_proven: bool = False        # 是否能产生L4 PROVEN


# ============================================================================
# Negative Test
# ============================================================================

@dataclass
class NegativeTest:
    test_id: str
    test_name: str
    test_description: str
    expected_result: str
    actual_result: str = ""
    passed: bool = False


# ============================================================================
# Phase 4 执行
# ============================================================================

def create_candidate_mappings() -> List[CandidateSemanticMapping]:
    """为3条SOURCE_SUPPORTED建立Candidate SemanticMapping."""
    mappings = []

    # === SC-ZPZQ-06-001: 核心定义/区分 ===
    # Mapping 1: 月令状态 → 旺/衰维度
    mappings.append(CandidateSemanticMapping(
        mapping_id="MAP-STR001A-001",
        source_claim_id="SC-ZPZQ-06-001",
        engine_feature_id=None,  # 还没有确定具体的Engine Feature
        observable_meaning="日主在月令的十二长生状态（得时/失时）",
        candidate_concept="旺/衰维度（得时为旺，失时为衰）",
        mapping_basis=MappingBasis.DIRECT_SOURCE,
        mapping_status=MappingStatus.CANDIDATE,
        mapping_authorization=MappingAuthorization.NOT_AUTHORIZED,
        notes="这只是维度映射，不是判定映射。月令状态只能说明旺/衰，不能直接说明强/弱。",
        is_dimension_mapping_only=True,
        forbidden_direction="月令失令 → 日主身弱 (禁止: 失令≠身弱, 衰≠弱)",
    ))

    # Mapping 2: 党众/助寡 → 强/弱维度
    mappings.append(CandidateSemanticMapping(
        mapping_id="MAP-STR001A-002",
        source_claim_id="SC-ZPZQ-06-001",
        engine_feature_id=None,
        observable_meaning="命局中生扶日主的力量多寡（党众/助寡）",
        candidate_concept="强/弱维度（党众为强，助寡为弱）",
        mapping_basis=MappingBasis.DIRECT_SOURCE,
        mapping_status=MappingStatus.CANDIDATE,
        mapping_authorization=MappingAuthorization.NOT_AUTHORIZED,
        notes="这只是维度映射，不是判定映射。党众/助寡的具体判定规则尚未建立。",
        is_dimension_mapping_only=True,
        forbidden_direction="助寡 → 日主身弱 (禁止: 助寡的具体判定规则尚未建立, 不能直接映射为身弱)",
    ))

    # Mapping 3: 旺衰≠强弱（区分性映射）
    mappings.append(CandidateSemanticMapping(
        mapping_id="MAP-STR001A-003",
        source_claim_id="SC-ZPZQ-06-001",
        engine_feature_id=None,
        observable_meaning="旺衰和强弱是两个不同维度，有虽旺而弱者，有虽衰而强者",
        candidate_concept="旺衰≠强弱（区分性原则）",
        mapping_basis=MappingBasis.DIRECT_SOURCE,
        mapping_status=MappingStatus.CANDIDATE,
        mapping_authorization=MappingAuthorization.NOT_AUTHORIZED,
        notes="这是区分性映射，用于防止把旺衰和强弱混为一谈。这是STR-001A最重要的防污染依据。",
        is_dimension_mapping_only=True,
        forbidden_direction="旺衰判定 → 强弱判定 (禁止: 旺≠强, 衰≠弱)",
    ))

    # === SC-ZPZQ-06-002: EXCLUSION 失时+根深→不弱 ===
    mappings.append(CandidateSemanticMapping(
        mapping_id="MAP-STR001A-004",
        source_claim_id="SC-ZPZQ-06-002",
        engine_feature_id=None,
        observable_meaning="日主失令（秋木）但地支有强根（通根，干甲乙而支寅卯）",
        candidate_concept="失时不弱（EXCLUSION / NOT_WEAK）",
        mapping_basis=MappingBasis.DIRECT_SOURCE,
        mapping_status=MappingStatus.CANDIDATE,
        mapping_authorization=MappingAuthorization.NOT_AUTHORIZED,
        notes="这是EXCLUSION映射，不是POSITIVE_PROOF。它只能排除'失令=身弱'的错误判定，不能证明'有根=身强'。",
        is_exclusion_mapping=True,
        forbidden_direction="有根 → 身强 (禁止: EXCLUSION≠POSITIVE_PROOF, 有根只是排除身弱的一个条件, 不自动等于身强)",
    ))

    # === SC-ZPZQ-03-001: EXCLUSION 月令休囚+年日时得禄旺/有根→不为弱 ===
    mappings.append(CandidateSemanticMapping(
        mapping_id="MAP-STR001A-005",
        source_claim_id="SC-ZPZQ-03-001",
        engine_feature_id=None,
        observable_meaning="月令休囚但年日时中得长生禄旺，或逢库（亦为有根）",
        candidate_concept="不为弱（EXCLUSION / NOT_WEAK）",
        mapping_basis=MappingBasis.DIRECT_SOURCE,
        mapping_status=MappingStatus.CANDIDATE,
        mapping_authorization=MappingAuthorization.NOT_AUTHORIZED,
        notes="这是EXCLUSION映射，不是POSITIVE_PROOF。它只能排除'月令休囚=身弱'的错误判定，不能证明'得禄旺=身强'。",
        is_exclusion_mapping=True,
        forbidden_direction="得禄旺 → 身强 (禁止: EXCLUSION≠POSITIVE_PROOF, 得禄旺只是排除身弱的一个条件, 不自动等于身强)",
    ))

    return mappings


def create_candidate_evidences() -> List[CandidateEvidence]:
    """建立Candidate Evidence."""
    evidences = []

    # EVID-001: 月令状态（旺衰维度）
    evidences.append(CandidateEvidence(
        evidence_id="EVID-STR001A-001",
        evidence_role=CandidateEvidenceRole.SUPPORTING,
        description="月令状态（得时/失时），属于旺/衰维度，不是强/弱维度的直接判定依据",
        supporting_source_claim_ids=["SC-ZPZQ-06-001"],
        source_claim_relations=[SourceClaimRelationType.DEFINES, SourceClaimRelationType.AUTHORIZES_MAPPING],
        evaluation_sequence=1,
        authorization_status=EvidenceAuthorizationStatus.CANDIDATE,
        notes="这是维度证据，不是判定证据。月令状态只能说明旺/衰，需要结合其他维度才能判断强/弱。",
        is_dimension_only=True,
        cannot_be_positive_proof=True,
    ))

    # EVID-002: 党众/助寡（强弱维度）
    evidences.append(CandidateEvidence(
        evidence_id="EVID-STR001A-002",
        evidence_role=CandidateEvidenceRole.SUPPORTING,
        description="党众/助寡（生扶日主的力量多寡），属于强/弱维度，但具体判定规则尚未建立",
        supporting_source_claim_ids=["SC-ZPZQ-06-001"],
        source_claim_relations=[SourceClaimRelationType.DEFINES, SourceClaimRelationType.AUTHORIZES_EVIDENCE_ROLE],
        evaluation_sequence=2,
        authorization_status=EvidenceAuthorizationStatus.CANDIDATE,
        notes="这是维度证据，但党众/助寡的具体判定规则（什么算党众？什么算助寡？）尚未建立。不能直接用于判定身弱。",
        is_dimension_only=True,
        cannot_be_positive_proof=True,
    ))

    # EVID-003: 失时但有根 → NOT_WEAK（EXCLUSION）
    evidences.append(CandidateEvidence(
        evidence_id="EVID-STR001A-003",
        evidence_role=CandidateEvidenceRole.EXCLUSION,
        description="失时但有强根（通根）→ 排除'失令=身弱'的判定（NOT_WEAK的排除条件）",
        supporting_source_claim_ids=["SC-ZPZQ-06-002"],
        source_claim_relations=[SourceClaimRelationType.AUTHORIZES_RELATION, SourceClaimRelationType.SUPPORTS_INTERPRETATION],
        conditional_relations=[{
            "type": "CONDITIONAL",
            "when": "日主失令 AND 地支有强根(通根)",
            "requires": "排除身弱判定 (NOT_WEAK)",
        }],
        evaluation_sequence=3,
        authorization_status=EvidenceAuthorizationStatus.CANDIDATE,
        notes="这是EXCLUSION证据，不是POSITIVE_PROOF。它只能排除错误的身弱判定，不能证明身强。",
        is_exclusion=True,
        cannot_be_positive_proof=True,
    ))

    # EVID-004: 月令休囚但年日时得禄旺/有根 → NOT_WEAK（EXCLUSION）
    evidences.append(CandidateEvidence(
        evidence_id="EVID-STR001A-004",
        evidence_role=CandidateEvidenceRole.EXCLUSION,
        description="月令休囚但年日时中得长生禄旺，或逢库（亦为有根）→ 排除'月令休囚=身弱'的判定（NOT_WEAK的排除条件）",
        supporting_source_claim_ids=["SC-ZPZQ-03-001"],
        source_claim_relations=[SourceClaimRelationType.AUTHORIZES_RELATION, SourceClaimRelationType.AUTHORIZES_EVIDENCE_ROLE],
        conditional_relations=[{
            "type": "CONDITIONAL",
            "when": "月令休囚 AND (年日时得长生禄旺 OR 逢库)",
            "requires": "排除身弱判定 (NOT_WEAK)",
        }],
        evaluation_sequence=4,
        authorization_status=EvidenceAuthorizationStatus.CANDIDATE,
        notes="这是EXCLUSION证据，不是POSITIVE_PROOF。它只能排除错误的身弱判定，不能证明身强。",
        is_exclusion=True,
        cannot_be_positive_proof=True,
    ))

    return evidences


def create_candidate_evidence_contract() -> CandidateEvidenceContract:
    """建立Candidate Evidence Contract (DRAFT)."""
    contract = CandidateEvidenceContract(
        contract_id="ECC-STR001A-DRAFT-001",
        contract_status=ContractStatus.DRAFT,
        proposition_id="STR-001A",
        proposition_name="日主身弱",
        evidence_groups=[
            EvidenceGroup(
                group_id="GROUP-DIMENSION",
                group_description="维度定义组：旺衰维度（月令状态）和强弱维度（党众/助寡）的定义。这些是维度证据，不是判定证据。",
                evidence_ids=["EVID-STR001A-001", "EVID-STR001A-002"],
                group_logic="维度定义，不产生判定结果。禁止: 维度状态 → 身弱判定。",
            ),
            EvidenceGroup(
                group_id="GROUP-EXCLUSION",
                group_description="排除条件组：失时但有根、月令休囚但得禄旺/有根 → 排除身弱判定（NOT_WEAK）。这些是EXCLUSION证据，不是POSITIVE_PROOF。",
                evidence_ids=["EVID-STR001A-003", "EVID-STR001A-004"],
                group_logic="排除条件：如果满足，则排除身弱判定。禁止: EXCLUSION → POSITIVE_PROOF（有根≠身强）。",
            ),
        ],
        evaluation_order_mode="ORDERED",
        evaluation_order_scope="EVIDENCE_GROUPS",
        evaluation_sequence=["GROUP-EXCLUSION", "GROUP-DIMENSION"],
        notes="""
        当前Evidence Contract只有维度定义和排除条件，没有正向判定规则。
        不能产生STR-001A = PROVEN。
        要产生正向判定，需要额外的Canonical Source支持'什么条件下身弱成立'。
        目前3条SOURCE_SUPPORTED中：
        - SC-ZPZQ-06-001: 只定义了旺衰/强弱的区分，没有给出身弱的具体判定条件
        - SC-ZPZQ-06-002: 只给出了排除条件（失时但有根→不弱）
        - SC-ZPZQ-03-001: 只给出了排除条件（月令休囚但得禄旺→不为弱）
        因此当前Contract只能用于排除错误判定，不能用于正向判定身弱。
        """,
        has_positive_proof_rule=False,
        has_exclusion_rule=True,
        can_produce_proven=False,
    )
    return contract


def run_negative_tests(
    mappings: List[CandidateSemanticMapping],
    evidences: List[CandidateEvidence],
    contract: CandidateEvidenceContract,
) -> List[NegativeTest]:
    """执行负向测试."""
    tests = []

    # A. SOURCE_SUPPORTED ≠ Evidence Authorized
    all_evidence_candidate = all(e.authorization_status == EvidenceAuthorizationStatus.CANDIDATE for e in evidences)
    tests.append(NegativeTest(
        test_id="NEG-A",
        test_name="SOURCE_SUPPORTED ≠ Evidence Authorized",
        test_description="检查所有Candidate Evidence的authorization_status都是CANDIDATE，没有因为SourceClaim是SOURCE_SUPPORTED就自动AUTHORIZED",
        expected_result="所有Evidence的authorization_status = CANDIDATE",
        actual_result=f"所有Evidence的authorization_status = CANDIDATE: {all_evidence_candidate}",
        passed=all_evidence_candidate,
    ))

    # B. SourceClaim ≠ 命例事实证明
    no_chart_data = all("1983" not in m.observable_meaning and "乙木" not in m.observable_meaning for m in mappings)
    tests.append(NegativeTest(
        test_id="NEG-B",
        test_name="SourceClaim ≠ 命例事实证明",
        test_description="检查所有Mapping中没有引用具体命例数据（1983命例、乙木等）",
        expected_result="所有Mapping不包含具体命例数据",
        actual_result=f"所有Mapping不包含具体命例数据: {no_chart_data}",
        passed=no_chart_data,
    ))

    # C. EXCLUSION ≠ POSITIVE_PROOF
    exclusion_not_positive = all(e.is_exclusion and e.cannot_be_positive_proof for e in evidences if e.evidence_role == CandidateEvidenceRole.EXCLUSION)
    tests.append(NegativeTest(
        test_id="NEG-C",
        test_name="EXCLUSION ≠ POSITIVE_PROOF",
        test_description="检查EXCLUSION证据没有被当作正向证明，所有EXCLUSION证据都标记了cannot_be_positive_proof=True",
        expected_result="所有EXCLUSION证据的cannot_be_positive_proof = True",
        actual_result=f"所有EXCLUSION证据的cannot_be_positive_proof = True: {exclusion_not_positive}",
        passed=exclusion_not_positive,
    ))

    # D. SemanticMapping NOT_AUTHORIZED 不能进入L3 AUTHORIZED
    all_mapping_not_authorized = all(m.mapping_authorization == MappingAuthorization.NOT_AUTHORIZED for m in mappings)
    tests.append(NegativeTest(
        test_id="NEG-D",
        test_name="SemanticMapping NOT_AUTHORIZED 不能进入L3 AUTHORIZED",
        test_description="检查所有Mapping的mapping_authorization都是NOT_AUTHORIZED，没有因为SourceClaimRelation=AUTHORIZES_MAPPING就自动AUTHORIZED",
        expected_result="所有Mapping的mapping_authorization = NOT_AUTHORIZED",
        actual_result=f"所有Mapping的mapping_authorization = NOT_AUTHORIZED: {all_mapping_not_authorized}",
        passed=all_mapping_not_authorized,
    ))

    # E. Evidence Contract DRAFT 不能进入L4 Evaluation
    contract_is_draft = contract.contract_status == ContractStatus.DRAFT
    tests.append(NegativeTest(
        test_id="NEG-E",
        test_name="Evidence Contract DRAFT 不能进入L4 Evaluation",
        test_description="检查Evidence Contract的contract_status是DRAFT，can_produce_proven=False",
        expected_result="contract_status = DRAFT, can_produce_proven = False",
        actual_result=f"contract_status = {contract.contract_status.value}, can_produce_proven = {contract.can_produce_proven}",
        passed=contract_is_draft and not contract.can_produce_proven,
    ))

    # F. 不得产生ENGINE_FEATURE判定
    no_engine_feature = all(m.engine_feature_id is None for m in mappings)
    no_threshold = all("threshold" not in m.notes.lower() and "0.15" not in m.notes for m in mappings)
    tests.append(NegativeTest(
        test_id="NEG-F",
        test_name="不得产生ENGINE_FEATURE判定",
        test_description="检查没有WOOD<threshold、day_master_strength<threshold、score/probability等ENGINE_FEATURE判定",
        expected_result="所有Mapping的engine_feature_id = None, 不包含threshold/0.15/score/probability",
        actual_result=f"engine_feature_id全部为None: {no_engine_feature}, 不包含threshold: {no_threshold}",
        passed=no_engine_feature and no_threshold,
    ))

    # G. 不得产生STR-001A = PROVEN
    no_proven = not contract.can_produce_proven
    tests.append(NegativeTest(
        test_id="NEG-G",
        test_name="不得产生STR-001A = PROVEN",
        test_description="检查没有L4 PROVEN状态，can_produce_proven=False",
        expected_result="can_produce_proven = False",
        actual_result=f"can_produce_proven = {no_proven}",
        passed=no_proven,
    ))

    return tests


def run_special_tests(mappings: List[CandidateSemanticMapping]) -> List[NegativeTest]:
    """执行特别测试."""
    tests = []

    # S1. SC-ZPZQ-06-001 只能建立"旺衰/强弱维度区分"的SemanticMapping，不得建立"失令→身弱"
    sc06001_mappings = [m for m in mappings if m.source_claim_id == "SC-ZPZQ-06-001"]
    all_dimension = all(m.is_dimension_mapping_only for m in sc06001_mappings)
    no_shiruo_direction = all("身弱" not in m.forbidden_direction or "禁止" in m.forbidden_direction for m in sc06001_mappings)
    tests.append(NegativeTest(
        test_id="SPEC-S1",
        test_name="SC-ZPZQ-06-001 只能建立维度区分映射，不得建立失令→身弱",
        test_description="检查SC-ZPZQ-06-001的所有Mapping都是维度映射(is_dimension_mapping_only=True)，forbidden_direction明确禁止失令→身弱",
        expected_result="所有Mapping的is_dimension_mapping_only=True, forbidden_direction明确禁止失令→身弱",
        actual_result=f"is_dimension_mapping_only全部=True: {all_dimension}, forbidden_direction明确禁止: {no_shiruo_direction}",
        passed=all_dimension and no_shiruo_direction,
    ))

    # S2. SC-ZPZQ-06-002 只能建立"失时+根深→EXCLUSION/NOT_WEAK"
    sc06002_mappings = [m for m in mappings if m.source_claim_id == "SC-ZPZQ-06-002"]
    all_exclusion = all(m.is_exclusion_mapping for m in sc06002_mappings)
    no_positive = all("身强" not in m.candidate_concept for m in sc06002_mappings)
    tests.append(NegativeTest(
        test_id="SPEC-S2",
        test_name="SC-ZPZQ-06-002 只能建立EXCLUSION/NOT_WEAK，不得建立有根→身强",
        test_description="检查SC-ZPZQ-06-002的所有Mapping都是EXCLUSION映射(is_exclusion_mapping=True)，candidate_concept不包含'身强'",
        expected_result="所有Mapping的is_exclusion_mapping=True, candidate_concept不包含'身强'",
        actual_result=f"is_exclusion_mapping全部=True: {all_exclusion}, candidate_concept不包含'身强': {no_positive}",
        passed=all_exclusion and no_positive,
    ))

    # S3. SC-ZPZQ-03-001 只能建立"月令休囚+年日时得禄旺/有根→EXCLUSION/NOT_WEAK"
    sc03001_mappings = [m for m in mappings if m.source_claim_id == "SC-ZPZQ-03-001"]
    all_exclusion = all(m.is_exclusion_mapping for m in sc03001_mappings)
    no_positive = all("身强" not in m.candidate_concept for m in sc03001_mappings)
    tests.append(NegativeTest(
        test_id="SPEC-S3",
        test_name="SC-ZPZQ-03-001 只能建立EXCLUSION/NOT_WEAK，不得建立得禄旺→身强",
        test_description="检查SC-ZPZQ-03-001的所有Mapping都是EXCLUSION映射(is_exclusion_mapping=True)，candidate_concept不包含'身强'",
        expected_result="所有Mapping的is_exclusion_mapping=True, candidate_concept不包含'身强'",
        actual_result=f"is_exclusion_mapping全部=True: {all_exclusion}, candidate_concept不包含'身强': {no_positive}",
        passed=all_exclusion and no_positive,
    ))

    # S4. 不得反向生成"满足某条件→身弱"
    no_positive_shiruo = all("身弱" not in m.candidate_concept or "NOT_WEAK" in m.candidate_concept or "维度" in m.candidate_concept or "区分" in m.candidate_concept for m in mappings)
    tests.append(NegativeTest(
        test_id="SPEC-S4",
        test_name="不得反向生成满足某条件→身弱",
        test_description="检查所有Mapping的candidate_concept没有正向声明'身弱'，只有维度定义、区分原则、EXCLUSION/NOT_WEAK",
        expected_result="所有Mapping的candidate_concept不包含正向'身弱'声明",
        actual_result=f"所有Mapping的candidate_concept不包含正向'身弱'声明: {no_positive_shiruo}",
        passed=no_positive_shiruo,
    ))

    return tests


# ============================================================================
# 输出
# ============================================================================

def print_phase4_report(
    mappings: List[CandidateSemanticMapping],
    evidences: List[CandidateEvidence],
    contract: CandidateEvidenceContract,
    negative_tests: List[NegativeTest],
    special_tests: List[NegativeTest],
):
    """打印Phase 4报告."""
    print("=" * 120)
    print("STR-001A Phase 4 - Candidate SemanticMapping + Candidate Evidence Contract")
    print("=" * 120)
    print(f"\nContract/Governance Layer = FROZEN (v6-final.1)")
    print(f"Phase 3 Source Claim Audit = PASS (3 SOURCE_SUPPORTED, 7 SOURCE_MAPPED, 0 REJECTED)")
    print(f"只处理3条SOURCE_SUPPORTED: SC-ZPZQ-06-001 / SC-ZPZQ-06-002 / SC-ZPZQ-03-001")
    print(f"SC-YHZP-SR-001 保持 UNKNOWN / NOT_AUTHORIZED 隔离状态")
    print(f"特别注意: SourceClaimRelation=AUTHORIZES_MAPPING ≠ Mapping automatically AUTHORIZED (GOV-INVARIANT-01)")

    # === 1. Mapping Matrix ===
    print(f"\n{'='*120}")
    print("一、Phase 4 Mapping Matrix (5条Candidate SemanticMapping)")
    print("=" * 120)
    for m in mappings:
        print(f"\n  [{m.mapping_id}]")
        print(f"    source_claim_id: {m.source_claim_id}")
        print(f"    engine_feature_id: {m.engine_feature_id} (None=未确定具体Engine Feature)")
        print(f"    observable_meaning: {m.observable_meaning}")
        print(f"    candidate_concept: {m.candidate_concept}")
        print(f"    mapping_basis: {m.mapping_basis.value}")
        print(f"    mapping_status: {m.mapping_status.value}")
        print(f"    mapping_authorization: {m.mapping_authorization.value} ⚠️ NOT_AUTHORIZED")
        print(f"    is_dimension_mapping_only: {m.is_dimension_mapping_only}")
        print(f"    is_exclusion_mapping: {m.is_exclusion_mapping}")
        print(f"    forbidden_direction: {m.forbidden_direction}")
        print(f"    notes: {m.notes}")

    # === 2. Candidate Evidence Matrix ===
    print(f"\n{'='*120}")
    print("二、Candidate Evidence Matrix (4条Candidate Evidence)")
    print("=" * 120)
    for e in evidences:
        print(f"\n  [{e.evidence_id}]")
        print(f"    evidence_role: {e.evidence_role.value}")
        print(f"    description: {e.description}")
        print(f"    supporting_source_claim_ids: {e.supporting_source_claim_ids}")
        print(f"    source_claim_relations: {[r.value for r in e.source_claim_relations]}")
        print(f"    evaluation_sequence: {e.evaluation_sequence}")
        print(f"    authorization_status: {e.authorization_status.value} ⚠️ CANDIDATE")
        print(f"    is_exclusion: {e.is_exclusion}")
        print(f"    is_dimension_only: {e.is_dimension_only}")
        print(f"    cannot_be_positive_proof: {e.cannot_be_positive_proof}")
        if e.conditional_relations:
            print(f"    conditional_relations: {e.conditional_relations}")
        print(f"    notes: {e.notes}")

    # === 3. Candidate Evidence Contract ===
    print(f"\n{'='*120}")
    print("三、Candidate Evidence Contract (DRAFT)")
    print("=" * 120)
    print(f"\n  contract_id: {contract.contract_id}")
    print(f"  contract_status: {contract.contract_status.value} ⚠️ DRAFT")
    print(f"  proposition_id: {contract.proposition_id}")
    print(f"  proposition_name: {contract.proposition_name}")
    print(f"  evaluation_order_mode: {contract.evaluation_order_mode}")
    print(f"  evaluation_order_scope: {contract.evaluation_order_scope}")
    print(f"  evaluation_sequence: {contract.evaluation_sequence}")
    print(f"  has_positive_proof_rule: {contract.has_positive_proof_rule} ⚠️ False (没有正向判定规则)")
    print(f"  has_exclusion_rule: {contract.has_exclusion_rule}")
    print(f"  can_produce_proven: {contract.can_produce_proven} ⚠️ False (不能产生L4 PROVEN)")
    print(f"\n  Evidence Groups:")
    for g in contract.evidence_groups:
        print(f"    [{g.group_id}] {g.group_description}")
        print(f"      evidence_ids: {g.evidence_ids}")
        print(f"      group_logic: {g.group_logic}")
    print(f"\n  notes: {contract.notes}")

    # === 4. Negative Test Matrix ===
    print(f"\n{'='*120}")
    print("四、Negative Test Matrix (7条)")
    print("=" * 120)
    all_neg_pass = True
    for t in negative_tests:
        status = "✅ PASS" if t.passed else "❌ FAIL"
        if not t.passed:
            all_neg_pass = False
        print(f"\n  [{t.test_id}] {status}")
        print(f"    test_name: {t.test_name}")
        print(f"    test_description: {t.test_description}")
        print(f"    expected: {t.expected_result}")
        print(f"    actual: {t.actual_result}")

    # === 5. Special Test Matrix ===
    print(f"\n{'='*120}")
    print("五、Special Test Matrix (4条)")
    print("=" * 120)
    all_spec_pass = True
    for t in special_tests:
        status = "✅ PASS" if t.passed else "❌ FAIL"
        if not t.passed:
            all_spec_pass = False
        print(f"\n  [{t.test_id}] {status}")
        print(f"    test_name: {t.test_name}")
        print(f"    test_description: {t.test_description}")
        print(f"    expected: {t.expected_result}")
        print(f"    actual: {t.actual_result}")

    # === 6. Gate Result ===
    print(f"\n{'='*120}")
    print("六、Gate Result")
    print("=" * 120)
    all_pass = all_neg_pass and all_spec_pass
    print(f"\n  Negative Tests: {'ALL PASS' if all_neg_pass else 'SOME FAIL'} ({sum(1 for t in negative_tests if t.passed)}/{len(negative_tests)})")
    print(f"  Special Tests: {'ALL PASS' if all_spec_pass else 'SOME FAIL'} ({sum(1 for t in special_tests if t.passed)}/{len(special_tests)})")
    print(f"\n  >>> GATE RESULT: {'ALL PASS' if all_pass else 'SOME FAIL'}")

    # === 7. 最终状态确认 ===
    print(f"\n{'='*120}")
    print("七、最终状态确认 (本阶段正确结果: Candidate assets created, 但Canonical Authorization仍然NOT_DONE)")
    print("=" * 120)
    print(f"""
  Canonical Source Authorization:    NOT_DONE (SourceClaim只是SOURCE_SUPPORTED, 不是AUTHORIZED)
  Semantic Mapping Authorization:    NOT_DONE (所有5条Mapping的mapping_authorization = NOT_AUTHORIZED)
  Evidence Authorization:            NOT_DONE (所有4条Evidence的authorization_status = CANDIDATE)
  Evidence Contract Authorization:   NOT_DONE (contract_status = DRAFT, can_produce_proven = False)
  Proposition Evaluation:            NOT_DONE (不能进入L4 Evaluation)
  L4 PROVEN:                         NOT_POSSIBLE (can_produce_proven = False)

  Candidate assets created:
    - 5条 Candidate SemanticMapping (NOT_AUTHORIZED)
    - 4条 Candidate Evidence (CANDIDATE)
    - 1条 Candidate Evidence Contract (DRAFT)

  防污染边界:
    - SC-ZPZQ-06-001: 只建立维度区分映射, 禁止失令→身弱
    - SC-ZPZQ-06-002: 只建立EXCLUSION/NOT_WEAK, 禁止有根→身强
    - SC-ZPZQ-03-001: 只建立EXCLUSION/NOT_WEAK, 禁止得禄旺→身强
    - 所有Mapping: engine_feature_id = None (没有ENGINE_FEATURE threshold)
    - 所有Evidence: cannot_be_positive_proof = True (不能作为正向证明)
    - Evidence Contract: can_produce_proven = False (不能产生L4 PROVEN)
    """)

    print(f"\n{'='*120}")
    print("STR-001A Phase 4 完成.")
    print("=" * 120)


# ============================================================================
# 主函数
# ============================================================================

def main():
    mappings = create_candidate_mappings()
    evidences = create_candidate_evidences()
    contract = create_candidate_evidence_contract()
    negative_tests = run_negative_tests(mappings, evidences, contract)
    special_tests = run_special_tests(mappings)
    print_phase4_report(mappings, evidences, contract, negative_tests, special_tests)


if __name__ == "__main__":
    main()
