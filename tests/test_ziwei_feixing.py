"""飞星派分析器测试"""

import pytest
from src.tongshu.engines.ziwei_feixing import FeixingAnalyzer
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
        "夫妻": PalaceFact(name="夫妻", earthly_branch="寅", heavenly_stem="丙", major_stars=("廉贞",), minor_stars=(), is_empty=False),
        "子女": PalaceFact(name="子女", earthly_branch="卯", heavenly_stem="丁", major_stars=(), minor_stars=(), is_empty=True),
        "财帛": PalaceFact(name="财帛", earthly_branch="辰", heavenly_stem="戊", major_stars=(), minor_stars=(), is_empty=True),
        "疾厄": PalaceFact(name="疾厄", earthly_branch="巳", heavenly_stem="己", major_stars=("太阳",), minor_stars=(), is_empty=False),
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


class TestFeixingAnalyzer:
    """飞星派分析器测试"""
    
    def test_init(self):
        """初始化测试"""
        fact = create_test_fact()
        analyzer = FeixingAnalyzer(fact)
        assert analyzer.fact == fact
    
    def test_trace_gonggan_feihua(self):
        """宫干飞化追踪测试"""
        fact = create_test_fact()
        analyzer = FeixingAnalyzer(fact)
        
        # 命宫天干为甲，四化为廉贞、破军、武曲、太阳
        steps = analyzer.trace_gonggan_feihua("命宫")
        assert len(steps) >= 1  # 至少找到一些飞化
        
        for step in steps:
            assert step.from_stem == "甲"
            assert step.sihua_type in ("禄", "权", "科", "忌")
    
    def test_all_gonggan_feihua(self):
        """所有宫干飞化测试"""
        fact = create_test_fact()
        analyzer = FeixingAnalyzer(fact)
        
        all_feihua = analyzer.all_gonggan_feihua()
        assert len(all_feihua) == 12  # 12宫
        assert "命宫" in all_feihua
    
    def test_analyze_lu_ji_trajectory(self):
        """禄忌轨迹分析测试"""
        fact = create_test_fact()
        analyzer = FeixingAnalyzer(fact)
        
        trajectory = analyzer.analyze_lu_ji_trajectory()
        assert isinstance(trajectory, list)
        
        # 如果找到禄忌轨迹，检查结构
        if trajectory:
            t = trajectory[0]
            assert hasattr(t, 'lu_star')
            assert hasattr(t, 'ji_star')
            assert hasattr(t, 'interaction')
    
    def test_analyze_gonggan_system(self):
        """宫干系统分析测试"""
        fact = create_test_fact()
        analyzer = FeixingAnalyzer(fact)
        
        result = analyzer.analyze_gonggan_system()
        assert "all_feihua" in result
        assert "hit_count" in result
        assert "most_hit_palace" in result
    
    def test_full_analysis(self):
        """完整分析测试"""
        fact = create_test_fact()
        analyzer = FeixingAnalyzer(fact)
        
        result = analyzer.full_analysis()
        assert result["method"] == "feixing"
        assert "gonggan_system" in result
        assert "lu_ji_trajectory" in result
        assert result["notes"]["no_xiaoxian"] is True
    
    def test_si_hua_table(self):
        """四化表验证测试"""
        # 验证飞星派四化表
        analyzer = FeixingAnalyzer.__new__(FeixingAnalyzer)
        assert analyzer.SIHUA_TABLE["甲"] == ("廉贞", "破军", "武曲", "太阳")
        assert analyzer.SIHUA_TABLE["戊"] == ("贪狼", "太阴", "右弼", "天机")
