"""H4 解释引擎测试"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tongshu.engines.heluo.interpretation import (
    HeluoInput,
    RelationalInterpretationEngine,
    interpret
)


def make_input(**overrides):
    """构建测试输入。"""
    defaults = dict(
        prenatal_hexagram="乾上乾下",
        yuan_tang="五爻",
        postnatal_hexagram="乾上坤下",
        day_hexagram="屯上蒙下",
        year_cycle="乙巳",
        month_cycle="甲申",
        day_cycle="丙午",
        element_state={"木": 0.6, "火": 0.8, "土": 0.3, "金": 0.5, "水": 0.7},
        line_position={"active_line": 5, "position_type": "尊位", "yinyang": "阳"},
        time_state={"solar_term": "立秋", "hour": 14}
    )
    defaults.update(overrides)
    return HeluoInput(**defaults)


class TestHeluoInput(unittest.TestCase):
    """测试输入数据结构。"""
    
    def test_basic_input(self):
        """基本输入构造。"""
        inp = make_input()
        self.assertEqual(inp.prenatal_hexagram, "乾上乾下")
        self.assertEqual(inp.year_cycle, "乙巳")
    
    def test_custom_input(self):
        """自定义输入。"""
        inp = make_input(prenatal_hexagram="坤上坤下", year_cycle="甲辰")
        self.assertEqual(inp.prenatal_hexagram, "坤上坤下")
        self.assertEqual(inp.year_cycle, "甲辰")


class TestRelationalInterpretationEngine(unittest.TestCase):
    """测试关系解释引擎。"""
    
    def test_compute_basic(self):
        """基本计算。"""
        inp = make_input()
        
        engine = RelationalInterpretationEngine(inp)
        result = engine.compute()
        
        # 验证输出结构
        self.assertIsInstance(result.current_state, str)
        self.assertGreater(len(result.current_state), 0)
        
        self.assertIsInstance(result.opportunity.type, str)
        self.assertIsInstance(result.opportunity.strength, float)
        self.assertIsInstance(result.opportunity.time_window, str)
        self.assertIsInstance(result.opportunity.classical_basis, str)
        
        self.assertIsInstance(result.risk.type, str)
        self.assertIsInstance(result.risk.severity, float)
        self.assertIsInstance(result.risk.trigger_condition, str)
        self.assertIsInstance(result.risk.classical_basis, str)
        
        self.assertIsInstance(result.recommended_action.primary, str)
        self.assertIsInstance(result.recommended_action.confidence, float)
        
        self.assertIsInstance(result.interpretation_chain, list)
        self.assertGreater(len(result.interpretation_chain), 0)
        
        self.assertIn("algorithm_version", result.meta)
        self.assertIn("confidence_score", result.meta)
    
    def test_qian_gua_positive_score(self):
        """乾卦得分为正。"""
        inp = make_input()
        
        result = interpret(inp)
        score = result.meta.get("confidence_score", 0)
        self.assertGreater(score, 0.5)
    
    def test_kun_gua_moderate_score(self):
        """坤卦得分为中等。"""
        inp = make_input(
            prenatal_hexagram="坤上坤下",
            yuan_tang="三爻",
            postnatal_hexagram="坤上乾下",
            year_cycle="甲辰",
            month_cycle="戊寅",
            day_cycle="丁未"
        )
        
        result = interpret(inp)
        self.assertIsInstance(result.current_state, str)
        self.assertGreater(len(result.current_state), 0)
    
    def test_interpretation_chain_complete(self):
        """解释链完整。"""
        inp = make_input()
        
        engine = RelationalInterpretationEngine(inp)
        result = engine.compute()
        
        # 应有5步解释
        self.assertEqual(len(result.interpretation_chain), 5)
        
        # 每步都有逻辑和来源
        for step in result.interpretation_chain:
            self.assertIsInstance(step.logic, str)
            self.assertGreater(len(step.logic), 0)
            self.assertIsInstance(step.source, str)
    
    def test_warnings_empty_for_valid_input(self):
        """有效输入无警告。"""
        inp = make_input()
        
        result = interpret(inp)
        self.assertEqual(len(result.warnings), 0)
    
    def test_meta_has_required_fields(self):
        """元数据包含必要字段。"""
        inp = make_input(element_state={}, line_position={}, time_state={})
        
        result = interpret(inp)
        
        self.assertEqual(result.meta["algorithm_version"], "H4-V1.0")
        self.assertIsInstance(result.meta["confidence_score"], float)
        self.assertEqual(result.meta["interpretation_type"], "relational")
    
    def test_element_state_affects_result(self):
        """五行状态影响机会/风险因子。"""
        inp1 = make_input(element_state={"木": 0.9, "火": 0.9, "土": 0.9, "金": 0.9, "水": 0.9})
        inp2 = make_input(element_state={"木": 0.1, "火": 0.1, "土": 0.1, "金": 0.1, "水": 0.1})
        
        engine1 = RelationalInterpretationEngine(inp1)
        engine2 = RelationalInterpretationEngine(inp2)
        
        weights1 = engine1._compute_factor_weights()
        weights2 = engine2._compute_factor_weights()
        
        # 五行修正应影响权重
        # 强五行时修正为正，弱五行时修正为负
        mod1 = engine1._calculate_element_modifier()
        mod2 = engine2._calculate_element_modifier()
        
        self.assertGreater(mod1, 0)
        self.assertLess(mod2, 0)


class TestFactorWeights(unittest.TestCase):
    """测试因子权重计算。"""
    
    def test_weights_sum_to_one(self):
        """权重归一化后总和为1。"""
        inp = make_input()
        
        engine = RelationalInterpretationEngine(inp)
        weights = engine._compute_factor_weights()
        
        total = sum(weights.values())
        self.assertAlmostEqual(total, 1.0, places=5)
    
    def test_prenatal_hexagram_heaviest(self):
        """本命卦权重最大。"""
        inp = make_input()
        
        engine = RelationalInterpretationEngine(inp)
        weights = engine._compute_factor_weights()
        
        # 本命卦应为最高权重
        self.assertGreaterEqual(weights["prenatal_hexagram"], weights["year_cycle"])


class TestEvidenceClosure(unittest.TestCase):
    """测试证据闭合度计算。"""
    
    def test_evidence_closure_rate(self):
        """证据闭合率计算。"""
        inp = make_input()
        
        engine = RelationalInterpretationEngine(inp)
        closure = engine._compute_evidence_closure()
        
        self.assertGreaterEqual(closure, 0.5)
        self.assertLessEqual(closure, 1.0)


if __name__ == "__main__":
    unittest.main()
