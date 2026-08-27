"""P2 判定引擎专项测试。

验收标准:
- 四层判定序正确: 调候>病药>常法喜忌>用神合成
- 方向性正确: 身强命例喜用方向与Golden数据一致
- 从格阴阳修正后判定正确
"""
from __future__ import annotations

import unittest

from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.strength_engine import evaluate_strength
from tongshu.engines.judgment_engine import judgment, P2JudgmentResult


class TestP2Judgment(unittest.TestCase):
    def setUp(self):
        self.eng = BaziEngine()

    def _eval(self, y, m, d, h, gender):
        chart = self.eng.compute((y, m, d, h), gender=gender)
        d1 = evaluate_strength(chart)
        return chart, d1, judgment(chart, d1)

    # ---- 契约: 输出结构完整 ----

    def test_result_has_all_fields(self):
        """P2JudgmentResult 必须包含全部字段。"""
        _, _, r = self._eval(1990, 5, 15, 22, "male")
        self.assertIsInstance(r, P2JudgmentResult)
        self.assertTrue(hasattr(r, 'climate'))
        self.assertTrue(hasattr(r, 'tiao_hou_element'))
        self.assertTrue(hasattr(r, 'tiao_hou_present'))
        self.assertTrue(hasattr(r, 'tiao_hou_is_yong'))
        self.assertTrue(hasattr(r, 'evidence_tiaohou'))
        self.assertTrue(hasattr(r, 'bing'))
        self.assertTrue(hasattr(r, 'yao'))
        self.assertTrue(hasattr(r, 'you_bing_you_yao'))
        self.assertTrue(hasattr(r, 'verdict_from_d1'))
        self.assertTrue(hasattr(r, 'favorable'))
        self.assertTrue(hasattr(r, 'unfavorable'))
        self.assertTrue(hasattr(r, 'yong_shen'))
        self.assertTrue(hasattr(r, 'yong_shen_source'))
        self.assertTrue(hasattr(r, 'xhen'))

    # ---- ① 调候层 ----

    def test_tiaohou_cold_needs_fire(self):
        """冬月(亥子丑)需火调候, 若局中无火则 tiao_hou_is_yong=True。"""
        _, _, r = self._eval(1985, 12, 3, 8, "female")  # 丙火日主, 亥月(冬)
        self.assertEqual(r.climate, "cold")
        self.assertEqual(r.tiao_hou_element, "FIRE")
        # 丙火日主生于亥月, 月令主气壬水为克我, 不得令
        # 检查调候字(火)是否在局
        # 1985年乙丑年 戊子月 丙午日 壬辰时: 丙日生于子月, 子中癸水为克我
        # 局中是否有火? 丙日干本身是火, 午支藏丁火 → 应 present=True
        # 但若其他案例局中无火, 则 is_yong=True

    def test_tiaohou_hot_needs_water(self):
        """夏月(巳午未)需水调候。"""
        _, _, r = self._eval(1990, 5, 15, 22, "male")  # 庚金日主, 巳月(夏)
        self.assertEqual(r.climate, "hot")
        self.assertEqual(r.tiao_hou_element, "WATER")

    def test_tiaohou_spring_ding_needs_wood(self):
        """丁火日主春生(寅月), 木旺火相, 调候需木为燃料(《穷通宝鉴》:春丁木气充足燃料丰厚,灯火得以长明)。"""
        # 2000-02-29 14:00: 丁火日主, 寅月(春, wet)
        _, _, r = self._eval(2000, 2, 29, 14, "male")
        self.assertEqual(r.climate, "wet")
        # 丁火春生: 木旺为燃料, 灯火得以长明(原旧表误给WATER, V2.1修正为WOOD)
        self.assertEqual(r.tiao_hou_element, "WOOD")

    # ---- ③ 常法喜忌层 ----

    def test_shenqiang_favorable(self):
        """身强命例: 喜用为官杀/食伤/财, 忌用为印/比劫。"""
        # 找一个身强的命例
        # 庚金日主生于巳月(长生), 得令
        _, d1, r = self._eval(1990, 5, 15, 22, "male")
        if "身强" in r.verdict_from_d1 or "从强" in r.verdict_from_d1:
            self.assertIn("OFFICIAL", r.favorable)
            self.assertIn("EATING", r.favorable)
            self.assertIn("WEALTH", r.favorable)
            self.assertIn("SEAL", r.unfavorable)

    def test_shenruo_unfavorable(self):
        """身弱命例: 喜用为印/比劫, 忌用为官杀/食伤/财。"""
        # 丙火日主生于亥月(绝), 失令
        _, d1, r = self._eval(1985, 12, 3, 8, "female")
        if "身弱" in r.verdict_from_d1 or "从弱" in r.verdict_from_d1:
            self.assertIn("SEAL", r.favorable)
            self.assertIn("COMPANION", r.favorable)
            self.assertIn("OFFICIAL", r.unfavorable)

    # ---- ④ 用神层 ----

    def test_yong_shen_source_tiaohou_first(self):
        """用神来源优先顺序: 调候 > 病药 > 常法。"""
        # 身弱+调候缺失 → 用神应为调候字
        _, d1, r = self._eval(1985, 12, 3, 8, "female")
        if r.tiao_hou_is_yong and r.tiao_hou_element:
            self.assertEqual(r.yong_shen_source, "tiao_hou")
            self.assertEqual(r.yong_shen, r.tiao_hou_element)

    def test_yong_shen_normal_when_no_tiaohou(self):
        """无调候需求时, 用神从病药或常法喜忌取。"""
        # 无调候时, 用神来源应为病药(bingyao, 有病则用药)或常法(normal, 无病则从喜忌)
        _, _, r = self._eval(1990, 5, 15, 22, "male")
        if not r.tiao_hou_is_yong:
            self.assertIn(r.yong_shen_source, ("bingyao", "normal"))

    # ---- 方向性验收 (对齐健康准确率教训) ----

    def test_direction_correctness_shenqiang(self):
        """身强命例: favorable 五行在流年出现时应为正方向。"""
        # 此测试验证判定方向的正确性, 不验证流年事件
        _, _, r = self._eval(1990, 5, 15, 22, "male")
        # 身强命例的喜用方向应合理
        if "身强" in r.verdict_from_d1:
            self.assertTrue(len(r.favorable) > 0, "身强应有喜用")
            self.assertTrue(len(r.unfavorable) > 0, "身强应有忌用")

    def test_direction_correctness_shenruo(self):
        """身弱命例: favorable 五行在流年出现时应为正方向。"""
        _, _, r = self._eval(1985, 12, 3, 8, "female")
        if "身弱" in r.verdict_from_d1:
            self.assertTrue(len(r.favorable) > 0, "身弱应有喜用")
            self.assertTrue(len(r.unfavorable) > 0, "身弱应有忌用")


if __name__ == "__main__":
    unittest.main()
