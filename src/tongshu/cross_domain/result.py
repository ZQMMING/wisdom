"""
P1.3 — Cross-Domain Orchestration Layer

设计原则：
  1. EvidenceCoverage 只做结构性组织，不产生 Judgment
  2. 各体系独立产出 Assertion，不互相比较 direction
  3. 保持体系 Provenance（by_engine 分离存储）
  4. 遵循 V13 §二：互补不比较，不投票、不评分、不多数决、不加权
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class EngineEvidenceSet:
    """单引擎的证据集（保持体系 Provenance）。"""
    engine: str
    evidence_ids: List[str] = field(default_factory=list)
    assertion_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "engine": self.engine,
            "evidence_ids": list(self.evidence_ids),
            "assertion_ids": list(self.assertion_ids),
        }


@dataclass(frozen=True)
class CrossDomainResult:
    """跨体系编排结果。

    严禁：
    - direction / polarity / strength / confidence / score / weight 字段
    - CONFLICTED / ALIGNED / PARTIAL 状态
    - vote / compare / rank 逻辑
    """
    case_id: str
    temporal_scope: str
    by_engine: Dict[str, EngineEvidenceSet]  # 按引擎分离的证据/断言
    domain: str
    semantic: str
    evidence_count: int
    source_engines: List[str]
    evidence_types: List[str]
    all_assertion_ids: List[str] = field(default_factory=list)
    no_assertion_count: int = 0

    def verify_no_cross_comparison(self) -> List[str]:
        """验证：没有任何跨体系方向比较逻辑被调用。"""
        errors: List[str] = []
        # 检查 no direction-related fields exist
        forbidden_attrs = {"direction", "polarity", "strength", "confidence", "score", "weight"}
        for attr in forbidden_attrs:
            if hasattr(self, attr):
                errors.append(f"CrossDomainResult has forbidden attribute: {attr}")
        return errors

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "temporal_scope": self.temporal_scope,
            "by_engine": {k: v.to_dict() for k, v in self.by_engine.items()},
            "domain": self.domain,
            "semantic": self.semantic,
            "evidence_count": self.evidence_count,
            "source_engines": list(self.source_engines),
            "evidence_types": list(self.evidence_types),
            "all_assertion_ids": list(self.all_assertion_ids),
            "no_assertion_count": self.no_assertion_count,
        }
