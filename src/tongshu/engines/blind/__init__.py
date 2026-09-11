"""盲派引擎包。

V2 架构：BlindPaiEngine（主引擎）+ 证据生产者 + 做功图/链 + 宫位。
"""
from __future__ import annotations

from .engine import (
    BlindPaiEngine,
    BlindPaiResult,
    BodyUseState,
    FrozenBaziState,
    GongShenRole,
    GongShenState,
    HostGuestScope,
    HostGuestState,
    MethodScope,
    StructureClarity,
    WorkEfficiency,
    WorkEfficiencyState,
)
from .evidence_producer import (
    BlindEvidenceProducer,
    BlindFeatureState,
    EvidenceItem,
    EvidenceList,
    Relevance,
)

__all__ = [
    "BlindPaiEngine",
    "BlindPaiResult",
    "BodyUseState",
    "FrozenBaziState",
    "GongShenRole",
    "GongShenState",
    "HostGuestScope",
    "HostGuestState",
    "MethodScope",
    "StructureClarity",
    "WorkEfficiency",
    "WorkEfficiencyState",
    "BlindEvidenceProducer",
    "BlindFeatureState",
    "EvidenceItem",
    "EvidenceList",
    "Relevance",
]
