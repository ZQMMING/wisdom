"""紫微斗数中州派断事方法 — Z5

继承三合派，扩展中州派特殊规则。
依据：王亭之《谈斗数》《紫微斗数讲义》

特殊能力：
1. 流昌流曲分析
2. 空宫全借对宫
3. 戊干太阳化科
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .ziwei_fact_layer import ZiweiFact, PalaceFact
from .ziwei_sanhe import SanheAnalyzer
from .ziwei_rule_graph import RuleGraph, RuleType


@dataclass(frozen=True)
class LiuchangLiuquResult:
    """流昌流曲分析结果"""
    palace_name: str
    star_type: str  # "流昌" or "流曲"
    has_star: bool


@dataclass(frozen=True)
class EmptyPalaceResult:
    """空宫处理结果"""
    palace_name: str
    borrowed_from: str | None
    borrowed_stars: tuple[str, ...]


class ZhongzhouAnalyzer(SanheAnalyzer):
    """中州派命盘分析器
    
    继承 SanheAnalyzer，添加中州派特殊规则。
    """
    
    def __init__(self, fact: ZiweiFact):
        super().__init__(fact)
        self.rules = RuleGraph.load("zhongzhou")
    
    # ── 中州派特殊分析 ────────────────────────────────────────
    
    def analyze_liuchangliuqu(self) -> list[LiuchangLiuquResult]:
        """分析流昌流曲（中州派独有）
        
        流昌流曲是运限辅助星曜，用于增强星曜力量。
        依据：王亭之《紫微斗数讲义》
        """
        results = []
        
        # 检查各宫是否含有流昌流曲
        for pname, pf in self.fact.palaces.items():
            all_stars = pf.major_stars + pf.minor_stars
            if "流昌" in all_stars:
                results.append(LiuchangLiuquResult(
                    palace_name=pname,
                    star_type="流昌",
                    has_star=True,
                ))
            if "流曲" in all_stars:
                results.append(LiuchangLiuquResult(
                    palace_name=pname,
                    star_type="流曲",
                    has_star=True,
                ))
        
        return results
    
    def analyze_empty_palace_full_borrow(self) -> list[EmptyPalaceResult]:
        """分析空宫全借对宫（中州派特性）
        
        中州派主张空宫时全借对宫主星，与三合派的"部分借"不同。
        依据：王亭之《谈斗数》
        """
        results = []
        BRANCHES = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
        
        for pname, pf in self.fact.palaces.items():
            if not pf.is_empty:
                continue
            
            # 找对宫
            try:
                branch_idx = BRANCHES.index(pf.earthly_branch)
                opposite_branch = BRANCHES[(branch_idx + 6) % 12]
                
                # 找对宫
                opposite_palace = None
                for other_name, other_pf in self.fact.palaces.items():
                    if other_pf.earthly_branch == opposite_branch:
                        opposite_palace = other_pf
                        break
                
                if opposite_palace and opposite_palace.major_stars:
                    results.append(EmptyPalaceResult(
                        palace_name=pname,
                        borrowed_from=opposite_palace.name,
                        borrowed_stars=opposite_palace.major_stars,
                    ))
                else:
                    results.append(EmptyPalaceResult(
                        palace_name=pname,
                        borrowed_from=None,
                        borrowed_stars=(),
                    ))
            except ValueError:
                results.append(EmptyPalaceResult(
                    palace_name=pname,
                    borrowed_from=None,
                    borrowed_stars=(),
                ))
        
        return results
    
    def check_wu_gan_taiyang_hua_ke(self) -> bool:
        """检查戊干太阳化科（中州派特殊四化）
        
        中州派戊干四化：贪狼禄、太阴权、太阳科、天机忌
        与通行版不同（通行版戊干右弼化科）
        
        依据：王亭之《谈斗数》
        """
        # 检查命宫天干是否为戊
        soul_palace = self.fact.soul_palace
        if not soul_palace:
            return False
        
        return soul_palace.heavenly_stem == "戊"
    
    # ── 覆盖父类方法 ──────────────────────────────────────────
    
    def analyze_palace(self, palace_name: str) -> dict:
        """覆盖宫位分析，使用中州派空宫全借逻辑"""
        result = super().analyze_palace(palace_name)
        
        # 如果是空宫，添加借星信息
        if result.empty:
            empty_results = self.analyze_empty_palace_full_borrow()
            for er in empty_results:
                if er.palace_name == palace_name:
                    return {**result.__dict__, "borrowed_stars": er.borrowed_stars}
        
        return result.__dict__
    
    def full_analysis(self) -> dict:
        """完整分析，包含中州派特殊项"""
        base = super().full_analysis()
        
        base["zhongzhou_special"] = {
            "liuchangliuqu": self.analyze_liuchangliuqu(),
            "empty_palace_borrow": self.analyze_empty_palace_full_borrow(),
            "wu_gan_taiyang_ke": self.check_wu_gan_taiyang_hua_ke(),
        }
        
        return base


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "ZhongzhouAnalyzer",
    "LiuchangLiuquResult",
    "EmptyPalaceResult",
]
