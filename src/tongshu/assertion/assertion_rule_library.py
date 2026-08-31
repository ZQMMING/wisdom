"""
P1.2-A — AssertionRuleLibrary（AuthorizedAssertionRule）

设计原则：
  1. direction 必须由原典授权规则产生，禁止 MappingLayer 自由决定
  2. 规则从 JSON 文件加载，支持热更新
  3. find_rule 根据语义原子和上下文匹配授权规则
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from ..spec.canonical import SemanticAtom, AssertionDirection

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AssertionRule:
    """授权断言规则：决定 domain + direction 的原典授权。

    direction 由此层授权产生，禁止其他层自由推断。
    """

    rule_id: str
    domain: str
    semantic_condition: str  # 匹配的语义键条件（atom_id 或 semantic_keys 子集）
    direction: AssertionDirection
    canonical_source: str  # 原典引用（如 "子平真诠·论用神"）


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

        匹配逻辑（优先级从高到低）：
        1. 精确匹配：atom.atom_id == rule.semantic_condition
        2. 子集匹配：semantic_condition 是 semantic_keys 的子集
        3. 通配符匹配：rule.domain == atom.domain_candidates 中的任意一个

        Args:
            atom: SemanticAtom 对象
            context: TemporalContext 字典（可选，包含 case_id、temporal_scope 等）

        Returns:
            匹配的 AssertionRule，未找到时返回 None（此时 direction 由调用方决定为 NEUTRAL）
        """
        context = context or {}

        for rule in self._rules:
            # 领域匹配
            if rule.domain not in atom.domain_candidates and rule.domain != "*":
                continue

            # 语义条件匹配
            condition = rule.semantic_condition
            atom_keys = set(atom.semantic_keys)
            atom_id = atom.atom_id

            if condition in atom_keys or condition == atom_id:
                return rule

            # 检查 semantic_condition 是否为 atom_keys 的子集
            if set(condition.split(",")).issubset(atom_keys):
                return rule

        return None

    def list_rules(self) -> List[AssertionRule]:
        """列出所有规则。"""
        return list(self._rules)

    @staticmethod
    def load(path: str) -> "AssertionRuleLibrary":
        """从 JSON 文件加载规则库。

        Args:
            path: JSON 文件路径

        Returns:
            AssertionRuleLibrary 实例

        JSON 格式：
        {
          "_meta": {"version": "1.0", "description": "..."},
          "rules": [
            {
              "rule_id": "ASR-001",
              "domain": "CAREER",
              "semantic_condition": "TEN_GOD_ZHENG_GUAN",
              "direction": "supportive",
              "canonical_source": "子平真诠·论正官"
            },
            ...
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
            rules.append(
                AssertionRule(
                    rule_id=rule_dict["rule_id"],
                    domain=rule_dict["domain"],
                    semantic_condition=rule_dict["semantic_condition"],
                    direction=AssertionDirection(rule_dict["direction"]),
                    canonical_source=rule_dict.get("canonical_source", ""),
                )
            )

        logger.info("AssertionRuleLibrary: loaded %d rules from %s", len(rules), path)
        return AssertionRuleLibrary(rules)
