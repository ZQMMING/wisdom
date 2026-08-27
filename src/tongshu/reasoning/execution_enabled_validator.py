"""B-6 硬规则执行器：execution_enabled 链完整性校验。

根据 Spec Owner 2026-08-21 裁定：

    IF execution_enabled=true
    THEN 必须存在:
        rule_id
          ↓
        semantic_mapping (rule_refs 指向 mapping)
          ↓
        concept (mapping 指向 concept)
          ↓
        evidence/source (concept 指向 passage/book)

    否则:
        自动降级: execution_enabled=false, status=pending

此校验在 RuleLoader.load() 时自动执行，作为加载的前置条件。
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class RuleChainResult:
    """单条规则的链校验结果。"""
    rule_id: str
    execution_enabled: bool
    chain_valid: bool
    violations: list[str] = field(default_factory=list)
    degraded: bool = False  # 是否被自动降级


@dataclass(frozen=True)
class ChainViolation:
    """具体违规信息。"""
    rule_id: str
    level: str  # 'rule' | 'mapping' | 'concept' | 'evidence'
    detail: str


class ExecutionEnabledValidator:
    """B-6 硬规则校验器。

    校验逻辑:
    1. rule.execution_enabled=true → 必须有 rule_refs（指向semantic_mapping）
    2. mapping 必须存在 → 必须有 concept_id
    3. concept 必须存在 → 必须有 source_refs（指向 passage/book/evidence）
    4. evidence 必须存在且 source_layer != null
    """

    def __init__(
        self,
        rules_dir: Path,
        mappings_dir: Path,
        concepts_dir: Path,
        evidence_dir: Path,
    ):
        self.rules_dir = rules_dir
        self.mappings_dir = mappings_dir
        self.concepts_dir = concepts_dir
        self.evidence_dir = evidence_dir

        # 预加载索引
        self._mappings: dict[str, dict] = {}
        self._concepts: dict[str, dict] = {}
        self._evidence: dict[str, dict] = {}
        self._load_indices()

    def _load_indices(self) -> None:
        """加载 mappings/concepts/evidence 到内存索引。"""
        for f in self.mappings_dir.glob("*.json"):
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for item in data:
                    mid = item.get("mapping_id") or item.get("id")
                    if mid:
                        self._mappings[mid] = item
            elif isinstance(data, dict):
                mid = data.get("mapping_id") or data.get("id")
                if mid:
                    self._mappings[mid] = data

        for f in self.concepts_dir.glob("*.json"):
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for item in data:
                    cid = item.get("concept_id") or item.get("id")
                    if cid:
                        self._concepts[cid] = item
            elif isinstance(data, dict):
                cid = data.get("concept_id") or data.get("id")
                if cid:
                    self._concepts[cid] = data

        for f in self.evidence_dir.glob("*.json"):
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for item in data:
                    eid = item.get("evidence_id") or item.get("id")
                    if eid:
                        self._evidence[eid] = item
            elif isinstance(data, dict):
                eid = data.get("evidence_id") or data.get("id")
                if eid:
                    self._evidence[eid] = data

    def validate_rule(self, rule: dict) -> RuleChainResult:
        """校验单条规则的链完整性。"""
        rule_id = rule.get("rule_id", "unknown")
        enabled = rule.get("execution_enabled", False)

        if not enabled:
            return RuleChainResult(
                rule_id=rule_id,
                execution_enabled=False,
                chain_valid=True,
            )

        violations: list[str] = []

        # 检查 1: rule_refs 指向 semantic_mapping
        rule_refs = rule.get("rule_refs", [])
        if not rule_refs:
            violations.append(f"rule {rule_id}: 缺少 rule_refs（未指向任何 semantic_mapping）")
        else:
            # 检查每个 ref 是否指向有效的 mapping
            mapping_ids = [r.get("mapping_id") for r in rule_refs if isinstance(r, dict)]
            missing_mappings = [
                mid for mid in mapping_ids
                if mid and mid not in self._mappings
            ]
            if missing_mappings:
                violations.append(
                    f"rule {rule_id}: rule_refs 指向的 mapping 不存在: {missing_mappings}"
                )

        # 检查 2: mapping → concept 链
        if not violations:
            for ref in rule_refs:
                if isinstance(ref, dict):
                    mapping_id = ref.get("mapping_id")
                    if mapping_id and mapping_id in self._mappings:
                        mapping = self._mappings[mapping_id]
                        concept_id = mapping.get("concept_id")
                        if not concept_id:
                            violations.append(
                                f"rule {rule_id}: mapping {mapping_id} 缺少 concept_id"
                            )
                        elif concept_id not in self._concepts:
                            violations.append(
                                f"rule {rule_id}: mapping {mapping_id} 引用的 concept {concept_id} 不存在"
                            )

        # 检查 3: concept → evidence/source 链
        if not violations:
            for ref in rule_refs:
                if isinstance(ref, dict):
                    mapping_id = ref.get("mapping_id")
                    if mapping_id and mapping_id in self._mappings:
                        mapping = self._mappings[mapping_id]
                        concept_id = mapping.get("concept_id")
                        if concept_id and concept_id in self._concepts:
                            concept = self._concepts[concept_id]
                            source_refs = concept.get("source_refs", [])
                            if not source_refs:
                                violations.append(
                                    f"rule {rule_id}: concept {concept_id} 缺少 source_refs"
                                )
                            else:
                                # 检查 source_refs 指向的 evidence 是否存在
                                evidence_ids = [
                                    s.get("evidence_id")
                                    for s in source_refs
                                    if isinstance(s, dict)
                                ]
                                missing_evidence = [
                                    eid for eid in evidence_ids
                                    if eid and eid not in self._evidence
                                ]
                                if missing_evidence:
                                    violations.append(
                                        f"rule {rule_id}: concept {concept_id} 引用证据不存在: {missing_evidence}"
                                    )

        # 检查 4: evidence.source_layer 不为 null
        if not violations:
            for ref in rule_refs:
                if isinstance(ref, dict):
                    mapping_id = ref.get("mapping_id")
                    if mapping_id and mapping_id in self._mappings:
                        mapping = self._mappings[mapping_id]
                        concept_id = mapping.get("concept_id")
                        if concept_id and concept_id in self._concepts:
                            concept = self._concepts[concept_id]
                            for src in concept.get("source_refs", []):
                                if isinstance(src, dict):
                                    eid = src.get("evidence_id")
                                    if eid and eid in self._evidence:
                                        ev = self._evidence[eid]
                                        if not ev.get("source_layer"):
                                            violations.append(
                                                f"rule {rule_id}: evidence {eid} 缺少 source_layer"
                                            )

        chain_valid = len(violations) == 0
        degraded = not chain_valid

        return RuleChainResult(
            rule_id=rule_id,
            execution_enabled=enabled,
            chain_valid=chain_valid,
            violations=violations,
            degraded=degraded,
        )

    def validate_all_rules(self, rules: list[dict]) -> list[RuleChainResult]:
        """批量校验所有规则。"""
        results = []
        for rule in rules:
            result = self.validate_rule(rule)
            results.append(result)

        # 汇总报告
        violations_count = sum(
            1 for r in results if r.violations
        )
        if violations_count > 0:
            log.warning(
                "B-6 硬规则: %d/%d 条规则存在链不完整问题，将自动降级",
                violations_count,
                len(results),
            )

        return results
