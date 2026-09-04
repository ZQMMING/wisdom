"""V-Validation Layer 测试

覆盖：
- Schema: Case/Event/Prediction 数据模型
- Backtest: 时间轴回测引擎
- Blind: 盲测协议
- Scoring: 多维度评分矩阵
- Ablation: 消融实验
- Baseline: 基线系统对比
"""
from __future__ import annotations
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tongshu.v_validation import (
    Case, Event, EvidenceGrade, EventSeverity, EventCategory,
    Prediction, Signal, ScoreCard,
    BacktestEngine, BlindProtocol, ScoringMatrix,
    AblationRunner, BaselineSystem, ValidationReport,
)


class TestSchema(unittest.TestCase):
    """Schema层测试。"""

    def test_case_creation(self):
        """Case创建与基本属性。"""
        case = Case(
            case_id="TEST-001",
            gender="male",
            birth_year=1990,
            birth_month=1,
            birth_day=1,
            birth_hour=12,
        )
        self.assertEqual(case.case_id, "TEST-001")
        self.assertEqual(case.birth_date_tuple, (1990, 1, 1, 12))
        self.assertIsNone(case.min_event_year)
        self.assertIsNone(case.max_event_year)

    def test_event_severity_mapping(self):
        """事件严重程度映射。"""
        self.assertEqual(EventSeverity.TRIVIAL, 1)
        self.assertEqual(EventSeverity.MAJOR, 4)
        self.assertEqual(EventSeverity.CRITICAL, 5)

    def test_evidence_grade_golden(self):
        """证据等级判断。"""
        self.assertTrue(EvidenceGrade.A.is_golden)
        self.assertTrue(EvidenceGrade.B.is_golden)
        self.assertFalse(EvidenceGrade.C.is_golden)

    def test_event_to_dict(self):
        """Event序列化。"""
        event = Event(
            date=date(2020, 8, 15),
            category=EventCategory.MARRIAGE,
            severity=EventSeverity.MAJOR,
            description="结婚",
            evidence_grade=EvidenceGrade.A,
        )
        d = event.to_dict()
        self.assertEqual(d["category"], "MARRIAGE")
        self.assertEqual(d["severity"], 4)
        self.assertEqual(d["evidence_grade"], "A")


class TestBacktestEngine(unittest.TestCase):
    """回测引擎测试。"""

    def test_backtest_empty(self):
        """空案例回测。"""
        case = Case(case_id="EMPTY", gender="male",
                    birth_year=1990, birth_month=1, birth_day=1, birth_hour=12)
        engine = BacktestEngine()
        results = engine.run(case, 2020, 2020)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].precision, 0.0)

    def test_backtest_stats(self):
        """回测统计聚合。"""
        case = Case(case_id="STATS", gender="male",
                    birth_year=1990, birth_month=1, birth_day=1, birth_hour=12)
        engine = BacktestEngine()
        engine.run(case, 2020, 2021)
        stats = engine.aggregate_stats()
        self.assertIn("mean_precision", stats)
        self.assertIn("cases_tested", stats)
        self.assertEqual(stats["cases_tested"], 1)


class TestBlindProtocol(unittest.TestCase):
    """盲测协议测试。"""

    def test_blind_run(self):
        """盲测运行。"""
        case = Case(case_id="BLIND", gender="male",
                    birth_year=1990, birth_month=1, birth_day=1, birth_hour=12,
                    events=[Event(date=date(2020, 6, 1), category=EventCategory.MARRIAGE,
                                  severity=EventSeverity.MAJOR, description="结婚")])
        blind = BlindProtocol([case])
        run = blind.run(case, 2020, 2020)
        self.assertEqual(run.case_id, "BLIND")
        self.assertEqual(run.start_year, 2020)
        self.assertIsNone(run.revealed_results)


class TestScoringMatrix(unittest.TestCase):
    """评分矩阵测试。"""

    def test_score_basic(self):
        """基础评分。"""
        pred = Prediction(case_id="TEST", target_year=2020, signals=[])
        event = Event(date=date(2020, 6, 1), category=EventCategory.MARRIAGE,
                      severity=EventSeverity.MAJOR, description="结婚")
        scores = ScoringMatrix.score(pred, event)
        self.assertIn("category", scores)
        self.assertIn("time", scores)
        self.assertEqual(len(scores), 6)

    def test_score_total(self):
        """总分计算。"""
        pred = Prediction(case_id="TEST", target_year=2020, signals=[])
        event = Event(date=date(2020, 6, 1), category=EventCategory.MARRIAGE,
                      severity=EventSeverity.MAJOR, description="结婚")
        total = ScoringMatrix.compute_total(pred, event)
        self.assertIsInstance(total, float)


class TestAblationRunner(unittest.TestCase):
    """消融实验测试。"""

    def test_ablation_run(self):
        """消融实验运行。"""
        case = Case(case_id="ABL", gender="male",
                    birth_year=1990, birth_month=1, birth_day=1, birth_hour=12)
        runner = AblationRunner(case)
        results = runner.run()
        self.assertIn("full", results)
        self.assertIn("no_yuantang", results)


class TestBaselineSystem(unittest.TestCase):
    """基线系统测试。"""

    def test_baseline_comparison(self):
        """基线对比。"""
        system = BaselineSystem()
        system.run_all([])  # 先运行
        result = system.get_comparison()
        self.assertIn("random", result)
        self.assertIn("combined", result)
        self.assertEqual(result["random"]["f1"], 0.21)


class TestValidationReport(unittest.TestCase):
    """验证报告测试。"""

    def test_report_generation(self):
        """报告生成。"""
        report = ValidationReport()
        report.add_section("summary", {"total_cases": 10, "pass_rate": 0.95})
        json_str = report.to_json()
        self.assertIn("summary", json_str)
        self.assertIn("total_cases", json_str)


if __name__ == "__main__":
    unittest.main()
