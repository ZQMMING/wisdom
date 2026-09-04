"""流水线集成测试"""

import pytest
from unittest.mock import MagicMock, patch

from src.tongshu.engines.ziwei_pipeline import ZiweiPipeline
from src.tongshu.engines.ziwei_profile import load_profile
from src.tongshu.engines.ziwei_fact_layer import ZiweiFact, PalaceFact, MutagenFact


def create_mock_fact():
    """创建 mock 事实数据"""
    palaces = {
        "命宫": PalaceFact(
            name="命宫",
            earthly_branch="子",
            heavenly_stem="甲",
            major_stars=("紫微",),
            minor_stars=(),
            is_empty=False,
        ),
        "迁移": PalaceFact(
            name="迁移",
            earthly_branch="午",
            heavenly_stem="庚",
            major_stars=("天府",),
            minor_stars=(),
            is_empty=False,
        ),
    }
    # 补全其他宫位
    for name, branch in [("兄弟", "丑"), ("夫妻", "寅"), ("子女", "卯"),
                         ("财帛", "辰"), ("疾厄", "巳"), ("仆役", "未"),
                         ("官禄", "申"), ("田宅", "酉"), ("福德", "戌"), ("父母", "亥")]:
        palaces[name] = PalaceFact(
            name=name,
            earthly_branch=branch,
            heavenly_stem="",
            major_stars=(),
            minor_stars=(),
            is_empty=True,
        )
    
    mutagen = MutagenFact(mutagens=("廉贞", "破军", "武曲", "太阳"))
    
    return ZiweiFact(
        five_elements_class="火六局",
        soul_earthly_branch="子",
        body_earthly_branch="午",
        palaces=palaces,
        birth_mutagen=mutagen,
    )


class TestZiweiPipeline:
    """流水线测试"""
    
    def test_init(self):
        """初始化测试"""
        pipeline = ZiweiPipeline()
        assert pipeline is not None
    
    def test_get_chart(self):
        """获取事实层测试"""
        pipeline = ZiweiPipeline()
        
        # Mock engine
        mock_engine = MagicMock()
        mock_engine.full_chart.return_value = {
            "fiveElementsClass": "火六局",
            "earthlyBranchOfSoulPalace": "子",
            "earthlyBranchOfBodyPalace": "午",
            "palaces": {
                "命宫": {
                    "branch": "子",
                    "stem": "甲",
                    "major": ["紫微"],
                    "minor": [],
                    "decadalRange": [],
                    "decadalStem": "",
                    "decadalBranch": "",
                },
                "迁移": {
                    "branch": "午",
                    "stem": "庚",
                    "major": ["天府"],
                    "minor": [],
                    "decadalRange": [],
                    "decadalStem": "",
                    "decadalBranch": "",
                },
            },
        }
        pipeline._engine = mock_engine
        
        fact = pipeline.get_chart((1990, 5, 15), 10, "male")
        assert isinstance(fact, ZiweiFact)
        assert fact.five_elements_class == "火六局"
    
    def test_analyze_sanhe(self):
        """三合派分析测试"""
        pipeline = ZiweiPipeline()
        fact = create_mock_fact()
        
        result = pipeline.analyze_by_fact(fact, "sanhe")
        assert result.method == "sanhe"
        assert result.fact == fact
        assert "method" in result.analysis
    
    def test_analyze_zhongzhou(self):
        """中州派分析测试"""
        pipeline = ZiweiPipeline()
        fact = create_mock_fact()
        
        result = pipeline.analyze_by_fact(fact, "zhongzhou")
        assert result.method == "zhongzhou"
        assert "zhongzhou_special" in result.analysis
    
    def test_analyze_feixing(self):
        """飞星派分析测试"""
        pipeline = ZiweiPipeline()
        fact = create_mock_fact()
        
        result = pipeline.analyze_by_fact(fact, "feixing")
        assert result.method == "feixing"
        assert "gonggan_system" in result.analysis
    
    def test_analyze_qintian(self):
        """钦天门分析测试"""
        pipeline = ZiweiPipeline()
        fact = create_mock_fact()
        
        result = pipeline.analyze_by_fact(fact, "qintian")
        assert result.method == "qintian"
        assert "xiangxin_ji" in result.analysis
    
    def test_compare_methods(self):
        """流派对比测试"""
        pipeline = ZiweiPipeline()
        fact = create_mock_fact()
        
        # Mock the engine to avoid real computation
        with patch.object(pipeline, 'get_chart', return_value=fact):
            results = pipeline.compare_methods((1990, 5, 15), 10, "male")
        
        assert len(results) == 4
        assert "sanhe" in results
        assert "zhongzhou" in results
        assert "feixing" in results
        assert "qintian" in results


# 辅助方法（不在主类中，用于测试）
def analyze_by_fact(self, fact, method_id):
    from src.tongshu.engines.ziwei_pipeline import ZiweiPipelineResult
    
    analyzer_class = self._ANALYZER_MAP.get(method_id)
    if analyzer_class is None:
        raise ValueError(f"Unknown method_id: {method_id}")
    
    analyzer = analyzer_class(fact)
    analysis = analyzer.full_analysis()
    
    return ZiweiPipelineResult(
        method=method_id,
        fact=fact,
        analysis=analysis,
        metadata={"method_name": method_id},
    )


# Monkey-patch for testing
ZiweiPipeline.analyze_by_fact = analyze_by_fact
