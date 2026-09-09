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

import weakref
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from tongshu.engines.bazi_engine import BaziChart, Pillar

# BZ-FNDR-10.1 (R-15 ⑭ 契约加固): 构造来源 provenance 常量.
# 用于把 "from_bazi_chart() 是唯一有效构造路径" 从文档声明升级为可机器校验契约.
CANONICAL_PROVENANCE_FACTORY = "from_bazi_chart"
CANONICAL_PROVENANCE_DIRECT = "direct-construction"

# BZ-FNDR-10.1: 经 from_bazi_chart() 工厂构造的实例集合 (weakref, 不阻止 GC).
# 下游 Engine Adapter 可用 is_factory_provenance() / assert_canonical_gate()
# 校验某个 CanonicalBaziChart 是否来自合法工厂路径, 而非直接堆 4 柱.
_FACTORY_INSTANCES: "weakref.WeakSet[CanonicalBaziChart]" = weakref.WeakSet()


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
    birth_datetime: Optional[datetime] = None

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
        instance = cls(
            year_pillar=chart.year_pillar,
            month_pillar=chart.month_pillar,
            day_pillar=chart.day_pillar,
            hour_pillar=chart.hour_pillar,
            day_master=chart.day_master,
            gender=chart.gender,
            start_age=chart.start_age,
            birth_datetime=chart.birth_datetime,
        )
        # BZ-FNDR-10.1: 把工厂构造的实例登记进 provenance 集合,
        # 使 is_factory_provenance() / assert_canonical_gate() 可机器校验.
        _FACTORY_INSTANCES.add(instance)
        return instance

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


# ============================================================================
# BZ-FNDR-10.1 (R-15 ⑭ 契约加固): 可执行构造路径 gate.
#
# 把 "from_bazi_chart() 是唯一有效构造路径" 从文档声明升级为机器可校验契约.
# 下游 Engine Adapter 在消费 CanonicalBaziChart 前调用 assert_canonical_gate(),
# 确保该实例来自合法工厂路径, 而非下游直接堆 4 柱 (MUST NOT recompute).
#
# 注意: 这是"可校验的软约束", 不改动 dataclass 结构、不新增字段、
# 不阻断语言层直接实例化 — 仅提供 provenance 追踪 + 显式 gate.
# ============================================================================

def is_factory_provenance(instance: "CanonicalBaziChart") -> bool:
    """返回该 CanonicalBaziChart 是否经 from_bazi_chart() 工厂构造.

    BZ-FNDR-10.1: 用于下游校验构造来源. 工厂构造的实例被登记进
    _FACTORY_INSTANCES; 直接实例化的实例不在此集合.

    Args:
        instance: 待校验的 CanonicalBaziChart

    Returns:
        True 若来自 from_bazi_chart(), False 若直接构造
    """
    return instance in _FACTORY_INSTANCES


def provenance_of(instance: "CanonicalBaziChart") -> str:
    """返回该实例的 provenance 标签.

    返回 CANONICAL_PROVENANCE_FACTORY (工厂) 或 CANONICAL_PROVENANCE_DIRECT (直接).
    """
    return (
        CANONICAL_PROVENANCE_FACTORY
        if is_factory_provenance(instance)
        else CANONICAL_PROVENANCE_DIRECT
    )


def assert_canonical_gate(
    instance: "CanonicalBaziChart",
    require_factory: bool = True,
) -> None:
    """下游 Engine Adapter 的消费前 gate (BZ-FNDR-10.1).

    把 "CanonicalBaziChart = 八字计算层冻结输入, 下游不得重排四柱" 变成
    可执行检查: require_factory=True 时, 若实例非工厂构造则 fail-closed 抛错.

    Args:
        instance: 待消费的 CanonicalBaziChart
        require_factory: True = 要求必须来自 from_bazi_chart() (默认);
                         False = 仅记录 provenance, 不阻断 (审计模式).

    Raises:
        ValueError: require_factory=True 且实例非工厂构造时.
    """
    if require_factory and not is_factory_provenance(instance):
        raise ValueError(
            "CanonicalBaziChart consumed by downstream engine must be built "
            "via CanonicalBaziChart.from_bazi_chart(bazi_engine.compute(...)). "
            "This instance was constructed directly (provenance="
            f"{provenance_of(instance)!r}). Downstream MUST NOT recompute "
            "four pillars (V2 一入口原则 + ⑭ 契约)."
        )
