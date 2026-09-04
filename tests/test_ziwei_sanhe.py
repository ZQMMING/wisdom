"""三合派分析器测试"""

import pytest
from unittest.mock import MagicMock

from src.tongshu.engines.ziwei_sanhe import SanheAnalyzer
from src.tongshu.engines.ziwei_fact_layer import ZiweiFact, PalaceFact, MutagenFact


def create_test_fact():
    """创建测试用的事实数据"""
    palaces = {
        "命宫": PalaceFact(
            name="命宫",
            earthly_branch="子",
            heavenly_stem="甲",
            major_stars=("紫微", "天府"),
            minor_stars=("左辅", "右弼"),
            is_empty=False,
        ),
        "兄弟": PalaceFact(
            name="兄弟",
            earthly_branch="丑",
            heavenly_stem="乙",
            major_stars=("天机",),
            minor_stars=(),
            is_empty=False,
        ),
        "夫妻": PalaceFact(
            name="夫妻",
            earthly_branch="寅",
            heavenly_stem="丙",
            major_stars=(),
            minor_stars=(),
            is_empty=True,
        ),
        # ... 其他宫位省略
    }
    
    # 补充其他宫位
    for name, branch in [("子女", "卯"), ("财帛", "辰"), ("疾厄", "巳"),
                         ("迁移", "午"), ("仆役", "未"), ("官禄", "申"),
                         ("田宅", "酉"), ("福德", "戌"), ("父母", "亥")]:
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
        five_elements_class="水二局",
        soul_earthly_branch="子",
        body_earthly_branch="午",
        palaces=palaces,
        birth_mutagen=mutagen,
    )


class TestSanheAnalyzer:
    """三合派分析器测试"""
    
    def test_init(self):
        """初始化测试"""
        fact = create_test_fact()
        analyzer = SanheAnalyzer(fact)
        assert analyzer.fact == fact
    
    def test_analyze_palace(self):
        """宫位分析测试"""
        fact = create_test_fact()
        analyzer = SanheAnalyzer(fact)
        
        result = analyzer.analyze_palace("命宫")
        assert result.palace_name == "命宫"
        assert result.main_stars == ("紫微", "天府")
        assert not result.empty
        assert len(result.sanfang_summary) > 0
    
    def test_analyze_empty_palace(self):
        """空宫分析测试"""
        fact = create_test_fact()
        analyzer = SanheAnalyzer(fact)
        
        result = analyzer.analyze_palace("夫妻")
        assert result.empty
        assert result.main_stars == ()
    
    def test_analyze_sanfang(self):
        """三方四正分析测试"""
        fact = create_test_fact()
        analyzer = SanheAnalyzer(fact)
        
        result = analyzer.analyze_sanfang("命宫")
        assert result["palace"] == "命宫"
        assert "迁移" in result["sanfang"] or "迁移" in result["sizheng"]
    
    def test_analyze_birth_sihua(self):
        """生年四化分析测试"""
        fact = create_test_fact()
        analyzer = SanheAnalyzer(fact)
        
        results = analyzer.analyze_birth_sihua()
        # 四化星可能不在宫位中（取决于星曜分布），只要不报错即可
        assert isinstance(results, list)
        for r in results:
            assert hasattr(r, 'sihua_type')
            assert hasattr(r, 'star')
            assert hasattr(r, 'palace')
    
    def test_full_analysis(self):
        """完整分析测试"""
        fact = create_test_fact()
        analyzer = SanheAnalyzer(fact)
        
        result = analyzer.full_analysis()
        assert result["method"] == "sanhe"
        assert "soul_palace" in result
        assert "birth_sihua" in result
        assert "main_pattern" in result
        assert result["meta"]["five_elements"] == "水二局"
    
    def test_get_sihua_summary(self):
        """四化汇总测试"""
        fact = create_test_fact()
        analyzer = SanheAnalyzer(fact)
        
        summary = analyzer.get_sihua_summary()
        assert "birth" in summary
        assert "total" in summary
        assert isinstance(summary["total"], int)
