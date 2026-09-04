"""钦天门分析器测试"""

import pytest
from src.tongshu.engines.ziwei_qintian import QintianAnalyzer
from src.tongshu.engines.ziwei_fact_layer import ZiweiFact, PalaceFact, MutagenFact


def create_test_fact():
    """创建测试用的事实数据"""
    palaces = {
        "命宫": PalaceFact(
            name="命宫",
            earthly_branch="子",
            heavenly_stem="甲",
            major_stars=("紫微",),
            minor_stars=(),
            is_empty=False,
        ),
        "兄弟": PalaceFact(name="兄弟", earthly_branch="丑", heavenly_stem="乙", major_stars=(), minor_stars=(), is_empty=True),
        "夫妻": PalaceFact(name="夫妻", earthly_branch="寅", heavenly_stem="丙", major_stars=(), minor_stars=(), is_empty=True),
        "子女": PalaceFact(name="子女", earthly_branch="卯", heavenly_stem="丁", major_stars=("太阳",), minor_stars=(), is_empty=False),
        "财帛": PalaceFact(name="财帛", earthly_branch="辰", heavenly_stem="戊", major_stars=(), minor_stars=(), is_empty=True),
        "疾厄": PalaceFact(name="疾厄", earthly_branch="巳", heavenly_stem="己", major_stars=(), minor_stars=(), is_empty=True),
        "迁移": PalaceFact(name="迁移", earthly_branch="午", heavenly_stem="庚", major_stars=(), minor_stars=(), is_empty=True),
        "仆役": PalaceFact(name="仆役", earthly_branch="未", heavenly_stem="辛", major_stars=(), minor_stars=(), is_empty=True),
        "官禄": PalaceFact(name="官禄", earthly_branch="申", heavenly_stem="壬", major_stars=(), minor_stars=(), is_empty=True),
        "田宅": PalaceFact(name="田宅", earthly_branch="酉", heavenly_stem="癸", major_stars=(), minor_stars=(), is_empty=True),
        "福德": PalaceFact(name="福德", earthly_branch="戌", heavenly_stem="", major_stars=(), minor_stars=(), is_empty=True),
        "父母": PalaceFact(name="父母", earthly_branch="亥", heavenly_stem="", major_stars=(), minor_stars=(), is_empty=True),
    }
    
    # 甲干四化：廉贞禄、破军权、武曲科、太阳忌
    mutagen = MutagenFact(mutagens=("廉贞", "破军", "武曲", "太阳"))
    
    return ZiweiFact(
        five_elements_class="火六局",
        soul_earthly_branch="子",
        body_earthly_branch="午",
        palaces=palaces,
        birth_mutagen=mutagen,
    )


class TestQintianAnalyzer:
    """钦天门分析器测试"""
    
    def test_init(self):
        """初始化测试"""
        fact = create_test_fact()
        analyzer = QintianAnalyzer(fact)
        assert analyzer.fact == fact
    
    def test_analyze_xiangxin_ji(self):
        """向心忌分析测试"""
        fact = create_test_fact()
        analyzer = QintianAnalyzer(fact)
        
        results = analyzer.analyze_xiangxin_ji()
        assert isinstance(results, list)
        
        # 如果找到向心忌，检查结构
        for r in results:
            assert hasattr(r, 'source_palace')
            assert hasattr(r, 'target_palace')
            assert hasattr(r, 'strength')
    
    def test_analyze_lixin_ji(self):
        """离心忌分析测试"""
        fact = create_test_fact()
        analyzer = QintianAnalyzer(fact)
        
        results = analyzer.analyze_lixin_ji()
        assert isinstance(results, list)
        
        # 如果找到离心忌，检查结构
        for r in results:
            assert hasattr(r, 'source_palace')
            assert hasattr(r, 'target_palace')
    
    def test_liji_analysis(self):
        """立极宫分析测试"""
        fact = create_test_fact()
        analyzer = QintianAnalyzer(fact)
        
        result = analyzer.liji_analysis()
        assert result.center_palace == "命宫"
        assert "xiangxin" in result.direction_analysis
        assert "lixin" in result.direction_analysis
        assert "self_hua" in result.direction_analysis
    
    def test_liji_analysis_custom_center(self):
        """自定义立极点测试"""
        fact = create_test_fact()
        analyzer = QintianAnalyzer(fact)
        
        result = analyzer.liji_analysis("夫妻")
        assert result.center_palace == "夫妻"
    
    def test_full_analysis(self):
        """完整分析测试"""
        fact = create_test_fact()
        analyzer = QintianAnalyzer(fact)
        
        result = analyzer.full_analysis()
        assert result["method"] == "qintian"
        assert "xiangxin_ji" in result
        assert "lixin_ji" in result
        assert "liji_analysis" in result
        assert "summary" in result
    
    def test_si_hua_table(self):
        """四化表验证测试"""
        analyzer = QintianAnalyzer.__new__(QintianAnalyzer)
        assert analyzer.SIHUA_TABLE["甲"] == ("廉贞", "破军", "武曲", "太阳")
        assert analyzer.SIHUA_TABLE["戊"] == ("贪狼", "太阴", "右弼", "天机")
    
    def test_calculate_ji_strength(self):
        """忌强度计算测试"""
        analyzer = QintianAnalyzer.__new__(QintianAnalyzer)
        
        # 重要宫位之间的忌
        assert analyzer._calculate_ji_strength("命宫", "官禄") == "强"
        # 重要宫位与一般宫位
        assert analyzer._calculate_ji_strength("命宫", "福德") == "中"
        # 一般宫位之间
        assert analyzer._calculate_ji_strength("福德", "田宅") == "弱"
