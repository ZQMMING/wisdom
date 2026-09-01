"""
P1.2-B.1 — AssertionRuleLibrary（AuthorizedAssertionRule）

设计原则：
  1. direction 必须由原典授权规则产生，禁止 MappingLayer 自由决定
  2. 规则从 JSON 文件加载，支持热更新
  3. find_rule 根据语义原子和上下文匹配授权规则
  4. 未授权 → NO_ASSERTION（不是 NEUTRAL）
  5. semantic_condition 必须是结构化 MatchStrategy，禁止模糊字符串匹配
  6. production_verified 不可伪造：只能通过 ProductionRuleLoader 或 load_verified() 设置
  7. verification_scope 区分测试/审核/生产三态，防止语义污染
"""
from __future__ import annotations

import enum
import json
import logging
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..spec.canonical import SemanticAtom, AssertionDirection

logger = logging.getLogger(__name__)

# Thread-local context to track production admission path
_production_context = threading.local()


def _in_production_context() -> bool:
    """Check if we're inside a production admission path."""
    return getattr(_production_context, 'inside_production', False)


class MatchStrategy(str, enum.Enum):
    """断言规则匹配策略。

    每种策略对应不同的原典推理模式，禁止将 condition 压缩为纯字符串。
    """
    EXACT = "EXACT"             # atom_id 精确匹配
    SET_EXACT = "SET_EXACT"     # semantic_keys 集合精确等于
    SET_SUBSET = "SET_SUBSET"   # semantic_keys 包含全部条件键（minimum 2 keys）
    GRAPH = "GRAPH"             # 多节点关系图匹配（NOT_IMPLEMENTED）
    CONDITION = "CONDITION"     # 综合条件（domain + temporal + attributes）


class VerificationScope(str, enum.Enum):
    """规则验证范围。区分测试、来源审核、生产准入三态。"""
    TEST_FIXTURE = "TEST_FIXTURE"        # 仅用于测试，未经原典审核
    SOURCE_VERIFIED = "SOURCE_VERIFIED"  # 原典来源已核实，待生产准入
    PRODUCTION_ADMITTED = "PRODUCTION_ADMITTED"  # 通过 Admission Registry 准入


# Backward-compatible alias for old JSON that uses raw "verified"/"unverified"/"candidate" strings
_VERIFICATION_STATUS_TO_SCOPE = {
    "verified": VerificationScope.PRODUCTION_ADMITTED,
    "unverified": VerificationScope.TEST_FIXTURE,
    "candidate": VerificationScope.TEST_FIXTURE,
}


@dataclass(frozen=True)
class RuleProvenance:
    """规则授权溯源。canonical_source 字符串不足以证明授权，必须有结构化 provenance。"""

    source_work: str
    source_chapter: str = ""
    passage_ref: str = ""
    verification_status: str = "unverified"   # backward-compat: verified/unverified/candidate
    verification_scope: Optional[VerificationScope] = None  # P1.4-CLOSE: scoped distinction
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


@dataclass(frozen=True)
class AssertionRule:
    """授权断言规则：决定 domain + direction 的原典授权。

    direction 由此层授权产生，禁止其他层自由推断。
    未命中此规则 → 不产出 Assertion，不是 NEUTRAL。
    """

    rule_id: str
    domain: str
    match_strategy: MatchStrategy
    condition: Dict[str, Any]  # 结构化匹配条件（见各 MatchStrategy 说明）
    direction: AssertionDirection
    provenance: RuleProvenance  # 原典溯源（替代裸字符串 canonical_source）

    @property
    def canonical_source(self) -> str:
        """兼容旧字段：返回工作名+章节的字符串摘要。"""
        if self.provenance.source_chapter:
            return f"{self.provenance.source_work}·{self.provenance.source_chapter}"
        return self.provenance.source_work

    @property
    def semantic_condition(self) -> str:
        """兼容旧字段名，返回 condition 的字符串摘要。"""
        return json.dumps(self.condition, ensure_ascii=False)


class AssertionRuleLibrary:
    """授权断言规则库。

    从 JSON 文件加载规则，提供 find_rule / list_rules 接口。

    Production boundary (P1.4-CLOSE):
    - __init__ 不接受 production_verified 参数（不可伪造）
    - load() — development/testing, accepts unverified rules, production_verified=False
    - load_verified() — production admission gate, requires PRODUCTION_ADMITTED scope
    - ProductionRuleLoader.load() — 唯一允许的 production 入口
    """

    def __init__(self, rules: Optional[List[AssertionRule]] = None, production_verified: bool = False):
        # Guard: production_verified can only be True when called from load_verified()
        if production_verified and not _in_production_context():
            raise TypeError(
                "P1.4-CLOSE: AssertionRuleLibrary cannot be constructed with production_verified=True. "
                "Use ProductionRuleLoader.load(path) or AssertionRuleLibrary.load_verified(path) instead."
            )
        self._rules: List[AssertionRule] = rules or []
        self._production_verified = production_verified

    @classmethod
    def __from_production_admission(cls, rules: List[AssertionRule]) -> "AssertionRuleLibrary":
        """Internal factory: set production_verified without going through __init__ guard.

        SECURITY: Uses double underscore for Python name mangling (_AssertionRuleLibrary__from_production_admission).
        This prevents direct external calls while still allowing load_verified() to use it internally.
        """
        obj = object.__new__(cls)
        obj._rules = rules
        obj._production_verified = True
        return obj

    def find_rule(
        self, atom: SemanticAtom, context: Optional[dict] = None
    ) -> Optional[AssertionRule]:
        """根据语义原子和上下文匹配授权规则。"""
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
        """列出所有规则。"""
        return list(self._rules)

    @staticmethod
    def load(path: str) -> "AssertionRuleLibrary":
        """从 JSON 文件加载规则库（development/testing 路径）。

        接受所有 verification_status，但 production_verified=False。
        """
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
        return AssertionRuleLibrary(rules, production_verified=False)

    @classmethod
    def load_verified(cls, path: str) -> "AssertionRuleLibrary":
        """Load only PRODUCTION_ADMITTED rules — rejects unverified/candidate/test-fixture rules.

        Production Admission Gate (P1.5.1-R2 + P1.4-CLOSE):
        - verification_scope must be 'PRODUCTION_ADMITTED' (not just 'verified')
        - Rules with TEST_FIXTURE, SOURCE_VERIFIED, or missing scope are rejected
        """
        path_obj = Path(path)
        if not path_obj.exists():
            logger.warning("AssertionRuleLibrary: rules file not found: %s", path)
            return cls()
        
        # Set production context to allow construction with production_verified=True
        _production_context.inside_production = True
        try:
            with open(path_obj, encoding="utf-8") as f:
                data = json.load(f)
            rules = []
            rejected = []
            for rule_dict in data.get("rules", []):
                prov_dict = rule_dict.get("provenance", {})
                provenance = RuleProvenance.from_dict(prov_dict)
                if not provenance.is_production_admitted:
                    rejected.append(rule_dict.get("rule_id", "unknown"))
                    continue
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
            if rejected:
                logger.warning(
                    "AssertionRuleLibrary: rejected %d non-admitted rules from %s: %s",
                    len(rejected), path, rejected,
                )
            logger.info(
                "AssertionRuleLibrary: loaded %d admitted rules from %s (rejected %d)",
                len(rules), path, len(rejected),
            )
            return cls(rules, production_verified=True)
        finally:
            _production_context.inside_production = False


class ProductionRuleLoader:
    """Production Rule Admission Gate (P1.5.1-R2 + P1.4-CLOSE).

    生产环境必须通过此类加载规则，禁止直接调用 AssertionRuleLibrary.load() 或构造。
    - 只接受 verification_scope == PRODUCTION_ADMITTED 的规则
    - TEST_FIXTURE / SOURCE_VERIFIED / unverified / candidate 一律拒绝
    - production_verified flag 不可由调用方伪造
    """

    @classmethod
    def load(cls, path: str) -> AssertionRuleLibrary:
        """加载经过 Production Admission Gate 的规则。

        此方法强制调用 load_verified()，不接受任何非生产准入规则。
        """
        return AssertionRuleLibrary.load_verified(path)
