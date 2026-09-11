"""紫微斗数流水线 — Z8 API 集成

统一入口，根据 MethodProfile 切换流派。
支持三合/中州/飞星/钦天四种流派的分析。

使用示例：
    from tongshu.engines.ziwei_pipeline import ZiweiPipeline
    from tongshu.engines.ziwei_profile import load_profile
    
    pipeline = ZiweiPipeline()
    profile = load_profile("sanhe")
    result = pipeline.analyze(
        birth_date=(1990, 5, 15),
        birth_hour=10,
        gender="male",
        method_profile=profile,
    )
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .ziwei_profile import MethodProfile, load_profile
from .ziwei_fact_layer import ZiweiFact, build_ziwei_fact
from .ziwei_sanhe import SanheAnalyzer
from .ziwei_zhongzhou import ZhongzhouAnalyzer
from .ziwei_feixing import FeixingAnalyzer
from .ziwei_qintian import QintianAnalyzer


MethodId = Literal["sanhe", "zhongzhou", "feixing", "qintian"]


@dataclass(frozen=True)
class ZiweiPipelineResult:
    """流水线分析结果"""
    method: MethodId
    fact: ZiweiFact
    analysis: dict[str, Any]
    metadata: dict[str, Any]


class ZiweiPipeline:
    """紫微斗数分析流水线
    
    统一入口，支持多流派切换。
    """
    
    # 流派到分析器的映射
    _ANALYZER_MAP = {
        "sanhe": SanheAnalyzer,
        "zhongzhou": ZhongzhouAnalyzer,
        "feixing": FeixingAnalyzer,
        "qintian": QintianAnalyzer,
    }
    
    def __init__(self, engine=None):
        """
        Args:
            engine: ZiweiEngine 实例（可选，默认会创建）
        """
        self._engine = engine
        self._cache: dict[str, Any] = {}
    
    @property
    def engine(self):
        """获取或创建 ZiweiEngine"""
        if self._engine is None:
            from .ziwei_engine import ZiweiEngine
            self._engine = ZiweiEngine()
        return self._engine
    
    def get_chart(self, lunar_date: tuple[int, int, int], hour: int, 
                  gender: str = "male") -> ZiweiFact:
        """获取事实层
        
        Args:
            lunar_date: 农历日期 (年, 月, 日)
            hour: 出生时辰（24小时制）
            gender: 性别（"male"/"female"）
        
        Returns:
            ZiweiFact 实例
        """
        cache_key = f"chart_{lunar_date}_{hour}_{gender}"
        if cache_key not in self._cache:
            raw_chart = self.engine.full_chart(lunar_date, hour, gender)
            self._cache[cache_key] = build_ziwei_fact(raw_chart)
        return self._cache[cache_key]
    
    def analyze(self, 
                birth_date: tuple[int, int, int],
                birth_hour: int,
                gender: str = "male",
                method_profile: MethodProfile | None = None) -> ZiweiPipelineResult:
        """执行完整分析
        
        Args:
            birth_date: 阳历出生日期 (年, 月, 日)
            birth_hour: 出生时辰（24小时制）
            gender: 性别
            method_profile: 流派配置（可选，默认三合派）
        
        Returns:
            ZiweiPipelineResult
        """
        if method_profile is None:
            method_profile = load_profile("sanhe")
        
        method_id = method_profile.school
        
        # 获取事实层
        fact = self.get_chart(birth_date, birth_hour, gender)
        
        # 获取分析器
        analyzer_class = self._ANALYZER_MAP.get(method_id)
        if analyzer_class is None:
            raise ValueError(f"Unknown method_id: {method_id}")
        
        # 执行分析
        analyzer = analyzer_class(fact)
        analysis = analyzer.full_analysis()
        
        return ZiweiPipelineResult(
            method=method_id,
            fact=fact,
            analysis=analysis,
            metadata={
                "method_name": method_profile.name,
                "source": fact.source,
                "calculation_version": fact.calculation_version,
            },
        )
    
    def get_analysis_by_method(self, fact: ZiweiFact, method_id: MethodId) -> dict:
        """对同一事实使用不同流派分析
        
        Args:
            fact: ZiweiFact 实例
            method_id: 流派标识
        
        Returns:
            分析结果字典
        """
        analyzer_class = self._ANALYZER_MAP.get(method_id)
        if analyzer_class is None:
            raise ValueError(f"Unknown method_id: {method_id}")
        
        analyzer = analyzer_class(fact)
        return analyzer.full_analysis()
    
    def compare_methods(self, birth_date: tuple[int, int, int],
                       birth_hour: int,
                       gender: str = "male") -> dict[str, dict]:
        """对比四种流派的分析结果
        
        Args:
            birth_date: 阳历出生日期
            birth_hour: 出生时辰
            gender: 性别
        
        Returns:
            {method_id: analysis} 字典
        """
        fact = self.get_chart(birth_date, birth_hour, gender)
        
        results = {}
        for method_id in self._ANALYZER_MAP:
            results[method_id] = self.get_analysis_by_method(fact, method_id)
        
        return results


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "ZiweiPipeline",
    "ZiweiPipelineResult",
    "MethodId",
]
