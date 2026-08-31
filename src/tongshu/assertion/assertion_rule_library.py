"""
P1.2-B.1 — AssertionRuleLibrary（AuthorizedAssertionRule）

设计原则：
  1. direction 必须由原典授权规则产生，禁止 MappingLayer 自由决定
  2. 规则从 JSON 文件加载，支持热更新
  3. find_rule 根据语义原子和上下文匹配授权规则
  4. 未授权 → NO_ASSERTION（不是 NEUTRAL）
  5. semantic_condition 必须是结构化 MatchStrategy，禁止模糊字符串匹配
"""
from __future__ import annotations

import enum
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..spec.canonical import SemanticAtom, AssertionDirection

logger = logging.getLogger(__name__)


class MatchStrategy(str, enum.Enum):
    """断言规则匹配策略。

    每种策略对应不同的原典推理模式，禁止将 condition 压缩为纯字符串。
    """
    EXACT = "EXACT"             # atom_id 精确匹配
    SET_EXACT = "SET_EXACT"     # semantic_keys 集合精确等于
    SET_SUBSET = "SET_SUBSET"   # semantic_keys 包含全部条件键（minimum 2 keys）
    GRAPH = "GRAPH"             # 多节点关系图匹配（NOT_IMPLEMENTED）
    CONDITION = "CONDITION"     # 综合条件（domain + temporal + attributes）


@dataclass(frozen=True)
class RuleProvenance:
    """规则授权溯源。canonical_source 字符串不足以证明授权，必须有结构化 provenance。"""

    source_work: str                    # 原典作品名（如 "子平真诠"）
    source_chapter: str = ""            # 章节名（如 "论正官"）
    passage_ref: str = ""               # 具体引文位置/段落引用
    verification_status: str = "unverified"  # verified / unverified / candidate
    verified_by: str = ""               # 核验者（人工/Agent ID）
    verification_version: str = ""      # 核验版本

    @classmethod
    def from_dict(cls, d: dict) -> "RuleProvenance":
        return cls(
            source_work=d.get("source_work", ""),
            source_chapter=d.get("source_chapter", ""),
            passage_ref=d.get("passage_ref", ""),
            verification_status=d.get("verification_status", "unverified"),
            verified_by=d.get("verified_by", ""),
            verification_version=d.get("verification_version", ""),
        )


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
    """

    def __init__(self, rules: Optional[List[AssertionRule]] = None):
        self._rules: List[AssertionRule] = rules or []

    def find_rule(
        self, atom: SemanticAtom, context: Optional[dict] = None
    ) -> Optional[AssertionRule]:
        """根据语义原子和上下文匹配授权规则。

        匹配逻辑（按优先级）：
        1. EXACT: atom.atom_id == condition["atom_id"]
        2. SET_EXACT: set(atom.semantic_keys) == set(condition["keys"])
        3. SET_SUBSET: set(condition["keys"]) ⊆ set(atom.semantic_keys)
        4. GRAPH: 子图匹配（condition["nodes"] 全部存在于 atom 上下文）
        5. CONDITION: 综合条件（domain + temporal + attributes）

        Args:
            atom: SemanticAtom 对象
            context: TemporalContext 字典（可选）

        Returns:
            匹配的 AssertionRule；None 表示无授权（调用方应返回 NO_ASSERTION）
        """
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
                    # SET_SUBSET 要求至少 2 个 key，防止单键过度泛化
                    return False
                return required.issubset(set(atom.semantic_keys))

            elif strategy == MatchStrategy.GRAPH:
                # GRAPH: 子图匹配（NOT_IMPLEMENTED —  placeholder）
                # TODO: 实现真正的图结构匹配（节点 + 关系方向 + 关系属性）
                raise NotImplementedError(
                    "MatchStrategy.GRAPH 尚未实现，仅支持 structural key presence"
                )

            elif strategy == MatchStrategy.CONDITION:
                # 综合条件：domain 必须匹配，可选 temporal 和 attributes 过滤
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
        """从 JSON 文件加载规则库。

        JSON 格式：
        {
          "_meta": {"version": "1.0", "description": "..."},
          "rules": [
            {
              "rule_id": "ASR-001",
              "domain": "CAREER",
              "match_strategy": "EXACT",
              "condition": {"atom_id": "TEN_GOD_ZHENG_GUAN"},
              "direction": "supportive",
              "canonical_source": "子平真诠·论正官"
            },
            {
              "rule_id": "ASR-002",
              "domain": "FINANCE",
              "match_strategy": "SET_SUBSET",
              "condition": {"keys": ["OUTPUT_ACTIVATION", "WEALTH_FLOW"]},
              "direction": "caution",
              "canonical_source": "滴天髓·食神章"
            }
          ]
        }
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
            provenance = RuleProvenance(
                source_work=prov_dict.get("source_work", rule_dict.get("canonical_source", "")),
                source_chapter=prov_dict.get("source_chapter", ""),
                passage_ref=prov_dict.get("passage_ref", ""),
                verification_status=prov_dict.get("verification_status", "unverified"),
                verified_by=prov_dict.get("verified_by", ""),
                verification_version=prov_dict.get("verification_version", ""),
            )
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
