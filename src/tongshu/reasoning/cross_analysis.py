"""Cross Analysis — DECISION-003 / 003.A / 003.B implementation.

Implements the deterministic algorithm specified in docs/cross_analysis.md.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

from ..spec.cross_states import CROSS_STATES, REASON_CODES
from ..spec.signal_ontology import get_relationship, ONTOLOGY_RELATIONSHIPS
from .signal_engine import Signal


@dataclass(frozen=True)
class CrossResult:
    """Result of Cross Analysis between Bazi and Ziwei signals."""
    status: str  # one of CROSS_STATES
    bazi_signal_refs: list[str]
    ziwei_signal_refs: list[str]
    ontology_relationship: str | None
    evidence_sufficient: bool
    reason_code: str | None

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "bazi_signal_refs": list(self.bazi_signal_refs),
            "ziwei_signal_refs": list(self.ziwei_signal_refs),
            "ontology_relationship": self.ontology_relationship,
            "evidence_sufficient": self.evidence_sufficient,
            "reason_code": self.reason_code,
        }


class CrossAnalyzer:
    """Deterministic Cross Analysis algorithm.

    Per docs/cross_analysis.md §5 decision tree.
    """

    def __init__(
        self,
        forbidden_inferences: Iterable = (),
    ):
        self._forbidden_inferences = list(forbidden_inferences)

    def analyze(
        self,
        bazi_signals: list[Signal],
        ziwei_signals: list[Signal],
    ) -> CrossResult:
        """Run Cross Analysis on the two signal lists.

        Args:
            bazi_signals: BASELINE/CYCLE/DAILY signals from Bazi Engine.
            ziwei_signals: BASELINE/CYCLE/DAILY signals from Ziwei Engine.

        Returns:
            CrossResult with one of the 4 mutually exclusive states.
        """
        # Step 0: Forbidden Inference filter (DECISION-003.B)
        bazi_valid = self._apply_forbidden_filter(bazi_signals)
        ziwei_valid = self._apply_forbidden_filter(ziwei_signals)

        # Step 1: Evidence sufficiency
        if not bazi_valid or not ziwei_valid:
            return CrossResult(
                status="INSUFFICIENT",
                bazi_signal_refs=[s.signal_id for s in bazi_valid],
                ziwei_signal_refs=[s.signal_id for s in ziwei_valid],
                ontology_relationship=None,
                evidence_sufficient=False,
                reason_code="EVIDENCE_MISSING",
            )

        # Step 2: Try same-type pairing first
        for sb in bazi_valid:
            for sz in ziwei_valid:
                if sb.ontology_type != sz.ontology_type:
                    continue
                # Same type
                if sb.direction == sz.direction:
                    return CrossResult(
                        status="ALIGNED",
                        bazi_signal_refs=[sb.signal_id],
                        ziwei_signal_refs=[sz.signal_id],
                        ontology_relationship=None,
                        evidence_sufficient=True,
                        reason_code="SAME_SIGNAL_AGREE",
                    )
                if _is_opposite(sb.direction, sz.direction):
                    return CrossResult(
                        status="CONFLICTED",
                        bazi_signal_refs=[sb.signal_id],
                        ziwei_signal_refs=[sz.signal_id],
                        ontology_relationship=None,
                        evidence_sufficient=True,
                        reason_code="OPPOSITE_DIRECTION",
                    )

        # Step 3: Cross-type path (DECISION-003.A)
        for sb in bazi_valid:
            for sz in ziwei_valid:
                if sb.ontology_type == sz.ontology_type:
                    continue
                rel = get_relationship(sb.ontology_type, sz.ontology_type)
                if rel is None:
                    continue  # not pre-registered; skip
                # Pre-registered. Allowed status MUST be PARTIAL.
                if rel.get("allowed_cross_status") != "PARTIAL":
                    continue
                # PARTIAL requires same direction (not opposite)
                if _is_opposite(sb.direction, sz.direction):
                    continue
                return CrossResult(
                    status="PARTIAL",
                    bazi_signal_refs=[sb.signal_id],
                    ziwei_signal_refs=[sz.signal_id],
                    ontology_relationship=rel["relationship"],
                    evidence_sufficient=True,
                    reason_code="SHARED_SUPERTYPE",
                )

        # No compatible pairing found
        return CrossResult(
            status="INSUFFICIENT",
            bazi_signal_refs=[s.signal_id for s in bazi_valid],
            ziwei_signal_refs=[s.signal_id for s in ziwei_valid],
            ontology_relationship=None,
            evidence_sufficient=False,
            reason_code="INSUFFICIENT_RULES",
        )

    def _apply_forbidden_filter(self, signals: list[Signal]) -> list[Signal]:
        """Filter signals that trigger Forbidden Inferences.

        Per DECISION-003.B: hard_block forbidden Signals are excluded entirely.
        For v1.0 demo, this is a stub. Real Forbidden Inference DB integration
        comes with the seed data.
        """
        return list(signals)


def _is_opposite(d1: str, d2: str) -> bool:
    """Per docs/cross_analysis.md §7.1."""
    if d1 == "INCREASE" and d2 == "DECREASE":
        return True
    if d1 == "DECREASE" and d2 == "INCREASE":
        return True
    return False
