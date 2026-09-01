# DEPRECATED (P1.2 DECISION-003 / P1.4): This module produces CONFLICTED outcomes
# which violate the 互补不比较 architecture principle.
# Replacement: Use CrossDomainOrchestrator (src/tongshu/cross_domain/orchestrator.py).
# Zero production calls confirmed. Keep only for research reference.

"""Phase 4 — Temporal Convergence Arbiter

Extends CrossAnalyzer pattern to support multi-system signal convergence.
Resolves ALIGNED / CONFLICTED / PARTIAL / INSUFFICIENT / UNDEFINED裁定.

Usage:
    from tongshu.signal.convergence import ConvergenceArbiter
    
    arbiter = ConvergenceArbiter()
    result = arbiter.converge(signals, context)
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from tongshu.signal.canonical_signal import CanonicalSignal
from tongshu.signal.adapters import AdapterContext


# ─── Convergence Outcomes ────────────────────────────────────────────────────

class ConvergenceOutcome(enum.Enum):
    """Five-way裁定 outcomes for multi-system signal convergence."""
    ALIGNED = "ALIGNED"           # All signals agree on same prediction
    CONFLICTED = "CONFLICTED"     # Signals disagree, no resolution
    PARTIAL = "PARTIAL"           # Partial agreement (subset aligned)
    INSUFFICIENT = "INSUFFICIENT" # Not enough evidence
    UNDEFINED = "UNDEFINED"       # Cannot determine


@dataclass
class ConvergenceResult:
    """Result of signal convergence analysis."""
    outcome: ConvergenceOutcome
    prediction: Optional[str] = None      # Best prediction if ALIGNED
    confidence: float = 0.0               # Overall confidence
    reason_codes: List[str] = field(default_factory=list)
    aligned_signals: List[CanonicalSignal] = field(default_factory=list)
    conflicted_signals: List[CanonicalSignal] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "outcome": self.outcome.value,
            "prediction": self.prediction,
            "confidence": self.confidence,
            "reason_codes": self.reason_codes,
            "aligned_count": len(self.aligned_signals),
            "conflicted_count": len(self.conflicted_signals),
            "notes": self.notes,
        }


# ─── Convergence Rules ────────────────────────────────────────────────────────

class ConvergenceRules:
    """Configurable rules for signal convergence."""
    
    # Time scale priority (higher = more authoritative)
    TIME_PRIORITY = {
        "HOURLY": 4,
        "DAILY": 3,
        "MONTHLY": 2,
        "YEARLY": 1,
    }
    
    # Minimum signals for valid convergence
    MIN_ALIGNED_COUNT = 2
    
    # Confidence thresholds
    HIGH_CONFIDENCE = 0.8
    MEDIUM_CONFIDENCE = 0.5
    LOW_CONFIDENCE = 0.3


# ─── Convergence Arbiter ──────────────────────────────────────────────────────

class ConvergenceArbiter:
    """Multi-system signal convergence arbiter (Phase 4).
    
    Resolves conflicts between signals from different systems:
    - BAZI (子平/盲派)
    - ZIWEI (紫微斗数)
    - HELUO (河洛理数)
    - YI (易经)
    
    Output: One of ALIGNED / CONFLICTED / PARTIAL / INSUFFICIENT / UNDEFINED
    """
    
    def __init__(self, rules: Optional[ConvergenceRules] = None):
        self.rules = rules or ConvergenceRules()
    
    def converge(
        self,
        signals: List[CanonicalSignal],
        context: Optional[AdapterContext] = None,
    ) -> ConvergenceResult:
        """Converge multiple signals into a single裁定 result.
        
        Args:
            signals: List of CanonicalSignal from different systems
            context: Optional adapter context with additional metadata
            
        Returns:
            ConvergenceResult with outcome and explanation
        """
        if not signals:
            return ConvergenceResult(
                outcome=ConvergenceOutcome.INSUFFICIENT,
                reason_codes=["NO_SIGNALS"],
                notes="No signals provided for convergence",
            )
        
        # Group by theme and time scope
        grouped = self._group_by_theme(signals)
        
        # Check for cross-system alignment
        aligned_groups = []
        conflicted_groups = []
        
        for theme, theme_signals in grouped.items():
            outcome = self._analyze_theme(theme_signals)
            if outcome.outcome == ConvergenceOutcome.ALIGNED:
                aligned_groups.append(outcome)
            elif outcome.outcome == ConvergenceOutcome.PARTIAL:
                aligned_groups.append(outcome)  # Partial counts as aligned
            else:
                conflicted_groups.append(outcome)
        
        # Determine overall outcome
        if len(conflicted_groups) > 0 and len(aligned_groups) == 0:
            overall_outcome = ConvergenceOutcome.CONFLICTED
        elif len(aligned_groups) > 0:
            overall_outcome = ConvergenceOutcome.ALIGNED
        elif len(signals) < self.rules.MIN_ALIGNED_COUNT:
            overall_outcome = ConvergenceOutcome.INSUFFICIENT
        else:
            overall_outcome = ConvergenceOutcome.PARTIAL
        
        # Build result
        reasons = []
        if overall_outcome == ConvergenceOutcome.ALIGNED:
            reasons.extend(["CROSS_SYSTEM_ALIGNED"])
        elif overall_outcome == ConvergenceOutcome.CONFLICTED:
            reasons.extend(["CROSS_SYSTEM_CONFLICTED"])
        elif overall_outcome == ConvergenceOutcome.INSUFFICIENT:
            reasons.extend(["INSUFFICIENT_EVIDENCE"])
        
        return ConvergenceResult(
            outcome=overall_outcome,
            prediction=aligned_groups[0].prediction if aligned_groups else None,
            confidence=self._calc_confidence(signals, aligned_groups),
            reason_codes=reasons,
            aligned_signals=[s for g in aligned_groups for s in g.aligned_signals],
            conflicted_signals=[s for g in conflicted_groups for s in g.conflicted_signals],
            notes=f"Aligned: {len(aligned_groups)}, Conflicted: {len(conflicted_groups)}",
        )
    
    def _group_by_theme(self, signals: List[CanonicalSignal]) -> Dict[str, List[CanonicalSignal]]:
        """Group signals by theme."""
        groups: Dict[str, List[CanonicalSignal]] = {}
        for sig in signals:
            theme = sig.theme or "UNKNOWN"
            if theme not in groups:
                groups[theme] = []
            groups[theme].append(sig)
        return groups
    
    def _analyze_theme(self, theme_signals: List[CanonicalSignal]) -> ConvergenceResult:
        """Analyze convergence within a single theme."""
        if len(theme_signals) < 2:
            return ConvergenceResult(
                outcome=ConvergenceOutcome.INSUFFICIENT,
                reason_codes=["SINGLE_SIGNAL"],
                aligned_signals=theme_signals,
            )
        
        # Check direction alignment
        directions = [s.direction for s in theme_signals]
        unique_directions = set(directions)
        
        if len(unique_directions) == 1:
            # All signals agree
            return ConvergenceResult(
                outcome=ConvergenceOutcome.ALIGNED,
                prediction=theme_signals[0].event_types[0] if theme_signals[0].event_types else None,
                confidence=sum(s.confidence for s in theme_signals) / len(theme_signals),
                aligned_signals=theme_signals,
            )
        elif len(unique_directions) == 2:
            # Partial alignment
            return ConvergenceResult(
                outcome=ConvergenceOutcome.PARTIAL,
                confidence=max(s.confidence for s in theme_signals) * 0.7,
                aligned_signals=theme_signals[:len(theme_signals)//2 + 1],
                conflicted_signals=theme_signals[len(theme_signals)//2 + 1:],
            )
        else:
            # Conflict
            return ConvergenceResult(
                outcome=ConvergenceOutcome.CONFLICTED,
                reason_codes=["DIVERGENT_SIGNALS"],
                conflicted_signals=theme_signals,
            )
    
    def _calc_confidence(
        self,
        all_signals: List[CanonicalSignal],
        aligned_groups: List[ConvergenceResult],
    ) -> float:
        """Calculate overall confidence based on alignment."""
        if not aligned_groups:
            return 0.0
        
        total_confidence = sum(g.confidence for g in aligned_groups)
        alignment_bonus = len(aligned_groups) * 0.1  # Bonus for multiple alignments
        
        return min(1.0, total_confidence / len(all_signals) + alignment_bonus)
