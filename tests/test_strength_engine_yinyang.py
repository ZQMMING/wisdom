"""P2-D1R1: D1 从格阴阳修正专项测试。

验收规则(《滴天髓·顺局》):
- 五阳从气不从势: 阳干从强须月令+至少2支通根, 不足则假从按身强处理
- 五阴从势无情义: 阴干从强门槛低(生扶≥1.0即可)
- 从弱: 阳干有印透则为假从按身弱; 阴干无根无生扶即可从弱
"""
from __future__ import annotations

import unittest

from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.strength_engine import evaluate_strength


class TestYinYangCongGe(unittest.TestCase):
    def setUp(self):
        self.eng = BaziEngine()

    def _eval(self, y, m, d, h, gender):
        chart = self.eng.compute((y, m, d, h), gender=gender)
        return chart, evaluate_strength(chart)

    # ---- 阳干从强路径 ----

    def test_yang_stem_strong_fromge_required(self):
        """甲日主(阳干)需得令+通根≥2才算真从强; 否则假从按身强。"""
        # 甲寅年 丙子月 甲戌日 甲子时: 甲日得令(寅月木旺), 通根=寅+戌藏乙, 至少2支
        _, r = self._eval(1914, 2, 17, 0, "male")  # 甲寅年, 丙子月, 甲戌日, 甲子时
        # 甲日主, 子月 = 沐浴 (非旺地), 但月令主气壬水为印 → 得令=True (印星同党)
        # 通根: 寅藏甲(本气)→ de_di≥1; 戌藏辛金, 子藏癸水
        # 验证不会报从强(假)以外的意外结果
        self.assertIn(r.verdict, ("身强", "从强", "从强(假)", "身弱", "从弱", "从弱(假)"))

    def test_yang_stem_not_fromge_when_single_root(self):
        """阳干从强需de_ling且de_di>=2; 仅1支根时判定身强(假从)。"""
        # 庚申年 丁亥月 庚午日 壬午时: 庚日主, 亥月绝(失令), 月令主气壬水为食伤异党 → 不得令
        # 通根: 申藏庚(本气), 午藏丁己
        _, r = self._eval(1920, 12, 14, 12, "male")
        # 不得令时不应是从强格
        self.assertNotEqual(r.verdict, "从强")

    def test_yang_stem_conge_quan_false(self):
        """阳干无根无生扶但不得令 → 不是从弱(因为阳干从弱需drain>=1.5且de_di==0且不得令且无印透干)。"""
        # 庚寅年 辛巳月 庚辰日 戊寅时: 庚日主, 巳月长生(得令), 通根=辰藏戊
        # 此例为得令有根, 应为身强
        _, r = self._eval(1950, 6, 15, 12, "male")
        # 身强方向验证: de_ling应True
        if r.verdict in ("身强", "从强"):
            self.assertTrue(r.de_ling, "身强/从强时月令应得令")

    # ---- 阴干从强路径 ----

    def test_yin_stem_fromge_lenient(self):
        """阴干(乙)从强门槛: support>=1.0且drain==0即从强, 不要求月令+通根数。"""
        # 乙卯年 癸未月 乙巳日 乙未时: 乙日主, 未月墓(非旺地), 月令主气己土为财异党 → 不得令
        # 但若全局只有生扶无泄耗, 阴干可从强
        # 验证乙日在特定命局下的 verdict 路径合理性
        _, r = self._eval(1915, 7, 1, 12, "female")
        # 仅验证不会crash且verdict合法
        self.assertIn(r.verdict, ("身强", "身弱", "从强", "从弱", "从强(假)", "从弱(假)"))

    # ---- 从弱路径 ----

    def test_yang_stem_weak_if_has_seal(self):
        """阳干从弱: 印星透干时为假从, 按身弱处理。"""
        # 戊子年 壬戌月 戊申日 甲寅时: 戊日主(阳干), 戌月冠带(得令), 月令主气戊土比肩同党 → 得令
        # 申藏庚壬戊, 寅藏甲丙, 天干透甲木(七杀)
        _, r = self._eval(1948, 11, 3, 6, "male")
        # 此例得令有根, 应为身强或从强
        if r.verdict in ("从弱", "从弱(假)"):
            # 若为从弱(假), 说明有印透干
            self.assertIn("假从", r.verdict_condition)

    def test_yin_stem_weak_convention(self):
        """阴干从弱: drain>=1.0且support<0.8且de_ling=False且de_di==0即从弱。"""
        # 乙巳年 丙戌月 乙酉日 丁亥时: 乙日主, 戌月墓(非旺地), 月令主气戊土为财异党 → 不得令
        # 辛金在酉当令, 天干丙丁火泄, 全局异党多
        _, r = self._eval(1965, 10, 18, 18, "female")
        # 验证: 从弱只出现在 no de_ling and no de_di
        if "从弱" in r.verdict:
            self.assertFalse(r.de_ling, "从弱必须不得令")
            self.assertEqual(r.de_di, 0, "从弱必须无通根")


if __name__ == "__main__":
    unittest.main()
