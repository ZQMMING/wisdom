"""P0-01 + P0-04 修复测试：统一解释引擎。

验证：
- yi/interpreter.py 的 YiInterpretationEngine（统一解释引擎）为 AUTHORITY 实现。
- YiInterpreter 完整路径产出有意义解读（含 risk/action/remediation）。
- 不同卦例产生不同解读。
- 禁止术语不出现在输出。
- confidence 不再是硬编码 0.7，而是随结构完整性的动态变量。

架构约束（Schema 9）：
- 不生成 fortune_score / luck_score。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path("E:/shuntian/src")))

import unittest

# Data functions (pure, no LLM)
from tongshu.engines.yi.classical_text import get_classical_text
from tongshu.engines.yi.hexagram_symbol import get_hexagram_symbol
from tongshu.engines.yi.image_expansion import expand_image
from tongshu.engines.yi.line_symbol import analyze_line_symbol
from tongshu.yi.interpreter import FORBIDDEN_TERMS, YiInterpretationEngine
from tongshu.yi.schema import DirectionLabel, YiStructure, YiStructureStatus

# P0-01 报告中的硬编码占位短语（修复后绝对不允许再出现）
_PLACEHOLDER_PHRASES = (
    "咨询专业寿星卷",
    "需结合具体人生领域分析",
    "请参照时辰与经典注解",
    "万能套话",
)


class TestYiInterpretationEngineDelegates(unittest.TestCase):
    """验证 AUTHORITY 实现 YiInterpretationEngine 的核心行为。"""

    def _build_yi_structure(self, hexagram_name, lines, yuantang_index):
        """从卦名/爻线构造 YiStructure（绕过 InterpretationInput）。"""
        symbol = get_hexagram_symbol(hexagram_name)
        line_symbol = analyze_line_symbol(lines, yuantang_index)
        classical = get_classical_text(hexagram_name)
        image = expand_image(symbol, line_symbol, classical)

        has_hexagram = bool(symbol and symbol.name)
        has_classical = bool(classical and (classical.gua_ci or classical.da_xiang_ci))

        if not has_hexagram:
            status = YiStructureStatus.NOT_APPLICABLE
        elif has_classical:
            status = YiStructureStatus.VALID
        else:
            status = YiStructureStatus.INCOMPLETE

        # auxiliary 关系（错卦/综卦/互卦）
        auxiliary = []
        if symbol:
            if symbol.cuo_gua:
                auxiliary.append(f"错卦:{symbol.cuo_gua}")
            if symbol.zong_gua:
                auxiliary.append(f"综卦:{symbol.zong_gua}")
            if symbol.hu_gua:
                auxiliary.append(f"互卦:{symbol.hu_gua}")

        classical_quote = classical.gua_ci if classical else ""
        classical_source = classical.gua_ci_source if classical else ""

        # image reasoning
        image_reasoning = []
        if image:
            for item in image.level_1_classical[:3]:
                image_reasoning.append(f"classical:{item.image}")
            for item in image.level_2_contextual[:2]:
                image_reasoning.append(f"context:{item.image}")

        ti_yong = symbol.ti_yong_relation if symbol else ""
        ti_trigram = symbol.lower_trigram if symbol else ""
        yong_trigram = symbol.upper_trigram if symbol else ""

        return YiStructure(
            truth_hexagram=symbol.name if symbol else "",
            true_line=line_symbol.yuantang_index + 1 if line_symbol else 0,
            position_name=line_symbol.yuantang if line_symbol else "",
            temporal_context="",
            ti_trigram=ti_trigram,
            yong_trigram=yong_trigram,
            ti_yong_relation=ti_yong,
            auxiliary_relations=auxiliary,
            classical_quote=classical_quote,
            classical_source=classical_source,
            image_reasoning=image_reasoning,
            layer=YiStructureStatus.VALID,  # dummy, engine checks structure
            status=status,
        )

    def _interpret(self, hexagram_name, lines, yuantang_index):
        engine = YiInterpretationEngine()
        structure = self._build_yi_structure(hexagram_name, lines, yuantang_index)
        return engine.interpret(structure)

    def test_not_placeholder_output(self):
        """state/opportunity/attention 不得包含占位短语。"""
        interp = self._interpret("乾为天", [1, 1, 1, -1, -1, -1], 3)
        for phrase in _PLACEHOLDER_PHRASES:
            self.assertNotIn(phrase, interp.state, f"state 包含占位短语: {phrase}")
            self.assertNotIn(phrase, interp.opportunity, f"opportunity 包含占位短语: {phrase}")
        self.assertTrue(interp.state.strip())
        self.assertTrue(interp.opportunity.strip())

    def test_output_references_hexagram_and_tiyong(self):
        """统一引擎的状态描述应包含卦名与体用关系。"""
        interp = self._interpret("乾为天", [1, 1, 1, -1, -1, -1], 3)
        self.assertIn("乾为天", interp.state)
        self.assertIn("体", interp.state)

    def test_confidence_is_float_not_hardcoded(self):
        """confidence 是 float 且在 [0, 1] 区间。"""
        interp = self._interpret("乾为天", [1, 1, 1, -1, -1, -1], 3)
        self.assertIsInstance(interp.confidence, float)
        self.assertTrue(0.0 <= interp.confidence <= 1.0)

    def test_remediation_field_present(self):
        """remediation 字段必须存在且非空（通过 AUTHORITY 引擎）。"""
        interp = self._interpret("乾为天", [1, 1, 1, -1, -1, -1], 3)
        self.assertIsInstance(interp.remediation, str)
        # remediation 是 YiInterpretationEngine 独有字段，wrapper 曾丢失
        self.assertTrue(
            len(interp.remediation.strip()) > 0,
            "remediation should not be empty — was lost in the ARCHIVED wrapper"
        )


class TestYiInterpretationEngineUnified(unittest.TestCase):
    """通过 YiInterpreter 公共入口验证统一引擎行为。"""

    def _build_yi_structure(self, hexagram_name, lines, yuantang_index):
        """从卦名/爻线构造 YiStructure。"""
        symbol = get_hexagram_symbol(hexagram_name)
        line_symbol = analyze_line_symbol(lines, yuantang_index)
        classical = get_classical_text(hexagram_name)
        image = expand_image(symbol, line_symbol, classical)

        has_hexagram = bool(symbol and symbol.name)
        has_classical = bool(classical and (classical.gua_ci or classical.da_xiang_ci))

        if not has_hexagram:
            status = YiStructureStatus.NOT_APPLICABLE
        elif has_classical:
            status = YiStructureStatus.VALID
        else:
            status = YiStructureStatus.INCOMPLETE

        auxiliary = []
        if symbol:
            if symbol.cuo_gua:
                auxiliary.append(f"错卦:{symbol.cuo_gua}")
            if symbol.zong_gua:
                auxiliary.append(f"综卦:{symbol.zong_gua}")
            if symbol.hu_gua:
                auxiliary.append(f"互卦:{symbol.hu_gua}")

        classical_quote = classical.gua_ci if classical else ""
        classical_source = classical.gua_ci_source if classical else ""

        image_reasoning = []
        if image:
            for item in image.level_1_classical[:3]:
                image_reasoning.append(f"classical:{item.image}")
            for item in image.level_2_contextual[:2]:
                image_reasoning.append(f"context:{item.image}")

        ti_yong = symbol.ti_yong_relation if symbol else ""
        ti_trigram = symbol.lower_trigram if symbol else ""
        yong_trigram = symbol.upper_trigram if symbol else ""

        return YiStructure(
            truth_hexagram=symbol.name if symbol else "",
            true_line=line_symbol.yuantang_index + 1 if line_symbol else 0,
            position_name=line_symbol.yuantang if line_symbol else "",
            temporal_context="",
            ti_trigram=ti_trigram,
            yong_trigram=yong_trigram,
            ti_yong_relation=ti_yong,
            auxiliary_relations=auxiliary,
            classical_quote=classical_quote,
            classical_source=classical_source,
            image_reasoning=image_reasoning,
            layer=YiStructureStatus.VALID,
            status=status,
        )

    def _interpret(self, hexagram_name, lines, yuantang_index):
        engine = YiInterpretationEngine()
        structure = self._build_yi_structure(hexagram_name, lines, yuantang_index)
        return engine.interpret(structure)

    def test_different_hexagrams_different_output(self):
        a = self._interpret("乾为天", [1, 1, 1, -1, -1, -1], 3)
        b = self._interpret("坤为地", [-1, -1, -1, 1, 1, 1], 0)
        self.assertNotEqual(a.state, b.state)

    def test_no_forbidden_terms_in_output(self):
        """输出不得包含 FORBIDDEN_TERMS（对应 B-11 TRUE GREEN）。"""
        interp = self._interpret("乾为天", [1, 1, 1, -1, -1, -1], 3)
        text = " ".join([
            interp.state,
            interp.opportunity,
            interp.risk,
            interp.action,
            interp.remediation,
        ])
        for term in FORBIDDEN_TERMS:
            self.assertNotIn(term, text, f"输出包含违禁词: {term}")

    def test_direction_label_from_tiyong_relation(self):
        """体用关系 → 方向标签映射（Schema 9 固定输出，非分数）。"""
        engine = YiInterpretationEngine()
        cases = [
            ("用生体（助）", DirectionLabel.POSITIVE),
            ("用克体（凶）", DirectionLabel.NEGATIVE),
            ("体生用（泄）", DirectionLabel.CHANGE),
            ("体克用（耗）", DirectionLabel.CHANGE),
            ("比和（平）", DirectionLabel.NEUTRAL),
        ]
        for relation, expected in cases:
            structure = YiStructure(
                truth_hexagram="乾为天",
                ti_yong_relation=relation,
                status=YiStructureStatus.VALID,
            )
            interp = engine.interpret(structure)
            self.assertEqual(interp.directional_label, expected, relation)


class TestConfidenceVaries(unittest.TestCase):
    """confidence 随结构完整性变化，而非固定值。"""

    def test_confidence_depends_on_structure(self):
        engine = YiInterpretationEngine()
        full = YiStructure(
            truth_hexagram="乾为天",
            true_line=4,
            position_name="九四",
            classical_quote="小往大来，亨矣。",
            status=YiStructureStatus.VALID,
        )
        incomplete = YiStructure(
            truth_hexagram="乾为天",
            status=YiStructureStatus.INCOMPLETE,
        )
        self.assertNotEqual(
            engine.interpret(full).confidence,
            engine.interpret(incomplete).confidence,
        )


if __name__ == "__main__":
    unittest.main()
