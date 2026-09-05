"""Canonical Bazi Chart — authoritative four-pillar facts.

This module provides the canonical upstream interface for all downstream
engines (Heluo, Ziwei, etc.) to consume validated Bazi facts.

Architecture:
  BaziEngine → BaziChart → CanonicalBaziChart → [Heluo|Ziwei|...]

Contract:
  - CanonicalBaziChart is READ-ONLY
  - Contains ONLY the four pillars + day_master + gender + start_age
  - No derived/interpretive fields (spouse_star, branch_clash_map, etc.)
  - All fields frozen (immutable)

Authority:
  - BaziChart authority proof is SEPARATE from this module
  - This module merely provides a clean upstream interface
  - See: src/tongshu/engines/bazi_engine.py for BaziChart definition
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tongshu.engines.bazi_engine import BaziChart, Pillar


@dataclass(frozen=True)
class CanonicalBaziChart:
    """Authoritative four-pillar facts for downstream engine consumption.

    This is the canonical upstream interface that all engines must consume.
    Downstream engines MUST NOT recompute four pillars — they receive them
    from this object.

    Attributes:
        year_pillar: Year pillar (heavenly_stem, earthly_branch)
        month_pillar: Month pillar
        day_pillar: Day pillar
        hour_pillar: Hour pillar
        day_master: Day master stem (e.g., "JIA", "YI")
        gender: "male" or "female"
        start_age: Start age in years (float)
    """

    year_pillar: Pillar
    month_pillar: Pillar
    day_pillar: Pillar
    hour_pillar: Pillar
    day_master: str
    gender: str
    start_age: float

    @classmethod
    def from_bazi_chart(cls, chart: "BaziChart") -> "CanonicalBaziChart":
        """Create CanonicalBaziChart from BaziChart.

        This is the ONLY valid creation path. It enforces the contract
        that downstream engines receive validated facts, not raw inputs.

        Args:
            chart: BaziChart from BaziEngine.compute()

        Returns:
            CanonicalBaziChart with only the authoritative facts
        """
        return cls(
            year_pillar=chart.year_pillar,
            month_pillar=chart.month_pillar,
            day_pillar=chart.day_pillar,
            hour_pillar=chart.hour_pillar,
            day_master=chart.day_master,
            gender=chart.gender,
            start_age=chart.start_age,
        )

    @property
    def bazi(self) -> list[tuple[str, str]]:
        """Return bazi as list of (stem, branch) tuples.

        Convenience property for legacy compatibility.
        DO NOT use for direct computation — use individual pillar fields.
        """
        return [
            (self.year_pillar.heavenly_stem, self.year_pillar.earthly_branch),
            (self.month_pillar.heavenly_stem, self.month_pillar.earthly_branch),
            (self.day_pillar.heavenly_stem, self.day_pillar.earthly_branch),
            (self.hour_pillar.heavenly_stem, self.hour_pillar.earthly_branch),
        ]

    @property
    def birth_hour(self) -> str:
        """Return birth hour branch name (e.g., 'WU' for 午时)."""
        return self.hour_pillar.earthly_branch

    def to_dict(self) -> dict:
        """Serialize to dictionary for debugging/logging."""
        return {
            "year_pillar": self.year_pillar.to_dict(),
            "month_pillar": self.month_pillar.to_dict(),
            "day_pillar": self.day_pillar.to_dict(),
            "hour_pillar": self.hour_pillar.to_dict(),
            "day_master": self.day_master,
            "gender": self.gender,
            "start_age": self.start_age,
        }

    def __str__(self) -> str:
        """Human-readable representation."""
        stems = " ".join(p.heavenly_stem for p in [
            self.year_pillar, self.month_pillar,
            self.day_pillar, self.hour_pillar
        ])
        branches = " ".join(p.earthly_branch for p in [
            self.year_pillar, self.month_pillar,
            self.day_pillar, self.hour_pillar
        ])
        return f"CanonicalBaziChart({stems} | {branches} | {self.gender} | start_age={self.start_age})"
