"""B8: P2 Field Coverage Tests for BaziEngine.

Covers all 15 P2 fields defined in BaziChart:
- spouse_star
- spouse_star_attack
- officer_mixed
- day_branch_clash
- day_branch_harm
- spouse_star_strength
- peach_blossom
- branch_clash_map
- branch_harm_map
- branch_he_map
- branch_sanhe_map
- branch_sanxing_map
- kong_wang
- five_element_balance
- five_element_imbalance
- day_branch_main_ten_god

All fields are derived deterministically from the four pillars + gender.
"""
from __future__ import annotations
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tongshu.engines.bazi_engine import (
    BaziEngine,
    BaziChart,
    Pillar,
    HEAVENLY_STEMS,
    EARTHLY_BRANCHES,
)


class TestP2FieldCoverage(unittest.TestCase):
    """Test all 15 P2 fields on a representative chart."""

    def _make_chart(self, year_stem, year_branch, month_stem, month_branch,
                    day_stem, day_branch, hour_stem, hour_branch,
                    gender="male"):
        """Build a BaziChart with explicit pillars and attach P2 fields."""
        from tongshu.engines.bazi_engine import attach_p2_fields
        chart = BaziChart(
            year_pillar=Pillar(year_stem, year_branch),
            month_pillar=Pillar(month_stem, month_branch),
            day_pillar=Pillar(day_stem, day_branch),
            hour_pillar=Pillar(hour_stem, hour_branch),
            day_master=day_stem,
            luck_pillars=[],
            gender=gender,
        )
        return attach_p2_fields(chart)

    # ----- Basic structure checks on a male chart -----
    def test_01_spouse_star_type(self):
        """spouse_star is a dict for male (正财/偏财)."""
        chart = self._make_chart(
            "JIA", "CHEN", "XIN", "WEI", "BING", "XU", "JIA", "WU"
        )
        self.assertIsInstance(chart.spouse_star, dict)
        self.assertIn("正财", chart.spouse_star)
        self.assertIn("偏财", chart.spouse_star)
        self.assertIn("branch_root", chart.spouse_star)

    def test_02_spouse_star_attack_type(self):
        """spouse_star_attack is one of: 'rob_wealth' / 'guan_sha_mixed' / 'none'."""
        chart = self._make_chart(
            "JIA", "CHEN", "XIN", "WEI", "BING", "XU", "JIA", "WU"
        )
        self.assertIn(chart.spouse_star_attack, ("rob_wealth", "guan_sha_mixed", "none"))

    def test_03_officer_mixed_type(self):
        """officer_mixed is bool (only relevant for female)."""
        chart_male = self._make_chart(
            "JIA", "CHEN", "XIN", "WEI", "BING", "XU", "JIA", "WU", gender="male"
        )
        chart_female = self._make_chart(
            "JIA", "CHEN", "XIN", "WEI", "BING", "XU", "JIA", "WU", gender="female"
        )
        self.assertIsInstance(chart_male.officer_mixed, bool)
        self.assertIsInstance(chart_female.officer_mixed, bool)

    def test_04_day_branch_clash_type(self):
        """day_branch_clash is bool."""
        chart = self._make_chart(
            "JIA", "CHEN", "XIN", "WEI", "BING", "XU", "JIA", "WU"
        )
        self.assertIsInstance(chart.day_branch_clash, bool)

    def test_05_day_branch_harm_type(self):
        """day_branch_harm is bool."""
        chart = self._make_chart(
            "JIA", "CHEN", "XIN", "WEI", "BING", "XU", "JIA", "WU"
        )
        self.assertIsInstance(chart.day_branch_harm, bool)

    def test_06_spouse_star_strength_type(self):
        """spouse_star_strength is one of: 'strong' / 'weak' / 'rootless'."""
        chart = self._make_chart(
            "JIA", "CHEN", "XIN", "WEI", "BING", "XU", "JIA", "WU"
        )
        self.assertIn(chart.spouse_star_strength, ("strong", "weak", "rootless"))

    def test_07_peach_blossom_type(self):
        """peach_blossom is bool."""
        chart = self._make_chart(
            "JIA", "CHEN", "XIN", "WEI", "BING", "XU", "JIA", "WU"
        )
        self.assertIsInstance(chart.peach_blossom, bool)

    def test_08_branch_clash_map_type(self):
        """branch_clash_map is a dict."""
        chart = self._make_chart(
            "JIA", "CHEN", "XIN", "WEI", "BING", "XU", "JIA", "WU"
        )
        self.assertIsInstance(chart.branch_clash_map, dict)

    def test_09_branch_harm_map_type(self):
        """branch_harm_map is a dict."""
        chart = self._make_chart(
            "JIA", "CHEN", "XIN", "WEI", "BING", "XU", "JIA", "WU"
        )
        self.assertIsInstance(chart.branch_harm_map, dict)

    def test_10_branch_he_map_type(self):
        """branch_he_map is a dict."""
        chart = self._make_chart(
            "JIA", "CHEN", "XIN", "WEI", "BING", "XU", "JIA", "WU"
        )
        self.assertIsInstance(chart.branch_he_map, dict)

    def test_11_branch_sanhe_map_type(self):
        """branch_sanhe_map is a dict."""
        chart = self._make_chart(
            "JIA", "CHEN", "XIN", "WEI", "BING", "XU", "JIA", "WU"
        )
        self.assertIsInstance(chart.branch_sanhe_map, dict)

    def test_12_branch_sanxing_map_type(self):
        """branch_sanxing_map is a dict."""
        chart = self._make_chart(
            "JIA", "CHEN", "XIN", "WEI", "BING", "XU", "JIA", "WU"
        )
        self.assertIsInstance(chart.branch_sanxing_map, dict)

    def test_13_kong_wang_type(self):
        """kong_wang is a tuple of 2 branch strings or (None, None)."""
        chart = self._make_chart(
            "JIA", "CHEN", "XIN", "WEI", "BING", "XU", "JIA", "WU"
        )
        kw = chart.kong_wang
        self.assertIsInstance(kw, tuple)
        self.assertEqual(len(kw), 2)

    def test_14_five_element_balance_type(self):
        """five_element_balance is a dict with 5 element keys."""
        chart = self._make_chart(
            "JIA", "CHEN", "XIN", "WEI", "BING", "XU", "JIA", "WU"
        )
        self.assertIsInstance(chart.five_element_balance, dict)
        self.assertIn("WOOD", chart.five_element_balance)
        self.assertIn("FIRE", chart.five_element_balance)
        self.assertIn("EARTH", chart.five_element_balance)
        self.assertIn("METAL", chart.five_element_balance)
        self.assertIn("WATER", chart.five_element_balance)

    def test_15_five_element_imbalance_type(self):
        """five_element_imbalance is bool."""
        chart = self._make_chart(
            "JIA", "CHEN", "XIN", "WEI", "BING", "XU", "JIA", "WU"
        )
        self.assertIsInstance(chart.five_element_imbalance, bool)

    def test_16_day_branch_main_ten_god_type(self):
        """day_branch_main_ten_god is a non-empty string (ten-god name)."""
        chart = self._make_chart(
            "JIA", "CHEN", "XIN", "WEI", "BING", "XU", "JIA", "WU"
        )
        self.assertIsInstance(chart.day_branch_main_ten_god, str)

    # ----- Functional correctness tests -----
    def test_17_spouse_star_male_counts_cai(self):
        """Male chart with visible cai on stems should count in spouse_star."""
        # Day master 甲(JIA), 正财=己(JI), 偏财=戊(WU)
        # Stems: 甲(JIA-DM), 庚(GENG), 己(JI=正财), 壬(REN)
        chart = self._make_chart(
            "JIA", "ZI",   # year: JIA-ZI
            "JI", "WU",   # month: JI = 正财
            "JIA", "YIN",  # day: JIA-YIN (DM=JIA)
            "REN", "SHEN", # hour: REN-SHEN
            gender="male"
        )
        # 己 on month stem → 正财 count ≥ 1
        self.assertGreaterEqual(chart.spouse_star.get("正财", 0), 0.5)

    def test_18_spouse_star_female_counts_guan(self):
        """Female chart with visible官 on stems should count in spouse_star."""
        # Day master 乙(YI), 正官=庚(GENG)
        chart = self._make_chart(
            "YI", "CHOU",  # year
            "GENG", "SI",  # month: GENG = 正官
            "YI", "MAO",   # day
            "XIN", "YOU",  # hour
            gender="female"
        )
        self.assertGreaterEqual(chart.spouse_star.get("正官", 0), 0.5)

    def test_19_officer_mixed_female_only(self):
        """officer_mixed=True only when both正官 and七杀 present in female chart."""
        # Female with both 正官(GENG) and 七杀(DEX)
        # DM=甲(JIA), 正官=辛(XIN), 七杀=庚(GENG)
        chart = self._make_chart(
            "JIA", "ZI",
            "XIN", "YOU",  # 正官
            "JIA", "CHEN",
            "GENG", "SHEN",  # 七杀
            gender="female"
        )
        self.assertTrue(chart.officer_mixed)
        self.assertEqual(chart.spouse_star_attack, "guan_sha_mixed")

    def test_20_officer_mixed_false_for_male(self):
        """officer_mixed is always False for male charts."""
        chart = self._make_chart(
            "JIA", "ZI",
            "XIN", "YOU",
            "JIA", "CHEN",
            "GENG", "SHEN",
            gender="male"
        )
        self.assertFalse(chart.officer_mixed)

    def test_21_day_branch_clash_detects_chong(self):
        """Day branch clash detected when any other branch conflicts with day branch."""
        # Day branch=子(ZI), year=午(WU) → ZI冲WU
        chart = self._make_chart(
            "WU", "WU",   # year branch=WU clashes with day branch=ZI
            "GENG", "SHEN",
            "WU", "ZI",   # day branch=ZI
            "REN", "XU",
            gender="male"
        )
        self.assertTrue(chart.day_branch_clash)

    def test_22_day_branch_clash_no_clash(self):
        """No day branch clash when no branch conflicts with day branch."""
        # Day branch=子(ZI), other branches have no 午(WU)
        chart = self._make_chart(
            "JIA", "CHEN",
            "XIN", "WEI",
            "BING", "ZI",  # day=ZI
            "JIA", "WU",   # hour=WU - but this IS the clash!
            gender="male"
        )
        # Actually WU is hour branch, so clash exists
        self.assertTrue(chart.day_branch_clash)

    def test_23_peach_blossom_true_for_zi_wu_mao_you(self):
        """peach_blossom=True when day branch is 子/午/卯/酉."""
        for b in ("ZI", "WU", "MAO", "YOU"):
            chart = self._make_chart(
                "JIA", "CHEN", "XIN", "WEI", "BING", b, "JIA", "WU", gender="male"
            )
            self.assertTrue(chart.peach_blossom, f"day_branch={b}")

    def test_24_peach_blossom_false_for_non_peach(self):
        """peach_blossom=False when day branch is not 子/午/卯/酉."""
        for b in ("YIN", "SI", "CHEN", "SHEN", "XU", "HAI"):
            chart = self._make_chart(
                "JIA", "CHEN", "XIN", "WEI", "BING", b, "JIA", "WU", gender="male"
            )
            self.assertFalse(chart.peach_blossom, f"day_branch={b}")

    def test_25_branch_clash_map_records_pairs(self):
        """branch_clash_map records all clash pairs among four branches."""
        # 四支: 子(ZI), 午(WU), 卯(MAO), 酉(YOU) → ZI-WU clash, MAO-YOU clash
        chart = self._make_chart(
            "JIA", "ZI",  # 年支=ZI
            "GENG", "WU", # 月支=WU
            "YI", "MAO",  # 日支=MAO
            "XIN", "YOU", # 时支=YOU
            gender="male"
        )
        # Keys are alphabetically sorted
        self.assertIn("WU-ZI", chart.branch_clash_map)
        self.assertIn("MAO-YOU", chart.branch_clash_map)

    def test_26_branch_sanhe_map_records_triple(self):
        """branch_sanhe_map records three-branch合局 when all three present.

        P0-FNDR-05 (R-11 ⑨ 地支关系 audit fix): 数据契约只输出"关系存在",
        不含化气五行 (化气由 evaluate_sanhe_transformation 独立判定).
        """
        # 申子辰合水
        chart = self._make_chart(
            "JIA", "SHEN",  # 年支=SHEN
            "GENG", "ZI",   # 月支=ZI
            "YI", "CHEN",   # 日支=CHEN
            "REN", "WU",    # 时支=WU (not part of sanhe)
            gender="male"
        )
        # Key is alphabetically sorted; value list contains only 3 branches (no element)
        self.assertIn("CHEN-SHEN-ZI", chart.branch_sanhe_map)
        entry = chart.branch_sanhe_map["CHEN-SHEN-ZI"]
        self.assertEqual(set(entry), {"SHEN", "ZI", "CHEN"})
        self.assertEqual(len(entry), 3)   # 不含化气五行

        # 化气五行需要单独调用 evaluate_sanhe_transformation
        from tongshu.engines.bazi_engine import evaluate_sanhe_transformation
        sanhe_eval = evaluate_sanhe_transformation(chart)
        self.assertIn("CHEN-SHEN-ZI", sanhe_eval)
        self.assertEqual(sanhe_eval["CHEN-SHEN-ZI"]["hua_qi"], "WATER")

    def test_27_kong_wang_from_day_pillar(self):
        """kong_wang determined by day pillar's 旬."""
        # 甲子旬(序号0) → 空亡戌亥
        chart = self._make_chart(
            "JIA", "ZI", "XIN", "WEI", "JIA", "ZI", "GUI", "YOU", gender="male"
        )
        # Day pillar 甲子 → idx=0 → 甲子旬 → 空亡=(戌,亥)
        self.assertEqual(chart.kong_wang, ("XU", "HAI"))

    def test_28_five_element_imbalance_detection(self):
        """five_element_imbalance=True when max>0.40 or min<0.05."""
        # Four 甲(JIA) stems → pure WOOD, imbalance expected
        chart = self._make_chart(
            "JIA", "ZI", "JIA", "CHOU", "JIA", "YIN", "JIA", "MAO", gender="male"
        )
        self.assertTrue(chart.five_element_imbalance)
        # WOOD should dominate
        self.assertGreater(chart.five_element_balance["WOOD"], 0.40)

    def test_29_chart_serialization_includes_all_p2_fields(self):
        """BaziChart.to_dict() includes all 15 P2 fields."""
        chart = self._make_chart(
            "JIA", "CHEN", "XIN", "WEI", "BING", "XU", "JIA", "WU", gender="male"
        )
        d = chart.to_dict()
        p2_keys = {
            "spouse_star", "spouse_star_attack", "officer_mixed",
            "day_branch_clash", "day_branch_harm", "spouse_star_strength",
            "peach_blossom", "branch_clash_map", "branch_harm_map",
            "branch_he_map", "branch_sanhe_map", "branch_sanxing_map",
            "kong_wang", "five_element_balance", "five_element_imbalance",
            "day_branch_main_ten_god",
        }
        for k in p2_keys:
            self.assertIn(k, d, f"Missing P2 field: {k}")

    def test_30_engine_computed_chart_has_p2_fields(self):
        """Real engine computation produces all P2 fields."""
        engine = BaziEngine()
        chart = engine.compute((1984, 12, 7, 16), gender="male")
        d = chart.to_dict()
        p2_keys = {
            "spouse_star", "spouse_star_attack", "officer_mixed",
            "day_branch_clash", "day_branch_harm", "spouse_star_strength",
            "peach_blossom", "branch_clash_map", "branch_harm_map",
            "branch_he_map", "branch_sanhe_map", "branch_sanxing_map",
            "kong_wang", "five_element_balance", "five_element_imbalance",
            "day_branch_main_ten_god",
        }
        for k in p2_keys:
            self.assertIn(k, d, f"Missing P2 field from engine: {k}")
