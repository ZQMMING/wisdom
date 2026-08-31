"""
P1.3 — CrossDomainOrchestrator

职责：
  1. 接收多个引擎的 Evidence
  2. 构建 EvidenceCoverage（结构性组织，不比较方向）
  3. 产出多体系独立 Assertion（各自通过 Authorized Rule）
  4. 输出 Structured Observation（非 Judgment / Convergence / Resolution）

严禁：
  - 比较不同引擎的 direction
  - 计算 confidence / weight / score
  - 产生 CONFLICTED / ALIGNED / PARTIAL
  - 投票 / 多数决
  - 任何旧 Signal / CrossAnalyzer / Convergence 调用
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, TypeVar

from ..spec.canonical import (
    EngineEvidence,
    SemanticAtom,
    CanonicalAssertion,
    EvidenceRef,
    EngineName,
)
from ..assertion.assertion_rule_library import AssertionRuleLibrary
from .result import CrossDomainResult, EngineEvidenceSet

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _first_or_none(lst: List[T], default: T = None) -> Optional[T]:
    """Safely get first element or None."""
    return lst[0] if lst else default


class CrossDomainOrchestrator:
    """跨体系证据编排器。

    接收多引擎 Evidence，产出多体系独立 Assertion + EvidenceCoverage。
    不产生 Judgment（由 AuthorizedJudgmentRuleLibrary 单独处理）。
    """

    def __init__(
        self,
        assertion_library: AssertionRuleLibrary,
    ):
        self._assertion_lib = assertion_library

    def orchestrate(
        self,
        case_id: str,
        temporal_scope: str,
        engine_evidences: Dict[str, List[EngineEvidence]],
        atom_map_fn,
    ) -> CrossDomainResult:
        """编排跨体系证据。

        Args:
            case_id: 命例 ID
            temporal_scope: 时间范围（birth/year/month/day/hour）
            engine_evidences: {engine_name: list[EngineEvidence]}
            atom_map_fn: Callable[[EngineEvidence], Optional[SemanticAtom]]
                将 EngineEvidence 映射到 SemanticAtom 的函数

        Returns:
            CrossDomainResult（Structured Observation）
        """
        by_engine: Dict[str, EngineEvidenceSet] = {}
        all_assertions: List[CanonicalAssertion] = []
        all_evidence_ids: List[str] = []
        all_assertion_ids: List[str] = []
        no_assertion_count = 0

        for engine_name, evidences in engine_evidences.items():
            engine_evidence_ids = []
            engine_assertion_ids = []

            for ev in evidences:
                engine_evidence_ids.append(ev.evidence_id)
                all_evidence_ids.append(ev.evidence_id)

                # Map to SemanticAtom
                atom = atom_map_fn(ev)
                if atom is None:
                    continue

                # Find authorized rule
                rule = self._assertion_lib.find_rule(atom, {"temporal_scope": temporal_scope})
                if rule is None:
                    no_assertion_count += 1
                    continue

                # Build Assertion（direction 来自规则授权，非 Orchestrator 决定）
                assertion = CanonicalAssertion(
                    assertion_id=f"AS-{ev.evidence_id}-{atom.atom_id}",
                    subject=case_id,
                    domain=rule.domain,
                    semantic=atom.atom_id,
                    direction=rule.direction,
                    temporal_scope=temporal_scope,
                    source_engine=engine_name,
                    source_rule=ev.evidence_id,
                    authorized_rule_id=rule.rule_id,
                    evidence=EvidenceRef(
                        evidence_id=ev.evidence_id,
                        engine=engine_name,
                        value=ev.value,
                        source_rule_ref=ev.source_rule_ref,
                        source_field=ev.source_field,
                        temporal_scope=ev.temporal_scope.value,
                        rule_id=ev.rule_id,
                        calculation_version=ev.calculation_version,
                        contract_version=ev.contract_version,
                    ),
                )
                all_assertions.append(assertion)
                engine_assertion_ids.append(assertion.assertion_id)
                all_assertion_ids.append(assertion.assertion_id)

            by_engine[engine_name] = EngineEvidenceSet(
                engine=engine_name,
                evidence_ids=engine_evidence_ids,
                assertion_ids=engine_assertion_ids,
            )

        # Build Coverage（纯结构性，不比较方向）
        domains = set(a.domain for a in all_assertions)
        sematics = set(a.semantic for a in all_assertions)
        engines = set(by_engine.keys())

        # Use first domain/semantic for single-coverage case
        # In real implementation, this would be per-domain-per-semantic
        sample_domain = next(iter(domains)) if domains else ""
        sample_semantic = next(iter(sematics)) if sematics else ""

        return CrossDomainResult(
            case_id=case_id,
            temporal_scope=temporal_scope,
            by_engine=by_engine,
            domain=sample_domain,
            semantic=sample_semantic,
            evidence_count=len(all_evidence_ids),
            source_engines=list(engines),
            evidence_types=list(sematics),
            all_assertion_ids=all_assertion_ids,
            no_assertion_count=no_assertion_count,
        )
