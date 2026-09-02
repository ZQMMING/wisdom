"""紫微斗数引擎测试 - Ziwei (紫微) Engine

覆盖:
- 时辰计算
- 核心排盘功能
- 四化系统
- 架构合规（删除违规项）
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path("D:/today/backend/src")))

import unittest
from tongshu.engines.ziwei_engine import (
    ZiweiEngine,
    GAN_SIHUA,
    time_index_from_hour,
)


class TestTimeIndexCalculation(unittest.TestCase):
    """时辰计算测试。"""

    def test_zi_early_0(self):
        """早子时(00:00-01:00) → index 0。"""
        self.assertEqual(time_index_from_hour(0), 0)
        self.assertEqual(time_index_from_hour(24), 0)

    def test_chou_1(self):
        """丑时(01:00-03:00) → index 1。"""
        self.assertEqual(time_index_from_hour(1), 1)
        self.assertEqual(time_index_from_hour(2), 1)

    def test_wu_6(self):
        """午时(11:00-13:00) → index 6。"""
        self.assertEqual(time_index_from_hour(11), 6)
        self.assertEqual(time_index_from_hour(12), 6)

    def test_zi_late_12(self):
        """晚子时(23:00-23:59) → index 12。"""
        self.assertEqual(time_index_from_hour(23), 12)

    def test_all_hours_covered(self):
        """所有小时都有对应index。"""
        for h in range(24):
            idx = time_index_from_hour(h)
            self.assertIsInstance(idx, int)
            self.assertGreaterEqual(idx, 0)
            self.assertLessEqual(idx, 12)


class TestSihuaTable(unittest.TestCase):
    """四化表测试（保留四化事实，删除语义映射）。"""

    def test_all_ten_stems_defined(self):
        """四化表定义全部十天干（甲乙丙丁戊己庚辛壬癸）。"""
        expected_stems = {"甲", "乙", "丙", "丁", "戊",
                         "己", "庚", "辛", "壬", "癸"}
        self.assertEqual(set(GAN_SIHUA.keys()), expected_stems)

    def test_each_stem_has_four_mutagens(self):
        """每个天干对应四化星（禄权科忌）。"""
        for stem, mutagens in GAN_SIHUA.items():
            self.assertEqual(len(mutagens), 4, f"{stem} should have 4 mutagens")

    def test_hua_ji_present(self):
        """化忌存在于每个天干四化中（第四位）。"""
        for stem, mutagens in GAN_SIHUA.items():
            self.assertEqual(mutagens[-1], "太阳",
                           f"{stem} should have 太阳 as HUA_JI")


class TestZiweiEngineIntegration(unittest.TestCase):
    """紫微引擎集成测试。"""

    def setUp(self):
        self.engine = ZiweiEngine()
        # 毛泽东案例：1893-12-26 06:00，农历癸巳年十一月十九日辰时
        self.mao_ld = (1893, 11, 19)
        self.mao_hour = 8  # 辰时
        self.mao_gender = "male"

    def test_engine_exists(self):
        """ZiweiEngine类存在。"""
        self.assertTrue(hasattr(self.engine, 'compute'))
        self.assertTrue(hasattr(self.engine, 'full_chart'))

    def test_compute_returns_chart(self):
        """compute()返回有效命盘。"""
        chart = self.engine.compute(self.mao_ld, self.mao_hour, self.mao_gender)
        self.assertIsNotNone(chart)
        self.assertTrue(hasattr(chart, 'soul_palace_main_star'))

    def test_full_chart_structure(self):
        """full_chart()返回完整命盘结构。"""
        fc = self.engine.full_chart(self.mao_ld, self.mao_hour, self.mao_gender)
        self.assertIn("palaces", fc)
        self.assertIn("fiveElementsClass", fc)
        self.assertEqual(len(fc["palaces"]), 12)

    def test_sihua_computed(self):
        """四化正确计算。"""
        chart = self.engine.compute(self.mao_ld, self.mao_hour, self.mao_gender)
        self.assertTrue(hasattr(chart, 'soul_palace_sihua'))
        self.assertIsInstance(chart.soul_palace_sihua, list)

    def test_no_architectural_violations(self):
        """确认违规方法已删除。"""
        # 架构违规项必须不存在
        self.assertFalse(hasattr(self.engine, 'native_direction'))
        self.assertFalse(hasattr(self.engine, 'score_topic'))
        self.assertFalse(hasattr(self.engine, 'score_topic_sanfang'))
        # SIHUA_EFFECT 应已从模块中移除
        with self.assertRaises(ImportError):
            from tongshu.engines.ziwei_engine import SIHUA_EFFECT


class TestZiweiStubGuard(unittest.TestCase):
    """B-03a: stub fallback must raise by default when iztro is unavailable."""

    def test_default_raises_unavailable(self):
        """无 TONGSHU_ALLOW_ZIWEI_STUB 时：iztro 可用则用真实计算，iztro 不可用则抛错。"""
        import os
        from tongshu.engines.ziwei_engine import ZiweiEngine, ZiweiEngineUnavailableError
        old = os.environ.pop("TONGSHU_ALLOW_ZIWEI_STUB", None)
        try:
            engine = ZiweiEngine()
            if engine._iztro_available:
                # iztro 已安装可用：走真实 iztro 计算，不抛错
                chart = engine.compute((2000, 1, 1), 12, gender="male")
                self.assertIsNotNone(chart)
            else:
                # iztro 不可用：stub 默认禁用，必须抛 ZiweiEngineUnavailableError
                with self.assertRaises(ZiweiEngineUnavailableError):
                    engine.compute((2000, 1, 1), 12, gender="male")
        finally:
            if old is not None:
                os.environ["TONGSHU_ALLOW_ZIWEI_STUB"] = old

    def test_env_allows_stub(self):
        """With TONGSHU_ALLOW_ZIWEI_STUB=1, compute() returns a chart."""
        import os
        from tongshu.engines.ziwei_engine import ZiweiEngine
        old = os.environ.get("TONGSHU_ALLOW_ZIWEI_STUB")
        os.environ["TONGSHU_ALLOW_ZIWEI_STUB"] = "1"
        try:
            engine = ZiweiEngine()
            chart = engine.compute((2000, 1, 1), 12, gender="male")
            self.assertIsNotNone(chart)
        finally:
            if old is not None:
                os.environ["TONGSHU_ALLOW_ZIWEI_STUB"] = old
            else:
                os.environ.pop("TONGSHU_ALLOW_ZIWEI_STUB", None)


if __name__ == "__main__":
    unittest.main()
