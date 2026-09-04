"""紫微斗数钦天门断事方法 — Z7

向心/离心忌系统 + 立极宫分析。
依据：蔡明宏《华山钦天四化紫微斗数飞星秘仪》

核心能力：
1. 向心忌（他宫化忌入本命）
2. 离心忌（本命化忌入他宫）
3. 立极宫分析
4. 四化飞星深度解读
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .ziwei_fact_layer import ZiweiFact, PalaceFact, MutagenFact
from .ziwei_rule_graph import RuleGraph, RuleType


# ============================================================================
# 类型定义
# ============================================================================

@dataclass(frozen=True)
class XiangxinJiResult:
    """向心忌结果"""
    source_palace: str
    target_palace: str
    sihua_type: str
    star: str
    strength: str  # "强"|"中"|"弱"


@dataclass(frozen=True)
class LixinJiResult:
    """离心忌结果"""
    source_palace: str
    target_palace: str
    sihua_type: str
    star: str
    strength: str


@dataclass(frozen=True)
class LiJiResult:
    """立极宫分析结果"""
    center_palace: str
    center_stem: str
    direction_analysis: dict[str, Any]


# ============================================================================
# 钦天门分析器
# ============================================================================

class QintianAnalyzer:
    """钦天门命盘分析器
    
    向心/离心忌系统是钦天门的特色。
    """
    
    # 钦天门专用四化表（与通行版一致）
    SIHUA_TABLE = {
        "甲": ("廉贞", "破军", "武曲", "太阳"),
        "乙": ("天机", "天梁", "紫微", "太阴"),
        "丙": ("天同", "天机", "文昌", "廉贞"),
        "丁": ("太阴", "天同", "天机", "巨门"),
        "戊": ("贪狼", "太阴", "右弼", "天机"),
        "己": ("武曲", "贪狼", "天梁", "文曲"),
        "庚": ("太阳", "武曲", "太阴", "天同"),
        "辛": ("巨门", "太阳", "文曲", "文昌"),
        "壬": ("天梁", "紫微", "左辅", "武曲"),
        "癸": ("破军", "巨门", "太阴", "贪狼"),
    }
    
    def __init__(self, fact: ZiweiFact):
        self.fact = fact
        self.rules = RuleGraph.load("qintian")
        self._cache: dict[str, Any] = {}
    
    # ── 向心忌 ────────────────────────────────────────────────
    
    def analyze_xiangxin_ji(self) -> list[XiangxinJiResult]:
        """分析向心忌
        
        向心忌 = 某宫宫干化忌，落入本命宫或其他重要宫位。
        这是"外力对我宫的冲击"。
        
        依据：蔡明宏《华山钦天四化秘仪》
        """
        results = []
        branches = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
        
        # 获取命宫
        soul_palace = self.fact.soul_palace
        if not soul_palace:
            return results
        
        # 遍历所有宫位，检查其宫干四化是否落入重要宫位
        important_palaces = {"命宫", "兄弟", "夫妻", "子女", "财帛", "官禄"}
        
        for pname, pf in self.fact.palaces.items():
            if not pf.heavenly_stem:
                continue
            
            stem = pf.heavenly_stem
            sihua_stars = self.SIHUA_TABLE.get(stem)
            if not sihua_stars:
                continue
            
            ji_star = sihua_stars[3]  # 忌是第四个
            
            # 查找忌星所在宫位
            for other_name, other_pf in self.fact.palaces.items():
                all_stars = other_pf.major_stars + other_pf.minor_stars
                if ji_star in all_stars and other_name in important_palaces:
                    strength = self._calculate_ji_strength(pname, other_name)
                    results.append(XiangxinJiResult(
                        source_palace=pname,
                        target_palace=other_name,
                        sihua_type="忌",
                        star=ji_star,
                        strength=strength,
                    ))
        
        return results
    
    # ── 离心忌 ────────────────────────────────────────────────
    
    def analyze_lixin_ji(self) -> list[LixinJiResult]:
        """分析离心忌
        
        离心忌 = 本命宫宫干化忌，落入他宫。
        这是"我对外的影响/损失"。
        
        依据：蔡明宏《华山钦天四化秘仪》
        """
        results = []
        
        soul_palace = self.fact.soul_palace
        if not soul_palace or not soul_palace.heavenly_stem:
            return results
        
        stem = soul_palace.heavenly_stem
        sihua_stars = self.SIHUA_TABLE.get(stem)
        if not sihua_stars:
            return results
        
        ji_star = sihua_stars[3]  # 忌
        
        # 查找忌星所在宫位
        for pname, pf in self.fact.palaces.items():
            if pname == "命宫":
                continue
            all_stars = pf.major_stars + pf.minor_stars
            if ji_star in all_stars:
                strength = self._calculate_ji_strength("命宫", pname)
                results.append(LixinJiResult(
                    source_palace="命宫",
                    target_palace=pname,
                    sihua_type="忌",
                    star=ji_star,
                    strength=strength,
                ))
        
        return results
    
    # ── 立极宫 ────────────────────────────────────────────────
    
    def liji_analysis(self, center_palace: str | None = None) -> LiJiResult:
        """立极宫分析
        
        钦天门以某一宫为立极点，分析其他宫位对此立极点的四化关系。
        默认以命宫为立极点。
        
        依据：蔡明宏《华山钦天四化秘仪》
        """
        if center_palace is None:
            center_palace = "命宫"
        
        center_pf = self.fact.palaces.get(center_palace)
        if not center_pf:
            return LiJiResult(
                center_palace=center_palace,
                center_stem="",
                direction_analysis={},
            )
        
        # 分析各宫对中心宫的向心/离心关系
        direction_analysis = {
            "xiangxin": [],  # 向心
            "lixin": [],     # 离心
            "self_hua": [],  # 自化
        }
        
        for pname, pf in self.fact.palaces.items():
            if not pf.heavenly_stem:
                continue
            
            stem = pf.heavenly_stem
            sihua_stars = self.SIHUA_TABLE.get(stem)
            if not sihua_stars:
                continue
            
            # 检查四化落宫
            for i, star in enumerate(sihua_stars[:4]):
                sihua_type = ["禄", "权", "科", "忌"][i]
                
                for other_name, other_pf in self.fact.palaces.items():
                    all_stars = other_pf.major_stars + other_pf.minor_stars
                    if star in all_stars:
                        if other_name == center_palace:
                            direction_analysis["xiangxin"].append({
                                "from": pname,
                                "type": sihua_type,
                                "star": star,
                            })
                        elif pname == center_palace:
                            direction_analysis["lixin"].append({
                                "from": pname,
                                "type": sihua_type,
                                "star": star,
                                "to": other_name,
                            })
        
        return LiJiResult(
            center_palace=center_palace,
            center_stem=center_pf.heavenly_stem,
            direction_analysis=direction_analysis,
        )
    
    # ── 辅助方法 ────────────────────────────────────────────────
    
    def _calculate_ji_strength(self, from_palace: str, to_palace: str) -> str:
        """计算忌的力量强度"""
        important = {"命宫", "官禄", "财帛", "迁移"}
        
        if from_palace in important and to_palace in important:
            return "强"
        elif from_palace in important or to_palace in important:
            return "中"
        return "弱"
    
    # ── 完整分析 ────────────────────────────────────────────────
    
    def full_analysis(self) -> dict:
        """完整钦天门分析"""
        xiangxin = self.analyze_xiangxin_ji()
        lixin = self.analyze_lixin_ji()
        liji = self.liji_analysis()
        
        return {
            "method": "qintian",
            "xiangxin_ji": [r.__dict__ for r in xiangxin],
            "lixin_ji": [r.__dict__ for r in lixin],
            "liji_analysis": liji.__dict__,
            "summary": {
                "xiangxin_count": len(xiangxin),
                "lixin_count": len(lixin),
                "strong_ji_count": sum(1 for r in xiangxin + lixin if r.strength == "强"),
            },
        }


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "QintianAnalyzer",
    "XiangxinJiResult",
    "LixinJiResult",
    "LiJiResult",
]
