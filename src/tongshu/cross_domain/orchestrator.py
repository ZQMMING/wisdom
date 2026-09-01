"""
P1.3 — CrossDomainOrchestrator

职责：
  1. 接收多个引擎的 Evidence
  2. 构建 MultiDomainSemanticCoverage（按 domain × semantic × engine 索引）
  3. 产出多体系独立 Assertion（各自通过 Authorized Rule）
  4. 输出 Structured Observation（非 Judgment / Convergence / Resolution）

严禁：
  - 比较不同引擎的 direction
  - 计算 confidence / weight / score
  - 产生 CONFLICTED / ALIGNED / PARTIAL
  - 投票 / 多数决
  - 任何旧 Signal / CrossAnalyzer / Convergence 调用
  - 暴露全局 evidence_count（用 coverage.total_assertions 替代）
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
from .result import (
    CrossDomainResult,
    EngineEvidenceSet,
    EngineAssertionSet,
    DomainSemanticIndex,
    MultiDomainSemanticCoverage,
)

logger = logging.getLogger(__name__)


class CrossDomainOrchestrator:
    """跨体系证据编排器。

    接收多引擎 Evidence，产出多体系独立 Assertion + MultiDomainSemanticCoverage。
    不产生 Judgment（由 AuthorizedJudgmentRuleLibrary 单独处理）。
    """

    def __init__(
        self,
        assertion_library: AssertionRuleLibrary,
    ):
        if not getattr(assertion_library, "_production_verified", False):
            raise ValueError(
                "P1.5 Production Boundary: CrossDomainOrchestrator requires a "
                "ProductionRuleLoader-loaded library. Use "
                "ProductionRuleLoader.load(path) instead of AssertionRuleLibrary.load()."
            )
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
        all_evidence_ids_by_engine: Dict[str, List[str]] = {}
        # coverage: domain → semantic → DomainSemanticIndex
        coverage_map: Dict[str, Dict[str, DomainSemanticIndex]] = {}

        for engine_name, evidences in engine_evidences.items():
            engine_evidence_ids: List[str] = []
            engine_assertion_ids: List[str] = []

            for ev in evidences:
                engine_evidence_ids.append(ev.evidence_id)

                # Map to SemanticAtom
                atom = atom_map_fn(ev)
                if atom is None:
                    continue

                # Find authorized rule
                rule = self._assertion_lib.find_rule(atom, {"temporal_scope": temporal_scope})
                if rule is None:
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
                engine_assertion_ids.append(assertion.assertion_id)

                # Index into Coverage（domain × semantic × engine）
                domain = assertion.domain
                semantic = assertion.semantic
                if domain not in coverage_map:
                    coverage_map[domain] = {}
                if semantic not in coverage_map[domain]:
                    coverage_map[domain][semantic] = DomainSemanticIndex(
                        domain=domain,
                        semantic=semantic,
                    )
                # Add engine to this domain × semantic index
                ds_index = coverage_map[domain][semantic]
                if engine_name not in ds_index.by_engine:
                    ds_index.by_engine[engine_name] = EngineAssertionSet(
                        engine=engine_name,
                    )
                ds_index.by_engine[engine_name].assertion_ids.append(assertion.assertion_id)

            all_evidence_ids_by_engine[engine_name] = engine_evidence_ids

        # Build by_engine
        for engine_name, evidence_ids in all_evidence_ids_by_engine.items():
            by_engine[engine_name] = EngineEvidenceSet(
                engine=engine_name,
                evidence_ids=evidence_ids,
                assertion_ids=[],  # Filled below
            )

        # Fill assertion_ids in by_engine from coverage
        for domain_index in coverage_map.values():
            for ds_index in domain_index.values():
                for engine_name, eng_set in ds_index.by_engine.items():
                    if engine_name in by_engine:
                        by_engine[engine_name].assertion_ids.extend(eng_set.assertion_ids)

        # Build final Coverage
        coverage = MultiDomainSemanticCoverage(coverage=coverage_map)

        return CrossDomainResult(
            case_id=case_id,
            temporal_scope=temporal_scope,
            by_engine=by_engine,
            coverage=coverage,
        )
