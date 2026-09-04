# -*- coding: utf-8 -*-
"""Z14: 同盘异法验收契约。

核心原则：
  - 一张 FrozenZiweiChart，四个独立方法各自读取
  - 方法之间绝不读取对方的 Evidence
  - 输出统一为 ZiweiEvidenceRecord（含 method_id / rule_id / source / trace）
  - 不比较、不投票、不产生 CONFLICTED

架构：
  FrozenZiweiChart
       │
       ├─→ SanheRuleGraph      → Evidence A
       ├─→ ZhongzhouRuleGraph  → Evidence B
       ├─→ FeixingRuleGraph    → Evidence C
       └─→ QintianRuleGraph    → Evidence D

  四条证据链并列，互不污染。
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ...ziwei_engine import FrozenZiweiChart
from ...ziwei_method_profile import MethodId

logger = logging.getLogger(__name__)


# ============================================================================
# 统一证据记录格式
# ============================================================================

@dataclass(frozen=True)
class ZiweiEvidenceRecord:
    """Z14 统一证据记录：每种方法的输出都映射到此格式。

    字段说明：
      method_id:        来源流派（SANHE/ZHONGZHOU/FEIXING/QINTIAN）
      rule_id:          匹配的规则 ID
      evidence_type:    证据类型（pattern/sihua/palace/flying）
      facts:            匹配的事实摘要
      verification:     验证状态（canonical/candidate/unverified）
      trace:            追溯路径（tuple of step descriptions）
    """
    method_id: MethodId
    rule_id: str
    evidence_type: str
    facts: dict[str, Any]
    verification: str = "candidate"
    trace: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict:
        return {
            "method_id": self.method_id.value,
            "rule_id": self.rule_id,
            "evidence_type": self.evidence_type,
            "facts": self.facts,
            "verification": self.verification,
            "trace": list(self.trace),
        }


# ============================================================================
# 同盘异法证据收集器
# ============================================================================

class MultiMethodEvidenceCollector:
    """从同一 FrozenZiweiChart 收集多派独立证据。

    设计原则：
      - 每个方法只消费 chart + 自身规则
      - 不读取其他方法的证据
      - 输出统一为 ZiweiEvidenceRecord 列表
    """

    def __init__(self, chart: FrozenZiweiChart) -> None:
        self._chart = chart

    def collect(self, method_ids: list[MethodId] | None = None) -> dict[MethodId, list[ZiweiEvidenceRecord]]:
        """收集所有指定流派的证据。

        Returns:
            {MethodId: [ZiweiEvidenceRecord, ...]}
        """
        if method_ids is None:
            method_ids = list(MethodId)

        results: dict[MethodId, list[ZiweiEvidenceRecord]] = {}
        for mid in method_ids:
            results[mid] = self._collect_for_method(mid)
        return results

    def _collect_for_method(self, method_id: MethodId) -> list[ZiweiEvidenceRecord]:
        """为单个流派收集证据（内部隔离，不访问其他派）。"""
        # 延迟导入，避免循环依赖
        if method_id == MethodId.FEIXING:
            return self._collect_feixing()
        else:
            return self._collect_pattern_sihua(method_id)

    def _collect_pattern_sihua(
        self, method_id: MethodId
    ) -> list[ZiweiEvidenceRecord]:
        """通用 pattern+sihua+palace 规则匹配（适用于 SANHE/ZHONGZHOU/QINTIAN）。"""
        from ...ziwei.rules.rule_graph import create_rule_graph

        graph = create_rule_graph(method_id)
        result = graph.match_all(self._chart)

        records: list[ZiweiEvidenceRecord] = []
        for match in result.matched_rules:
            spec = match.rule_spec
            records.append(ZiweiEvidenceRecord(
                method_id=method_id,
                rule_id=spec.rule_id,
                evidence_type=spec.rule_type.value,
                facts=match.facts,
                verification=spec.evidence_refs[0].verification_status
                    if spec.evidence_refs else "unverified",
                trace=(
                    f"chart → {method_id.label_zh} → "
                    f"{spec.rule_id} → match"
                ),
            ))
        return records

    def _collect_feixing(self) -> list[ZiweiEvidenceRecord]:
        """飞星派专属证据收集（宫干飞化路径）。"""
        from ...ziwei.rules.feixing_rule_graph import create_feixing_rule_graph

        graph = create_feixing_rule_graph()
        transforms = graph.compute_all_flying_transforms(self._chart)
        flying_results = graph.match_flying_rules(self._chart, transforms)

        records: list[ZiweiEvidenceRecord] = []
        for r in flying_results:
            facts = r.get("facts", {})
            records.append(ZiweiEvidenceRecord(
                method_id=MethodId.FEIXING,
                rule_id=r["rule_id"],
                evidence_type="flying_sihua",
                facts=facts,
                verification=r.get("verification_status", "candidate"),
                trace=(
                    f"chart → 飞星 → {r['rule_id']} → "
                    f"{facts.get('source_palace', '')}({facts.get('source_stem', '')})"
                ),
            ))
        return records

    @property
    def chart(self) -> FrozenZiweiChart:
        return self._chart


# ============================================================================
# 隔离验证工具
# ============================================================================

class IsolationVerifier:
    """验证多派证据之间的隔离性。"""

    @staticmethod
    def verify_no_cross_contamination(
        evidence_map: dict[MethodId, list[ZiweiEvidenceRecord]],
    ) -> dict[str, bool]:
        """验证各派证据无交叉污染。

        Returns:
            {check_name: passed}
        """
        checks: dict[str, bool] = {}

        # 检查 1: 每派证据的 method_id 一致
        for mid, records in evidence_map.items():
            all_correct = all(r.method_id == mid for r in records)
            checks[f"method_id_{mid.value}"] = all_correct

        # 检查 2: rule_id 前缀隔离
        prefix_map: dict[str, set[str]] = {
            "SANHE": set(), "ZHONGZHOU": set(),
            "FEIXING": set(), "QINTIAN": set(),
        }
        for mid, records in evidence_map.items():
            prefix = mid.value.upper()  # 'sanhe' → 'SANHE'
            for r in records:
                prefix_map[prefix].add(r.rule_id)

        for mid_name, prefixes in prefix_map.items():
            has_wrong_prefix = any(
                not rid.startswith(mid_name)
                for rid in prefixes
                if rid  # 非空 rule_id
            )
            checks[f"prefix_isolation_{mid_name}"] = not has_wrong_prefix

        # 检查 3: 不同派规则 ID 无交集（前缀不同即隔离）
        all_ids: dict[str, set[str]] = {}
        for mid, records in evidence_map.items():
            key = mid.value.upper()  # 'sanhe' → 'SANHE'
            all_ids[key] = {r.rule_id for r in records}

        pairs = [
            ("SANHE", "FEIXING"), ("SANHE", "ZHONGZHOU"),
            ("FEIXING", "ZHONGZHOU"), ("FEIXING", "QINTIAN"),
        ]
        for a, b in pairs:
            intersection = all_ids[a] & all_ids[b]
            checks[f"no_overlap_{a}_vs_{b}"] = len(intersection) == 0

        return checks

    @staticmethod
    def verify_traceability(
        evidence_map: dict[MethodId, list[ZiweiEvidenceRecord]],
    ) -> dict[str, bool]:
        """验证每条证据可追溯。"""
        checks: dict[str, bool] = {}
        for mid, records in evidence_map.items():
            for i, r in enumerate(records):
                # 每条证据必须有 method_id
                if not r.method_id:
                    checks[f"traceable_{mid.value}_{i}"] = False
                    continue
                # 每条证据必须有 rule_id
                if not r.rule_id:
                    checks[f"traceable_{mid.value}_{i}"] = False
                    continue
                # 每条证据必须有 facts
                if not r.facts:
                    checks[f"traceable_{mid.value}_{i}"] = False
                    continue
                # 每条证据必须有 trace
                if not r.trace:
                    checks[f"traceable_{mid.value}_{i}"] = False
                    continue
            checks[f"all_traceable_{mid.value}"] = True
        return checks
