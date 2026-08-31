"""
P1.2-A — JudgmentRuleLibrary（AuthorizedJudgmentRule）

设计原则：
  1. Judgment 必须由原典授权规则产生，禁止"聚合即判断"
  2. EvidenceCoverage 只做结构性组织，不产生 Judgment
  3. 规则从 JSON 文件加载，支持热更新
  4. find_judgment 根据 EvidenceCoverage 匹配授权规则
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from ..spec.canonical import EvidenceCoverage

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class JudgmentRule:
    """授权判断规则：决定何时 EvidenceCoverage 升级为 Judgment。

    authorized_by 字段即为 Judgment.authorized_by 的值。
    """

    rule_id: str
    domain: str
    semantic: str
    required_evidence_count: int  # 最少证据数量阈值
    canonical_source: str  # 原典引用（如 "滴天髓·合婚章"）


class JudgmentRuleLibrary:
    """授权判断规则库。

    从 JSON 文件加载规则，提供 find_judgment / list_rules 接口。
    """

    def __init__(self, rules: Optional[List[JudgmentRule]] = None):
        self._rules: List[JudgmentRule] = rules or []

    def find_judgment(self, coverage: EvidenceCoverage) -> Optional[JudgmentRule]:
        """根据 EvidenceCoverage 匹配授权规则。

        匹配逻辑：
        1. domain 和 semantic 精确匹配
        2. evidence_count >= required_evidence_count

        Args:
            coverage: EvidenceCoverage 对象

        Returns:
            匹配的 JudgmentRule，未找到时返回 None
        """
        for rule in self._rules:
            if rule.domain != coverage.domain:
                continue
            if rule.semantic != coverage.semantic:
                continue
            if coverage.evidence_count < rule.required_evidence_count:
                continue
            return rule
        return None

    def list_rules(self) -> List[JudgmentRule]:
        """列出所有规则。"""
        return list(self._rules)

    @staticmethod
    def load(path: str) -> "JudgmentRuleLibrary":
        """从 JSON 文件加载规则库。

        Args:
            path: JSON 文件路径

        Returns:
            JudgmentRuleLibrary 实例

        JSON 格式：
        {
          "_meta": {"version": "1.0", "description": "..."},
          "rules": [
            {
              "rule_id": "JUD-001",
              "domain": "CAREER",
              "semantic": "OUTPUT_ACTIVATION",
              "required_evidence_count": 2,
              "canonical_source": "滴天髓·官煞章"
            },
            ...
          ]
        }
        """
        path_obj = Path(path)
        if not path_obj.exists():
            logger.warning("JudgmentRuleLibrary: rules file not found: %s", path)
            return JudgmentRuleLibrary()

        with open(path_obj, encoding="utf-8") as f:
            data = json.load(f)

        rules = []
        for rule_dict in data.get("rules", []):
            rules.append(
                JudgmentRule(
                    rule_id=rule_dict["rule_id"],
                    domain=rule_dict["domain"],
                    semantic=rule_dict["semantic"],
                    required_evidence_count=rule_dict["required_evidence_count"],
                    canonical_source=rule_dict.get("canonical_source", ""),
                )
            )

        logger.info("JudgmentRuleLibrary: loaded %d rules from %s", len(rules), path)
        return JudgmentRuleLibrary(rules)
