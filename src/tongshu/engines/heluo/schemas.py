"""河洛数据类（frozen dataclass）— 向后兼容。

新版请用 numbers.TianDiShu 替代 TianDiNumbers。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class Trigram:
    """八卦一个（不包括上下卦位）。"""
    name: str
    index: int
    element: str
    nature: Literal["阳", "阴"]
    binary: str


@dataclass(frozen=True)
class Hexagram:
    """六十四卦一个（上卦下卦位）。"""
    number: int
    name: str
    upper: Trigram
    lower: Trigram


@dataclass(frozen=True)
class StemNumberMap:
    """天干取数定局（C-01 / C-02 同一映射）。"""
    values: dict[str, int]


@dataclass(frozen=True)
class BranchNumberMap:
    """地支取数定局（C-03）。"""
    values: dict[str, tuple[int, int]]


@dataclass(frozen=True)
class TianDiNumbers:
    """天数 / 地数（向后兼容）。"""
    tian_numbers: tuple[int, ...]
    di_numbers: tuple[int, ...]
    tian_total: int
    di_total: int


@dataclass(frozen=True)
class YuanTangResult:
    """元堂取法结果（向后兼容）。"""
    hexagram: "Hexagram"
    yao_index: int
    yao_nature: Literal["阳", "阴"]
    mapping: dict[str, int] = field(default_factory=dict)
    rule_variant: str = "default"


__all__ = [
    "Trigram", "Hexagram", "StemNumberMap", "BranchNumberMap",
    "TianDiNumbers", "YuanTangResult",
]
