"""中州派分析器测试"""

import pytest
from src.tongshu.engines.ziwei_zhongzhou import ZhongzhouAnalyzer
from src.tongshu.engines.ziwei_fact_layer import ZiweiFact, PalaceFact, MutagenFact


def create_test_fact():
    """创建测试用的事实数据"""
    palaces = {
        "命宫": PalaceFact(
            name="命宫",
            earthly_branch="子",
            heavenly_stem="戊",
            major_stars=("紫微",),
            minor_stars=("流昌",),
            is_empty=False,
        ),
        "兄弟": PalaceFact(name="兄弟", earthly_branch="丑", heavenly_stem="", major_stars=(), minor_stars=(), is_empty=True),
        "夫妻": PalaceFact(name="夫妻", earthly_branch="寅", heavenly_stem="", major_stars=(), minor_stars=(), is_empty=True),
        "子女": PalaceFact(name="子女", earthly_branch="卯", heavenly_stem="", major_stars=(), minor_stars=(), is_empty=True),
        "财帛": PalaceFact(name="财帛", earthly_branch="辰", heavenly_stem="", major_stars=("天机",), minor_stars=(), is_empty=False),
        "疾厄": PalaceFact(name="疾厄", earthly_branch="巳", heavenly_stem="", major_stars=(), minor_stars=(), is_empty=True),
        "迁移": PalaceFact(name="迁移", earthly_branch="午", heavenly_stem="", major_stars=("天府",), minor_stars=(), is_empty=False),
        "仆役": PalaceFact(name="仆役", earthly_branch="未", heavenly_stem="", major_stars=(), minor_stars=(), is_empty=True),
        "官禄": PalaceFact(name="官禄", earthly_branch="申", heavenly_stem="", major_stars=(), minor_stars=(), is_empty=True),
        "田宅": PalaceFact(name="田宅", earthly_branch="酉", heavenly_stem="", major_stars=(), minor_stars=(), is_empty=True),
        "福德": PalaceFact(name="福德", earthly_branch="戌", heavenly_stem="", major_stars=(), minor_stars=(), is_empty=True),
        "父母": PalaceFact(name="父母", earthly_branch="亥", heavenly_stem="", major_stars=(), minor_stars=(), is_empty=True),
    }
    
    mutagen = MutagenFact(mutagens=("贪狼", "太阴", "太阳", "天机"))
    
    return ZiweiFact(
        five_elements_class="木三局",
        soul_earthly_branch="子",
        body_earthly_branch="午",
        palaces=palaces,
        birth_mutagen=mutagen,
    )


class TestZhongzhouAnalyzer:
    """中州派分析器测试"""
    
    def test_init(self):
        """初始化测试"""
        fact = create_test_fact()
        analyzer = ZhongzhouAnalyzer(fact)
        assert analyzer.fact == fact
    
    def test_analyze_liuchangliuqu(self):
        """流昌流曲分析测试"""
        fact = create_test_fact()
        analyzer = ZhongzhouAnalyzer(fact)
        
        results = analyzer.analyze_liuchangliuqu()
        assert len(results) >= 1
        assert any(r.star_type == "流昌" for r in results)
    
    def test_analyze_empty_palace(self):
        """空宫全借测试"""
        fact = create_test_fact()
        analyzer = ZhongzhouAnalyzer(fact)
        
        results = analyzer.analyze_empty_palace_full_borrow()
        # 应该有借星的空宫
        assert len(results) > 0
    
    def test_check_wu_gan_taiyang_ke(self):
        """戊干太阳化科测试"""
        fact = create_test_fact()
        analyzer = ZhongzhouAnalyzer(fact)
        
        # 命宫天干为戊，应返回 True
        assert analyzer.check_wu_gan_taiyang_hua_ke() is True
    
    def test_full_analysis(self):
        """完整分析测试"""
        fact = create_test_fact()
        analyzer = ZhongzhouAnalyzer(fact)
        
        result = analyzer.full_analysis()
        assert result["method"] == "sanhe"  # 继承自父类
        assert "zhongzhou_special" in result
        zh = result["zhongzhou_special"]
        assert "liuchangliuqu" in zh
        assert "empty_palace_borrow" in zh
        assert "wu_gan_taiyang_ke" in zh
    
    def test_analyze_palace_empty(self):
        """空宫分析测试"""
        fact = create_test_fact()
        analyzer = ZhongzhouAnalyzer(fact)
        
        result = analyzer.analyze_palace("夫妻")
        assert result.get("empty")
        # 夫妻宫（寅）对宫是申（官禄），官禄空，所以无借星
        # 夫妻宫（寅）三方为辰（财帛）、申（官禄）、戌（福德）
        # 寅的对宫是申，申为空，所以夫妻借不到星
        # 但寅的三方可能有星（辰有财帛天机）
