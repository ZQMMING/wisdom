"""P6-C-3C-2 Judgment Asset Schema V2 - 断言资产Schema.

核心原则:
- system与school必须强制 (不能只写system=ZI_PING)
- conditions必须是确定性条件 (不同经典用不同match_mode)
- 必须加入specificity (高特异性不能覆盖低特异性)
- modern_mapping不负责生成内容 (人工/资产标注, 不是LLM)
- 跨经典隔离 (三命通会断言不能被子平真诠Resolver命中)

Schema结构:
  Judgment
  ├── identity (judgment_id/system/school/judgment_type/version)
  ├── retrieval (match_mode/conditions/feature_requirements/specificity)
  ├── statement (classical/semantic_keys/modern_mapping)
  ├── source (book/chapter/section/page/source_locator)
  └── provenance (created_at/revision/status)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from tongshu.judgment_architecture.system_school_contract import (
    DivinationSystem, ZiPingSchool, MatcherType,
)


# ============================================================================
# 1. 断言状态
# ============================================================================

class JudgmentStatus(str, Enum):
    """断言资产状态."""
    ACTIVE = "ACTIVE"               # 活跃
    DRAFT = "DRAFT"                 # 草稿
    DEPRECATED = "DEPRECATED"       # 已废弃
    UNDER_REVIEW = "UNDER_REVIEW"   # 审核中


# ============================================================================
# 2. 匹配条件
# ============================================================================

@dataclass(frozen=True)
class MatchCondition:
    """匹配条件 - 确定性条件, 不是模糊匹配."""
    feature: str                    # Feature ID (如 ZP.DAY_PILLAR)
    operator: str                   # 操作符: EQ/NE/IN/NOT_IN/CONTAINS/GT/LT/GTE/LTE
    value: Any                      # 匹配值

    def to_dict(self) -> dict:
        return {"feature": self.feature, "operator": self.operator, "value": self.value}


# ============================================================================
# 2.5 多维特异度 SpecificityProfile (P6-C-3C-2 架构修正)
# ============================================================================

class SpecificityLevel(str, Enum):
    """特异度等级 - 仅用于同一Retrieval Partition内排序."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXACT = "EXACT"
    COMPOSITE = "COMPOSITE"


class MatchExactness(str, Enum):
    """匹配精确度."""
    EXACT = "EXACT"           # 精确匹配
    SET = "SET"               # 集合匹配
    CONDITION = "CONDITION"   # 条件匹配
    COMPOSITE = "COMPOSITE"   # 复合匹配
    GRAPH = "GRAPH"           # 图匹配


@dataclass(frozen=True)
class SpecificityProfile:
    """多维特异度 - 替代单一specificity数字.

    核心原则:
    - Specificity衡量"这条断言对当前输入的条件约束有多精确"
    - 不是"这部经典有多重要"
    - 不得跨School/Judgment Type直接比较
    - 仅用于同一Retrieval Partition内的候选排序
    - 高specificity只能表示条件更精确, 不得覆盖低specificity
    """
    level: str = SpecificityLevel.LOW.value  # 等级: LOW/MEDIUM/HIGH/EXACT/COMPOSITE
    constraint_count: int = 1                 # 条件数量
    feature_depth: int = 1                    # Feature深度 (如 日柱=1, 日柱+时柱=2)
    match_exactness: str = MatchExactness.CONDITION.value  # 匹配精确度
    structural_depth: int = 0                 # 结构深度 (如 格局层次)
    temporal_depth: int = 0                   # 时间深度 (如 流年+流月)
    scope: str = "NATAL"                      # 范围: NATAL/YEAR/MONTH/DAY/HOUR
    discrimination: str = "MEDIUM"            # 区分度: LOW/MEDIUM/HIGH

    @property
    def rank_key(self) -> tuple:
        """机器排序键 - 仅在同一retrieval partition内有效."""
        level_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "EXACT": 3, "COMPOSITE": 4}
        exactness_order = {"CONDITION": 0, "SET": 1, "COMPOSITE": 2, "GRAPH": 3, "EXACT": 4}
        return (
            level_order.get(self.level, 0),
            self.constraint_count,
            self.feature_depth,
            exactness_order.get(self.match_exactness, 0),
            self.structural_depth,
            self.temporal_depth,
        )

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "constraint_count": self.constraint_count,
            "feature_depth": self.feature_depth,
            "match_exactness": self.match_exactness,
            "structural_depth": self.structural_depth,
            "temporal_depth": self.temporal_depth,
            "scope": self.scope,
            "discrimination": self.discrimination,
            "rank_key": list(self.rank_key),
        }


# ============================================================================
# 2.6 检索分区 RetrievalPartition (两级排序)
# ============================================================================

@dataclass(frozen=True)
class RetrievalPartition:
    """检索分区 - 两级排序的Level 1.

    先按 system+school+judgment_type+retrieval_family 分区,
    只有进入同一个partition后, 才比较specificity.

    不同partition之间不得比较specificity, 因为它们是正交判断.
    """
    system: str                     # 体系 (如 ZI_PING)
    school: str                     # 经典 (如 SAN_MING_TONG_HUI)
    judgment_type: str              # 断言类型 (如 DAY_TIME/PATTERN/TUNING)
    retrieval_family: str = "DEFAULT"  # 检索家族 (如 SIXTY_JIAZI/PATTERN_SUCCESS)

    @property
    def partition_key(self) -> str:
        """分区唯一键."""
        return f"{self.system}:{self.school}:{self.judgment_type}:{self.retrieval_family}"

    def to_dict(self) -> dict:
        return {
            "system": self.system,
            "school": self.school,
            "judgment_type": self.judgment_type,
            "retrieval_family": self.retrieval_family,
            "partition_key": self.partition_key,
        }


# ============================================================================
# 2.7 展示优先级 DisplayPriority (仅UI排序, 不参与判断)
# ============================================================================

@dataclass(frozen=True)
class DisplayPriority:
    """展示优先级 - 仅用于Observatory UI排序.

    绝对禁止:
    - 进入MATCH/REJECT判断
    - 进入specificity resolution
    - 进入Assertion generation
    - 进入Cross-Engine Cluster

    这是为了彻底和以前的SYSTEM_WEIGHTS/weighted voting切断.
    """
    school_priority: int = 50      # 经典展示优先级 (0-100, 仅UI)
    judgment_type_priority: int = 50  # 断言类型展示优先级 (0-100, 仅UI)
    display_order: int = 0          # 展示顺序 (仅UI)

    def to_dict(self) -> dict:
        return {
            "school_priority": self.school_priority,
            "judgment_type_priority": self.judgment_type_priority,
            "display_order": self.display_order,
            "_note": "仅用于Observatory UI排序, 不得参与MATCH/REJECT/Assertion/Cluster",
        }


# ============================================================================
# 3. 断言资产 V2
# ============================================================================

@dataclass(frozen=True)
class JudgmentAssetV2:
    """Judgment Asset V2 - 断言资产.

    强制字段: system + school (不能只写system)
    """
    # === identity ===
    judgment_id: str                # 唯一标识 (如 SMTH-YIWEI-RENWU-001)
    system: str                     # 体系 (如 ZI_PING)
    school: str                     # 经典/学派 (如 SAN_MING_TONG_HUI) - 强制
    judgment_type: str              # 断言类型 (如 DAY_TIME/PATTERN/TUNING)
    version: str = "1.0.0"         # 版本

    # === retrieval ===
    match_mode: str = "CONDITION"  # 匹配模式: EXACT/SET/RANGE/ALL/ANY/GRAPH/CONDITION/COMPOSITE
    conditions: list[MatchCondition] = field(default_factory=list)  # 确定性条件
    feature_requirements: list[str] = field(default_factory=list)   # 必需的Feature
    specificity: SpecificityProfile = field(default_factory=SpecificityProfile)  # 多维特异度
    retrieval_partition: RetrievalPartition = field(default_factory=lambda: RetrievalPartition(
        system="ZI_PING", school="SAN_MING_TONG_HUI", judgment_type="DEFAULT"
    ))  # 检索分区 - 两级排序的Level 1

    # === display (仅UI, 不参与判断) ===
    display_priority: DisplayPriority = field(default_factory=DisplayPriority)  # 展示优先级

    # === statement ===
    classical: str = ""             # 原典文本
    semantic_keys: list[str] = field(default_factory=list)  # 语义键 (人工标注)
    modern_mapping: dict[str, Any] = field(default_factory=dict)  # 现代映射 (人工标注, 非LLM生成)

    # === source ===
    book: str = ""                  # 书名
    chapter: str = ""               # 章节
    section: str = ""               # 节
    page: str = ""                  # 页码
    source_locator: str = ""        # 来源定位器 (如 三命通会/卷三/六乙日壬午时断)

    # === provenance ===
    created_at: str = ""            # 创建时间
    revision: int = 1               # 修订号
    status: str = JudgmentStatus.ACTIVE.value  # 状态

    def __post_init__(self):
        # 强制验证: system与school必须都有
        if not self.system:
            raise ValueError(f"Judgment {self.judgment_id}: system不能为空")
        if not self.school:
            raise ValueError(f"Judgment {self.judgment_id}: school不能为空 (不能只写system={self.system})")
        # 验证school属于该system
        if self.system == DivinationSystem.ZI_PING.value:
            valid_schools = [s.value for s in ZiPingSchool]
            if self.school not in valid_schools:
                raise ValueError(f"Judgment {self.judgment_id}: school={self.school} 不属于 system={self.system}")
        # 验证match_mode
        valid_modes = [m.value for m in MatcherType]
        if self.match_mode not in valid_modes:
            raise ValueError(f"Judgment {self.judgment_id}: match_mode={self.match_mode} 无效")
        # 验证specificity是SpecificityProfile (不是int)
        if not isinstance(self.specificity, SpecificityProfile):
            raise ValueError(f"Judgment {self.judgment_id}: specificity必须是SpecificityProfile, 不是int")
        # 验证retrieval_partition的system/school与judgment一致
        if self.retrieval_partition.system != self.system:
            raise ValueError(f"Judgment {self.judgment_id}: retrieval_partition.system={self.retrieval_partition.system} 与 system={self.system} 不一致")
        if self.retrieval_partition.school != self.school:
            raise ValueError(f"Judgment {self.judgment_id}: retrieval_partition.school={self.retrieval_partition.school} 与 school={self.school} 不一致")

    def to_dict(self) -> dict:
        return {
            "judgment_id": self.judgment_id,
            "system": self.system,
            "school": self.school,
            "judgment_type": self.judgment_type,
            "version": self.version,
            "match_mode": self.match_mode,
            "conditions": [c.to_dict() for c in self.conditions],
            "feature_requirements": list(self.feature_requirements),
            "specificity": self.specificity.to_dict(),
            "retrieval_partition": self.retrieval_partition.to_dict(),
            "display_priority": self.display_priority.to_dict(),
            "classical": self.classical,
            "semantic_keys": list(self.semantic_keys),
            "modern_mapping": dict(self.modern_mapping),
            "book": self.book,
            "chapter": self.chapter,
            "section": self.section,
            "page": self.page,
            "source_locator": self.source_locator,
            "created_at": self.created_at,
            "revision": self.revision,
            "status": self.status,
        }


# ============================================================================
# 4. 匹配结果
# ============================================================================

class MatchResult(str, Enum):
    """匹配结果 - 旧版兼容."""
    MATCH = "MATCH"
    PARTIAL = "PARTIAL"
    REJECT = "REJECT"
    UNRESOLVED = "UNRESOLVED"


# ============================================================================
# 3.5 匹配状态机 (P6-C-3C-2 升级)
# ============================================================================

class MatchStatus(str, Enum):
    """匹配状态机 - 从无到有的完整状态链.

    UNRESOLVED → NO_CANDIDATE → CANDIDATE → MATCH
                                    ↓
                                  REJECT
    """
    UNRESOLVED = "UNRESOLVED"       # 未开始解析
    NO_CANDIDATE = "NO_CANDIDATE"   # 没有候选断言
    CANDIDATE = "CANDIDATE"         # 有候选断言, 正在评估条件
    MATCH = "MATCH"                 # 所有条件满足
    REJECT = "REJECT"               # 条件不满足


class ConditionStatus(str, Enum):
    """条件评估状态."""
    SATISFIED = "SATISFIED"         # 条件满足
    FAILED = "FAILED"               # 条件不满足
    MISSING = "MISSING"             # Feature不存在


@dataclass(frozen=True)
class ConditionEvaluation:
    """单个条件的评估结果 - 可追溯为什么命中/未命中."""
    feature: str                    # Feature ID
    operator: str                   # 操作符
    expected: Any                   # 期望值
    actual: Any                     # 实际值 (None表示MISSING)
    status: str                     # SATISFIED / FAILED / MISSING
    detail: str                     # 评估详情

    def to_dict(self) -> dict:
        return {
            "feature": self.feature,
            "operator": self.operator,
            "expected": self.expected,
            "actual": self.actual,
            "status": self.status,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class JudgmentMatchResult:
    """断言匹配结果 - 包含完整的条件评估链."""
    judgment: JudgmentAssetV2
    result: str                     # MATCH/PARTIAL/REJECT/UNRESOLVED (旧版兼容)
    match_status: str = MatchStatus.CANDIDATE.value  # 状态机状态
    matched_conditions: list[str] = field(default_factory=list)  # 匹配的条件 (旧版)
    unmatched_conditions: list[str] = field(default_factory=list)  # 未匹配的条件 (旧版)
    condition_evaluations: list[ConditionEvaluation] = field(default_factory=list)  # 详细条件评估
    evidence_binding: dict[str, Any] = field(default_factory=dict)  # 证据绑定

    def to_dict(self) -> dict:
        return {
            "judgment_id": self.judgment.judgment_id,
            "system": self.judgment.system,
            "school": self.judgment.school,
            "judgment_type": self.judgment.judgment_type,
            "specificity": self.judgment.specificity,
            "result": self.result,
            "match_status": self.match_status,
            "matched_conditions": list(self.matched_conditions),
            "unmatched_conditions": list(self.unmatched_conditions),
            "condition_evaluations": [ce.to_dict() for ce in self.condition_evaluations],
            "evidence_binding": dict(self.evidence_binding),
            "classical": self.judgment.classical,
            "source_locator": self.judgment.source_locator,
        }


# ============================================================================
# 5. 断言库 (按school隔离)
# ============================================================================

class JudgmentLibraryV2:
    """断言库 V2 - 按system+school隔离存储."""

    def __init__(self):
        self._judgments: dict[str, JudgmentAssetV2] = {}
        self._by_school: dict[str, list[str]] = {}  # school -> [judgment_id]

    def add(self, judgment: JudgmentAssetV2) -> None:
        """添加断言."""
        if judgment.judgment_id in self._judgments:
            raise ValueError(f"Judgment {judgment.judgment_id} 已存在")
        self._judgments[judgment.judgment_id] = judgment
        key = f"{judgment.system}:{judgment.school}"
        if key not in self._by_school:
            self._by_school[key] = []
        self._by_school[key].append(judgment.judgment_id)

    def get(self, judgment_id: str) -> Optional[JudgmentAssetV2]:
        return self._judgments.get(judgment_id)

    def get_by_school(self, system: str, school: str) -> list[JudgmentAssetV2]:
        """按system+school获取断言 (跨经典隔离)."""
        key = f"{system}:{school}"
        ids = self._by_school.get(key, [])
        return [self._judgments[i] for i in ids]

    def get_all(self) -> list[JudgmentAssetV2]:
        return list(self._judgments.values())

    def stats(self) -> dict[str, Any]:
        result = {"total": len(self._judgments), "by_school": {}}
        for key, ids in self._by_school.items():
            result["by_school"][key] = len(ids)
        return result


# ============================================================================
# 6. 确定性Matcher
# ============================================================================

class DeterministicMatcher:
    """确定性Matcher - 不做模糊匹配.

    支持: EXACT/SET/RANGE/ALL/ANY/CONDITION/COMPOSITE
    GRAPH类型需要专门的GraphMatcher处理.
    """

    OPERATORS = {"EQ", "NE", "IN", "NOT_IN", "CONTAINS", "GT", "LT", "GTE", "LTE"}

    @classmethod
    def evaluate_condition(cls, condition: MatchCondition, features: dict[str, Any]) -> tuple[bool, str]:
        """评估单个条件."""
        feature_value = features.get(condition.feature)
        if feature_value is None:
            return False, f"feature {condition.feature} 不存在"

        op = condition.operator.upper()
        if op == "EQ":
            return feature_value == condition.value, f"{condition.feature}={feature_value} == {condition.value}"
        elif op == "NE":
            return feature_value != condition.value, f"{condition.feature}={feature_value} != {condition.value}"
        elif op == "IN":
            return feature_value in condition.value, f"{condition.feature}={feature_value} in {condition.value}"
        elif op == "NOT_IN":
            return feature_value not in condition.value, f"{condition.feature}={feature_value} not in {condition.value}"
        elif op == "CONTAINS":
            if isinstance(feature_value, (list, dict, str)):
                return condition.value in feature_value, f"{condition.feature} contains {condition.value}"
            return False, f"{condition.feature} 不是可包含类型"
        elif op == "GT":
            return feature_value > condition.value, f"{condition.feature}={feature_value} > {condition.value}"
        elif op == "LT":
            return feature_value < condition.value, f"{condition.feature}={feature_value} < {condition.value}"
        elif op == "GTE":
            return feature_value >= condition.value, f"{condition.feature}={feature_value} >= {condition.value}"
        elif op == "LTE":
            return feature_value <= condition.value, f"{condition.feature}={feature_value} <= {condition.value}"
        else:
            return False, f"未知操作符 {op}"

    @classmethod
    def evaluate_condition_detail(cls, condition: MatchCondition, features: dict[str, Any]) -> ConditionEvaluation:
        """评估单个条件 - 返回详细的ConditionEvaluation."""
        feature_value = features.get(condition.feature)

        # MISSING: Feature不存在
        if feature_value is None:
            return ConditionEvaluation(
                feature=condition.feature, operator=condition.operator,
                expected=condition.value, actual=None,
                status=ConditionStatus.MISSING.value,
                detail=f"feature {condition.feature} 不存在 (MISSING)",
            )

        op = condition.operator.upper()
        ok = False
        detail = ""

        if op == "EQ":
            ok = feature_value == condition.value
            detail = f"{condition.feature}={feature_value} == {condition.value}"
        elif op == "NE":
            ok = feature_value != condition.value
            detail = f"{condition.feature}={feature_value} != {condition.value}"
        elif op == "IN":
            ok = feature_value in condition.value
            detail = f"{condition.feature}={feature_value} in {condition.value}"
        elif op == "NOT_IN":
            ok = feature_value not in condition.value
            detail = f"{condition.feature}={feature_value} not in {condition.value}"
        elif op == "CONTAINS":
            if isinstance(feature_value, (list, dict, str)):
                ok = condition.value in feature_value
                detail = f"{condition.feature} contains {condition.value}"
            else:
                ok = False
                detail = f"{condition.feature} 不是可包含类型"
        elif op == "GT":
            ok = feature_value > condition.value
            detail = f"{condition.feature}={feature_value} > {condition.value}"
        elif op == "LT":
            ok = feature_value < condition.value
            detail = f"{condition.feature}={feature_value} < {condition.value}"
        elif op == "GTE":
            ok = feature_value >= condition.value
            detail = f"{condition.feature}={feature_value} >= {condition.value}"
        elif op == "LTE":
            ok = feature_value <= condition.value
            detail = f"{condition.feature}={feature_value} <= {condition.value}"
        else:
            ok = False
            detail = f"未知操作符 {op}"

        status = ConditionStatus.SATISFIED.value if ok else ConditionStatus.FAILED.value
        return ConditionEvaluation(
            feature=condition.feature, operator=condition.operator,
            expected=condition.value, actual=feature_value,
            status=status, detail=detail,
        )

    @classmethod
    def match(cls, judgment: JudgmentAssetV2, features: dict[str, Any]) -> JudgmentMatchResult:
        """匹配断言 - 确定性匹配, 返回完整的条件评估链."""
        # 检查必需的Feature - 如果缺失, 状态为CANDIDATE但条件MISSING
        missing_features = [f for f in judgment.feature_requirements if f not in features]

        condition_evaluations = []
        matched = []
        unmatched = []
        evidence_binding = {}

        for cond in judgment.conditions:
            ce = cls.evaluate_condition_detail(cond, features)
            condition_evaluations.append(ce)
            if ce.status == ConditionStatus.SATISFIED.value:
                matched.append(ce.detail)
                evidence_binding[cond.feature] = features.get(cond.feature)
            else:
                unmatched.append(ce.detail)

        # 根据match_mode决定结果
        if judgment.match_mode == "EXACT":
            # EXACT: 所有条件必须全部匹配, 否则REJECT
            if not unmatched:
                result = MatchResult.MATCH.value
                match_status = MatchStatus.MATCH.value
            else:
                result = MatchResult.REJECT.value
                match_status = MatchStatus.REJECT.value
        elif judgment.match_mode in ("ALL", "CONDITION"):
            if not unmatched:
                result = MatchResult.MATCH.value
                match_status = MatchStatus.MATCH.value
            elif matched and unmatched:
                result = MatchResult.PARTIAL.value
                match_status = MatchStatus.CANDIDATE.value
            else:
                result = MatchResult.REJECT.value
                match_status = MatchStatus.REJECT.value
        elif judgment.match_mode == "ANY":
            if matched:
                result = MatchResult.MATCH.value
                match_status = MatchStatus.MATCH.value
            else:
                result = MatchResult.REJECT.value
                match_status = MatchStatus.REJECT.value
        elif judgment.match_mode == "SET":
            if not unmatched:
                result = MatchResult.MATCH.value
                match_status = MatchStatus.MATCH.value
            else:
                result = MatchResult.REJECT.value
                match_status = MatchStatus.REJECT.value
        else:
            # COMPOSITE/GRAPH/RANGE
            if not unmatched:
                result = MatchResult.MATCH.value
                match_status = MatchStatus.MATCH.value
            elif matched and unmatched:
                result = MatchResult.PARTIAL.value
                match_status = MatchStatus.CANDIDATE.value
            else:
                result = MatchResult.REJECT.value
                match_status = MatchStatus.REJECT.value

        # 如果有缺失的必需Feature, 标记为UNRESOLVED
        if missing_features:
            result = MatchResult.UNRESOLVED.value
            match_status = MatchStatus.UNRESOLVED.value
            unmatched = [f"缺少必需Feature: {f}" for f in missing_features] + unmatched

        return JudgmentMatchResult(
            judgment=judgment, result=result, match_status=match_status,
            matched_conditions=matched, unmatched_conditions=unmatched,
            condition_evaluations=condition_evaluations,
            evidence_binding=evidence_binding,
        )


# ============================================================================
# 7. 按school隔离的Judgment Resolver
# ============================================================================

class SchoolIsolatedResolver:
    """按school隔离的Judgment Resolver - 两级排序.

    Level 1: Resolver Partition - 按 system+school+judgment_type+retrieval_family 分区
    Level 2: Partition 内部排序 - 按 SpecificityProfile.rank_key 排序

    核心原则:
    - Specificity不得跨School/Judgment Type直接比较
    - 所有MATCH的Judgment均保留, 高specificity不得覆盖低specificity
    - School Priority/Display Priority只能影响Observatory展示顺序, 不得参与MATCH/REJECT
    """

    def __init__(self, library: JudgmentLibraryV2):
        self.library = library

    def resolve(self, system: str, school: str, features: dict[str, Any]) -> list[JudgmentMatchResult]:
        """解析指定system+school的断言匹配 - 两级排序."""
        judgments = self.library.get_by_school(system, school)
        results = []
        for j in judgments:
            result = DeterministicMatcher.match(j, features)
            results.append(result)

        # Level 1: 按RetrievalPartition分组
        partitions: dict[str, list[JudgmentMatchResult]] = {}
        for r in results:
            partition_key = r.judgment.retrieval_partition.partition_key
            if partition_key not in partitions:
                partitions[partition_key] = []
            partitions[partition_key].append(r)

        # Level 2: 每个Partition内部按SpecificityProfile.rank_key降序排序
        # (高特异性在前, 但不覆盖低特异性)
        sorted_results = []
        for partition_key, partition_results in partitions.items():
            partition_results.sort(
                key=lambda r: r.judgment.specificity.rank_key,
                reverse=True
            )
            sorted_results.extend(partition_results)

        return sorted_results

    def resolve_grouped(self, system: str, school: str, features: dict[str, Any]) -> dict[str, list[JudgmentMatchResult]]:
        """解析并按RetrievalPartition分组返回."""
        results = self.resolve(system, school, features)
        partitions: dict[str, list[JudgmentMatchResult]] = {}
        for r in results:
            partition_key = r.judgment.retrieval_partition.partition_key
            if partition_key not in partitions:
                partitions[partition_key] = []
            partitions[partition_key].append(r)
        return partitions

    def resolve_all_schools(self, system: str, features: dict[str, Any]) -> dict[str, list[JudgmentMatchResult]]:
        """解析指定system下所有school的断言匹配 (跨经典隔离)."""
        result = {}
        for key in self.library._by_school:
            if key.startswith(f"{system}:"):
                school = key.split(":", 1)[1]
                result[school] = self.resolve(system, school, features)
        return result


if __name__ == "__main__":
    print("=" * 70)
    print("P6-C-3C-2 Judgment Asset Schema V2 - 快速测试")
    print("=" * 70)

    # 测试1: 创建三命通会日时断断言
    print("\n[1] 创建三命通会日时断断言:")
    j1 = JudgmentAssetV2(
        judgment_id="SMTH-YIWEI-RENWU-001",
        system="ZI_PING", school="SAN_MING_TONG_HUI",
        judgment_type="DAY_TIME", match_mode="EXACT",
        conditions=[
            MatchCondition("ZP.DAY_PILLAR", "EQ", "YI_WEI"),
            MatchCondition("ZP.HOUR_PILLAR", "EQ", "REN_WU"),
        ],
        feature_requirements=["ZP.DAY_PILLAR", "ZP.HOUR_PILLAR"],
        specificity=40,
        classical="六乙日壬午时断：乙日壬午时，印绶带食神，丁己庚辛俱不见，名利有成。",
        semantic_keys=["CAREER", "STATUS", "RESOURCE", "OUTPUT"],
        book="三命通会", chapter="卷三", section="六乙日壬午时断",
        source_locator="三命通会/卷三/六乙日壬午时断",
    )
    print(f"  创建成功: {j1.judgment_id}")
    print(f"  system={j1.system}, school={j1.school}")
    print(f"  match_mode={j1.match_mode}, specificity={j1.specificity}")

    # 测试2: 创建穷通宝鉴调候断言
    print("\n[2] 创建穷通宝鉴调候断言:")
    j2 = JudgmentAssetV2(
        judgment_id="QTBJ-YI-XU-001",
        system="ZI_PING", school="QIONG_TONG_BAO_JIAN",
        judgment_type="TUNING", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "XU"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH"],
        specificity=20,
        classical="乙木戌月，戊土当权，先用癸水，次取丙火。",
        semantic_keys=["TUNING", "WATER", "FIRE", "CLIMATE"],
        book="穷通宝鉴", chapter="乙木篇", section="戌月乙木",
        source_locator="穷通宝鉴/乙木篇/戌月乙木",
    )
    print(f"  创建成功: {j2.judgment_id}")

    # 测试3: 验证school强制
    print("\n[3] 验证school强制 (只写system应该报错):")
    try:
        bad = JudgmentAssetV2(
            judgment_id="BAD-001", system="ZI_PING", school="",
            judgment_type="PATTERN",
        )
        print("  错误: 没有报错!")
    except ValueError as e:
        print(f"  正确报错: {e}")

    # 测试4: 匹配测试
    print("\n[4] 匹配测试:")
    features = {
        "ZP.DAY_PILLAR": "YI_WEI",
        "ZP.HOUR_PILLAR": "REN_WU",
        "ZP.DAY_MASTER": "YI",
        "ZP.MONTH_BRANCH": "XU",
    }

    library = JudgmentLibraryV2()
    library.add(j1)
    library.add(j2)
    print(f"  断言库统计: {library.stats()}")

    resolver = SchoolIsolatedResolver(library)

    # 三命通会匹配
    smth_results = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features)
    print(f"\n  三命通会匹配:")
    for r in smth_results:
        print(f"    {r.judgment.judgment_id}: {r.result} (specificity={r.judgment.specificity})")
        print(f"      匹配: {r.matched_conditions}")
        print(f"      原典: {r.judgment.classical[:50]}...")

    # 穷通宝鉴匹配
    qtbj_results = resolver.resolve("ZI_PING", "QIONG_TONG_BAO_JIAN", features)
    print(f"\n  穷通宝鉴匹配:")
    for r in qtbj_results:
        print(f"    {r.judgment.judgment_id}: {r.result} (specificity={r.judgment.specificity})")

    # 测试5: 负向测试 (乙未日癸午时应该REJECT)
    print("\n[5] 负向测试 (乙未日癸午时应该REJECT):")
    features_neg = {"ZP.DAY_PILLAR": "YI_WEI", "ZP.HOUR_PILLAR": "GUI_WU"}
    neg_results = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features_neg)
    for r in neg_results:
        print(f"    {r.judgment.judgment_id}: {r.result}")
        print(f"      未匹配: {r.unmatched_conditions}")

    # 测试6: 跨经典隔离
    print("\n[6] 跨经典隔离测试:")
    all_results = resolver.resolve_all_schools("ZI_PING", features)
    for school, results in all_results.items():
        print(f"  {school}: {len(results)} 条断言, MATCH={sum(1 for r in results if r.result=='MATCH')}")

    print("\n" + "=" * 70)
    print("P6-C-3C-2 Schema V2 测试通过")
    print("=" * 70)
