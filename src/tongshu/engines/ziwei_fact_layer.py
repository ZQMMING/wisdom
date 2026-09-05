"""紫微斗数事实层 — Z2 Fact Layer

职责：
  - 定义完整的紫微事实数据结构（ZiweiFact）
  - 从 full_chart() 原始数据转换为结构化事实
  - 不依赖 MethodProfile，纯事实提取

设计原则：
  1. Fact Layer 是 immutable 的 — 一旦计算完成不应修改
  2. Fact Layer 不包含任何断事逻辑 — 那是 Rule/Method 层的职责
  3. Fact Layer 支持 MethodProfile 切换 — 同事实可用不同方法分析

与 ZiweiChart 的区别：
  - ZiweiChart: 计算结果摘要（仅命宫主星+四化）
  - ZiweiFact: 完整盘面事实（12宫全部数据）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Sequence


# ============================================================================
# 基础类型
# ============================================================================

@dataclass(frozen=True)
class PalaceFact:
    """单个宫位的事实数据"""
    
    # 宫位标识
    name: str                    # 宫名（命宫、兄弟、夫妻...）
    earthly_branch: str          # 地支（子、丑、寅...）
    heavenly_stem: str           # 天干（甲、乙、丙...）
    
    # 星曜事实
    major_stars: tuple[str, ...] = field(default_factory=tuple)   # 主星
    minor_stars: tuple[str, ...] = field(default_factory=tuple)   # 辅星
    
    # 大限事实
    decadal_range: tuple[int, int] | None = None  # 大限范围 (起始岁数, 结束岁数)
    decadal_stem: str = ""            # 大限天干
    decadal_branch: str = ""          # 大限地支
    
    # 四化事实（由宫干引发）
    self_mutagen: tuple[str, ...] = field(default_factory=tuple)  # 自化列表 ("自化禄", ...)
    
    # 空宫标记
    is_empty: bool = False            # 是否无主星
    
    def __post_init__(self):
        # 计算空宫标记
        if not object.__getattribute__(self, 'is_empty'):
            object.__setattr__(self, 'is_empty', len(self.major_stars) == 0)


@dataclass(frozen=True)
class MutagenFact:
    """某时间周期的四化事实"""
    
    # 时间标识
    year: int | None = None           # 年份（None 表示本命）
    month: int | None = None          # 月份（None 表示大限）
    day: int | None = None            # 日期（None 表示流月）
    
    # 四化星
    mutagens: tuple[str, ...] = field(default_factory=tuple)  # (禄,权,科,忌)
    
    @property
    def hua_lu(self) -> str | None:
        return self.mutagens[0] if len(self.mutagens) > 0 else None
    
    @property
    def hua_quan(self) -> str | None:
        return self.mutagens[1] if len(self.mutagens) > 1 else None
    
    @property
    def hua_ke(self) -> str | None:
        return self.mutagens[2] if len(self.mutagens) > 2 else None
    
    @property
    def hua_ji(self) -> str | None:
        return self.mutagens[3] if len(self.mutagens) > 3 else None


# ============================================================================
# 核心事实层
# ============================================================================

@dataclass(frozen=True)
class ZiweiFact:
    """紫微斗数完整事实层
    
    包含：
    - 五行局（纳音起局基础）
    - 命宫/身宫信息
    - 12宫完整数据
    - 各时间周期四化
    """
    
    # === 基础信息 ===
    five_elements_class: str = ""         # 五行局（水二局、木三局...）
    soul_earthly_branch: str = ""         # 命宫地支
    body_earthly_branch: str = ""         # 身宫地支
    soul_borrowed: bool = False           # 命宫是否借对宫主星
    
    # === 12宫数据 ===
    palaces: dict[str, PalaceFact] = field(default_factory=dict)
    
    # === 四化数据 ===
    birth_mutagen: MutagenFact = field(default_factory=MutagenFact)        # 生年四化
    decadal_mutagen: MutagenFact = field(default_factory=MutagenFact)      # 大限四化
    yearly_mutagen: MutagenFact = field(default_factory=MutagenFact)       # 流年四化
    monthly_mutagen: MutagenFact = field(default_factory=MutagenFact)      # 流月四化
    daily_mutagen: MutagenFact = field(default_factory=MutagenFact)        # 流日四化
    
    # === 元数据 ===
    source: str = "unknown"                 # 数据来源 (iztro/stub)
    calculation_version: str = "2026.09"   # 计算方法版本
    
    # === 派生属性 ===
    
    @property
    def soul_palace(self) -> PalaceFact | None:
        """命宫事实"""
        for pf in self.palaces.values():
            if pf.name == "命宫":
                return pf
        return None
    
    @property
    def body_palace(self) -> PalaceFact | None:
        """身宫事实"""
        for pf in self.palaces.values():
            if pf.name == "身宫":
                return pf
        return None
    
    @property
    def soul_main_stars(self) -> tuple[str, ...]:
        """命宫主星（已处理借星）"""
        sp = self.soul_palace
        if sp and sp.major_stars:
            return sp.major_stars
        if self.soul_borrowed:
            # 借对宫主星
            opposite_branch = _opposite_branch(self.soul_earthly_branch)
            for pf in self.palaces.values():
                if pf.earthly_branch == opposite_branch and pf.major_stars:
                    return pf.major_stars
        return ()
    
    @property
    def empty_palaces(self) -> FrozenSet[str]:
        """所有空宫名称集合"""
        return frozenset(name for name, pf in self.palaces.items() if pf.is_empty)
    
    @property
    def all_branches(self) -> dict[str, str]:
        """宫名->地支映射"""
        return {name: pf.earthly_branch for name, pf in self.palaces.items()}
    
    def to_dict(self) -> dict:
        """序列化为字典（用于测试和调试）"""
        return {
            "five_elements_class": self.five_elements_class,
            "soul_earthly_branch": self.soul_earthly_branch,
            "body_earthly_branch": self.body_earthly_branch,
            "soul_borrowed": self.soul_borrowed,
            "palaces": {
                name: {
                    "name": pf.name,
                    "branch": pf.earthly_branch,
                    "stem": pf.heavenly_stem,
                    "major": list(pf.major_stars),
                    "minor": list(pf.minor_stars),
                    "decadal_range": pf.decadal_range,
                    "is_empty": pf.is_empty,
                }
                for name, pf in self.palaces.items()
            },
            "birth_mutagen": list(self.birth_mutagen.mutagens) if self.birth_mutagen.mutagens else [],
            "source": self.source,
        }


# ============================================================================
# 工具函数
# ============================================================================

def _opposite_branch(branch: str) -> str:
    """获取对冲地支"""
    BRANCHES = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
    try:
        idx = BRANCHES.index(branch)
        return BRANCHES[(idx + 6) % 12]
    except ValueError:
        return ""


def _branch_to_sanfang(branch: str) -> tuple[str, str, str, str]:
    """获取三方四正地支（本宫、对宫、三合1、三合2）"""
    BRANCHES = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
    try:
        idx = BRANCHES.index(branch)
        return (
            branch,
            BRANCHES[(idx + 6) % 12],      # 对宫
            BRANCHES[(idx + 4) % 12],      # 三合1
            BRANCHES[(idx + 8) % 12],      # 三合2
        )
    except ValueError:
        return (branch, "", "", "")


def build_ziwei_fact(raw_chart: dict, birth_mutagen: list[str] | None = None) -> ZiweiFact:
    """从 full_chart() 原始数据构建 ZiweiFact
    
    Args:
        raw_chart: iztro full_chart() 返回的字典
        birth_mutagen: 生年四化星列表（可选，不传则从宫干推导）
    
    Returns:
        ZiweiFact 实例
    """
    palaces = {}
    for pname, pdata in raw_chart.get("palaces", {}).items():
        major = tuple(pdata.get("major", []))
        minor = tuple(pdata.get("minor", []))
        drange = pdata.get("decadalRange", [])
        decadal_range = (drange[0], drange[1]) if len(drange) == 2 else None
        
        # 计算自化（需要 GAN_SIHUA，此处暂不计算，由后续方法层处理）
        palaces[pname] = PalaceFact(
            name=pname,
            earthly_branch=pdata.get("branch", ""),
            heavenly_stem=pdata.get("stem", ""),
            major_stars=major,
            minor_stars=minor,
            decadal_range=decadal_range,
            decadal_stem=pdata.get("decadalStem", ""),
            decadal_branch=pdata.get("decadalBranch", ""),
        )
    
    # 构建出生四化
    birth_mut = birth_mutagen or []
    birth_mutagen_fact = MutagenFact(mutagens=tuple(birth_mut))
    
    return ZiweiFact(
        five_elements_class=raw_chart.get("fiveElementsClass", ""),
        soul_earthly_branch=raw_chart.get("soulPalaceBranch", ""),
        body_earthly_branch=raw_chart.get("bodyPalaceBranch", ""),
        palaces=palaces,
        birth_mutagen=birth_mutagen_fact,
        source="iztro",
    )


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "PalaceFact",
    "MutagenFact",
    "ZiweiFact",
    "build_ziwei_fact",
    "_opposite_branch",
    "_branch_to_sanfang",
]
