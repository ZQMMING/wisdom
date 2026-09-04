# -*- coding: utf-8 -*-
"""Z13: 飞星派规则图谱（FeixingRuleGraph）测试。

覆盖：
- Z13-A: PalaceStemContract（宫干事实提取 + 自化检测）
- Z13-B: FlyingTransformFact（飞化计算）
- Z13-C: FeixingRuleGraph（飞化规则匹配 + 隔离验证）
- 生产路径集成（真实 FrozenZiweiChart → FeixingRuleGraph）
"""
from __future__ import annotations
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tongshu.engines.ziwei_engine import ZiweiEngine, GAN_SIHUA
from tongshu.engines.ziwei_method_profile import MethodId
from tongshu.engines.ziwei.rules.feixing_rule_graph import (
    PalaceStemContract,
    FeixingRuleGraph,
    FlyingTransformFact,
    create_feixing_rule_graph,
)


class TestPalaceStemContract(unittest.TestCase):
    """Z13-A: 宫干事实契约测试。"""

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()
        cls.chart = cls.engine.full_chart((2000, 1, 1), 12, 'male')

    def test_extract_returns_12_facts(self):
        """提取全部 12 宫的宫干事实。"""
        facts = PalaceStemContract.extract(self.chart)
        self.assertEqual(len(facts), 12)

    def test_all_facts_have_names(self):
        """每个 PalaceStemFact 有 palace_name 和 stem。"""
        facts = PalaceStemContract.extract(self.chart)
        for f in facts:
            self.assertTrue(f.palace_name, f"宫位名不应为空")
            # stem 可以为空（无宫干的情况）

    def test_get_palace_stem(self):
        """get_palace_stem 返回正确宫干。"""
        stem = PalaceStemContract.get_palace_stem(self.chart, '命宫')
        self.assertIsInstance(stem, str)
        # 2000-01-01 男命命宫干为甲
        self.assertEqual(stem, '甲')

    def test_get_palace_stem_missing(self):
        """不存在的宫位返回空字符串。"""
        stem = PalaceStemContract.get_palace_stem(self.chart, ' nonexistent')
        self.assertEqual(stem, '')

    def test_self_mutagen_detection(self):
        """自化检测：财帛(庚)太阴自化禄。"""
        facts = PalaceStemContract.extract(self.chart)
        caibo = next(f for f in facts if f.palace_name == '财帛')
        self.assertTrue(PalaceStemContract.has_self_mutagen(caibo),
                        "财帛(庚)太阴应自化禄")

    def test_no_self_mutagen_when_empty(self):
        """空宫干不应触发自化。"""
        facts = PalaceStemContract.extract(self.chart)
        # 找一个可能无宫干的宫（理论上所有宫都有宫干，但测试防御性）
        for f in facts:
            if not f.stem:
                self.assertFalse(PalaceStemContract.has_self_mutagen(f))


class TestFlyingTransform(unittest.TestCase):
    """Z13-B: 飞化计算测试。"""

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()
        cls.chart = cls.engine.full_chart((2000, 1, 1), 12, 'male')

    def test_total_transforms(self):
        """飞化总数 = 有宫干的宫数 × 4（四化）。"""
        graph = create_feixing_rule_graph()
        transforms = graph.compute_all_flying_transforms(self.chart)
        # 2000-01-01 男命所有 12 宫均有宫干
        self.assertEqual(len(transforms), 48)

    def test_transform_structure(self):
        """每条 FlyingTransformFact 结构完整。"""
        graph = create_feixing_rule_graph()
        transforms = graph.compute_all_flying_transforms(self.chart)
        for t in transforms:
            self.assertTrue(t.source_palace)
            self.assertTrue(t.source_stem)
            self.assertTrue(t.transformation)
            self.assertIn(t.transformation, ('化禄', '化权', '化科', '化忌'))
            self.assertTrue(t.target_star)
            self.assertTrue(t.target_palace or t.direction == 'self')
            self.assertIn(t.direction, ('in', 'out', 'self'))

    def test_self_mutagen_transform(self):
        """自化飞化：direction=self。"""
        graph = create_feixing_rule_graph()
        transforms = graph.compute_all_flying_transforms(self.chart)
        self_transforms = [t for t in transforms if t.direction == 'self']
        # 财帛(庚)太阴自化禄，官禄(戊)天机自化忌
        self.assertGreaterEqual(len(self_transforms), 2,
                                "至少有2个自化")
        self_names = {t.source_palace for t in self_transforms}
        self.assertIn('财帛', self_names)
        self.assertIn('官禄', self_names)

    def test_natal_stem_not_used(self):
        """飞化计算不使用生年干（birth_year stem），只用宫干。"""
        # 2000年是庚年，命宫干是甲 —— 如果用了生年干会出错
        graph = create_feixing_rule_graph()
        transforms = graph.compute_all_flying_transforms(self.chart)
        # 命宫干=甲，甲廉破武阳
        ming_transforms = [t for t in transforms if t.source_palace == '命宫']
        self.assertEqual(len(ming_transforms), 4)
        stems_used = {t.source_stem for t in ming_transforms}
        self.assertEqual(stems_used, {'甲'},
            f"命宫飞化应使用甲干，实际: {stems_used}")


class TestFeixingRuleGraph(unittest.TestCase):
    """Z13-C: 飞化规则图谱测试。"""

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()
        cls.chart = cls.engine.full_chart((2000, 1, 1), 12, 'male')

    def test_rule_graph_creation(self):
        """FeixingRuleGraph 可正确创建。"""
        graph = create_feixing_rule_graph()
        self.assertEqual(graph.method_id, MethodId.FEIXING)

    def test_match_flying_rules_structure(self):
        """match_flying_rules 返回结构化结果。"""
        graph = create_feixing_rule_graph()
        transforms = graph.compute_all_flying_transforms(self.chart)
        results = graph.match_flying_rules(self.chart, transforms)
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertIn('rule_id', r)
            self.assertIn('method_id', r)
            self.assertIn('facts', r)
            self.assertIn('verification_status', r)

    def test_method_id_isolation(self):
        """所有匹配结果的 method_id = FEIXING。"""
        graph = create_feixing_rule_graph()
        transforms = graph.compute_all_flying_transforms(self.chart)
        results = graph.match_flying_rules(self.chart, transforms)
        for r in results:
            self.assertEqual(r['method_id'], 'feixing',
                f"method_id 应为 feixing，实际: {r['method_id']}")

    def test_no_cross_method_rules(self):
        """飞星规则不包含三合/中州/钦天的 rule_id 前缀。"""
        graph = create_feixing_rule_graph()
        transforms = graph.compute_all_flying_transforms(self.chart)
        results = graph.match_flying_rules(self.chart, transforms)
        rule_ids = {r['rule_id'] for r in results}
        for rid in rule_ids:
            self.assertTrue(rid.startswith('FEIXING-'),
                f"rule_id 应以 FEIXING- 开头: {rid}")

    def test_laiyin_rule_generated(self):
        """来因宫规则：化忌落宫被识别。"""
        graph = create_feixing_rule_graph()
        transforms = graph.compute_all_flying_transforms(self.chart)
        results = graph.match_flying_rules(self.chart, transforms)
        laiyn_results = [r for r in results if r['rule_id'] == 'FEIXING-LAIYIN']
        self.assertGreater(len(laiyn_results), 0, "应至少有一条来因宫规则")

    def test_self_mutagen_rule_generated(self):
        """自化规则：自化飞化被识别。"""
        graph = create_feixing_rule_graph()
        transforms = graph.compute_all_flying_transforms(self.chart)
        results = graph.match_flying_rules(self.chart, transforms)
        self_results = [r for r in results
                        if r['rule_id'] == 'FEIXING-SELF-MUTAGEN']
        self.assertGreater(len(self_results), 0, "应至少有一条自化规则")


class TestProductionIntegration(unittest.TestCase):
    """Z13-D: 生产路径集成测试。"""

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()

    def test_end_to_end_real_chart(self):
        """真实 FrozenZiweiChart → PalaceStemContract → FeixingRuleGraph。"""
        chart = self.engine.full_chart((2000, 1, 1), 12, 'male')

        # A: 宫干事实
        stem_facts = PalaceStemContract.extract(chart)
        self.assertEqual(len(stem_facts), 12)

        # B: 飞化计算
        graph = create_feixing_rule_graph()
        transforms = graph.compute_all_flying_transforms(chart)
        self.assertEqual(len(transforms), 48)

        # C: 规则匹配
        results = graph.match_flying_rules(chart, transforms)
        self.assertGreater(len(results), 0)

        # D: 验证无诊断语义（facts 只有结构性事实，不含 INCREASE/DECLINE/STABLE）
        for r in results:
            self.assertEqual(r['method_id'], 'feixing')
            # direction/polarity/strength/confidence 是 Signal 层诊断字段，
            # 不得出现在证据事实中。飞化 facts 中的 direction 是"入/出/自化"
            # 的结构描述（FlyingTransformFact.direction），与此无关。
            self.assertNotIn('polarity', r['facts'])
            self.assertNotIn('strength', r['facts'])
            self.assertNotIn('confidence', r['facts'])
            # 不含 Signal 层方向值
            for v in r['facts'].values():
                if isinstance(v, str):
                    self.assertNotIn(v, ('INCREASE', 'DECLINE', 'STABLE',
                                         'POSITIVE', 'NEGATIVE', 'NEUTRAL'))

    def test_different_charts_produce_different_transforms(self):
        """不同命盘产生不同飞化结果。"""
        charts = [
            self.engine.full_chart((2000, 1, 1), 12, 'male'),
            self.engine.full_chart((1990, 5, 15), 10, 'female'),
            self.engine.full_chart((1984, 10, 15), 8, 'female'),
        ]
        graph = create_feixing_rule_graph()
        transform_sets = []
        for c in charts:
            ts = graph.compute_all_flying_transforms(c)
            # 用 (source_palace, stem, target_star) 作为标识
            key = tuple((t.source_palace, t.source_stem, t.target_star)
                        for t in ts)
            transform_sets.append(key)

        # 三个不同命盘的飞化结果应不同
        self.assertNotEqual(transform_sets[0], transform_sets[1])
        self.assertNotEqual(transform_sets[1], transform_sets[2])


if __name__ == "__main__":
    unittest.main()
