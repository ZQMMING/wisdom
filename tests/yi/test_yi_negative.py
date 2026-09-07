"""Yi Engine Negative Tests — E4

失败场景覆盖:
- 无效输入处理
- 缺失数据降级
- 异常路径测试
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import unittest
from tongshu.engines.yi.yao_ci_data import get_yao_ci, YAO_CI
from tongshu.engines.yi.hexagram_symbol import get_hexagram_symbol


class TestInvalidInputHandling(unittest.TestCase):
    """无效输入处理测试。"""

    def test_empty_hexagram_name(self):
        """空卦名返回空。"""
        text, source = get_yao_ci("", "初九")
        self.assertEqual(text, "")
        self.assertEqual(source, "")

    def test_none_line_position(self):
        """None爻位返回空。"""
        text, source = get_yao_ci("乾为天", None)  # type: ignore
        self.assertEqual(text, "")
        self.assertEqual(source, "")

    def test_numeric_line_position(self):
        """数字爻位返回空。"""
        text, source = get_yao_ci("乾为天", "1")
        self.assertEqual(text, "")
        self.assertEqual(source, "")

    def test_out_of_range_line(self):
        """超出范围的爻位返回空。"""
        # "初八" 不在 LINE_NAME_TO_INDEX 中（只有初九/初六/初一）
        text, source = get_yao_ci("乾为天", "初八")
        self.assertEqual(text, "")
        self.assertEqual(source, "")


class TestMissingDataDegradation(unittest.TestCase):
    """缺失数据降级测试。"""

    def test_unknown_hexagram_symbol(self):
        """未知卦的卦象返回默认值。"""
        sym = get_hexagram_symbol("不存在的卦")
        self.assertEqual(sym.upper_trigram, "?")
        self.assertEqual(sym.lower_trigram, "?")
        # cuo_gua/zong_gua 可能返回组合字符串
        self.assertIsInstance(sym.cuo_gua, str)
        self.assertIsInstance(sym.zong_gua, str)

    def test_unknown_hexagram_yao_ci(self):
        """未知卦的爻辞返回空。"""
        text, source = get_yao_ci("不存在的卦", "初九")
        self.assertEqual(text, "")
        self.assertEqual(source, "")

    def test_all_hexagrams_in_yao_ci(self):
        """YAO_CI覆盖所有64卦。"""
        self.assertEqual(len(YAO_CI), 64)


class TestExceptionPaths(unittest.TestCase):
    """异常路径测试。"""

    def test_corrupted_source_field(self):
        """source字段格式异常时仍可检索。"""
        # 验证修复后无双后缀
        for key, entries in YAO_CI.items():
            for entry in entries:
                _, _, text, source = entry
                # source不应包含重复后缀
                self.assertNotIn("三三", source)
                self.assertNotIn("二二", source)
                self.assertNotIn("五五", source)
                self.assertNotIn("初六六", source)


if __name__ == "__main__":
    unittest.main()
