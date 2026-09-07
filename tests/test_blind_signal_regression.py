# -*- coding: utf-8 -*-
"""Blind Signal Regression Test

验证 CanonicalSignal 构造参数完整性，确保 strength 参数已添加。
测试标准输入 (1990, 5, 15, 10, 'male') 全路径不崩溃。
"""
import sys
import unittest
from pathlib import Path

# ─── 路径独立定位 ──────────────────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / 'src'))

from tongshu.engines.blind_bazi_engine import BlindBaziEngine, compute_blind_bazi
from tongshu.engines.blind_yingqi import BlindYingqiEngine


class TestBlindSignalRegression(unittest.TestCase):
    """Blind Signal 回归测试 - P1 修复验证"""

    def test_standard_input_no_crash(self):
        """标准输入不崩溃：CanonicalSignal 必须包含 strength 参数"""
        birth = (1990, 5, 15, 10)
        gender = 'male'

        # 应不抛出 TypeError: missing 1 required positional argument: 'strength'
        result = compute_blind_bazi(birth, gender)

        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'signals'))

    def test_signal_strength_not_none(self):
        """验证所有信号的 strength 不为 None"""
        birth = (1990, 5, 15, 10)
        result = compute_blind_bazi(birth, 'male')

        for signal in result.signals:
            self.assertIsNotNone(signal.strength,
                f"Signal {signal.signal_id} has None strength")
            self.assertGreaterEqual(signal.strength, 0.0,
                f"Signal {signal.signal_id} strength < 0")
            self.assertLessEqual(signal.strength, 1.0,
                f"Signal {signal.signal_id} strength > 1")

    def test_signal_count_reasonable(self):
        """验证信号数量合理（不应为0或异常多）"""
        birth = (1990, 5, 15, 10)
        result = compute_blind_bazi(birth, 'male')

        # 至少有1个信号（因为默认有体用关系）
        self.assertGreater(len(result.signals), 0,
            "Should have at least one signal")
        # 信号数量不超过20个（防止过度生成）
        self.assertLessEqual(len(result.signals), 20,
            "Should not have too many signals")

    def test_yingqi_no_crash(self):
        """应期分析不崩溃"""
        birth = (1990, 5, 15, 10)
        engine = BlindYingqiEngine()

        # 应期分析不应崩溃
        result = engine.analyze(birth, 'male', target_age=40)

        self.assertIsNotNone(result)
        self.assertEqual(result.age, 40)
        self.assertTrue(hasattr(result, 'triggers'))
        self.assertTrue(hasattr(result, 'yingqi_events'))

    def test_multiple_birth_years(self):
        """多个出生年份验证稳定性"""
        births = [
            (1990, 5, 15, 10),
            (1985, 3, 20, 14),
            (1978, 8, 8, 8),
        ]

        for birth in births:
            with self.subTest(birth=birth):
                result = compute_blind_bazi(birth, 'male')
                self.assertIsNotNone(result)
                # 每个信号都有 strength
                for signal in result.signals:
                    self.assertIsInstance(signal.strength, float)


if __name__ == '__main__':
    unittest.main()
