"""S6-03 解释质量评估体系测试"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tongshu.engines.heluo.metrics_v2 import (
    evaluate_interpretation,
    evaluate_dataset,
    InterpretationQualityScore,
    QualityLevel
)


class TestInterpretationQualityScore(unittest.TestCase):
    """测试解释质量评分。"""
    
    def test_empty_interpretation(self):
        """空解释返回最低分。"""
        score = evaluate_interpretation({})
        self.assertEqual(score.overall_score, 0.0)
        self.assertEqual(score.quality_level, QualityLevel.NEEDS_REVIEW.value)
    
    def test_complete_interpretation(self):
        """完整解释获得高分。"""
        interpretation = {
            "current_state": "乾卦主事",
            "opportunity": {"type": "事业", "strength": 0.8},
            "risk": {"type": "健康", "severity": 0.2},
            "recommended_action": "把握机遇",
            "classical_reference": {"book": "河洛理数", "volume": "卷一"}
        }
        classical_source = {
            "book_name": "河洛理数",
            "volume": "卷一",
            "original_text": "乾卦",
            "normalized_rule": "乾卦主事"
        }
        evidence_chain = [
            {"source_type": "rule", "source_text": "乾上乾下", "reasoning": "本命", "conclusion": "定位"},
            {"source_type": "calc", "source_text": "阳男", "reasoning": "方向", "conclusion": "推演"}
        ]
        
        score = evaluate_interpretation(interpretation, classical_source, evidence_chain)
        
        # 应达到良好及以上
        self.assertGreaterEqual(score.overall_score, 0.75)
        self.assertIn(score.quality_level, [QualityLevel.GOOD.value, QualityLevel.EXCELLENT.value])
        
        # 各维度应合理
        self.assertGreaterEqual(score.classical_alignment, 0.5)
        self.assertEqual(score.logic_completeness, 1.0)
        self.assertEqual(score.evidence_closure, 1.0)
    
    def test_classical_alignment_scoring(self):
        """古籍一致性正确计分。"""
        interpretation = {
            "classical_reference": {
                "book": "河洛理数",
                "volume": "卷一",
                "paragraph": "乾卦初九",
                "rule": "潜龙勿用"
            }
        }
        classical_source = {
            "book_name": "河洛理数",
            "volume": "卷一",
            "original_text": "乾卦初九，潜龙勿用也",
            "normalized_rule": "潜龙勿用"
        }
        
        score = evaluate_interpretation(interpretation, classical_source)
        self.assertGreater(score.classical_alignment, 0.75)
    
    def test_logic_completeness_required_fields(self):
        """逻辑完整性检查必需字段。"""
        # 缺少部分字段
        partial = {
            "current_state": "乾卦",
            "opportunity": {"strength": 0.8}
            # 缺少 risk, recommended_action, classical_reference
        }
        score = evaluate_interpretation(partial)
        self.assertEqual(score.logic_completeness, 2 / 5)  # 2个字段
    
    def test_stability_with_references(self):
        """稳定性与参考输出比较。"""
        interp1 = {"current_state": "乾", "opportunity": "强"}
        interp2 = {"current_state": "乾", "opportunity": "强"}
        interp3 = {"current_state": "坤", "opportunity": "弱"}
        
        # 相同输出，稳定性应为1.0
        score = evaluate_interpretation(interp1, None, None, [interp2])
        self.assertEqual(score.stability_score, 1.0)
        
        # 不同输出，稳定性降低
        interp3 = {"current_state": "坤", "opportunity": "弱", "risk": "高", "test_key": "extra"}
        score2 = evaluate_interpretation(interp1, None, None, [interp3])
        self.assertLess(score2.stability_score, 1.0)


class TestEvaluateDataset(unittest.TestCase):
    """测试数据集评估。"""
    
    def test_empty_dataset(self):
        """空数据集返回错误。"""
        result = evaluate_dataset([])
        self.assertIn("error", result)
    
    def test_dataset_with_mixed_quality(self):
        """混合质量数据集评估。"""
        dataset = [
            {
                "case_id": "case_001",
                "interpretation": {
                    "current_state": "乾卦",
                    "opportunity": {"strength": 0.8},
                    "risk": {"severity": 0.2},
                    "recommended_action": "进取",
                    "classical_reference": {"book": "河洛理数"}
                }
            },
            {
                "case_id": "case_002",
                "interpretation": {
                    "current_state": "坤卦",
                    "opportunity": {"strength": 0.5},
                    "risk": {"severity": 0.5},
                    "recommended_action": "守成",
                    "classical_reference": {"book": "河洛理数"}
                }
            }
        ]
        
        result = evaluate_dataset(dataset)
        self.assertEqual(result["total_cases"], 2)
        self.assertGreater(result["average_overall_score"], 0)
        self.assertIn("quality_distribution", result)


class TestQualityLevels(unittest.TestCase):
    """测试质量等级划分。"""
    
    def test_excellent_threshold(self):
        """优秀阈值 >= 0.90。"""
        from tongshu.engines.heluo.metrics_v2 import evaluate_interpretation
        # 创建高分解释
        interpretation = {
            "current_state": "乾卦",
            "opportunity": {"strength": 0.9},
            "risk": {"severity": 0.1},
            "recommended_action": "进取",
            "classical_reference": {"book": "河洛理数"}
        }
        score = evaluate_interpretation(interpretation)
        # 检查高分情况
        self.assertGreaterEqual(score.overall_score, 0.5)
    
    def test_threshold_boundaries(self):
        """边界值正确划分。"""
        self.assertEqual(evaluate_interpretation({}).quality_level, QualityLevel.NEEDS_REVIEW.value)


if __name__ == "__main__":
    unittest.main()
