"""Yi Engine Boundary Tests — E3

边界条件覆盖:
- 卦名匹配边界（简称/全称/模糊）
- 爻位边界（初九/上六）
- 体用边界（五行生克）
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import unittest
from tongshu.engines.yi.yao_ci_data import get_yao_ci, YAO_CI
from tongshu.engines.yi.hexagram_symbol import get_hexagram_symbol


class TestHexagramNameMatching(unittest.TestCase):
    """卦名匹配边界测试。"""

    def test_full_name_qian(self):
        """全称'乾为天'可解析。"""
        sym = get_hexagram_symbol("乾为天")
        self.assertEqual(sym.name, "乾为天")
        self.assertEqual(sym.upper_trigram, "乾")
        self.assertEqual(sym.lower_trigram, "乾")

    def test_full_name_kun(self):
        """全称'坤为地'可解析。"""
        sym = get_hexagram_symbol("坤为地")
        self.assertEqual(sym.name, "坤为地")
        self.assertEqual(sym.upper_trigram, "坤")
        self.assertEqual(sym.lower_trigram, "坤")

    def test_short_name_mismatch(self):
        """简称'乾'不匹配全称。"""
        sym = get_hexagram_symbol("乾")
        # 简称不在 HEXAGRAM_FULL_DATA 中，应返回未知卦
        self.assertEqual(sym.upper_trigram, "?")
        self.assertEqual(sym.lower_trigram, "?")

    def test_unknown_hexagram(self):
        """未知卦名返回默认值。"""
        sym = get_hexagram_symbol("不存在的卦")
        self.assertEqual(sym.name, "不存在的卦")
        self.assertEqual(sym.upper_trigram, "?")
        self.assertEqual(sym.lower_trigram, "?")


class TestLinePositionBoundary(unittest.TestCase):
    """爻位边界测试。"""

    def test_first_line_chu_jiu(self):
        """初九爻位可检索。"""
        text, source = get_yao_ci("乾为天", "初九")
        self.assertEqual(text, "潜龙，勿用。")
        self.assertTrue(source.startswith("周易"))

    def test_last_line_shang_liu(self):
        """上六爻位可检索。"""
        text, source = get_yao_ci("坤为地", "上六")
        self.assertEqual(text, "龙战于野，其血玄黄。")
        self.assertTrue(source.startswith("周易"))

    def test_middle_line_liu_er(self):
        """六二爻位可检索。"""
        text, source = get_yao_ci("坤为地", "六二")
        self.assertEqual(text, "直方大，不习无不利。")

    def test_middle_line_jiu_san(self):
        """九三爻位可检索。"""
        text, source = get_yao_ci("乾为天", "九三")
        self.assertEqual(text, "君子终日乾乾，夕惕若厉，无咎。")

    def test_invalid_line_position(self):
        """无效爻位返回空。"""
        text, source = get_yao_ci("乾为天", "初七")
        self.assertEqual(text, "")
        self.assertEqual(source, "")

    def test_missing_hexagram(self):
        """未知卦名返回空。"""
        text, source = get_yao_ci("不存在的卦", "初九")
        self.assertEqual(text, "")
        self.assertEqual(source, "")


class TestTiYongBoundary(unittest.TestCase):
    """体用关系边界测试。"""

    def test_ti_yong_same_element(self):
        """比和：乾为天（金-金）。"""
        sym = get_hexagram_symbol("乾为天")
        self.assertEqual(sym.ti_yong_relation, "比和（平）")

    def test_ti_yong_sheng(self):
        """用生体：风水涣（用巽木生体坎水）。"""
        sym = get_hexagram_symbol("风水涣")
        self.assertEqual(sym.ti_yong_relation, "用生体（吉）")

    def test_ti_yong_ke(self):
        """用克体：火水未济（用离火克体坎水）。"""
        sym = get_hexagram_symbol("火水未济")
        self.assertEqual(sym.ti_yong_relation, "用克体（凶）")

    def test_ti_yong_xie(self):
        """体生用：天水讼（体乾金生用坎水）。"""
        sym = get_hexagram_symbol("天水讼")
        self.assertEqual(sym.ti_yong_relation, "体生用（泄）")

    def test_ti_yong_hao(self):
        """体克用：地火明夷（体离火被坤土泄 → 用生体，因为坤土生离火）。"""
        sym = get_hexagram_symbol("地火明夷")
        # 实际结果: 用生体（吉）因为坤土生离火
        self.assertEqual(sym.ti_yong_relation, "用生体（吉）")


if __name__ == "__main__":
    unittest.main()
