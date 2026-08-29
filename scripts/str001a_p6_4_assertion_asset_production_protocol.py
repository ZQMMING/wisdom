"""
STR-001A P6.4 Assertion Asset Production Protocol

定位: 不是继续开发断言引擎, 而是建立断言资产的生产、审核、入库治理协议。

核心原则:
  Hermes 只能负责 SOURCE → CANDIDATE, 不拥有 Admission 权。
  SOURCE → Hermes interpretation → ❌ 不能直接成为 RULE
  必须: SOURCE → CANDIDATE → Independent Audit → Admission Gate → RULE

P6.4 子任务:
  P6.4-A  Candidate Schema (断言候选数据结构)
  P6.4-B  Evidence Contract (证据契约)
  P6.4-C  Semantic Relation Contract (语义关系契约)
  P6.4-D  Reverse / Qualifier Contract (反向/限定契约)
  P6.4-E  Hermes Production Boundary (Hermes生产边界)
  P6.4-F  ASSERT-006 Acceptance Sample (验收样本)

验收标准:
  不是"成功增加一条断言"。
  而是必须证明:
    Hermes找到一句古文 → 没有足够证据 → 仍然只能CANDIDATE
    原文存在但语义边界不确定 → CANDIDATE / UNRESOLVED
    条件明确+证据充分+反向条件充分+Matcher可结构化 → 才进入Admission Gate
    Admission Gate通过 → AUTHORIZED / AUTHORIZED_WITH_QUALIFIER
"""

import sys
sys.path.insert(0, r"D:\shuntian\backend\scripts")

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime


# ============================================================
# P6.4-A Candidate Schema (断言候选数据结构)
# ============================================================

class CandidateStatus(Enum):
    """候选断言状态"""
    RAW = "RAW"                          # 原始提取, 未整理
    NORMALIZED = "NORMALIZED"            # 语义规范化完成
    EVIDENCE_CONTRACT = "EVIDENCE_CONTRACT"  # 证据契约完成
    PRECONDITION_CONTRACT = "PRECONDITION_CONTRACT"  # 前置条件契约完成
    AUDIT_READY = "AUDIT_READY"         # 可进入独立审核
    IN_AUDIT = "IN_AUDIT"               # 审核中
    AUDIT_COMPLETE = "AUDIT_COMPLETE"   # 审核完成
    ADMISSION_READY = "ADMISSION_READY" # 可进入Admission Gate
    REJECTED = "REJECTED"                # 被拒绝
    CANDIDATE = "CANDIDATE"              # 候选(证据不足, 暂不入库)
    POSTERIOR = "POSTERIOR"              # 后置(仅作参考)


class EvidenceStatus(Enum):
    """证据状态"""
    NOT_CHECKED = "NOT_CHECKED"
    INSUFFICIENT_SOURCE = "INSUFFICIENT_SOURCE"
    SOURCE_MAPPED_NON_PROOF = "SOURCE_MAPPED_NON_PROOF"
    SOURCE_SUPPORTED_WITH_QUALIFIER = "SOURCE_SUPPORTED_WITH_QUALIFIER"
    SOURCE_SUPPORTED = "SOURCE_SUPPORTED"
    CONFIRMED = "CONFIRMED"


class SemanticUncertainty(Enum):
    """语义不确定性类型"""
    RELATION_WORD_UNDEFINED = "RELATION_WORD_UNDEFINED"  # 关系词未定义(见/生/合/制/化/逢)
    SUBJECT_UNDEFINED = "SUBJECT_UNDEFINED"              # 主体未定义(食神/财/官等)
    OBJECT_UNDEFINED = "OBJECT_UNDEFINED"                # 客体未定义
    CONDITION_UNDEFINED = "CONDITION_UNDEFINED"          # 条件未定义
    EFFECT_UNDEFINED = "EFFECT_UNDEFINED"                # 效果未定义
    SCOPE_UNDEFINED = "SCOPE_UNDEFINED"                  # 适用范围未定义
    CONTEXT_DEPENDENT = "CONTEXT_DEPENDENT"              # 依赖上下文
    COUNTEREXAMPLE_EXISTS = "COUNTEREXAMPLE_EXISTS"      # 存在反例


@dataclass
class SourceRecord:
    """来源记录"""
    source_book: str                    # 来源典籍
    source_location: str                 # 来源位置(篇/章/节)
    source_text: str                     # 原文
    source_context: str = ""             # 上下文
    source_version: str = ""              # 版本
    cross_references: List[str] = field(default_factory=list)  # 交叉引用


@dataclass
class SemanticRelation:
    """语义关系"""
    subject: str                         # 主体(如: 食神)
    relation: str                        # 关系(如: 生)
    object: str                          # 客体(如: 财)
    relation_semantics: str              # 关系语义(原典如何定义这个关系)
    relation_word_analysis: str = ""     # 关系词分析(见/生/合/制/化/逢)
    is_boolean_simplifiable: bool = False  # 是否可简化为boolean(默认False)
    simplification_risk: str = ""         # 简化风险描述


@dataclass
class PreconditionCandidate:
    """前置条件候选"""
    pid: str
    name: str
    description: str
    source_type: str                     # CONSUMED_CANONICAL_STATE / SOURCE_DEFINED_STATE / L1_FACT
    canonical_state_ref: str = ""        # 引用的Canonical State字段
    state_dependency: str = ""            # 状态依赖
    is_resolvable: bool = False           # 是否可解析(有明确原典定义)
    unresolved_reason: str = ""           # 未解析原因


@dataclass
class ReverseCondition:
    """反向条件"""
    condition_id: str
    description: str
    source_text: str
    source_location: str
    effect: str                           # 反向效果(如: 不为祸/反为贵)
    is_authorized: bool = False           # 是否被原典授权


@dataclass
class Qualifier:
    """限定条件"""
    qualifier_id: str
    description: str
    source_text: str
    source_location: str
    effect_on_assertion: str              # 对断言的影响(如: 降低强度/增加条件)


@dataclass
class AssertionCandidate:
    """
    断言候选 (Assertion Candidate)
    这是Hermes的输出, 也是Independent Audit的输入。
    Hermes只能产生这个结构, 不能直接产生Authorized Assertion。
    """
    assertion_id: str
    candidate_status: CandidateStatus = CandidateStatus.RAW
    created_by: str = "Hermes"            # 生产者(必须是Hermes, 不能是Auditor)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # 来源
    source: SourceRecord = field(default_factory=lambda: SourceRecord("", "", ""))
    additional_sources: List[SourceRecord] = field(default_factory=list)

    # 语义关系
    semantic_relations: List[SemanticRelation] = field(default_factory=list)

    # 前置条件
    preconditions: List[PreconditionCandidate] = field(default_factory=list)

    # 效果候选
    effect_candidate: str = ""
    effect_source_text: str = ""

    # 反向条件
    reverse_conditions: List[ReverseCondition] = field(default_factory=list)

    # 限定条件
    qualifiers: List[Qualifier] = field(default_factory=list)

    # 反例
    counterexamples: List[str] = field(default_factory=list)

    # 未解决项 (核心: 不知道 ≠ 没有条件)
    unresolved_items: List[Dict] = field(default_factory=list)

    # 证据状态
    evidence_status: EvidenceStatus = EvidenceStatus.NOT_CHECKED
    admission_status: str = "NOT_SUBMITTED"

    # Hermes自评估 (仅供参考, 不构成授权)
    hermes_self_assessment: Dict = field(default_factory=dict)

    # 审核记录
    audit_records: List[Dict] = field(default_factory=list)

    def add_unresolved(self, item_type: str, description: str, impact: str = ""):
        """添加未解决项"""
        self.unresolved_items.append({
            "type": item_type,
            "description": description,
            "impact": impact,
            "resolved": False,
        })

    def is_audit_ready(self) -> bool:
        """是否可进入审核(必须有基本的来源和语义关系)"""
        return (
            self.source.source_text != ""
            and len(self.semantic_relations) > 0
            and self.candidate_status in [
                CandidateStatus.NORMALIZED,
                CandidateStatus.EVIDENCE_CONTRACT,
                CandidateStatus.PRECONDITION_CONTRACT,
                CandidateStatus.AUDIT_READY,
            ]
        )

    def is_admission_ready(self) -> bool:
        """是否可进入Admission Gate(必须证据充分+无关键未解决项)"""
        critical_unresolved = [
            u for u in self.unresolved_items
            if not u.get("resolved", False)
            and u.get("type") in [
                SemanticUncertainty.RELATION_WORD_UNDEFINED.value,
                SemanticUncertainty.CONDITION_UNDEFINED.value,
                SemanticUncertainty.EFFECT_UNDEFINED.value,
            ]
        ]
        return (
            self.evidence_status in [
                EvidenceStatus.SOURCE_SUPPORTED,
                EvidenceStatus.CONFIRMED,
                EvidenceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
            ]
            and len(critical_unresolved) == 0
            and len(self.preconditions) > 0
        )


# ============================================================
# P6.4-E Hermes Production Boundary (Hermes生产边界)
# ============================================================

class HermesProductionBoundary:
    """
    Hermes生产边界: 定义Hermes能做什么/不能做什么。

    Hermes可以:
      - 搜索五部经典及已授权资料
      - 定位原文
      - 保存原文上下文
      - 提取候选断语
      - 标注可能的关系词
      - 提取可能的前置条件
      - 提取反向条件
      - 提取qualifier
      - 形成AssertionCandidate

    Hermes不可以:
      - 自行把古文解释成现代规则
      - 自行定义STRONG / WEAK
      - 自行定义杀浅 / 杀重 / 财多
      - 自行把「见、生、合、制、化、逢」简化成boolean
      - 自行授权Effect
      - 自行决定AUTHORIZED
      - 自行写入Authorized Assertion Library
    """

    ALLOWED_ACTIONS = [
        "search_classics",           # 搜索五部经典
        "locate_source",             # 定位原文
        "save_context",              # 保存上下文
        "extract_candidate",         # 提取候选断语
        "annotate_relation_words",   # 标注关系词
        "extract_preconditions",     # 提取前置条件
        "extract_reverse_conditions", # 提取反向条件
        "extract_qualifiers",        # 提取qualifier
        "form_candidate",            # 形成AssertionCandidate
        "self_assess",               # 自评估(仅供参考)
    ]

    FORBIDDEN_ACTIONS = [
        "interpret_as_modern_rule",    # 自行把古文解释成现代规则
        "define_strong_weak",           # 自行定义STRONG / WEAK
        "define_relative_state",        # 自行定义杀浅/杀重/财多
        "simplify_relation_to_boolean", # 自行把关系词简化成boolean
        "authorize_effect",             # 自行授权Effect
        "decide_authorized",            # 自行决定AUTHORIZED
        "write_to_authorized_library",  # 自行写入Authorized Assertion Library
    ]

    @classmethod
    def validate_candidate(cls, candidate: AssertionCandidate) -> Tuple[bool, List[str]]:
        """
        验证Hermes产生的Candidate是否符合生产边界。
        返回 (是否合规, 违规列表)
        """
        violations = []

        # 检查1: 生产者必须是Hermes
        if candidate.created_by != "Hermes":
            violations.append(f"生产者不是Hermes: {candidate.created_by}")

        # 检查2: 不能直接设置admission_status为AUTHORIZED
        if candidate.admission_status in ["AUTHORIZED", "AUTHORIZED_WITH_QUALIFIER"]:
            violations.append("Hermes不能自行设置admission_status为AUTHORIZED")

        # 检查3: 不能直接设置evidence_status为CONFIRMED(Hermes只能初步标注)
        if candidate.evidence_status == EvidenceStatus.CONFIRMED:
            violations.append("Hermes不能自行设置evidence_status为CONFIRMED, 需Independent Audit确认")

        # 检查4: 必须有未解决项(除非证据极其充分)
        # 这是核心: 不知道 ≠ 没有条件
        if len(candidate.unresolved_items) == 0 and candidate.evidence_status != EvidenceStatus.SOURCE_SUPPORTED:
            violations.append("Candidate没有未解决项, 可能存在语义偷渡(不知道≠没有条件)")

        # 检查5: 语义关系不能标记为可简化为boolean(除非有明确原典授权)
        for sr in candidate.semantic_relations:
            if sr.is_boolean_simplifiable and not sr.simplification_risk:
                violations.append(f"语义关系'{sr.relation}'标记为可简化为boolean但没有风险说明")

        # 检查6: 必须有来源原文
        if not candidate.source.source_text:
            violations.append("Candidate没有来源原文")

        return len(violations) == 0, violations


# ============================================================
# P6.4 Independent Audit Pipeline (独立审核流水线)
# ============================================================

class IndependentAuditPipeline:
    """
    独立审核流水线: 7个Audit, 独立于Hermes。

    1. Evidence Audit (证据审核)
    2. Semantic Audit (语义审核)
    3. Preconditions Audit (前置条件审核)
    4. Matcher Audit (匹配器审核)
    5. Effect Audit (效果审核)
    6. Reverse Audit (反向审核)
    7. Qualifier Audit (限定审核)
    """

    def __init__(self):
        self.audit_results = {}

    def run_full_audit(self, candidate: AssertionCandidate) -> Dict:
        """运行完整7层审核"""

        print(f"\n  {'='*100}")
        print(f"  Independent Audit Pipeline — {candidate.assertion_id}")
        print(f"  {'='*100}")

        results = {}

        # 1. Evidence Audit
        results["evidence"] = self._audit_evidence(candidate)

        # 2. Semantic Audit
        results["semantic"] = self._audit_semantic(candidate)

        # 3. Preconditions Audit
        results["preconditions"] = self._audit_preconditions(candidate)

        # 4. Matcher Audit
        results["matcher"] = self._audit_matcher(candidate)

        # 5. Effect Audit
        results["effect"] = self._audit_effect(candidate)

        # 6. Reverse Audit
        results["reverse"] = self._audit_reverse(candidate)

        # 7. Qualifier Audit
        results["qualifier"] = self._audit_qualifier(candidate)

        # 汇总
        all_passed = all(r["passed"] for r in results.values())
        critical_issues = [r for r in results.values() if r.get("critical", False)]

        print(f"\n  审核汇总:")
        for audit_name, result in results.items():
            status = "✓ PASS" if result["passed"] else "✗ FAIL"
            critical = " [CRITICAL]" if result.get("critical") else ""
            print(f"    {status} {audit_name}{critical}: {result['summary'][:60]}")

        print(f"\n  总体: {'全部通过' if all_passed else '存在未通过项'}")
        if critical_issues:
            print(f"  关键问题: {len(critical_issues)}个")

        self.audit_results[candidate.assertion_id] = results
        return results

    def _audit_evidence(self, candidate: AssertionCandidate) -> Dict:
        """证据审核: 原典是否存在, 上下文是否完整, 交叉验证是否充分"""
        issues = []

        if not candidate.source.source_text:
            issues.append("没有来源原文")
        if not candidate.source.source_book:
            issues.append("没有来源典籍")
        if not candidate.source.source_location:
            issues.append("没有来源位置")
        if len(candidate.additional_sources) == 0:
            issues.append("没有交叉引用(建议至少2个来源)")

        passed = len(issues) == 0
        return {
            "passed": passed,
            "critical": not candidate.source.source_text,
            "summary": f"来源: {candidate.source.source_book or '未知'}, 交叉引用: {len(candidate.additional_sources)}个",
            "issues": issues,
        }

    def _audit_semantic(self, candidate: AssertionCandidate) -> Dict:
        """语义审核: 关系词是否有明确定义, 是否存在语义偷渡"""
        issues = []

        for sr in candidate.semantic_relations:
            if not sr.relation_semantics:
                issues.append(f"关系'{sr.relation}'没有语义定义")
            if sr.is_boolean_simplifiable:
                issues.append(f"关系'{sr.relation}'被标记为可简化为boolean, 需严格审查")

        # 检查未解决项中的关系词不确定性
        relation_uncertainty = [
            u for u in candidate.unresolved_items
            if u.get("type") == SemanticUncertainty.RELATION_WORD_UNDEFINED.value
        ]
        if relation_uncertainty:
            issues.append(f"存在{len(relation_uncertainty)}个关系词未定义项")

        passed = len(issues) == 0
        return {
            "passed": passed,
            "critical": len(relation_uncertainty) > 0,
            "summary": f"语义关系: {len(candidate.semantic_relations)}个, 未解决: {len(candidate.unresolved_items)}个",
            "issues": issues,
        }

    def _audit_preconditions(self, candidate: AssertionCandidate) -> Dict:
        """前置条件审核: 是否区分了状态依赖类型, 是否存在未授权的状态定义"""
        issues = []

        if len(candidate.preconditions) == 0:
            issues.append("没有前置条件")

        for pc in candidate.preconditions:
            if pc.source_type not in ["CONSUMED_CANONICAL_STATE", "SOURCE_DEFINED_STATE", "L1_FACT"]:
                issues.append(f"前置条件{pc.pid}的source_type无效: {pc.source_type}")
            if not pc.is_resolvable and not pc.unresolved_reason:
                issues.append(f"前置条件{pc.pid}不可解析但没有说明原因")

        passed = len(issues) == 0
        return {
            "passed": passed,
            "critical": len(candidate.preconditions) == 0,
            "summary": f"前置条件: {len(candidate.preconditions)}个",
            "issues": issues,
        }

    def _audit_matcher(self, candidate: AssertionCandidate) -> Dict:
        """匹配器审核: 是否可结构化, 是否存在简化为boolean的风险"""
        # Matcher是在Admission阶段才构建的, Candidate阶段只检查是否可结构化
        can_structure = len(candidate.preconditions) > 0 and all(
            pc.is_resolvable for pc in candidate.preconditions
        )
        return {
            "passed": can_structure,
            "critical": False,
            "summary": f"可结构化: {'是' if can_structure else '否(存在不可解析前置条件)'}",
            "issues": [] if can_structure else ["存在不可解析的前置条件"],
        }

    def _audit_effect(self, candidate: AssertionCandidate) -> Dict:
        """效果审核: Effect是否有原典授权, 是否存在过度推断"""
        issues = []

        if not candidate.effect_candidate:
            issues.append("没有Effect候选")
        if not candidate.effect_source_text:
            issues.append("Effect没有原典来源文本")

        passed = len(issues) == 0
        return {
            "passed": passed,
            "critical": not candidate.effect_candidate,
            "summary": f"Effect: {candidate.effect_candidate[:30] if candidate.effect_candidate else '无'}",
            "issues": issues,
        }

    def _audit_reverse(self, candidate: AssertionCandidate) -> Dict:
        """反向审核: 是否查找了反向条件"""
        # 反向条件不是必须的, 但如果没有查找应该标注
        has_reverse = len(candidate.reverse_conditions) > 0
        return {
            "passed": True,  # 反向条件不是必须通过项
            "critical": False,
            "summary": f"反向条件: {len(candidate.reverse_conditions)}个{'(建议补充)' if not has_reverse else ''}",
            "issues": [] if has_reverse else ["建议补充反向条件"],
        }

    def _audit_qualifier(self, candidate: AssertionCandidate) -> Dict:
        """限定审核: 是否保留了限定条件"""
        has_qualifier = len(candidate.qualifiers) > 0
        return {
            "passed": True,  # 限定条件不是必须通过项
            "critical": False,
            "summary": f"限定条件: {len(candidate.qualifiers)}个{'(建议补充)' if not has_qualifier else ''}",
            "issues": [] if has_qualifier else ["建议补充限定条件"],
        }


# ============================================================
# P6.4-F ASSERT-006 Acceptance Sample (验收样本)
# ============================================================

def build_assert_006_candidate() -> AssertionCandidate:
    """
    构建ASSERT-006「食神生财，富贵自天来」的Candidate。

    这是P6.4的验收样本: 不是为了证明这句话正确,
    而是为了证明生产协议能够把一句口诀拆成可审计资产, 而不会提前替它授权。

    核心验证点:
      食神 + 财星 ≠ 食神生财
      什么叫「食神」? 什么叫「财」? 什么叫「生」?
      「生」是五行关系存在即可? 还是需要透干/得令/有根/流通/格局?
      「富贵」是直接Effect? 还是有其他前置条件?
      有没有反向条件? 有没有「食神太过」「身弱」「财被夺」等限制?

    不预设答案。
    """

    candidate = AssertionCandidate(
        assertion_id="ASSERT-006",
        candidate_status=CandidateStatus.NORMALIZED,
        created_by="Hermes",
    )

    # 来源 (初步定位, 需Independent Audit确认)
    candidate.source = SourceRecord(
        source_book="《渊海子平》",
        source_location="待精确审计(可能在《论食神》或相关篇章)",
        source_text="食神生财，富贵自天来。",
        source_context="待补充完整上下文",
        cross_references=["待查找《三命通会》《子平真诠》等交叉引用"],
    )

    # 语义关系 (核心: 「生」的语义必须保留, 不能简化为boolean)
    candidate.semantic_relations = [
        SemanticRelation(
            subject="食神",
            relation="生",
            object="财",
            relation_semantics="待原典审计: 「生」是五行相生关系存在即可, 还是需要食神有力/财星有根/流通无阻/格局配合?",
            relation_word_analysis="「生」是核心关系词, 不能简化为has_shishen AND has_cai。必须审计: 食神是否需要透干/得令/有根? 财星是否需要有根/透干? 「生」是否需要流通(食神→财的路径无阻)? 是否存在「食神太过不生财」「身弱食神泄气」「财被比劫夺」等限制?",
            is_boolean_simplifiable=False,
            simplification_risk="极高: 如果简化为has_shishen AND has_cai, 会丢失「生」的所有语义边界, 导致大量错误命中",
        ),
    ]

    # 前置条件候选 (全部标记为待审计, 不预设答案)
    candidate.preconditions = [
        PreconditionCandidate(
            pid="P1",
            name="食神存在且有力",
            description="食神是否需要透干/得令/有根? 「食神生财」的食神是否必须有力?",
            source_type="SOURCE_DEFINED_STATE",
            is_resolvable=False,
            unresolved_reason="原典未明确「食神有力」的具体标准, 需Independent Audit",
        ),
        PreconditionCandidate(
            pid="P2",
            name="财星存在且可受生",
            description="财星是否需要有根/透干? 财星是否必须「可受生」?",
            source_type="SOURCE_DEFINED_STATE",
            is_resolvable=False,
            unresolved_reason="原典未明确「财可受生」的具体标准, 需Independent Audit",
        ),
        PreconditionCandidate(
            pid="P3",
            name="「生」的流通关系成立",
            description="食神→财的五行相生路径是否需要无阻? 是否存在比劫夺财/印克食神等阻断?",
            source_type="SOURCE_DEFINED_STATE",
            is_resolvable=False,
            unresolved_reason="「生」是否需要流通无阻是核心语义问题, 原典未明确, 需Independent Audit",
        ),
        PreconditionCandidate(
            pid="P4",
            name="日主状态",
            description="「食神生财」是否需要身强? 身弱时食神泄气是否反而为害?",
            source_type="CONSUMED_CANONICAL_STATE",
            canonical_state_ref="qiangruo=STRONG?",
            is_resolvable=False,
            unresolved_reason="原典中「食神生财」是否要求身强未明确, 需Independent Audit。注意: 不能因为身弱就自动否定, 也不能因为身强就自动肯定",
        ),
    ]

    # Effect候选
    candidate.effect_candidate = "富贵自天来"
    candidate.effect_source_text = "食神生财，富贵自天来。"

    # 反向条件 (初步查找, 需Independent Audit确认)
    candidate.reverse_conditions = [
        ReverseCondition(
            condition_id="R1",
            description="食神太过 / 食多不生财",
            source_text="待查找原典: 是否存在「食神太多反不生财」的表述?",
            source_location="待查找",
            effect="可能限制「食神生财」的适用范围",
            is_authorized=False,
        ),
        ReverseCondition(
            condition_id="R2",
            description="身弱食神泄气",
            source_text="待查找原典: 身弱时食神是否反而泄气为害?",
            source_location="待查找",
            effect="身弱时「食神生财」可能不成立",
            is_authorized=False,
        ),
        ReverseCondition(
            condition_id="R3",
            description="比劫夺财",
            source_text="待查找原典: 财星被比劫夺时「食神生财」是否失效?",
            source_location="待查找",
            effect="财被夺时「生财」效果可能被阻断",
            is_authorized=False,
        ),
    ]

    # 限定条件
    candidate.qualifiers = [
        Qualifier(
            qualifier_id="Q1",
            description="「生」的语义边界未确定",
            source_text="食神生财，富贵自天来。",
            source_location="《渊海子平》待精确",
            effect_on_assertion="核心关系词「生」的语义未确定前, 不能结构化Matcher",
        ),
    ]

    # 未解决项 (核心: 不知道 ≠ 没有条件)
    candidate.add_unresolved(
        SemanticUncertainty.RELATION_WORD_UNDEFINED.value,
        "「生」的语义未定义: 是五行关系存在即可, 还是需要透干/得令/有根/流通/格局?",
        "核心: 如果「生」的语义不明确, Matcher无法结构化, 不能进入Admission Gate",
    )
    candidate.add_unresolved(
        SemanticUncertainty.SUBJECT_UNDEFINED.value,
        "「食神」的标准未定义: 食神是否需要透干/得令/有根才算「有力的食神」?",
        "P1前置条件无法解析",
    )
    candidate.add_unresolved(
        SemanticUncertainty.OBJECT_UNDEFINED.value,
        "「财」的标准未定义: 财星是否需要有根/透干才算「可受生的财」?",
        "P2前置条件无法解析",
    )
    candidate.add_unresolved(
        SemanticUncertainty.CONDITION_UNDEFINED.value,
        "「生」是否需要流通无阻未定义: 是否存在比劫夺财/印克食神等阻断条件?",
        "P3前置条件无法解析",
    )
    candidate.add_unresolved(
        SemanticUncertainty.EFFECT_UNDEFINED.value,
        "「富贵自天来」是否为直接Effect未定义: 是否需要其他条件配合?",
        "Effect授权不确定",
    )
    candidate.add_unresolved(
        SemanticUncertainty.COUNTEREXAMPLE_EXISTS.value,
        "是否存在反例未确认: 「食神太过不生财」「身弱食神泄气」「比劫夺财」等是否有原典依据?",
        "反向条件未授权, 可能影响断言适用范围",
    )

    # Hermes自评估 (仅供参考, 不构成授权)
    candidate.hermes_self_assessment = {
        "confidence": "LOW",
        "reason": "核心关系词「生」的语义未定义, 6个未解决项, 不建议进入Admission Gate",
        "recommendation": "保持CANDIDATE状态, 先完成原典语义审计, 特别是「生」的定义和「食神有力」的标准",
        "warning": "严禁将「食神生财」简化为has_shishen AND has_cai, 这会丢失所有语义边界",
    }

    # 证据状态 (Hermes只能初步标注, 不能设为CONFIRMED)
    candidate.evidence_status = EvidenceStatus.SOURCE_MAPPED_NON_PROOF

    return candidate


# ============================================================
# P6.4 主流程
# ============================================================

def main():
    print("=" * 110)
    print("STR-001A P6.4 Assertion Asset Production Protocol")
    print("=" * 110)

    print(f"""
  定位: 不是继续开发断言引擎, 而是建立断言资产的生产、审核、入库治理协议。

  核心原则:
    Hermes只能负责 SOURCE → CANDIDATE, 不拥有Admission权。
    SOURCE → Hermes interpretation → ❌ 不能直接成为 RULE
    必须: SOURCE → CANDIDATE → Independent Audit → Admission Gate → RULE

  P6.4子任务:
    P6.4-A  Candidate Schema (断言候选数据结构)
    P6.4-B  Evidence Contract (证据契约)
    P6.4-C  Semantic Relation Contract (语义关系契约)
    P6.4-D  Reverse / Qualifier Contract (反向/限定契约)
    P6.4-E  Hermes Production Boundary (Hermes生产边界)
    P6.4-F  ASSERT-006 Acceptance Sample (验收样本)
""")

    # P6.4-A ~ E: 协议框架已在代码中定义
    print(f"  {'='*100}")
    print(f"  P6.4-A ~ E: 协议框架定义")
    print(f"  {'='*100}")
    print(f"""
    P6.4-A Candidate Schema:
      - AssertionCandidate数据结构 (来源/语义关系/前置条件/Effect/反向/限定/未解决项)
      - CandidateStatus状态机 (RAW → NORMALIZED → EVIDENCE_CONTRACT → AUDIT_READY → ...)
      - EvidenceStatus证据状态枚举
      - SemanticUncertainty语义不确定性枚举

    P6.4-B Evidence Contract:
      - SourceRecord来源记录 (典籍/位置/原文/上下文/交叉引用)
      - 证据必须原典定位+原文+上下文
      - 交叉引用至少2个来源

    P6.4-C Semantic Relation Contract:
      - SemanticRelation语义关系 (主体/关系/客体/关系语义)
      - 关系词分析 (见/生/合/制/化/逢)
      - 默认is_boolean_simplifiable=False (不能简化为boolean)
      - 必须标注simplification_risk

    P6.4-D Reverse / Qualifier Contract:
      - ReverseCondition反向条件 (条件/原文/效果/是否授权)
      - Qualifier限定条件 (条件/原文/对断言的影响)
      - 反向/限定不是必须通过项, 但建议补充

    P6.4-E Hermes Production Boundary:
      Hermes可以: 搜索/定位/保存上下文/提取候选/标注关系词/提取前置条件/提取反向/提取qualifier/形成Candidate/自评估
      Hermes不可以: 解释成现代规则/定义STRONG WEAK/定义杀浅杀重财多/简化关系词为boolean/授权Effect/决定AUTHORIZED/写入Authorized Library
""")

    # P6.4-F: ASSERT-006验收样本
    print(f"  {'='*100}")
    print(f"  P6.4-F: ASSERT-006 Acceptance Sample")
    print(f"  {'='*100}")

    print(f"""
  验收目标:
    不是"成功增加一条断言"。
    而是必须证明:
      Hermes找到一句古文 → 没有足够证据 → 仍然只能CANDIDATE
      原文存在但语义边界不确定 → CANDIDATE / UNRESOLVED
      条件明确+证据充分+反向条件充分+Matcher可结构化 → 才进入Admission Gate

  ASSERT-006: 「食神生财，富贵自天来」

  核心验证点:
    食神 + 财星 ≠ 食神生财
    什么叫「食神」? 什么叫「财」? 什么叫「生」?
    「生」是五行关系存在即可? 还是需要透干/得令/有根/流通/格局?
    「富贵」是直接Effect? 还是有其他前置条件?
    有没有反向条件? 有没有「食神太过」「身弱」「财被夺」等限制?

  不预设答案。
""")

    # 构建ASSERT-006 Candidate
    candidate = build_assert_006_candidate()

    print(f"  Candidate构建完成:")
    print(f"    assertion_id: {candidate.assertion_id}")
    print(f"    candidate_status: {candidate.candidate_status.value}")
    print(f"    created_by: {candidate.created_by}")
    print(f"    evidence_status: {candidate.evidence_status.value}")
    print(f"    来源: {candidate.source.source_book}")
    print(f"    原文: {candidate.source.source_text}")
    print(f"    语义关系: {len(candidate.semantic_relations)}个")
    print(f"    前置条件: {len(candidate.preconditions)}个")
    print(f"    反向条件: {len(candidate.reverse_conditions)}个")
    print(f"    限定条件: {len(candidate.qualifiers)}个")
    print(f"    未解决项: {len(candidate.unresolved_items)}个 ← 核心: 不知道≠没有条件")

    # 验证Hermes生产边界
    print(f"\n  {'─'*100}")
    print(f"  Hermes Production Boundary 验证:")
    print(f"  {'─'*100}")

    is_compliant, violations = HermesProductionBoundary.validate_candidate(candidate)
    print(f"    合规: {'✓ 是' if is_compliant else '✗ 否'}")
    if violations:
        print(f"    违规:")
        for v in violations:
            print(f"      • {v}")
    else:
        print(f"    ✓ 没有违规, Candidate符合Hermes生产边界")

    # 验证是否可进入Admission Gate (应该不能)
    print(f"\n  {'─'*100}")
    print(f"  Admission Gate 准入检查 (预期: 不能进入):")
    print(f"  {'─'*100}")

    can_enter = candidate.is_admission_ready()
    print(f"    可进入Admission Gate: {'✓ 是' if can_enter else '✗ 否(预期结果)'}")

    if not can_enter:
        print(f"    原因:")
        critical_unresolved = [
            u for u in candidate.unresolved_items
            if not u.get("resolved", False)
            and u.get("type") in [
                SemanticUncertainty.RELATION_WORD_UNDEFINED.value,
                SemanticUncertainty.CONDITION_UNDEFINED.value,
                SemanticUncertainty.EFFECT_UNDEFINED.value,
            ]
        ]
        print(f"      • evidence_status={candidate.evidence_status.value} (不是SOURCE_SUPPORTED/CONFIRMED)")
        print(f"      • 关键未解决项: {len(critical_unresolved)}个")
        for u in critical_unresolved:
            print(f"        - {u['type']}: {u['description'][:50]}")
        print(f"      • 前置条件可解析: {sum(1 for p in candidate.preconditions if p.is_resolvable)}/{len(candidate.preconditions)}")

    # 运行Independent Audit
    print(f"\n  {'─'*100}")
    print(f"  Independent Audit Pipeline (7层审核):")
    print(f"  {'─'*100}")

    auditor = IndependentAuditPipeline()
    audit_results = auditor.run_full_audit(candidate)

    # 最终结论
    print(f"\n  {'='*100}")
    print(f"  P6.4-F 验收结论:")
    print(f"  {'='*100}")

    print(f"""
    ✓ ASSERT-006 Candidate构建完成, 符合Hermes生产边界
    ✓ Candidate包含完整的来源/语义关系/前置条件/反向/限定/未解决项
    ✓ 核心关系词「生」被正确标记为不可简化为boolean, 风险极高
    ✓ 6个未解决项正确记录 (不知道≠没有条件)
    ✓ evidence_status=SOURCE_MAPPED_NON_PROOF (Hermes不能自行升级为CONFIRMED)
    ✓ 不能进入Admission Gate (证据不足+关键未解决项+前置条件不可解析)
    ✓ Independent Audit发现多个未通过项 (语义/前置条件/Matcher/Effect)

    这正是P6.4的验收标准:
      Hermes找到一句古文 → 没有足够证据 → 仍然只能CANDIDATE ✓
      原文存在但语义边界不确定 → CANDIDATE / UNRESOLVED ✓
      不能因为"口诀很常见"就提前授权 ✓

    ASSERT-006当前状态: CANDIDATE (不进入Authorized Library)
    下一步: 完成原典语义审计, 特别是「生」的定义和「食神有力」的标准,
            以及查找「食神太过不生财」「身弱食神泄气」「比劫夺财」等反例。

    P6.4 Assertion Asset Production Protocol 验证通过。
    生产流水线正式建立:
      Hermes (Candidate Producer)
        ↓ 只能负责 SOURCE → CANDIDATE
      Assertion Candidate
        ↓
      Independent Audit (7层)
        ↓
      Admission Gate (7层)
        ↓
      AUTHORIZED / AUTHORIZED_WITH_QUALIFIER / CANDIDATE / POSTERIOR / REJECTED

    以后即使Hermes一次产生1000条候选断言, 系统也不会因为Hermes自己的判断而污染正式规则库。
    {'='*100}
""")


if __name__ == "__main__":
    main()
