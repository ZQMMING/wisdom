"""DTS-103 日支通根 - 旺衰评分新增维度验证。

验收标准:
1. 有根案例 (日支藏干含比/劫): tonggen_score=+1, rule_refs 含 DTS-103
2. 无根案例 (日支藏干不含比/劫): tonggen_score=-1
3. 1980-06-22 案例: 总分从 3→4, MODERATE→STRONG
4. score_detail 包含 tonggen_score / tonggen_rooted
5. T-3 全量回归无新失败
"""
import os, sys, json
from pathlib import Path
import unittest
from datetime import datetime, date
from zoneinfo import ZoneInfo

os.environ['TONGSHU_AUTHORITY_CREDENTIALS'] = 'architecture-governance:schema-v1-arch-gov-2026;admission_registry:test-cred-hash'
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from tongshu.reasoning.judgment import WANGSHUAIJudgment, _check_tonggen, JudgmentConclusion
from tongshu.engines.bazi_engine import BaziEngine
from tongshu.reasoning.ziping_bridge import run_ziping_judgment


def _pillar(stem, branch, pos):
    return {"position": pos, "heavenly_stem": stem, "earthly_branch": branch}


def _ctx(year, month, day, hour, dm):
    pillars = [
        _pillar(*year, "YEAR"), _pillar(*month, "MONTH"),
        _pillar(*day, "DAY"), _pillar(*hour, "HOUR"),
    ]
    return {"natal": {"pillars": pillars, "day_master": dm}}


class TestDTS103Tonggen(unittest.TestCase):
    """DTS-103 日支通根打分维度测试。"""

    def test_19800622_tonggen_has_root(self):
        """1980-06-22: 丙寅日 → 寅藏丙比肩 → 有根 (+1)。"""
        # GENG-SHEN, REN-WU, BING-YIN, GUI-SI
        c = _ctx(("GENG", "SHEN"), ("REN", "WU"), ("BING", "YIN"), ("GUI", "SI"), "BING")
        score, rooted = _check_tonggen("BING", c["natal"]["pillars"])
        self.assertEqual(score, 1, "丙寅: 寅藏丙=比肩, 应有根")
        self.assertTrue(rooted)

    def test_19800622_total_score_strong(self):
        """1980-06-22: 通根 +1 使总分 3→4, MODERATE→STRONG。"""
        c = _ctx(("GENG", "SHEN"), ("REN", "WU"), ("BING", "YIN"), ("GUI", "SI"), "BING")
        j = WANGSHUAIJudgment.judge([], c)
        self.assertEqual(j.conclusion, JudgmentConclusion.STRONG)
        self.assertEqual(j.score, 4.0)
        detail = j.score_detail or {}
        self.assertEqual(detail.get("tonggen_score"), 1)
        self.assertTrue(detail.get("tonggen_rooted"))
        # DTS-103 应出现在 rule_refs 和 evidence_refs
        self.assertIn("DTS-103", j.rule_refs)
        self.assertIn("E-DTS-103-001", j.evidence_refs)

    def test_no_root_negative_score(self):
        """无根案例: 日支藏干不含比/劫 → tonggen=-1。"""
        # 甲日主, 日支午(丁火+己土, 无甲乙比劫)
        c = _ctx(("REN", "ZI"), ("JIA", "YIN"), ("JIA", "WU"), ("GENG", "SHEN"), "JIA")
        score, rooted = _check_tonggen("JIA", c["natal"]["pillars"])
        self.assertEqual(score, -1, "甲午: 午藏丁己, 无比劫根, 应无根")
        self.assertFalse(rooted)

    def test_score_detail_fields_present(self):
        """score_detail 必须包含 tonggen_score / tonggen_rooted。"""
        c = _ctx(("GENG", "SHEN"), ("REN", "WU"), ("BING", "YIN"), ("GUI", "SI"), "BING")
        j = WANGSHUAIJudgment.judge([], c)
        detail = j.score_detail or {}
        self.assertIn("tonggen_score", detail)
        self.assertIn("tonggen_rooted", detail)
        self.assertIn("total_score", detail)

    def test_reasoning_contains_tonggen(self):
        """reasoning 字符串必须包含通根说明。"""
        c = _ctx(("GENG", "SHEN"), ("REN", "WU"), ("BING", "YIN"), ("GUI", "SI"), "BING")
        j = WANGSHUAIJudgment.judge([], c)
        self.assertIn("通根", j.reasoning)
        self.assertIn("YIN", j.reasoning)
        self.assertIn("有根", j.reasoning)

    def test_full_pipeline_19800622(self):
        """端到端: BaziEngine → run_ziping_judgment → WANGSHUAI=STRONG。"""
        engine = BaziEngine()
        dt = datetime(1980, 6, 22, 10, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
        chart = engine.compute(solar_date=(1980, 6, 22, 10), gender="male", birth_datetime=dt)
        synth = run_ziping_judgment(chart)
        self.assertEqual(synth.wangshuai.conclusion, JudgmentConclusion.STRONG)
        self.assertEqual(synth.wangshuai.score, 4.0)


class TestDTS103BackwardCompatibility(unittest.TestCase):
    """DTS-103 引入后不破坏既有行为。"""

    def test_wangshuai_strong_preserved(self):
        """强案例: 甲木寅月建禄 + 党众透干 → 仍为 STRONG。"""
        c = _ctx(("JIA", "MAO"), ("YI", "YIN"), ("JIA", "YIN"), ("GENG", "SHEN"), "JIA")
        j = WANGSHUAIJudgment.judge([], c)
        self.assertEqual(j.conclusion, JudgmentConclusion.STRONG)

    def test_wangshuai_weak_preserved(self):
        """弱案例: JIA-MAO (from WANG-005) → 仍为 MODERATE。"""
        c = _ctx(("GENG", "SHEN"), ("REN", "SHEN"), ("JIA", "MAO"), ("GUI", "CHOU"), "JIA")
        j = WANGSHUAIJudgment.judge([], c)
        # JIA-MAO: 失令(-2) + 失地(-2) + 党众+2 + 通根+1 = -1 → MODERATE
        self.assertEqual(j.conclusion, JudgmentConclusion.MODERATE)
        self.assertEqual(j.score, -1.0)


if __name__ == "__main__":
    unittest.main()
