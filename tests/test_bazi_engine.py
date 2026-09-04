"""八字引擎测试 - Bazi (八字) Engine

覆盖:
- Pillar 属性 (stem_element, branch_element)
- pillar_to_chinese 转换
- BaziChart 结构验证
- 阴阳干排列 (甲子、乙丑...)
- 10天干 12地支映射完整性
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import unittest
from tongshu.engines.bazi_engine import (
    HEAVENLY_STEMS,
    EARTHLY_BRANCHES,
    STEM_ELEMENT,
    STEM_POLARITY,
    Pillar,
    pillar_to_chinese,
    BaziChart,
    BaziEngine,
)


class TestPillarProperties(unittest.TestCase):
    """Pillar 数据属性测试。"""
    
    def test_all_stem_elements(self):
        """所有天干五行映射完整。"""
        expected = {
            "JIA": "WOOD", "YI": "WOOD",
            "BING": "FIRE", "DING": "FIRE",
            "WU": "EARTH", "JI": "EARTH",
            "GENG": "METAL", "XIN": "METAL",
            "REN": "WATER", "GUI": "WATER",
        }
        self.assertEqual(STEM_ELEMENT, expected)
    
    def test_all_branch_elements(self):
        """所有地支五行映射完整。"""
        p = Pillar("JIA", "YIN")
        self.assertEqual(p.branch_element, "WOOD")
        
        p = Pillar("BING", "WU")
        self.assertEqual(p.branch_element, "FIRE")
        
        p = Pillar("WU", "CHEN")
        self.assertEqual(p.branch_element, "EARTH")
        
        p = Pillar("GENG", "SHEN")
        self.assertEqual(p.branch_element, "METAL")
        
        p = Pillar("REN", "ZI")
        self.assertEqual(p.branch_element, "WATER")
    
    def test_pillar_to_chinese_jiachen(self):
        """甲辰转换。"""
        p = Pillar("JIA", "CHEN")
        self.assertEqual(pillar_to_chinese(p), "甲辰")
    
    def test_pillar_to_chinese_xinwei(self):
        """辛未转换。"""
        p = Pillar("XIN", "WEI")
        self.assertEqual(pillar_to_chinese(p), "辛未")
    
    def test_pillar_to_chinese_bingxu(self):
        """丙戌转换。"""
        p = Pillar("BING", "XU")
        self.assertEqual(pillar_to_chinese(p), "丙戌")


class TestBaziChartStructure(unittest.TestCase):
    """八字命盘结构测试。"""
    
    def test_full_chart_has_day_master(self):
        """完整命盘包含日主。"""
        chart = BaziChart(
            year_pillar=Pillar("JIA", "CHEN"),
            month_pillar=Pillar("XIN", "WEI"),
            day_pillar=Pillar("BING", "XU"),
            hour_pillar=Pillar("JIA", "WU"),
            day_master="BING",
            luck_pillars=[],
        )
        self.assertEqual(chart.day_master, "BING")
        self.assertIsNotNone(chart.to_dict())
    
    def test_chart_serialization(self):
        """命盘序列化完整。"""
        chart = BaziChart(
            year_pillar=Pillar("JIA", "CHEN"),
            month_pillar=Pillar("XIN", "WEI"),
            day_pillar=Pillar("BING", "XU"),
            hour_pillar=Pillar("JIA", "WU"),
            day_master="BING",
            luck_pillars=[],
        )
        data = chart.to_dict()
        self.assertIn("year_pillar", data)
        self.assertIn("day_master", data)
        self.assertEqual(data["day_master"], "BING")


class TestBaziEngine(unittest.TestCase):
    """八字引擎功能测试。"""
    
    def test_engine_computes_jixiaolan(self):
        """纪晓岚八字验证（公历1724-07-02 午时）。"""
        engine = BaziEngine()
        result = engine.compute((1724, 8, 3, 11), gender="male")
        
        self.assertEqual(result.year_pillar.heavenly_stem, "JIA")   # 甲
        self.assertEqual(result.year_pillar.earthly_branch, "CHEN")  # 辰
        self.assertEqual(result.day_pillar.heavenly_stem, "BING")    # 丙
        self.assertEqual(result.day_pillar.earthly_branch, "XU")     # 戌
        self.assertEqual(result.hour_pillar.heavenly_stem, "JIA")    # 甲
        self.assertEqual(result.hour_pillar.earthly_branch, "WU")    # 午
        self.assertEqual(result.day_master, "BING")
    
    def test_deterministic_output(self):
        """相同输入产生相同输出。"""
        engine = BaziEngine()
        r1 = engine.compute((1724, 6, 11, 12), gender="male")
        r2 = engine.compute((1724, 6, 11, 12), gender="male")
        self.assertEqual(r1.day_master, r2.day_master)


class TestStemBranchMapping(unittest.TestCase):
    """天干地支映射完整性测试。"""
    
    def test_10_stems_count(self):
        """天干数量正确。"""
        self.assertEqual(len(HEAVENLY_STEMS), 10)
    
    def test_12_branches_count(self):
        """地支数量正确。"""
        self.assertEqual(len(EARTHLY_BRANCHES), 12)
    
    def test_60_jiazi_cycle(self):
        """60甲子周期完整性。"""
        stems = len(HEAVENLY_STEMS)  # 10
        branches = len(EARTHLY_BRANCHES)  # 12
        gcd = (stems * branches) // __import__("math").gcd(stems, branches)
        self.assertEqual(gcd, 60)


class TestDayBranchPositionalFilter(unittest.TestCase):
    """ Regression test for calc_day_branch_clash / calc_day_branch_harm.

    Bug: 原实现用值过滤 `if b != day_b`，当日支地支在年/月/时重复出现时，
    会把所有同值地支全部排除，导致漏判冲/害。
    Fix: 改为按位置排除日柱（索引 2），只保留年(0)/月(1)/时(3)。
    """

    def test_clash_with_duplicate_day_branch_value(self):
        """日支=子，年支=子，月支=午：日支应被月支冲（True）。

        原 bug 行为：four_branches=[子, 午, 子, 亥]，值过滤后 other=[亥]，
        因为 BRANCH_CLASH["子"]="午" 不在 other 中，错误返回 False。
        正确行为：other=[年支子, 月支午, 时支亥]，月支午在冲表中，返回 True。
        """
        from tongshu.engines.bazi_engine import (
            BaziChart, Pillar, calc_day_branch_clash, BRANCH_CLASH,
        )
        # 四柱：年=甲子, 月=丙午, 日=戊子, 时=壬亥
        chart = BaziChart(
            year_pillar=Pillar("JIA", "ZI"),
            month_pillar=Pillar("BING", "WU"),
            day_pillar=Pillar("WU", "ZI"),
            hour_pillar=Pillar("REN", "HAI"),
            day_master="WU",
            luck_pillars=[],
            gender="male",
        )
        # 日支=子，月支=午，子午冲应触发
        self.assertEqual(chart.four_branches(), ["ZI", "WU", "ZI", "HAI"])
        self.assertTrue(calc_day_branch_clash(chart),
                        "日支被子/月支午冲，应为 True")

    def test_clash_no_clash_with_duplicate_value(self):
        """日支=子，年支=子，月支=丑，时支=寅：无冲（False）。

        值过滤 bug 下：other=[丑, 寅]（排除了所有子），BRANCH_CLASH["子"]="午"
        不在 other 中，结果也是 False——但路径不同，需确保逻辑正确。
        """
        from tongshu.engines.bazi_engine import (
            BaziChart, Pillar, calc_day_branch_clash,
        )
        chart = BaziChart(
            year_pillar=Pillar("JIA", "ZI"),
            month_pillar=Pillar("JIA", "CHOU"),
            day_pillar=Pillar("WU", "ZI"),
            hour_pillar=Pillar("WU", "YIN"),
            day_master="WU",
            luck_pillars=[],
            gender="male",
        )
        self.assertFalse(calc_day_branch_clash(chart),
                         "日支子无冲，应为 False")

    def test_harm_with_duplicate_day_branch_value(self):
        """日支=子，年支=子，月支=未：日支被月支害（True）。

        原 bug：值过滤后 other=[未, 亥]（假设时支=亥），
        但如果是 [子, 未, 子, 亥]，值过滤 other=[未, 亥]，结果碰巧也对。
        更极端 case：[子, 未, 子, 丑]，值过滤 other=[未, 丑]——也碰巧对。
        真正的问题在于：当日支的冲/害目标也在四柱中重复出现时才会出错。
        这里用 [子, 未, 子, 丑] 测试：日支子被害未（子未害），
        年支也是子，值过滤会把年支子也排除，但害关系只看 other 中是否有未。
        """
        from tongshu.engines.bazi_engine import (
            BaziChart, Pillar, calc_day_branch_harm, BRANCH_HARM,
        )
        # 四柱：年=子, 月=未, 日=子, 时=丑
        chart = BaziChart(
            year_pillar=Pillar("JIA", "ZI"),
            month_pillar=Pillar("JIA", "WEI"),
            day_pillar=Pillar("WU", "ZI"),
            hour_pillar=Pillar("WU", "CHOU"),
            day_master="WU",
            luck_pillars=[],
            gender="male",
        )
        # 子未害，月支未应在 other 中（位置过滤保留月支）
        self.assertTrue(calc_day_branch_harm(chart),
                        "日支未被子/月支未害，应为 True")

    def test_clash_all_same_branch_no_clash(self):
        """四支全同（子子子子）：无冲（False）。

        位置过滤后 other=[年支子, 月支子, 时支子]，
        BRANCH_CLASH["子"]="午" 不在其中，返回 False——正确。
        """
        from tongshu.engines.bazi_engine import (
            BaziChart, Pillar, calc_day_branch_clash,
        )
        chart = BaziChart(
            year_pillar=Pillar("JIA", "ZI"),
            month_pillar=Pillar("JIA", "ZI"),
            day_pillar=Pillar("WU", "ZI"),
            hour_pillar=Pillar("WU", "ZI"),
            day_master="WU",
            luck_pillars=[],
            gender="male",
        )
        self.assertFalse(calc_day_branch_clash(chart),
                         "四支全子，无冲，应为 False")


if __name__ == "__main__":
    unittest.main()

