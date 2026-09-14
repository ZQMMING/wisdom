# -*- coding: utf-8 -*-
"""Z27: 庙旺利陷亮度表（明刊《捷览》星论补遗）测试"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
os.environ["TONGSHU_ALLOW_ZIWEI_STUB"] = "1"

from tongshu.engines.ziwei_engine import ZiweiEngine
from tongshu.engines.ziwei.rules.brightness import BRIGHTNESS_TABLE, get_brightness
from tongshu.engines.ziwei.rules.interpretation import NihaiAssertionResolver


def _chart():
    engine = ZiweiEngine()
    return engine.full_chart((1983, 9, 29), 11, "male")


class TestBrightnessTable:
    """亮度表数据完整性：14 主星 × 12 地支全覆盖"""

    def test_14_stars(self):
        assert set(BRIGHTNESS_TABLE.keys()) == {
            "紫微", "天机", "太阳", "武曲", "天同", "廉贞", "天府", "太阴",
            "贪狼", "巨门", "天相", "天梁", "七杀", "破军",
        }

    def test_12_branches(self):
        branches = {"子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"}
        for star, row in BRIGHTNESS_TABLE.items():
            assert set(row.keys()) == branches, f"{star} 缺地支"
            assert all(v in ("庙", "平", "陷") for v in row.values()), f"{star} 非法亮度"

    def test_get_brightness_known(self):
        assert get_brightness("紫微", "子") == "庙"
        assert get_brightness("紫微", "辰") == "陷"
        assert get_brightness("太阳", "午") == "庙"
        assert get_brightness("太阳", "亥") == "陷"
        assert get_brightness("七杀", "午") == "庙"

    def test_get_brightness_unknown(self):
        assert get_brightness("不存在星", "子") == "平"
        assert get_brightness("紫微", "X") == "平"


class TestChartBrightness:
    """full_chart 亮度注入：1983 案例"""

    def test_palace_brightness_field(self):
        chart = _chart()
        assert "brightness" in chart.palaces["命宫"]

    def test_minggong_qisha_miao(self):
        """命宫辰，七杀庙（明刊口径）"""
        chart = _chart()
        assert chart.palaces["命宫"]["brightness"]["七杀"] == "庙"

    def test_fude_ziwei_miao(self):
        """福德宫午，紫微庙"""
        chart = _chart()
        assert chart.palaces["福德"]["brightness"]["紫微"] == "庙"

    def test_xiongdi_taiyang_miao(self):
        """兄弟宫卯，太阳庙"""
        chart = _chart()
        assert chart.palaces["兄弟"]["brightness"]["太阳"] == "庙"


class TestBrightnessAssertions:
    """resolver 亮度断言触发"""

    def test_brightness_assertions_present(self):
        entries = NihaiAssertionResolver().resolve(_chart())
        bright = [e for e in entries if e.category == "庙旺利陷" and e.source.startswith("明刊")]
        assert len(bright) >= 10

    def test_qisha_ming_miao(self):
        entries = NihaiAssertionResolver().resolve(_chart())
        hit = [e for e in entries if e.star == "七杀" and e.category == "庙旺利陷"]
        assert hit and "入庙" in hit[0].text

    def test_taiyang_wu_special(self):
        """太阳午庙（倪师原话）——用另一个案例触发：需命盘太阳在午。"""
        # 1983 案例太阳在卯（兄弟宫），午宫紫微。构造直接调用表数据断言：
        assert get_brightness("太阳", "午") == "庙"
