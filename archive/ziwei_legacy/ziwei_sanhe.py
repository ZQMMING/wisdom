"""紫微斗数三合派断事方法 — Z4

基于 RuleGraph 实现三合派完整的命盘分析逻辑。
依据：《紫微斗数全书》《全集》

核心能力：
1. 格局识别（三方四正分析）
2. 四化解读（生年/大限/流年）
3. 宫位分析（十二宫主题）
4. 命盘整体评估
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .ziwei_fact_layer import ZiweiFact, PalaceFact
from .ziwei_rule_graph import RuleGraph, RuleType


# ============================================================================
# 类型定义
# ============================================================================

@dataclass(frozen=True)
class PatternResult:
    """格局识别结果"""
    pattern_id: str
    pattern_name: str
    confidence: float  # 0-1
    details: dict = field(default_factory=dict)


@dataclass(frozen=True)
class SiHuaResult:
    """四化解读结果"""
    sihua_type: str  # "禄"|"权"|"科"|"忌"
    star: str
    palace: str
    source: str  # "birth"|"decadal"|"yearly"
    impact: str  # "strong"|"moderate"|"weak"


@dataclass(frozen=True)
class PalaceAnalysis:
    """宫位分析结果"""
    palace_name: str
    main_stars: tuple[str, ...]
    has_sihua: bool
    empty: bool
    sanfang_summary: list[str] = field(default_factory=list)
    borrowed_stars: tuple[str, ...] = field(default_factory=tuple)


# ============================================================================
# 三合派分析器
# ============================================================================

class SanheAnalyzer:
    """三合派命盘分析器
    
    基于 Z2 Fact Layer + Z3 Rule Graph 实现完整三合派断事。
    """
    
    def __init__(self, fact: ZiweiFact):
        self.fact = fact
        self.rules = RuleGraph.load("sanhe")
        self._cache: dict[str, Any] = {}
    
    # ── 格局识别 ────────────────────────────────────────────────
    
    def analyze_patterns(self) -> list[PatternResult]:
        """识别命盘格局"""
        results = []
        
        # 查询格局规则
        pattern_rules = self.rules.query_rules(RuleType.PATTERN, "sanhe")
        
        for rule in pattern_rules:
            try:
                if rule.condition(self.fact):
                    effect = rule.effect(self.fact)
                    results.append(PatternResult(
                        pattern_id=rule.rule_id,
                        pattern_name=effect.get("pattern", ""),
                        confidence=0.95,
                        details=effect,
                    ))
            except Exception as e:
                logger.warning(f"Rule {rule.rule_id} error: {e}")
        
        return results
    
    def get_main_pattern(self) -> PatternResult | None:
        """获取主格局（优先级最高的）"""
        patterns = self.analyze_patterns()
        return patterns[0] if patterns else None
    
    # ── 三方四正分析 ──────────────────────────────────────────────
    
    def analyze_sanfang(self, palace_name: str) -> dict:
        """分析指定宫位的三方四正"""
        BRANCHES = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
        PALACE_NAMES = ["命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄", 
                       "迁移", "仆役", "官禄", "田宅", "福德", "父母"]
        
        try:
            idx = PALACE_NAMES.index(palace_name)
        except ValueError:
            return {"error": f"Unknown palace: {palace_name}"}
        
        # 三方四正索引
        branches = [
            PALACE_NAMES[idx],
            PALACE_NAMES[(idx + 4) % 12],
            PALACE_NAMES[(idx + 8) % 12],
            PALACE_NAMES[(idx + 6) % 12],
        ]
        
        result = {
            "palace": palace_name,
            "sanfang": branches[:-1],
            "sizheng": branches[-1:],
            "stars": {},
        }
        
        for name in branches:
            pf = self.fact.palaces.get(name)
            if pf:
                result["stars"][name] = {
                    "major": pf.major_stars,
                    "minor": pf.minor_stars,
                    "empty": pf.is_empty,
                }
        
        return result
    
    # ── 四化分析 ─────────────────────────────────────────────────
    
    def analyze_birth_sihua(self) -> list[SiHuaResult]:
        """分析生年四化落宫"""
        results = []
        mutagen = self.fact.birth_mutagen
        
        if not mutagen or not mutagen.mutagens:
            return results
        
        # 建星→宫位映射
        star_to_palace = {}
        for pname, pf in self.fact.palaces.items():
            for star in pf.major_stars + pf.minor_stars:
                if star not in star_to_palace:
                    star_to_palace[star] = pname
        
        # 四化类型映射
        sihua_types = ["禄", "权", "科", "忌"]
        
        for i, star in enumerate(mutagen.mutagens[:4]):
            if star:
                palace = star_to_palace.get(star)
                if palace:
                    results.append(SiHuaResult(
                        sihua_type=sihua_types[i],
                        star=star,
                        palace=palace,
                        source="birth",
                        impact=self._calculate_impact(star, palace),
                    ))
        
        return results
    
    def analyze_decadal_sihua(self, decadal_start: int) -> list[SiHuaResult]:
        """分析指定大限的四化"""
        # 简化实现：使用大限天干推导
        # 实际应查询具体大限的干支
        results = []
        
        for pname, pf in self.fact.palaces.items():
            if pf.decadal_range and pf.decadal_range[0] == decadal_start:
                stem = pf.decadal_stem
                if stem:
                    # 这里应该调用 ziwei_profile.get_sihua_table()
                    # 简化为占位符
                    results.append(SiHuaResult(
                        sihua_type="",
                        star="",
                        palace=pname,
                        source=f"decadal_{decadal_start}",
                        impact="",
                    ))
        
        return results
    
    # ── 宫位分析 ─────────────────────────────────────────────────
    
    def analyze_palace(self, palace_name: str) -> PalaceAnalysis:
        """分析指定宫位"""
        pf = self.fact.palaces.get(palace_name)
        if not pf:
            return PalaceAnalysis(
                palace_name=palace_name,
                main_stars=(),
                has_sihua=False,
                empty=True,
                sanfang_summary=[],
            )
        
        # 分析三方
        sanfang_data = self.analyze_sanfang(palace_name)
        sanfang_stars = []
        for name, stars in sanfang_data.get("stars", {}).items():
            sanfang_stars.extend(stars.get("major", ()))
        
        return PalaceAnalysis(
            palace_name=palace_name,
            main_stars=pf.major_stars,
            has_sihua=bool(pf.self_mutagen),
            empty=pf.is_empty,
            sanfang_summary=list(dict.fromkeys(sanfang_stars)),  # 去重保序
        )
    
    def analyze_all_palaces(self) -> list[PalaceAnalysis]:
        """分析所有宫位"""
        return [
            self.analyze_palace(name)
            for name in ["命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄",
                        "迁移", "仆役", "官禄", "田宅", "福德", "父母"]
        ]
    
    # ── 整体命盘评估 ──────────────────────────────────────────────
    
    def full_analysis(self) -> dict:
        """完整命盘分析"""
        return {
            "method": "sanhe",
            "soul_palace": self.analyze_palace("命宫"),
            "body_palace": self.analyze_palace("身宫"),
            "main_pattern": self.get_main_pattern(),
            "birth_sihua": self.analyze_birth_sihua(),
            "palaces": self.analyze_all_palaces(),
            "meta": {
                "five_elements": self.fact.five_elements_class,
                "soul_branch": self.fact.soul_earthly_branch,
                "body_branch": self.fact.body_earthly_branch,
                "soul_borrowed": self.fact.soul_borrowed,
            },
        }
    
    # ── 辅助方法 ─────────────────────────────────────────────────
    
    def _calculate_impact(self, star: str, palace: str) -> str:
        """计算四化影响强度"""
        # 简化逻辑：命宫、官禄宫、财帛宫影响强
        important_palaces = {"命宫", "官禄", "财帛", "迁移"}
        if palace in important_palaces:
            return "strong"
        elif palace in {"夫妻", "福德"}:
            return "moderate"
        return "weak"
    
    def get_sihua_summary(self) -> dict:
        """四化汇总"""
        birth = self.analyze_birth_sihua()
        return {
            "birth": {r.sihua_type: r.star for r in birth},
            "total": len(birth),
        }


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "SanheAnalyzer",
    "PatternResult",
    "SiHuaResult",
    "PalaceAnalysis",
]
