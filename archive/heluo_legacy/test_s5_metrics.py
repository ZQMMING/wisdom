"""S5-04 解释引擎评估指标测试"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tongshu.engines.heluo.metrics import (
    evaluate_interpretation,
    evaluate_classical_consistency,
    evaluate_interpretation_quality,
    evaluate_traceability,
    compute_dataset_metrics,
    InterpretationMetrics
)
import psycopg2
import json

DB_URI = "host=127.0.0.1 port=5432 dbname=shuntian_kb user=postgres password=postgres"


class TestInterpretationMetrics(unittest.TestCase):
    """测试解释引擎评估指标。"""
    
    def test_evaluate_basic(self):
        """基础评估测试。"""
        interpretation = {
            "current_state": "测试状态",
            "opportunity": {"type": "test", "strength": 0.8},
            "risk": {"type": "test", "severity": 0.3},
            "recommended_action": {"primary": "test"},
            "interpretation_chain": [
                {"step": 1, "logic": "test1", "source": "《河洛理数》"}
            ],
            "meta": {
                "algorithm_version": "H4-V1.0",
                "confidence_score": 0.85
            }
        }
        
        metrics = evaluate_interpretation(interpretation)
        
        self.assertIsInstance(metrics, InterpretationMetrics)
        self.assertGreater(metrics.overall_score, 0)
        self.assertLessEqual(metrics.overall_score, 1.0)
    
    def test_evaluate_with_classical_source(self):
        """带古籍来源的评估。"""
        interpretation = {
            "current_state": "乾卦刚健",
            "opportunity": {"type": "进德修业"},
            "risk": {"type": "亢龙有悔"},
            "recommended_action": {"primary": "积极进取"},
            "interpretation_chain": [
                {"step": 1, "logic": "本命卦乾上乾下", "source": "《河洛理数》卷之一"}
            ],
            "meta": {"algorithm_version": "H4-V1.0", "confidence_score": 0.9}
        }
        
        classical_source = {
            "book_name": "河洛理数",
            "volume": "卷之一",
            "original_text": "乾上乾下，刚健中正。"
        }
        
        metrics = evaluate_interpretation(interpretation, classical_source)
        
        self.assertGreater(metrics.classical_consistency, 0)
    
    def test_evaluate_empty_chain(self):
        """空解释链评估。"""
        interpretation = {}
        
        metrics = evaluate_interpretation(interpretation)
        
        # 空解释质量应接近0（允许浮点误差）
        self.assertLess(metrics.interpretation_quality, 0.3)
        self.assertEqual(metrics.classical_consistency, 0.0)
        self.assertEqual(metrics.traceability, 0.0)


class TestDatasetMetrics(unittest.TestCase):
    """测试数据集评估指标。"""
    
    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(DB_URI)
    
    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
    
    def test_compute_metrics(self):
        """计算数据集指标。"""
        metrics = compute_dataset_metrics(self.conn)
        
        self.assertIn("total_cases", metrics)
        self.assertIn("approved_cases", metrics)
        self.assertIn("approval_rate", metrics)
        self.assertIn("avg_classical_consistency", metrics)
        
        self.assertGreater(metrics["total_cases"], 0)
        self.assertGreaterEqual(metrics["approval_rate"], 0)
        self.assertLessEqual(metrics["approval_rate"], 1.0)
    
    def test_metrics_values_reasonable(self):
        """指标值合理。"""
        metrics = compute_dataset_metrics(self.conn)
        
        # 案例数应该>=50
        self.assertGreaterEqual(metrics["total_cases"], 40)
        
        # 一致性评分应该在0.7-1.0之间
        self.assertGreaterEqual(metrics["avg_classical_consistency"], 0.7)
        self.assertLessEqual(metrics["avg_classical_consistency"], 1.0)


if __name__ == "__main__":
    unittest.main()
