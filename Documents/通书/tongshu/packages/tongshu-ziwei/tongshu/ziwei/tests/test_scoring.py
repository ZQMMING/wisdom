# -*- coding: utf-8 -*-
"""紫微断事层V2.7测试: 生年四化落宫 + 主题评分"""
from __future__ import annotations
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
os.environ.setdefault("TONGSHU_ALLOW_ZIWEI_STUB", "1")

from tongshu.ziwei.engine import ZiweiEngine


class TestZiweiSihuaPalace(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e = ZiweiEngine()

    def test_stub_generates_chart(self):
        """Stub模式下generate Chart不为None"""
        chart = self.e.compute((1893, 11, 19), 8, 'male')
        self.assertIsNotNone(chart)
        # Stub should produce a main star based on day_master
        self.assertIsInstance(chart.soul_palace_main_star, str)


class TestZiweiKnowledge(unittest.TestCase):
    """知识层测试"""

    def test_main_star_organ_coverage(self):
        """14主星全部有脏腑信息（中文key）"""
        from tongshu.ziwei.knowledge import MAIN_STAR_ORGAN, PINYIN_TO_CN
        self.assertEqual(len(MAIN_STAR_ORGAN), 14)
        # MAIN_STAR_ORGAN uses Chinese names as keys
        for pinyin, cn in PINYIN_TO_CN.items():
            self.assertIn(cn, MAIN_STAR_ORGAN, f"Missing organ info for {cn} (pinyin={pinyin})")

    def test_theme_to_palace_coverage(self):
        """主题到宫位的映射非空"""
        from tongshu.ziwei.knowledge import THEME_TO_PALACE
        self.assertGreater(len(THEME_TO_PALACE), 0)
        # 核心主题应覆盖
        for theme in ["婚姻", "健康", "财运", "事业"]:
            self.assertIn(theme, THEME_TO_PALACE)


if __name__ == "__main__":
    unittest.main()
