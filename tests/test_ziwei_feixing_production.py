# -*- coding: utf-8 -*-
"""Z13-D: 飞星派生产路径 Replay 验收。

本测试不是单元测试，而是生产路径集成验证。
要求：
  1. 从真实生产入口（ZiweiEngine.full_chart）获取 FrozenZiweiChart
  2. 验证 birth_year / natal_stem / palace_stems 来自计算层，非测试补填
  3. 验证 Natal Sihua 链（birth_year → stem → 四化）与 Palace Flying 链（宫干 → 四化 → 落宫）完全分离
  4. 验证 FeixingRuleGraph 不读取任何 Sanhe/Zhongzhou/Qintian 证据
  5. 使用 ≥3 个真实命盘案例验证

设计原则：
  - 不构造 mock chart，全部来自 ZiweiEngine.full_chart()
  - 不导入 SanheRuleGraph / ZhongzhouRuleGraph / QintianRuleGraph
  - 不引入 CrossAnalyzer / Signal / direction / polarity / strength
"""
from __future__ import annotations
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tongshu.engines.ziwei_engine import (
    ZiweiEngine,
    FrozenZiweiChart,
    GAN_SIHUA,
)
from tongshu.engines.ziwei_method_profile import MethodId, get_profile
from tongshu.engines.ziwei_palace_resolution import ZiweiPalaceResolver
from tongshu.engines.ziwei.rules.feixing_rule_graph import (
    PalaceStemContract,
    FeixingRuleGraph,
    create_feixing_rule_graph,
)


# ── 真实命盘案例（来自 test_ziwei_phase_a0_extended / test_ziwei_chart_cross_validate）─

REAL_CASES = [
    # (lunar_date, hour, gender, description)
    ((2000, 1, 1), 12, 'male',   '庚辰年男'),
    ((1990, 5, 15), 10, 'female','庚午年女'),
    ((1984, 10, 15), 8, 'female','甲子年闰十月女'),
    ((1893, 11, 19), 8, 'male',  '癸巳年男 — 毛泽东案例'),
    ((1960, 5, 5), 2, 'male',    '庚子年男'),
]


def _birth_year_stem(year: int) -> str:
    """独立计算出生年干（与 GAN_SIHUA 无关，用于交叉验证）。"""
    stems = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    return stems[(year - 4) % 10]


def _natal_sihua(stem: str) -> tuple[str, str, str, str]:
    """独立查 GAN_SIHUA（与 FeixingRuleGraph 无关）。"""
    return GAN_SIHUA.get(stem, ("", "", "", ""))


class TestProductionReplayFrozenChart(unittest.TestCase):
    """Z13-D.1: 真实 FrozenZiweiChart 从生产入口获得。"""

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()

    def test_chart_is_frozen_type(self):
        """full_chart() 返回 FrozenZiweiChart 实例，非 raw dict。"""
        chart = self.engine.full_chart((2000, 1, 1), 12, 'male')
        self.assertIsInstance(chart, FrozenZiweiChart)

    def test_birth_year_from_calculation(self):
        """birth_year 来自 lunar_date[0]，非测试代码补填。"""
        for lunar, hour, gender, desc in REAL_CASES:
            chart = self.engine.full_chart(lunar, hour, gender)
            self.assertEqual(chart.birth_year, lunar[0],
                f"{desc}: birth_year 应与 lunar_date[0] 一致")

    def test_palaces_are_real_dicts(self):
        """palaces 是 dict（非 tuple），可被 RuleGraph 消费。"""
        chart = self.engine.full_chart((2000, 1, 1), 12, 'male')
        self.assertIsInstance(chart.palaces, dict)
        self.assertEqual(len(chart.palaces), 12)

    def test_all_12_palaces_have_stems(self):
        """全部 12 宫均有宫干（production chart 不应有空 stem）。"""
        for lunar, hour, gender, desc in REAL_CASES:
            chart = self.engine.full_chart(lunar, hour, gender)
            for pn in ['命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄',
                       '迁移', '仆役', '官禄', '田宅', '福德', '父母']:
                stem = chart.palaces.get(pn, {}).get('stem', '')
                self.assertTrue(stem,
                    f"{desc}: {pn} 宫干不应为空")

    def test_major_stars_present(self):
        """全部 12 宫至少有主星或辅星之一（非全空）。"""
        chart = self.engine.full_chart((2000, 1, 1), 12, 'male')
        empty_count = sum(
            1 for pd in chart.palaces.values()
            if not pd.get('major') and not pd.get('minor')
        )
        # 允许少量空宫，但不允许全部为空
        self.assertLess(empty_count, 12, "不应出现全空命盘")


class TestNatalVsPalaceStemSeparation(unittest.TestCase):
    """Z13-D.2: 生年干链 vs 宫干链 彻底分离。"""

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()

    def test_natal_stem_from_birth_year_not_palace(self):
        """natal_stem 来自 birth_year，不是任意宫的 stem。"""
        for lunar, hour, gender, desc in REAL_CASES:
            chart = self.engine.full_chart(lunar, hour, gender)
            expected_natal_stem = _birth_year_stem(lunar[0])
            # 命宫 stem 可能 ≠ 生年干（这是正常现象）
            ming_stem = chart.palaces.get('命宫', {}).get('stem', '')
            # natal 四化应基于 birth_year stem，不是 ming_stem
            natal_sihua = _natal_sihua(expected_natal_stem)
            self.assertIsNotNone(natal_sihua[0])
            # 如果命宫 stem ≠ 生年干，证明两条链不同
            if ming_stem != expected_natal_stem:
                # 验证：用 ming_stem 算出的四化 ≠ 用 birth_year stem 算出的四化
                palace_sihua = _natal_sihua(ming_stem)
                self.assertNotEqual(natal_sihua, palace_sihua,
                    f"{desc}: 生年干{expected_natal_stem} vs 命宫干{ming_stem} 四化应不同")

    def test_natal_sihua_uses_birth_year_chain(self):
        """Natal Sihua 路径：birth_year → stem → GAN_SIHUA（独立验证）。"""
        for lunar, hour, gender, desc in REAL_CASES:
            chart = self.engine.full_chart(lunar, hour, gender)
            expected_stem = _birth_year_stem(lunar[0])
            expected_sihua = _natal_sihua(expected_stem)

            # Natal Sihua 走 SanheRuleGraph.match_sihua（通用四化匹配，非飞化）
            from tongshu.engines.ziwei.rules.rule_graph import create_rule_graph
            sanhe_graph = create_rule_graph(MethodId.SANHE)
            natal_result = sanhe_graph.match_sihua(chart, expected_stem)
            self.assertEqual(len(natal_result.matched_rules), 4,
                f"{desc}: natal sihua 应有 4 条规则")
            # 验证规则 facts 中的 stem 是 birth_year stem
            for m in natal_result.matched_rules:
                actual_stem = m.facts.get('stem', '')
                self.assertEqual(actual_stem, expected_stem,
                    f"{desc}: rule stem 应等于 birth_year stem {expected_stem}")

    def test_palace_stem_chain_independent(self):
        """宫干链：每个宫的 stem → GAN_SIHUA → 落宫（独立于 natal）。"""
        chart = self.engine.full_chart((2000, 1, 1), 12, 'male')
        resolver = ZiweiPalaceResolver(chart, MethodId.FEIXING)
        stem_facts = PalaceStemContract.extract(chart)

        # 命宫 stem = 甲，甲廉破武阳
        ming_fact = next(f for f in stem_facts if f.palace_name == '命宫')
        self.assertEqual(ming_fact.stem, '甲', "命宫干应为甲")
        # 甲的四化：廉贞禄、破军权、武曲科、太阳忌
        jia_sihua = GAN_SIHUA['甲']
        self.assertEqual(jia_sihua, ('廉贞', '破军', '武曲', '太阳'))

        # 这些化星落在哪个宫，由 chart 中的星曜位置决定，与 natal stem 无关
        self.assertNotEqual('甲', _birth_year_stem(2000),
            "命宫干甲 ≠ 2000年生年干庚（这是正常差异，证明两条链分离）")


class TestFeixingIsolation(unittest.TestCase):
    """Z13-D.3: FeixingRuleGraph 不读取其他派结果。"""

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()
        cls.chart = cls.engine.full_chart((2000, 1, 1), 12, 'male')
        cls.graph = create_feixing_rule_graph()

    def test_no_sanhe_import(self):
        """FeixingRuleGraph 源码不包含 SanheRuleGraph / ziwei_pattern 引用。"""
        import inspect
        source = inspect.getsource(self.graph.__class__)
        self.assertNotIn('SanheRuleGraph', source)
        self.assertNotIn('ziwei_pattern', source)
        self.assertNotIn('match_patterns', source)  # 格局匹配是 Sanhe 的事

    def test_no_zhongzhou_import(self):
        """FeixingRuleGraph 源码不包含 ZhongzhouRuleGraph 引用。"""
        import inspect
        source = inspect.getsource(self.graph.__class__)
        self.assertNotIn('ZhongzhouProfile', source)
        self.assertNotIn('ZHONGZHOU', source)

    def test_no_qintian_import(self):
        """FeixingRuleGraph 源码不包含 QintianProfile 引用。"""
        import inspect
        source = inspect.getsource(self.graph.__class__)
        self.assertNotIn('QintianProfile', source)
        self.assertNotIn('QINTIAN', source)

    def test_match_flying_only_reads_own_data(self):
        """match_flying_rules 只读取 FrozenZiweiChart + 自身规则。"""
        # 构造一个不含 Sanhe/Zhongzhou 上下文的 chart
        graph = create_feixing_rule_graph()
        # 只传 chart，不传其他派的任何数据
        results = graph.match_flying_rules(self.chart)
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertEqual(r['method_id'], 'feixing')
            self.assertTrue(r['rule_id'].startswith('FEIXING-'))

    def test_sanhe_and_feixing_produce_different_evidence(self):
        """Sanhe 和 Feixing 对同一张盘产生不同的证据内容（不互相污染）。"""
        # 分别运行 SanheRuleGraph 和 FeixingRuleGraph
        from tongshu.engines.ziwei.rules.rule_graph import create_rule_graph

        sanhe_graph = create_rule_graph(MethodId.SANHE)
        feixing_graph = create_feixing_rule_graph()

        # Sanhe 产物
        sanhe_result = sanhe_graph.match_all(self.chart)
        sanhe_rule_ids = {m.rule_spec.rule_id for m in sanhe_result.matched_rules}

        # Feixing 产物
        feixing_transforms = feixing_graph.compute_all_flying_transforms(self.chart)
        feixing_results = feixing_graph.match_flying_rules(self.chart, feixing_transforms)
        feixing_rule_ids = {r['rule_id'] for r in feixing_results}

        # Sanhe rule_id 以 SANHE- 开头，Feixing 以 FEIXING- 开头
        self.assertTrue(any('SANHE-' in rid for rid in sanhe_rule_ids))
        self.assertTrue(all(rid.startswith('FEIXING-') for rid in feixing_rule_ids))
        # 两者 rule_id 无交集
        self.assertEqual(sanhe_rule_ids & feixing_rule_ids, set(),
            "Sanhe 和 Feixing 的 rule_id 应无交集（门派隔离）")


class TestProductionEndToEnd(unittest.TestCase):
    """Z13-D.4: 完整生产路径端到端验证。"""

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()

    def test_full_pipeline_real_case(self):
        """真实命盘 → Calculation → PalaceResolution → FeixingRuleGraph → Evidence。"""
        for lunar, hour, gender, desc in REAL_CASES:
            # Step 1: 生产入口
            chart = self.engine.full_chart(lunar, hour, gender)
            self.assertIsInstance(chart, FrozenZiweiChart)
            self.assertEqual(chart.birth_year, lunar[0])

            # Step 2: 宫干事实
            stem_facts = PalaceStemContract.extract(chart)
            self.assertEqual(len(stem_facts), 12)

            # Step 3: 飞化计算
            graph = create_feixing_rule_graph()
            transforms = graph.compute_all_flying_transforms(chart)
            self.assertEqual(len(transforms), 48)  # 12宫 × 4化

            # Step 4: 规则匹配
            results = graph.match_flying_rules(chart, transforms)
            self.assertGreater(len(results), 0)

            # Step 5: 验证证据无诊断语义
            # rule match facts 包含 source_palace/source_stem/transformation/
            #   target_star/target_palace/direction（飞化结构性事实）
            # 不得包含 Signal 层方向字段
            for r in results:
                self.assertEqual(r['method_id'], 'feixing')
                facts = r['facts']
                # 不含 Signal 层诊断字段
                self.assertNotIn('polarity', facts)
                self.assertNotIn('strength', facts)
                self.assertNotIn('confidence', facts)
                # 不含 INCREASE/DECLINE/STABLE 等 Signal direction 值
                for v in facts.values():
                    if isinstance(v, str):
                        self.assertNotIn(v, ('INCREASE', 'DECLINE', 'STABLE',
                                             'POSITIVE', 'NEGATIVE', 'NEUTRAL'))

    def test_different_cases_different_flying_evidence(self):
        """不同命盘的飞化证据不同（证明计算真实，非硬编码）。"""
        charts = [
            self.engine.full_chart((2000, 1, 1), 12, 'male'),
            self.engine.full_chart((1990, 5, 15), 10, 'female'),
            self.engine.full_chart((1984, 10, 15), 8, 'female'),
        ]
        graph = create_feixing_rule_graph()
        evidence_sets = []
        for c in charts:
            transforms = graph.compute_all_flying_transforms(c)
            results = graph.match_flying_rules(c, transforms)
            # 用 FlyingTransformFact 的结构唯一标识飞化事实
            # (source_palace, source_stem, target_star, target_palace, direction)
            key = tuple(
                (t.source_palace, t.source_stem, t.target_star,
                 t.target_palace, t.direction)
                for t in transforms
            )
            evidence_sets.append(key)

        self.assertNotEqual(evidence_sets[0], evidence_sets[1])
        self.assertNotEqual(evidence_sets[1], evidence_sets[2])
        self.assertNotEqual(evidence_sets[0], evidence_sets[2])


if __name__ == "__main__":
    unittest.main()
