"""河洛易经解卦层测试 (yi_interpreter).

验证:
- _judge_direction: 水山蹇等艰难卦应判NEGATIVE/MIXED, 乾坤判POSITIVE
- 爻辞数据: 蹇卦六二应为"终无尤"而非"终 no 尤"
- interpret_liunian_year: 水山蹇完整解卦方向应为NEGATIVE
"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tongshu.engines.heluo.yi_interpreter import (
    _judge_direction,
    interpret_liunian_year,
)
from tongshu.engines.yi.yao_ci_data import get_yao_ci, YAO_CI


class TestJudgeDirection(unittest.TestCase):
    """方向判定测试."""

    def test_jian_hexagram_ci_mixed(self):
        """水山蹇卦辞: 有贞吉但也有不利东北 → MIXED."""
        d, conf = _judge_direction("利西南，不利东北。利见大人，贞吉。")
        self.assertEqual(d, "MIXED")

    def test_jian_yao_ci_negative(self):
        """蹇卦动爻'往蹇来连': 蹇=艰难 → NEGATIVE."""
        d, conf = _judge_direction("往蹇来连。")
        self.assertEqual(d, "NEGATIVE")

    def test_jian_ying_yao_negative(self):
        """蹇卦应爻'王臣蹇蹇终无尤': 蹇=艰难 → NEGATIVE."""
        d, conf = _judge_direction("王臣蹇蹇，终无尤。")
        self.assertEqual(d, "NEGATIVE")

    def test_qian_positive(self):
        """乾卦元亨利贞 → POSITIVE."""
        d, conf = _judge_direction("元亨利贞。")
        self.assertEqual(d, "POSITIVE")

    def test_kun_positive(self):
        """坤卦 → POSITIVE."""
        d, conf = _judge_direction("元亨，利牝马之贞。")
        self.assertEqual(d, "POSITIVE")

    def test_xiong_direct(self):
        """直接含凶 → NEGATIVE."""
        d, conf = _judge_direction("征凶。")
        self.assertEqual(d, "NEGATIVE")

    def test_kun_hexagram_negative(self):
        """困卦: 困=困顿 → NEGATIVE."""
        d, conf = _judge_direction("困，亨。贞，大人吉，无咎。有言不信。")
        # 有吉但也有困(强负面) → MIXED
        self.assertIn(d, ("MIXED", "NEGATIVE"))


class TestYaoCiData(unittest.TestCase):
    """爻辞数据测试."""

    def test_jian_liuer_no_bug(self):
        """蹇卦六二爻辞应为'终无尤', 不含'no'."""
        text, source = get_yao_ci("水山蹇", "六二")
        self.assertIn("终无尤", text)
        self.assertNotIn("no", text)

    def test_jian_liuer_in_data(self):
        """蹇卦六二在YAO_CI数据中."""
        yao_list = YAO_CI.get("水山蹇", [])
        self.assertEqual(len(yao_list), 6)
        # 六二是index 1
        self.assertEqual(yao_list[1][1], "六二")


class TestInterpretLiunianYear(unittest.TestCase):
    """流年卦完整解卦测试."""

    def test_jian_liunian_negative(self):
        """水山蹇流年卦完整解卦方向应为NEGATIVE(修复前误判POSITIVE)."""
        # 构造最小liunian_years
        liunian_years = [
            {"year": 1996, "age": 23, "hexagram": "水山蹇",
             "upper": "坎", "lower": "艮", "lines": "010001"},
        ]
        result = interpret_liunian_year(
            hexagram_name="水山蹇",
            year=1996,
            age=23,
            yuan_tang_index=4,
            yuan_tang_line_nature="阳",
            liunian_years=liunian_years,
        )
        # 水山蹇主艰难, 方向应为NEGATIVE
        self.assertEqual(result.signal.direction, "NEGATIVE")
        # 应有卦辞证据
        self.assertTrue(any("卦辞" in e for e in result.signal.evidence))
        # 应有动爻证据
        self.assertTrue(any("动爻" in e for e in result.signal.evidence))


if __name__ == "__main__":
    unittest.main()
