# -*- coding: utf-8 -*-
"""紫微格局识别测试 - V2.6补充格局+空宫借星"""
from __future__ import annotations
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path("D:/today/backend/src")))
os.environ["TONGSHU_ALLOW_ZIWEI_STUB"] = "1"

from tongshu.engines.ziwei_pattern import recognize_patterns, recognize_patterns_from_chart


class TestZiweiPattern(unittest.TestCase):
    def test_lianfu_tonggong(self):
        """廉贞+天府同宫 → 廉府同宫"""
        patterns = recognize_patterns(['廉贞', '天府'])
        names = [p[0] for p in patterns]
        self.assertIn('廉府同宫', names)

    def test_wuxiang_tonggong(self):
        """武曲+天相同宫 → 武相同宫"""
        patterns = recognize_patterns(['武曲', '天相'])
        names = [p[0] for p in patterns]
        self.assertIn('武相同宫', names)

    def test_tianfu_zuoming(self):
        """天府独坐 → 天府坐命"""
        patterns = recognize_patterns(['天府'])
        names = [p[0] for p in patterns]
        self.assertIn('天府坐命', names)

    def test_zifu_tonggong(self):
        """紫微+天府同宫 → 紫府同宫"""
        patterns = recognize_patterns(['紫微', '天府'])
        names = [p[0] for p in patterns]
        self.assertIn('紫府同宫', names)

    def test_empty_palace_no_pattern(self):
        """空宫(无主星) → 无格局"""
        patterns = recognize_patterns([])
        self.assertEqual(patterns, [])

    def test_single_star_not_duplicated(self):
        """单星格局不与多星格局重复"""
        # 廉贞+天府: 应有廉府同宫, 不应同时有廉贞坐命
        patterns = recognize_patterns(['廉贞', '天府'])
        names = [p[0] for p in patterns]
        self.assertIn('廉府同宫', names)
        self.assertNotIn('廉贞坐命', names)
        self.assertNotIn('天府坐命', names)

    def test_recognize_from_chart_none(self):
        """chart为None → 空列表"""
        result = recognize_patterns_from_chart(None)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
