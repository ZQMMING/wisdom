# -*- coding: utf-8 -*-
"""Z30: 亮度表逐字对照修正 + 命图26 端到端验证"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
os.environ["TONGSHU_ALLOW_ZIWEI_STUB"] = "1"

from tongshu.engines.ziwei.rules.brightness import BRIGHTNESS_TABLE, get_brightness
from tongshu.engines.ziwei_engine import ZiweiEngine


class TestBrightnessCorrections:
    def test_wuqu_mao_is_xian(self):
        """武曲卯=陷（原文'卯申酉陷'）"""
        assert get_brightness("武曲", "卯") == "陷"

    def test_lianzhen_you_is_xian(self):
        """廉贞酉=陷（原文'巳酉亥陷'）"""
        assert get_brightness("廉贞", "酉") == "陷"

    def test_wuqu_shen_you_xian(self):
        """武曲申酉=陷（原文同句，未破坏）"""
        assert get_brightness("武曲", "申") == "陷"
        assert get_brightness("武曲", "酉") == "陷"

    def test_lianzhen_si_hai_xian(self):
        """廉贞巳亥=陷（原文同句）"""
        assert get_brightness("廉贞", "巳") == "陷"
        assert get_brightness("廉贞", "亥") == "陷"

    def test_qixing_wu_miao(self):
        """七杀午=庙（Z27 裁决保持，未被误改）"""
        assert get_brightness("七杀", "午") == "庙"


class TestMingTu26Case:
    """古今命图26（秀才之命）：丙辰年十月廿八子时 阳男 木三局"""

    def test_five_elements(self):
        """五行局=木三局（与原著命图一致）"""
        chart = ZiweiEngine().full_chart((1976, 10, 28), 23, "male")
        assert chart.fiveElementsClass == "木三局"

    def test_soul_branch_hai(self):
        """命宫地支=亥（与原著'命[身]生亥'一致）"""
        chart = ZiweiEngine().full_chart((1976, 10, 28), 23, "male")
        assert chart.soul_earthly_branch == "亥"

    def test_body_branch_hai(self):
        """身宫地支=亥（原著命身同宫亥）"""
        chart = ZiweiEngine().full_chart((1976, 10, 28), 23, "male")
        assert chart.body_earthly_branch == "亥"

    def test_ming_tianliang(self):
        """命宫主星=天梁"""
        chart = ZiweiEngine().full_chart((1976, 10, 28), 23, "male")
        assert chart.palaces["命宫"]["major"] == ["天梁"]
