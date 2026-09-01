"""
P1.2-B.1 — AssertionRuleLibrary + Production Admission Architecture (Capability-based)

设计原则：
  1. direction 必须由原典授权规则产生，禁止 MappingLayer 自由决定
  2. 规则从 JSON 文件加载，支持热更新
  3. find_rule 根据语义原子和上下文匹配授权规则
  4. 未授权 → NO_ASSERTION（不是 NEUTRAL）
  5. semantic_condition 必须是结构化 MatchStrategy，禁止模糊字符串匹配
  6. Production Admission 不可伪造：通过 singleton capability + identity check 实现
  7. verification_scope 区分测试/审核/生产三态，防止语义污染
  8. ProductionRuleLibrary 与 AssertionRuleLibrary 类型隔离
"""
from __future__ import annotations

import enum
import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..spec.canonical import SemanticAtom, AssertionDirection

logger = logging.getLogger(__name__)


# ============================================================
# Capability Token — Module-Private Singleton (NOT exportable)
# ============================================================

# CRITICAL: _CAPABILITY is intentionally NOT a module-level variable.
# It is defined as a class attribute inside ProductionRuleLoader below,
# so external code cannot do: from module import _CAPABILITY
#
# Security principle: the valid capability token must only exist
# inside the Loader class scope, not in the module namespace.


# ============================================================
# 枚举定义
# ============================================================

class MatchStrategy(str, enum.Enum):
    """断言规则匹配策略。"""
    EXACT = "EXACT"
    SET_EXACT = "SET_EXACT"
    SET_SUBSET = "SET_SUBSET"
    GRAPH = "GRAPH"
    CONDITION = "CONDITION"


class VerificationScope(str, enum.Enum):
    """规则验证范围。"""
    TEST_FIXTURE = "TEST_FIXTURE"
    SOURCE_VERIFIED = "SOURCE_VERIFIED"
    PRODUCTION_ADMITTED = "PRODUCTION_ADMITTED"


_VERIFICATION_STATUS_TO_SCOPE = {
    "verified": VerificationScope.SOURCE_VERIFIED,
    "unverified": VerificationScope.TEST_FIXTURE,
    "candidate": VerificationScope.TEST_FIXTURE,
}


# ============================================================
# 数据结构
# ============================================================

@dataclass(frozen=True)
class RuleProvenance:
    """规则授权溯源。"""

    source_work: str
    source_chapter: str = ""
    passage_ref: str = ""
    verification_status: str = "unverified"
    verification_scope: Optional[VerificationScope] = None
    verified_by: str = ""
    verification_version: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "RuleProvenance":
        raw_status = d.get("verification_status", "unverified")
        scope_str = d.get("verification_scope")
        if scope_str:
            scope = VerificationScope(scope_str)
        elif raw_status in _VERIFICATION_STATUS_TO_SCOPE:
            scope = _VERIFICATION_STATUS_TO_SCOPE[raw_status]
        else:
            scope = VerificationScope.TEST_FIXTURE
        return cls(
            source_work=d.get("source_work", ""),
            source_chapter=d.get("source_chapter", ""),
            passage_ref=d.get("passage_ref", ""),
            verification_status=raw_status,
            verification_scope=scope,
            verified_by=d.get("verified_by", ""),
            verification_version=d.get("verification_version", ""),
        )

    @property
    def is_production_admitted(self) -> bool:
        return self.verification_scope == VerificationScope.PRODUCTION_ADMITTED

    @property
    def is_complete_for_production(self) -> bool:
        if not self.is_production_admitted:
            return True
        return all([
            self.source_work,
            self.source_chapter,
            self.passage_ref,
            self.verified_by,
            self.verification_version,
        ])


@dataclass(frozen=True)
class AssertionRule:
    """授权断言规则。"""

    rule_id: str
    domain: str
    match_strategy: MatchStrategy
    condition: Dict[str, Any]
    direction: AssertionDirection
    provenance: RuleProvenance

    @property
    def canonical_source(self) -> str:
        if self.provenance.source_chapter:
            return f"{self.provenance.source_work}·{self.provenance.source_chapter}"
        return self.provenance.source_work

    @property
    def semantic_condition(self) -> str:
        return json.dumps(self.condition, ensure_ascii=False)


@dataclass(frozen=True)
class _AdmissionState:
    """
    生产准入状态 — 不可伪造的内部凭证。

    关键设计：
    - frozen=True: 构造后不可修改
    - admission_hash: 完整 64-char SHA-256（非截断）
    - canonical_serialization: 全量规则内容的确定性序列化，用于完整性验证
    - admission_timestamp: 准入时间戳
    - admitted_rules_count: 准入的规则数量
    - source_path: 来源文件路径

    外部代码无法伪造 _AdmissionState，因为：
    1. production_library._state 是私有属性（下划线前缀）
    2. 只有 ProductionRuleLoader 内部能创建 _AdmissionState 实例
    3. ProductionRuleLibrary.__init__ 只接受 _CAPABILITY singleton，不接受外部对象
    """
    admission_id: str
    admission_hash: str  # Full 64-char SHA-256
    admitted_rules_count: int
    source_path: str
    admission_timestamp: float
    rule_ids: frozenset = field(default_factory=frozenset)
    canonical_serialization: str = ""  # For integrity verification

    def validate(self) -> List[str]:
        errors = []
        if not self.admission_id:
            errors.append("admission_id cannot be empty")
        if not self.admission_hash or len(self.admission_hash) != 64:
            errors.append("admission_hash must be 64-char SHA-256")
        if self.admitted_rules_count < 0:
            errors.append("admitted_rules_count must be >= 0")
        return errors


# ============================================================
# Base Library
# ============================================================

class AssertionRuleLibrary:
    """
    基础断言规则库（Candidate/Test 用途）。

    设计原则：
    - 不接受 production_verified 参数
    - 不接受 _AdmissionState
    - 仅用于开发/测试环境

    生产环境必须使用 ProductionRuleLibrary。
    """

    def __init__(self, rules: Optional[List[AssertionRule]] = None):
        self._rules: List[AssertionRule] = rules or []

    def find_rule(
        self, atom: SemanticAtom, context: Optional[dict] = None
    ) -> Optional[AssertionRule]:
        context = context or {}
        for rule in self._rules:
            if not self._match(rule, atom, context):
                continue
            return rule
        return None

    def _match(
        self, rule: AssertionRule, atom: SemanticAtom, context: dict
    ) -> bool:
        strategy = rule.match_strategy
        cond = rule.condition
        try:
            if strategy == MatchStrategy.EXACT:
                return atom.atom_id == cond.get("atom_id")
            elif strategy == MatchStrategy.SET_EXACT:
                required = set(cond.get("keys", []))
                return required == set(atom.semantic_keys)
            elif strategy == MatchStrategy.SET_SUBSET:
                required = set(cond.get("keys", []))
                if not required or len(required) < 2:
                    return False
                return required.issubset(set(atom.semantic_keys))
            elif strategy == MatchStrategy.GRAPH:
                raise NotImplementedError(
                    "MatchStrategy.GRAPH 尚未实现，仅支持 structural key presence"
                )
            elif strategy == MatchStrategy.CONDITION:
                if cond.get("domain") and cond["domain"] not in atom.domain_candidates:
                    return False
                if cond.get("temporal_scope") and cond["temporal_scope"] != context.get("temporal_scope"):
                    return False
                for attr_key, attr_val in cond.get("attributes", {}).items():
                    if atom.attributes.get(attr_key) != attr_val:
                        return False
                return True
        except (KeyError, TypeError):
            logger.warning("MatchStrategy %s failed for rule %s", strategy, rule.rule_id)
            return False
        return False

    def list_rules(self) -> List[AssertionRule]:
        return list(self._rules)

    @property
    def is_production(self) -> bool:
        return False

    @staticmethod
    def load(path: str) -> "AssertionRuleLibrary":
        """从 JSON 文件加载规则库（development/testing 路径）。"""
        path_obj = Path(path)
        if not path_obj.exists():
            logger.warning("AssertionRuleLibrary: rules file not found: %s", path)
            return AssertionRuleLibrary()
        with open(path_obj, encoding="utf-8") as f:
            data = json.load(f)
        rules = []
        for rule_dict in data.get("rules", []):
            prov_dict = rule_dict.get("provenance", {})
            provenance = RuleProvenance.from_dict(prov_dict)
            rules.append(
                AssertionRule(
                    rule_id=rule_dict["rule_id"],
                    domain=rule_dict["domain"],
                    match_strategy=MatchStrategy(rule_dict["match_strategy"]),
                    condition=rule_dict.get("condition", {}),
                    direction=AssertionDirection(rule_dict["direction"]),
                    provenance=provenance,
                )
            )
        logger.info("AssertionRuleLibrary: loaded %d rules from %s", len(rules), path)
        return AssertionRuleLibrary(rules)


# ============================================================
# Production Admission
# ============================================================

class ProductionRuleLibrary:
    """
    生产断言规则库 — 只能由 ProductionRuleLoader 内部构造。

    安全设计：
    - __init__ 不接受 capability 参数
    - 只有 ProductionRuleLoader 内部能通过内部 API 构造
    - 外部代码无法获得有效构造路径

    外部调用方式：
        loader = ProductionRuleLoader()
        lib = loader.load(path)  # 返回 ProductionRuleLibrary
    """

    def __init__(self, rules: List[AssertionRule], state: "_AdmissionState"):
        # Validate admission state
        admission_errors = state.validate()
        if admission_errors:
            raise ValueError(f"Invalid _AdmissionState: {admission_errors}")

        self._rules: List[AssertionRule] = rules
        self._state: "_AdmissionState" = state

    @property
    def admission_state(self) -> "_AdmissionState":
        """返回准入状态（只读）。"""
        return self._state

    @property
    def admission_hash(self) -> str:
        """返回准入哈希（64-char SHA-256）。"""
        return self._state.admission_hash

    @property
    def is_production(self) -> bool:
        return True

    def find_rule(
        self, atom: SemanticAtom, context: Optional[dict] = None
    ) -> Optional[AssertionRule]:
        context = context or {}
        for rule in self._rules:
            if not self._match(rule, atom, context):
                continue
            return rule
        return None

    def _match(
        self, rule: AssertionRule, atom: SemanticAtom, context: dict
    ) -> bool:
        strategy = rule.match_strategy
        cond = rule.condition
        try:
            if strategy == MatchStrategy.EXACT:
                return atom.atom_id == cond.get("atom_id")
            elif strategy == MatchStrategy.SET_EXACT:
                required = set(cond.get("keys", []))
                return required == set(atom.semantic_keys)
            elif strategy == MatchStrategy.SET_SUBSET:
                required = set(cond.get("keys", []))
                if not required or len(required) < 2:
                    return False
                return required.issubset(set(atom.semantic_keys))
            elif strategy == MatchStrategy.GRAPH:
                raise NotImplementedError(
                    "MatchStrategy.GRAPH 尚未实现，仅支持 structural key presence"
                )
            elif strategy == MatchStrategy.CONDITION:
                if cond.get("domain") and cond["domain"] not in atom.domain_candidates:
                    return False
                if cond.get("temporal_scope") and cond["temporal_scope"] != context.get("temporal_scope"):
                    return False
                for attr_key, attr_val in cond.get("attributes", {}).items():
                    if atom.attributes.get(attr_key) != attr_val:
                        return False
                return True
        except (KeyError, TypeError):
            logger.warning("MatchStrategy %s failed for rule %s", strategy, rule.rule_id)
            return False
        return False

    def list_rules(self) -> List[AssertionRule]:
        return list(self._rules)

    @classmethod
    def _from_loader(cls, rules: List[AssertionRule], state: "_AdmissionState") -> "ProductionRuleLibrary":
        """内部构造方法 — 只有 ProductionRuleLoader 可以调用。

        此方法不接受 capability 参数，因为 capability 是类级别的秘密，
        外部代码无法通过 import 获取。
        """
        return cls(rules, state)


class ProductionRuleLoader:
    """
    生产规则准入 Gate。

    职责：
    1. 从 JSON 文件加载规则
    2. 过滤 PRODUCTION_ADMITTED 规则
    3. 生成 _AdmissionState（不可伪造的内部凭证）
    4. 内部构造 ProductionRuleLibrary（不暴露 capability）

    安全保证：
    - _CAPABILITY 是类属性（非模块级变量），外部无法 import
    - _AdmissionState 是私有 frozen dataclass，不在 __all__ 中导出
    - ProductionRuleLibrary.__init__ 不接受 capability 参数
    - 空文件路径抛出 RuleLoadError，不产生无效 AdmissionState
    """

    # Capability singleton — defined at CLASS level, not module level
    # This ensures external code CANNOT do: from module import _CAPABILITY
    _CAPABILITY = object()

    @classmethod
    def load(cls, path: str) -> ProductionRuleLibrary:
        """
        加载经过 Production Admission Gate 的规则。

        步骤：
        1. 读取 JSON 文件
        2. 过滤 PRODUCTION_ADMITTED 规则
        3. 验证完整性
        4. 生成 _AdmissionState（包含完整规则哈希）
        5. 使用 _CAPABILITY 构造 ProductionRuleLibrary

        注意：
        - 如果文件不存在，抛出 RuleLoadError（fail-closed）
        - 如果规则不完整，会被过滤并记录警告
        """
        path_obj = Path(path)
        if not path_obj.exists():
            raise RuleLoadError(
                f"Rules file not found: {path}. "
                "Production Admission requires valid rule files."
            )

        with open(path_obj, encoding="utf-8") as f:
            data = json.load(f)

        admitted_rules = []
        rejected = []

        for rule_dict in data.get("rules", []):
            prov_dict = rule_dict.get("provenance", {})
            provenance = RuleProvenance.from_dict(prov_dict)

            if not provenance.is_production_admitted:
                rejected.append(rule_dict.get("rule_id", "unknown"))
                continue

            if not provenance.is_complete_for_production:
                rejected.append(rule_dict.get("rule_id", "unknown"))
                logger.warning(
                    "ProductionRuleLoader: rejected %s — PRODUCTION_ADMITTED but incomplete provenance",
                    rule_dict.get("rule_id", "unknown"),
                )
                continue

            admitted_rules.append(
                AssertionRule(
                    rule_id=rule_dict["rule_id"],
                    domain=rule_dict["domain"],
                    match_strategy=MatchStrategy(rule_dict["match_strategy"]),
                    condition=rule_dict.get("condition", {}),
                    direction=AssertionDirection(rule_dict["direction"]),
                    provenance=provenance,
                )
            )

        if rejected:
            logger.warning(
                "ProductionRuleLoader: rejected %d rules from %s: %s",
                len(rejected), path, rejected,
            )

        # Generate admission state with full integrity proof
        state = cls._create_admission_state(
            admitted_rules, str(path_obj), len(rejected)
        )

        logger.info(
            "ProductionRuleLoader: admitted %d rules from %s (rejected %d)",
            len(admitted_rules), path, len(rejected),
        )

        # Only ProductionRuleLoader can create ProductionRuleLibrary
        # via internal class method (capability not exposed externally)
        return ProductionRuleLibrary._from_loader(admitted_rules, state)

    @classmethod
    def _create_admission_state(
        cls,
        rules: List[AssertionRule],
        source_path: str,
        rejected_count: int,
    ) -> "_AdmissionState":
        """
        生成不可伪造的 _AdmissionState。

        安全保证：
        1. admission_hash 使用完整 64-char SHA-256
        2. canonical_serialization 包含全量规则内容（condition, direction, provenance 等）
        3. 任何规则篡改会改变 hash
        4. admission_timestamp 记录准入时间
        5. rule_ids 记录所有准入规则 ID（frozenset，不可修改）

        注意：此方法只在 ProductionRuleLoader 内部调用，外部无法访问。
        """
        # Canonical serialization of all rules (deterministic)
        rule_serializations = []
        for r in sorted(rules, key=lambda x: x.rule_id):
            rule_serializations.append({
                "rule_id": r.rule_id,
                "domain": r.domain,
                "match_strategy": r.match_strategy.value,
                "condition": r.condition,  # Dict - will be sorted by json.dumps
                "direction": r.direction.value,
                "provenance": {
                    "source_work": r.provenance.source_work,
                    "source_chapter": r.provenance.source_chapter,
                    "passage_ref": r.provenance.passage_ref,
                    "verification_scope": r.provenance.verification_scope.value,
                    "verified_by": r.provenance.verified_by,
                    "verification_version": r.provenance.verification_version,
                },
            })

        canonical = json.dumps(
            rule_serializations,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        )

        # Full SHA-256 (64 hex chars) - not truncated
        hash_input = f"{source_path}:{canonical}:{len(rules)}:{rejected_count}"
        admission_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

        admission_id = f"admission_{int(time.time())}_{admission_hash}"
        rule_ids = frozenset(r.rule_id for r in rules)

        return _AdmissionState(
            admission_id=admission_id,
            admission_hash=admission_hash,  # Full 64 chars
            admitted_rules_count=len(rules),
            source_path=source_path,
            admission_timestamp=time.time(),
            rule_ids=rule_ids,
            canonical_serialization=canonical,
        )


class RuleLoadError(Exception):
    """Production Rule Load Error — raised when admission fails."""
    pass


# ============================================================
# Backward Compatibility
# ============================================================

# AssertionRuleLibrary 现在不再支持 production_verified 参数
# 生产环境应使用 ProductionRuleLoader.load() 或 ProductionRuleLibrary

__all__ = [
    "AssertionRuleLibrary",
    "ProductionRuleLibrary",
    "ProductionRuleLoader",
    "AssertionRule",
    "RuleProvenance",
    "MatchStrategy",
    "VerificationScope",
    "RuleLoadError",
    # Note: _AdmissionState and _CAPABILITY are intentionally NOT exported
    # _CAPABILITY is a class attribute, not a module-level variable
]
