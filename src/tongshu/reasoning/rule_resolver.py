"""P4-A Rule Resolver - 规则身份对齐层.

解决 EngineEvidence.rule_id ≠ Rule.rule_id 的问题.

链路:
  EngineEvidence(engine, engine_rule_id, value)
    ↓ RuleResolver.resolve()
  ResolvedRule(canonical_rule_ids[], match_status)
    ↓ P3SignalEngine
  SemanticSignal[]

硬契约:
  - 不修改Engine, 不修改历史Evidence
  - 支持一对一, 支持一对多(一条Evidence映射到多条Rule)
  - 支持条件映射(根据value字段选择不同Rule)
  - 未匹配必须明确标记 UNRESOLVED
  - 禁止 fallback 到旧 direction/polarity

匹配状态:
  - RESOLVED: 成功映射到至少一条已迁移Rule
  - PARTIAL: 映射到Rule但Rule未迁移(produces_semantic_atoms)
  - UNRESOLVED: 映射表中无对应条目
  - RULE_NOT_FOUND: 映射到rule_id但规则文件不存在
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger(__name__)


class MatchStatus(str, Enum):
    """规则匹配状态."""
    RESOLVED = "RESOLVED"              # 成功映射到已迁移Rule
    PARTIAL = "PARTIAL"                # 映射到Rule但未迁移
    UNRESOLVED = "UNRESOLVED"          # 映射表无对应条目
    RULE_NOT_FOUND = "RULE_NOT_FOUND"  # 映射到rule_id但文件不存在


@dataclass
class ResolvedRule:
    """解析后的规则结果."""
    engine: str
    engine_rule_id: str
    canonical_rule_ids: list[str] = field(default_factory=list)
    match_status: str = MatchStatus.UNRESOLVED.value
    resolution_type: str = ""  # one_to_one / one_to_many / conditional / unresolved
    reason: str = ""
    evidence_value: Any = None

    def to_dict(self) -> dict:
        return {
            "engine": self.engine,
            "engine_rule_id": self.engine_rule_id,
            "canonical_rule_ids": self.canonical_rule_ids,
            "match_status": self.match_status,
            "resolution_type": self.resolution_type,
            "reason": self.reason,
            "evidence_value": str(self.evidence_value) if self.evidence_value else None,
        }


class RuleResolver:
    """P4 Rule Resolver - EngineEvidence rule_id → canonical Rule rule_id.

    加载映射表 data/rule_resolution_map.json, 提供resolve方法.
    """

    def __init__(self, map_path: Path | str, rules_dir: Path | str):
        self._map_path = Path(map_path)
        self._rules_dir = Path(rules_dir)
        self._map: dict = {}
        self._migrated_rules: set[str] = set()
        self._all_rules: set[str] = set()
        self._load_map()
        self._load_rules_index()

    def _load_map(self) -> None:
        """加载映射表."""
        if not self._map_path.exists():
            log.warning("Rule resolution map not found: %s", self._map_path)
            self._map = {"mappings": {}}
            return
        with open(self._map_path, encoding="utf-8") as f:
            self._map = json.load(f)
        log.info(
            "Loaded rule resolution map: %d engines",
            len(self._map.get("mappings", {})),
        )

    def _load_rules_index(self) -> None:
        """加载规则文件索引, 判断哪些已迁移."""
        if not self._rules_dir.is_dir():
            log.warning("Rules dir not found: %s", self._rules_dir)
            return
        for f in sorted(self._rules_dir.glob("*.json")):
            with open(f, encoding="utf-8") as fh:
                rule = json.load(fh)
            rid = rule.get("rule_id")
            if rid:
                self._all_rules.add(rid)
                if "produces_semantic_atoms" in rule.get("conclusion", {}):
                    self._migrated_rules.add(rid)
        log.info(
            "Rules index: %d total, %d migrated",
            len(self._all_rules), len(self._migrated_rules),
        )

    def resolve(
        self,
        engine: str,
        engine_rule_id: str,
        evidence_value: Any = None,
    ) -> ResolvedRule:
        """解析一条EngineEvidence的rule_id到canonical Rule rule_id列表.

        Args:
            engine: 引擎名 (ZI_PING / BLIND_SCHOOL / ZI_WEI / HE_LUO / YI_JING)
            engine_rule_id: EngineEvidence的rule_id
            evidence_value: EngineEvidence的value(用于条件映射)

        Returns:
            ResolvedRule
        """
        result = ResolvedRule(
            engine=engine,
            engine_rule_id=engine_rule_id,
            evidence_value=evidence_value,
        )

        # 查找映射表
        engine_mappings = self._map.get("mappings", {}).get(engine, {})
        mapping = engine_mappings.get(engine_rule_id)

        if not mapping:
            result.match_status = MatchStatus.UNRESOLVED.value
            result.reason = f"No mapping entry for {engine}/{engine_rule_id}"
            return result

        result.resolution_type = mapping.get("resolution_type", "unknown")

        # 根据映射类型解析
        if mapping["resolution_type"] == "one_to_one":
            result.canonical_rule_ids = [mapping["rule_id"]]
        elif mapping["resolution_type"] == "one_to_many":
            result.canonical_rule_ids = list(mapping["rule_ids"])
        elif mapping["resolution_type"] == "conditional":
            condition_field = mapping.get("condition_field", "value")
            conditions = mapping.get("conditions", {})
            default = mapping.get("default", [])
            # 根据evidence_value选择
            val_str = str(evidence_value) if evidence_value else ""
            matched = conditions.get(val_str, default)
            result.canonical_rule_ids = list(matched) if isinstance(matched, list) else [matched]
        elif mapping["resolution_type"] == "unresolved":
            result.match_status = MatchStatus.UNRESOLVED.value
            result.reason = mapping.get("reason", "Marked as unresolved in mapping")
            return result
        else:
            result.match_status = MatchStatus.UNRESOLVED.value
            result.reason = f"Unknown resolution_type: {mapping['resolution_type']}"
            return result

        # 检查canonical_rule_ids是否存在
        existing_ids = [rid for rid in result.canonical_rule_ids if rid in self._all_rules]
        missing_ids = [rid for rid in result.canonical_rule_ids if rid not in self._all_rules]

        if missing_ids:
            result.reason = f"Rule files not found: {missing_ids}"

        # 检查是否已迁移
        migrated_ids = [rid for rid in existing_ids if rid in self._migrated_rules]
        unmigrated_ids = [rid for rid in existing_ids if rid not in self._migrated_rules]

        if migrated_ids and not unmigrated_ids:
            result.match_status = MatchStatus.RESOLVED.value
            result.canonical_rule_ids = migrated_ids
        elif migrated_ids and unmigrated_ids:
            result.match_status = MatchStatus.PARTIAL.value
            result.reason = f"Partially migrated: {len(migrated_ids)} migrated, {len(unmigrated_ids)} not"
            result.canonical_rule_ids = migrated_ids  # 只用已迁移的
        elif existing_ids and not migrated_ids:
            result.match_status = MatchStatus.PARTIAL.value
            result.reason = f"Rules found but not migrated: {existing_ids}"
            result.canonical_rule_ids = []
        else:
            result.match_status = MatchStatus.RULE_NOT_FOUND.value
            result.canonical_rule_ids = []

        return result

    def resolve_batch(
        self,
        evidence_list: list[dict],
    ) -> list[ResolvedRule]:
        """批量解析EngineEvidence列表."""
        results = []
        for ev in evidence_list:
            result = self.resolve(
                engine=ev.get("engine", ""),
                engine_rule_id=ev.get("rule_id", ""),
                evidence_value=ev.get("value"),
            )
            results.append(result)
        return results

    def get_stats(self, results: list[ResolvedRule]) -> dict:
        """统计解析结果."""
        from collections import Counter
        status_counts = Counter(r.match_status for r in results)
        engine_counts = Counter(r.engine for r in results)
        resolved_by_engine = Counter(
            r.engine for r in results if r.match_status == MatchStatus.RESOLVED.value
        )
        return {
            "total": len(results),
            "by_status": dict(status_counts),
            "by_engine": dict(engine_counts),
            "resolved_by_engine": dict(resolved_by_engine),
            "resolved_count": status_counts.get(MatchStatus.RESOLVED.value, 0),
            "unresolved_count": status_counts.get(MatchStatus.UNRESOLVED.value, 0),
            "partial_count": status_counts.get(MatchStatus.PARTIAL.value, 0),
        }
