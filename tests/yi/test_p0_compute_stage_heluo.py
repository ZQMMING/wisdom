"""P0-03 修复测试：ComputeStage 接入河洛 + 易经解释引擎。

验证：
- ComputeStage.run() 调用 HeluoCanonical，产出 HeluoResult。
- 河洛结果传入 YiAdapter → YiStructure。
- YiStructure 传入 YiInterpretationEngine → YiInterpretation。
- 干支符号转译（英文 → 中文）正确。
- 河洛/易经失败时降级为 None，不中断既有 bazi/ziwei/huangli 主链路。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path("D:/today/backend/src")))

import unittest
from datetime import date

from tongshu.canonical.composer import CanonicalComposer
from tongshu.engines.bazi_engine import BaziEngine
from tongshu.pipeline import TONGSHUPipeline
from tongshu.pipeline_stages.compute_stage import ComputeStage

_REPO_ROOT = Path(__file__).resolve().parents[3]  # D:\\today
if not (_REPO_ROOT / "backend" / "data").is_dir():
    _REPO_ROOT = Path("D:/today")


def _make_stage(pipeline):
    stage = pipeline.compute_stage
    stage.composer = CanonicalComposer(
        theme="WORK",
        engine_versions={
            "bazi": "1.0.0",
            "ziwei": "1.0.0",
            "rules": "1.0.0",
            "reasoning": "1.0.0",
        },
    )
    return stage


class TestComputeStageHeluoYi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline = TONGSHUPipeline.for_demo(_REPO_ROOT)
        cls.stage = _make_stage(cls.pipeline)

    def _run(self):
        return self.stage.run(
            analysis_date=date(2026, 8, 17),
            birth_date=(1984, 12, 7, 16),
            gender="male",
            theme="WORK",
            request_id="RR-TEST-0001",
            trace_id="TRACE-TEST-0001",
        )

    def test_heluo_result_populated(self):
        cr = self._run()
        self.assertIsNotNone(cr.heluo_result)
        self.assertTrue(cr.heluo_result.prenatal.hexagram_name)
        self.assertTrue(cr.heluo_result.postnatal.hexagram_name)
        self.assertTrue(cr.heluo_result.yuantang.yuantang)

    def test_yi_structure_populated_from_heluo(self):
        cr = self._run()
        self.assertIsNotNone(cr.yi_structure)
        # YiStructure.truth_hexagram 必须等于河洛后天卦（结果已传入 YiAdapter）
        self.assertEqual(
            cr.yi_structure.truth_hexagram,
            cr.heluo_result.postnatal.hexagram_name,
        )

    def test_yi_interpretation_populated(self):
        cr = self._run()
        self.assertIsNotNone(cr.yi_interpretation)
        self.assertTrue(cr.yi_interpretation.state)
        self.assertEqual(cr.yi_interpretation.phase, 6)
        # Schema 9：严禁 fortune_score / luck_score
        self.assertFalse(cr.yi_interpretation.has_fortune_score)


class TestBaziToHeluoPillars(unittest.TestCase):
    def test_converts_english_pillars_to_chinese(self):
        chart = BaziEngine().compute((1984, 12, 7, 16), gender="male")
        pillars = ComputeStage._bazi_to_heluo_pillars(chart)
        self.assertEqual(len(pillars), 4)
        for gan, zhi in pillars:
            self.assertIn(gan, "甲乙丙丁戊己庚辛壬癸")
            self.assertIn(zhi, "子丑寅卯辰巳午未申酉戌亥")


class TestHeluoYiDegradation(unittest.TestCase):
    """河洛/易经失败时降级为 None，不中断主链路。"""

    @classmethod
    def setUpClass(cls):
        cls.pipeline = TONGSHUPipeline.for_demo(_REPO_ROOT)
        cls.stage = _make_stage(cls.pipeline)

    def test_heluo_failure_degrades_gracefully(self):
        original = self.stage.heluo_canonical

        class _BrokenCanonical:
            def calculate(self, **kwargs):
                raise RuntimeError("boom")

        self.stage.heluo_canonical = _BrokenCanonical()
        try:
            cr = self.stage.run(
                analysis_date=date(2026, 8, 17),
                birth_date=(1984, 12, 7, 16),
                gender="male",
                theme="WORK",
                request_id="RR-TEST-0002",
                trace_id="TRACE-TEST-0002",
            )
            # 主链路结果必须仍在（不因河洛失败而崩溃）
            self.assertIsNotNone(cr.bazi_chart)
            self.assertIsNotNone(cr.canonical)
            # 河洛/易经降级为 None
            self.assertIsNone(cr.heluo_result)
            self.assertIsNone(cr.yi_structure)
            self.assertIsNone(cr.yi_interpretation)
        finally:
            self.stage.heluo_canonical = original


if __name__ == "__main__":
    unittest.main()
