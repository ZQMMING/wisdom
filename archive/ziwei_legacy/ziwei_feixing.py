"""紫微斗数飞星派断事方法 — Z6

独立的飞化路径建模系统，与三合/中州/钦天完全不同逻辑。
依据：梁若瑜《专论四化》《十八飞星秘仪》

核心能力：
1. 宫干飞化路径追踪
2. 禄忌轨迹分析
3. 不依赖小限
4. 宫位互动关系分析
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
class FeihuaStep:
    """单次飞化步骤"""
    from_palace: str
    from_stem: str
    sihua_type: str  # "禄"|"权"|"科"|"忌"
    target_star: str
    to_palace: str
    to_branch: str


@dataclass(frozen=True)
class LuJiTrajectory:
    """禄忌轨迹"""
    palace_name: str
    lu_star: str
    ji_star: str
    lu_palace: str
    ji_palace: str
    interaction: str  # "相生"|"相克"|"比和"


# ============================================================================
# 飞星派分析器
# ============================================================================

class FeixingAnalyzer:
    """飞星派命盘分析器
    
    独立的飞化路径建模，不与三合派共享逻辑。
    """
    
    # 飞星派专用四化表（通常与通行版一致）
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
        self.rules = RuleGraph.load("feixing")
        self._cache: dict[str, Any] = {}
    
    # ── 宫干飞化 ────────────────────────────────────────────────
    
    def trace_gonggan_feihua(self, palace_name: str) -> list[FeihuaStep]:
        """追踪宫干飞化路径
        
        从指定宫位的宫干出发，追踪四化落宫。
        依据：梁若瑜《专论四化》
        """
        pf = self.fact.palaces.get(palace_name)
        if not pf or not pf.heavenly_stem:
            return []
        
        stem = pf.heavenly_stem
        sihua_stars = self.SIHUA_TABLE.get(stem)
        if not sihua_stars:
            return []
        
        steps = []
        branches = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
        
        for i, star in enumerate(sihua_stars[:4]):
            # 查找该星所在宫位
            for other_name, other_pf in self.fact.palaces.items():
                all_stars = other_pf.major_stars + other_pf.minor_stars
                if star in all_stars:
                    steps.append(FeihuaStep(
                        from_palace=palace_name,
                        from_stem=stem,
                        sihua_type=["禄", "权", "科", "忌"][i],
                        target_star=star,
                        to_palace=other_name,
                        to_branch=other_pf.earthly_branch,
                    ))
                    break
        
        return steps
    
    def all_gonggan_feihua(self) -> dict[str, list[FeihuaStep]]:
        """所有宫位的宫干飞化"""
        result = {}
        for pname in self.fact.palaces:
            result[pname] = self.trace_gonggan_feihua(pname)
        return result
    
    # ── 禄忌轨迹 ────────────────────────────────────────────────
    
    def analyze_lu_ji_trajectory(self) -> list[LuJiTrajectory]:
        """分析禄忌轨迹
        
        禄星和忌星所在宫位的互动关系。
        依据：梁若瑜《十八飞星秘仪》
        """
        results = []
        
        # 找禄星和忌星
        lu_star = None
        ji_star = None
        lu_palace = None
        ji_palace = None
        
        mutagen = self.fact.birth_mutagen
        if mutagen and mutagen.mutagens:
            if len(mutagen.mutagens) > 0:
                lu_star = mutagen.mutagens[0]
            if len(mutagen.mutagens) > 3:
                ji_star = mutagen.mutagens[3]
        
        if lu_star and ji_star:
            # 找落宫
            for pname, pf in self.fact.palaces.items():
                all_stars = pf.major_stars + pf.minor_stars
                if lu_star in all_stars and lu_palace is None:
                    lu_palace = pname
                if ji_star in all_stars and ji_palace is None:
                    ji_palace = pname
        
        if lu_palace and ji_palace:
            # 判断互动关系
            interaction = self._calculate_interaction(lu_palace, ji_palace)
            results.append(LuJiTrajectory(
                palace_name=self.fact.soul_palace.name if self.fact.soul_palace else "命宫",
                lu_star=lu_star,
                ji_star=ji_star,
                lu_palace=lu_palace,
                ji_palace=ji_palace,
                interaction=interaction,
            ))
        
        return results
    
    def _calculate_interaction(self, palace_a: str, palace_b: str) -> str:
        """计算两宫互动关系"""
        PALACE_NAMES = ["命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄", 
                       "迁移", "仆役", "官禄", "田宅", "福德", "父母"]
        try:
            idx_a = PALACE_NAMES.index(palace_a)
            idx_b = PALACE_NAMES.index(palace_b)
            
            # 同宫
            if idx_a == idx_b:
                return "同宫"
            
            # 对冲
            if (idx_a - idx_b) % 12 == 6:
                return "对冲"
            
            # 三合
            if (idx_a - idx_b) % 4 == 0:
                return "三合"
            
            # 其他
            return "相邻"
        except ValueError:
            return "未知"
    
    # ── 宫干分析 ────────────────────────────────────────────────
    
    def analyze_gonggan_system(self) -> dict:
        """宫干系统分析
        
        分析各宫天干引发的四化落宫情况。
        """
        all_feihua = self.all_gonggan_feihua()
        
        # 统计每个宫被飞化的次数
        hit_count = {}
        for steps in all_feihua.values():
            for step in steps:
                hit_count[step.to_palace] = hit_count.get(step.to_palace, 0) + 1
        
        return {
            "all_feihua": {k: [s.__dict__ for s in v] for k, v in all_feihua.items()},
            "hit_count": hit_count,
            "most_hit_palace": max(hit_count, key=hit_count.get) if hit_count else None,
        }
    
    # ── 命盘评估 ────────────────────────────────────────────────
    
    def full_analysis(self) -> dict:
        """完整飞星派分析"""
        gonggan = self.analyze_gonggan_system()
        trajectory = self.analyze_lu_ji_trajectory()
        
        return {
            "method": "feixing",
            "gonggan_system": gonggan,
            "lu_ji_trajectory": [t.__dict__ for t in trajectory],
            "notes": {
                "no_xiaoxian": True,  # 飞星派不使用小限
                "gonggan_priority": True,  # 宫干飞化优先
            },
        }


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "FeixingAnalyzer",
    "FeihuaStep",
    "LuJiTrajectory",
]
