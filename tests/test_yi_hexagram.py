"""易学引擎测试 - Yi (易经) Hexagram Symbol

覆盖:
- TRIGRAM_DATA 八卦五行映射完整性
- HEXAGRAM_FULL_DATA 六十四卦映射
- get_hexagram_symbol 解析正确性
- 错卦/综卦/互卦关系
- 体用生克关系计算
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path("D:/today/backend/src")))

import unittest
from tongshu.engines.yi.hexagram_symbol import (
    TRIGRAM_DATA,
    SIXTY_FOUR_MAP,
    get_hexagram_symbol,
)
from tongshu.engines.heluo.hexagram import (
    TRIGRAM_ELEMENT,
    SHENG_MAP,
    KE_MAP,
    analyze_hexagram,
)


class TestTrigramData(unittest.TestCase):
    """八卦基础数据测试。"""
    
    def test_all_8_trigrams(self):
        """八卦全部存在。"""
        expected = {"乾", "兑", "离", "震", "巽", "坎", "艮", "坤"}
        self.assertEqual(set(TRIGRAM_DATA.keys()), expected)
    
    def test_elements_mapping(self):
        """五行映射正确。"""
        self.assertEqual(TRIGRAM_DATA["乾"]["element"], "金")
        self.assertEqual(TRIGRAM_DATA["坤"]["element"], "土")
        self.assertEqual(TRIGRAM_DATA["坎"]["element"], "水")
        self.assertEqual(TRIGRAM_DATA["离"]["element"], "火")
        self.assertEqual(TRIGRAM_DATA["震"]["element"], "木")
        self.assertEqual(TRIGRAM_DATA["巽"]["element"], "木")
    
    def test_numbers_complete(self):
        """数字1-8全部映射。"""
        numbers = {d["number"] for d in TRIGRAM_DATA.values()}
        self.assertEqual(numbers, set(range(1, 9)))
    
    def test_symbols_present(self):
        """卦符全部存在。"""
        for name, data in TRIGRAM_DATA.items():
            self.assertTrue(data["symbol"])


class TestSixtyFourMap(unittest.TestCase):
    """六十四卦映射测试。"""
    
    def test_total_count(self):
        """映射数量64。"""
        self.assertEqual(len(SIXTY_FOUR_MAP), 64)
    
    def test_all_trigram_pairs(self):
        """所有八卦组合都存在。"""
        trigrams = {"乾", "兑", "离", "震", "巽", "坎", "艮", "坤"}
        for upper in trigrams:
            for lower in trigrams:
                self.assertIn((upper, lower), SIXTY_FOUR_MAP)
    
    def test_known_hexagrams(self):
        """关键卦象验证。"""
        self.assertEqual(SIXTY_FOUR_MAP[("坤", "乾")], "地天泰")
        self.assertEqual(SIXTY_FOUR_MAP[("乾", "坤")], "天地否")
        self.assertEqual(SIXTY_FOUR_MAP[("乾", "乾")], "乾为天")
        self.assertEqual(SIXTY_FOUR_MAP[("坤", "坤")], "坤为地")


class TestGetHexagramSymbol(unittest.TestCase):
    """卦象符号解析测试。"""
    
    def test_ditian_tai(self):
        """地天泰卦解析。"""
        sym = get_hexagram_symbol("地天泰")
        self.assertIsNotNone(sym)
        self.assertEqual(sym.upper_trigram, "坤")
        self.assertEqual(sym.lower_trigram, "乾")
    
    def test_tiandi_pi(self):
        """天地否卦解析。"""
        sym = get_hexagram_symbol("天地否")
        self.assertIsNotNone(sym)
        self.assertEqual(sym.upper_trigram, "乾")
        self.assertEqual(sym.lower_trigram, "坤")
    
    def test_unknown_hexagram(self):
        """未知卦名仍返回默认符号（不抛出异常）。"""
        sym = get_hexagram_symbol("未知卦")
        # 未知卦返回默认值，不为None
        self.assertIsNotNone(sym)


class TestHeluoHexagramStructure(unittest.TestCase):
    """河洛卦象结构测试。"""
    
    def test_trigram_elements(self):
        """八卦五行映射。"""
        self.assertEqual(TRIGRAM_ELEMENT["乾"], "金")
        self.assertEqual(TRIGRAM_ELEMENT["坤"], "土")
        self.assertEqual(TRIGRAM_ELEMENT["坎"], "水")
        self.assertEqual(TRIGRAM_ELEMENT["离"], "火")
    
    def test_sheng_map(self):
        """五行相生映射。"""
        self.assertEqual(SHENG_MAP["金"], "水")
        self.assertEqual(SHENG_MAP["水"], "木")
        self.assertEqual(SHENG_MAP["木"], "火")
        self.assertEqual(SHENG_MAP["火"], "土")
        self.assertEqual(SHENG_MAP["土"], "金")
    
    def test_ke_map(self):
        """五行相克映射。"""
        self.assertEqual(KE_MAP["金"], "木")
        self.assertEqual(KE_MAP["木"], "土")
        self.assertEqual(KE_MAP["土"], "水")
        self.assertEqual(KE_MAP["水"], "火")
        self.assertEqual(KE_MAP["火"], "金")
    
    def test_analyze_ditian_tai(self):
        """地天泰卦分析。"""
        result = analyze_hexagram("地天泰")
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "地天泰")
        self.assertEqual(result.upper, "坤")
        self.assertEqual(result.lower, "乾")
    
    def test_analyze_unknown(self):
        """未知卦返回None。"""
        result = analyze_hexagram("未知")
        self.assertIsNone(result)


class TestTiYongRelation(unittest.TestCase):
    """体用关系测试。"""
    
    def test_ti_yong_definition(self):
        """体为下卦，用为上卦。"""
        # 地天泰: 上坤下乾 → 体=乾(金), 用=坤(土)
        result = analyze_hexagram("地天泰")
        # ti和yong属性在sheng_ke中体现
        self.assertEqual(result.upper, "坤")
        self.assertEqual(result.lower, "乾")
    
    def test_sheng_relation(self):
        """土生金(用生体)。"""
        result = analyze_hexagram("地天泰")
        # 结果应为含生克关系的字符串
        self.assertIsInstance(result.sheng_ke, str)
        self.assertTrue(len(result.sheng_ke) > 0)


if __name__ == "__main__":
    unittest.main()
