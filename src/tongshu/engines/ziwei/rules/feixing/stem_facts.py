from dataclasses import dataclass, field
from typing import Literal

from ....ziwei_engine import FrozenZiweiChart, GAN_SIHUA


# ============================================================================
# Z13-A: PalaceStemFact — 宫干事实层
# ============================================================================


@dataclass(frozen=True)
class PalaceStemFact:
    """单宫宫干事实：纯计算事实，无诊断语义。"""
    palace_name: str
    stem: str
    branch: str
    major_stars: tuple[str, ...] = field(default_factory=tuple)
    minor_stars: tuple[str, ...] = field(default_factory=tuple)

    def has_stem(self) -> bool:
        return bool(self.stem)

    def to_dict(self) -> dict:
        return {
            "palace_name": self.palace_name,
            "stem": self.stem,
            "branch": self.branch,
            "major_stars": list(self.major_stars),
            "minor_stars": list(self.minor_stars),
        }


class PalaceStemContract:
    """宫干事实契约：从 FrozenZiweiChart 提取确定性宫干事实。

    Z13-A 独立层：不涉及任何飞化计算，只返回事实。
    """

    @staticmethod
    def extract(chart: FrozenZiweiChart) -> tuple[PalaceStemFact, ...]:
        """从 chart 提取全部 12 宫的宫干事实。"""
        facts: list[PalaceStemFact] = []
        for palace_name, pd in chart.palaces.items():
            facts.append(PalaceStemFact(
                palace_name=palace_name,
                stem=pd.get("stem", ""),
                branch=pd.get("branch", ""),
                major_stars=tuple(pd.get("major", [])),
                minor_stars=tuple(pd.get("minor", [])),
            ))
        return tuple(facts)

    @staticmethod
    def get_palace_stem(chart: FrozenZiweiChart, palace_name: str) -> str:
        """安全获取指定宫位的宫干（空字符串表示无宫干）。"""
        return chart.palaces.get(palace_name, {}).get("stem", "")

    @staticmethod
    def has_self_mutagen(palace_fact: PalaceStemFact) -> bool:
        """判断某宫是否有自化（宫干四化落回本宫）。"""
        if not palace_fact.stem:
            return False
        sihua = GAN_SIHUA.get(palace_fact.stem, ())
        if not sihua:
            return False
        all_stars = set(palace_fact.major_stars) | set(palace_fact.minor_stars)
        return any(star in all_stars for star in sihua)


# ============================================================================
# Z13-B: FlyingTransform — 飞化事实层
# ============================================================================


@dataclass(frozen=True)
class FlyingTransformFact:
    """单次飞化事实：宫干 → 四化 → 落宫。

    例如：命宫(甲) → 廉贞化禄 → 子女宫
    这是纯事实，不含"事业好/坏"等判断。
    """
    source_palace: str
    source_stem: str
    transformation: str
    target_star: str
    target_palace: str
    direction: Literal["in", "out", "self"]

    def to_dict(self) -> dict:
        return {
            "source_palace": self.source_palace,
            "source_stem": self.source_stem,
            "transformation": self.transformation,
            "target_star": self.target_star,
            "target_palace": self.target_palace,
            "direction": self.direction,
        }
