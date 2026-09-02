"""紫微斗数引擎测试 - Ziwei (紫微) Engine

覆盖:
- MAIN_STAR_USO 映射完整性
- Sihua 效果映射
- 中文字星名到拼音键映射
- time_index_from_hour 时辰计算
- 晚子时/早子时边界
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


class TestMainStarMapping(unittest.TestCase):
    """主星映射测试。"""
    
    def test_all_14_main_stars_mapped(self):
        """14主星全部映射到USO类型（2026-08-27 修正：补天相）。"""
        expected_keys = {
            "ZIWEI", "TIANFU", "TAIYANG", "TIANLIANG",
            "WUQU", "TAIYIN", "TIANTONG", "TIANJI",
            "TANLANG", "LIANZHEN", "POJUN", "QISHA", "JUMEN",
            "TIANXIANG",
        }
        self.assertEqual(set(MAIN_STAR_USO.keys()), expected_keys)
    
    def test_tianxiang_not_mapped(self):
        """天相已映射（《紫微斗数全书》14主星之一，2026-08-27 修正）。"""
        self.assertIn("TIANXIANG", MAIN_STAR_USO)
    
    def test_all_stars_have_uso_type(self):
        """所有主星都有USO类型。"""
        for star, uso in MAIN_STAR_USO.items():
            self.assertIn(uso, {"SUPPORT", "RESOURCE", "REFLECTION", "ACTION", "CONSTRAINT", "CHANGE"})


class TestSihuaEffect(unittest.TestCase):
    """四化效果测试。"""
    
    def test_all_four_sihua_mapped(self):
        """四化全部映射。"""
        expected = {"HUA_LU", "HUA_QUAN", "HUA_KE", "HUA_JI"}
        self.assertEqual(set(SIHUA_EFFECT.keys()), expected)
    
    def test_hua_ji_is_restricted(self):
        """化忌方向为DECREASE。"""
        self.assertEqual(SIHUA_EFFECT["HUA_JI"]["direction"], "DECREASE")
        self.assertEqual(SIHUA_EFFECT["HUA_JI"]["polarity"], "restricted")
    
    def test_hua_ji_is_decrease_only(self):
        """只有化忌是DECREASE。"""
        for key, effect in SIHUA_EFFECT.items():
            if key != "HUA_JI":
                self.assertEqual(effect["direction"], "INCREASE")


class TestChineseStarMapping(unittest.TestCase):
    """中文字星名映射测试。"""
    
    def test_all_chinese_stars_mapped(self):
        """所有中文星名映射到拼音键（2026-08-27 修正：天相已补，14主星齐全）。"""
        chinese_names = set(CHINESE_STAR_TO_KEY.keys())
        self.assertEqual(len(chinese_names), 14)  # 含天相
    
    def test_tianxiang_absent(self):
        """天相已在映射中（《紫微斗数全书》14主星之一，2026-08-27 修正）。"""
        self.assertIn("天相", CHINESE_STAR_TO_KEY)
    
    def test_mapping_matches_main_star(self):
        """映射键与MAIN_STAR_USO一致。"""
        for cn, key in CHINESE_STAR_TO_KEY.items():
            self.assertIn(key, MAIN_STAR_USO)


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


class TestZiweiEngineIntegration(unittest.TestCase):
    """紫微引擎集成测试。"""

    def test_engine_exists(self):
        """ZiweiEngine类存在。"""
        from tongshu.engines.ziwei_engine import ZiweiEngine
        self.assertTrue(hasattr(ZiweiEngine, 'compute'))

    def test_adapter_exists(self):
        """ZiweiAdapter类存在。"""
        from tongshu.engines.ziwei_adapter import ZiweiAdapter
        self.assertTrue(hasattr(ZiweiAdapter, 'compute'))


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
                # iztro 已安装可用：走真实 iztro 计算，不抛错（stub 未被启用也无妨）
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
