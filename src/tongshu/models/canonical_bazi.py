"""CanonicalBaziChart — Authoritative four-pillar fact container.

H17-B Contract:
  - Sole upstream source of four-pillar facts for all downstream engines
  - BaziEngine produces this from BirthInput (not re-computed by consumers)
  - Immutable after creation (frozen dataclass)

Architecture:
  BirthInput → BaziAdapter.compute() → BaziChart → CanonicalBaziChart
                                              ↓
                                    Heluo / Blind / Ziwei consume

Usage:
  canonical = CanonicalBaziChart.from_bazi_chart(bazi_chart)
  result = heluo_engine.calculate(canonical)
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.engines.bazi_engine import Pillar


@dataclass(frozen=True)
class CanonicalBaziChart:
    """Immutable container for authoritative four-pillar facts.

    Fields:
        year_pillar: 年柱 (JIA CHEN format)
        month_pillar: 月柱
        day_pillar: 日柱
        hour_pillar: 时柱
        day_master: 日主天干 (WU, JIA, etc.)
        gender: 性别 (male/female)
        start_age: 起运年龄（岁）
        birth_datetime: 出生时间（北京时间）
        solar_terms: 节气信息（可选）
    """

    year_pillar: Pillar
    month_pillar: Pillar
    day_pillar: Pillar
    hour_pillar: Pillar
    day_master: str
    gender: str
    start_age: float
    birth_datetime: Optional[datetime] = None
    solar_terms: dict = field(default_factory=dict)

    @classmethod
    def from_bazi_chart(cls, chart) -> "CanonicalBaziChart":
        """Create CanonicalBaziChart from BaziChart.

        Args:
            chart: BaziChart instance from BaziAdapter.compute()

        Returns:
            CanonicalBaziChart with all four pillars and metadata
        """
        return cls(
            year_pillar=chart.year_pillar,
            month_pillar=chart.month_pillar,
            day_pillar=chart.day_pillar,
            hour_pillar=chart.hour_pillar,
            day_master=chart.day_master,
            gender=chart.gender,
            start_age=chart.start_age,
            birth_datetime=chart.birth_datetime,
        )

    @property
    def bazi(self) -> List[tuple[str, str]]:
        """Return four pillars as list of (stem, branch) tuples.

        Returns:
            [("JIA", "CHEN"), ("XIN", "WEI"), ("WU", "CHEN"), ("WU", "WU")]
        """
        return [
            (self.year_pillar.heavenly_stem, self.year_pillar.earthly_branch),
            (self.month_pillar.heavenly_stem, self.month_pillar.earthly_branch),
            (self.day_pillar.heavenly_stem, self.day_pillar.earthly_branch),
            (self.hour_pillar.heavenly_stem, self.hour_pillar.earthly_branch),
        ]

    @property
    def birth_hour(self) -> str:
        """Return birth hour branch (e.g., 'WU' for 午时)."""
        return self.hour_pillar.earthly_branch

    def __repr__(self) -> str:
        return (
            f"CanonicalBaziChart("
            f"year={self.year_pillar}, "
            f"month={self.month_pillar}, "
            f"day={self.day_pillar}, "
            f"hour={self.hour_pillar}, "
            f"dm={self.day_master}, "
            f"g={self.gender}, "
            f"age={self.start_age})"
        )
