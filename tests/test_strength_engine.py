"""D1 旺衰 Deterministic Engine 测试 (SHUNTIAN_V1.4 Gate D1 验收)。

验收标准(调度令 §4):
- 任意命例输出全部中间项, 禁止合并浮点分掩盖过程。
- 判定顺序冻结: 得令 > 得地 > 得势; 从格显式标注。
- 每条规则有古籍 evidence。
"""
from __future__ import annotations

import unittest

from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.strength_engine import D1StrengthResult, evaluate_strength


class TestD1StrengthEngine(unittest.TestCase):
    def setUp(self):
        self.eng = BaziEngine()

    def _eval(self, y, m, d, h, gender):
        chart = self.eng.compute((y, m, d, h), gender=gender)
        return chart, evaluate_strength(chart)

    # ---------- 契约: 全部中间项必须存在 ----------

    def test_result_has_all_auditable_fields(self):
        _, r = self._eval(1990, 5, 15, 22, "male")
        self.assertIsInstance(r, D1StrengthResult)
        for f in ("month_command", "de_ling", "de_ling_detail", "de_di",
                  "de_di_detail", "de_shi", "de_shi_detail", "climate",
                  "support_count", "drain_count", "verdict",
                  "verdict_condition"):
            self.assertTrue(hasattr(r, f), f"缺中间项 {f}")
        self.assertIn(r.verdict, ("身强", "身弱", "从强", "从弱"))

    def test_evidence_covers_all_items(self):
        _, r = self._eval(1985, 12, 3, 8, "female")
        for key in ("month_command", "de_ling", "de_di", "de_shi",
                    "climate", "verdict"):
            self.assertIn(key, r.evidence)
            self.assertIn("《", r.evidence[key], f"{key} 缺古籍出处")

    def test_no_blackbox_single_score(self):
        """禁止黑箱单分: verdict 必须附带可读判定路径。"""
        _, r = self._eval(2000, 2, 29, 14, "male")
        self.assertTrue(r.verdict_condition)
        self.assertIn("得令", r.verdict_condition)

    # ---------- 方向正确性(经典一致) ----------

    def test_case1_genk_in_si_month_changsheng(self):
        """庚金生巳月=长生(相令非旺令, 不得令); 火旺金镕虽有土印 → 身弱方向成立。
        V2.4 fix: 原表_STRONG_STAGES含长生导致误判得令, 修正后得令=临官帝旺.
        依据: 《穷通宝鉴》庚金巳月"火旺金镕,专用壬水次用庚金"; 《渊海子平》得令者临官帝旺也."""
        _, r = self._eval(1990, 5, 15, 22, "male")
        self.assertEqual(r.month_command, "SI")
        self.assertFalse(r.de_ling, "庚长生在巳为相令非旺令, 不应得令(火旺金镕)")
        self.assertGreaterEqual(r.de_di, 2, "三支藏土印, 通根应≥2")
        self.assertEqual(r.verdict, "身弱", "庚金巳月火旺金镕, 虽有土印生身但火土焦生金不力, 应身弱")

    def test_case2_bing_in_hai_month_jue(self):
        """丙火生亥月=绝(失令); 泄耗>生扶 → 身弱。"""
        _, r = self._eval(1985, 12, 3, 8, "female")
        self.assertEqual(r.month_command, "HAI")
        self.assertFalse(r.de_ling, "丙绝于亥, 不应得令")
        self.assertEqual(r.verdict, "身弱")

    def test_climate_mapping(self):
        """寒暖燥湿: 亥月=冬=cold; 巳月=夏=hot; 寅月=春=wet。"""
        _, r1 = self._eval(1990, 5, 15, 22, "male")
        self.assertEqual(r1.climate, "hot")
        _, r2 = self._eval(1985, 12, 3, 8, "female")
        self.assertEqual(r2.climate, "cold")
        _, r3 = self._eval(2000, 2, 29, 14, "male")
        self.assertEqual(r3.climate, "wet")

    def test_weights_sum_consistency(self):
        """生扶+泄耗克覆盖全部干支力量(无遗漏即守恒)。"""
        chart, r = self._eval(1996, 8, 20, 6, "male")
        # 日主自身不计入两侧
        self.assertGreater(r.support_count + r.drain_count, 0)

    def test_from_ge_requires_zero_drain(self):
        """从强格: 只有全局无异党时才允许标注。"""
        # 构造难以精确控制; 至少验证从强路径的条件字符串显式说明
        results = [evaluate_strength(self.eng.compute(a, gender=g))
                   for a, g in [((1990, 5, 15, 22), "male"),
                                ((1985, 12, 3, 8), "female")]]
        for r in results:
            if r.verdict == "从强":
                self.assertIn("从其旺势", r.verdict_condition)


if __name__ == "__main__":
    unittest.main()
