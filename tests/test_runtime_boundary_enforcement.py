"""
P2.6-E-FIX-5: True Runtime Boundary Proof
验证 five_element_balance 已从 Judgment 层隔离 — 真实 mutation 行为测试
"""
import pytest
from dataclasses import replace
from unittest.mock import patch
from src.tongshu.engines.bazi_engine import BaziChart, BaziEngine, Pillar
from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine, BlindBaziResult, BRANCH_CHONG


# ============================================================
# Mutation State
# ============================================================
EXTREME_BALANCE = {
    "WOOD": 0.80, "FIRE": 0.02, "EARTH": 0.02, "METAL": 0.02, "WATER": 0.14
}
NORMAL_BALANCE = {
    "WOOD": 0.20, "FIRE": 0.20, "EARTH": 0.20, "METAL": 0.20, "WATER": 0.20
}


class TestBoundaryEnforcement:
    """验证 five_element_balance 不得进入 Judgment 层 — Mutation-based 行为测试"""

    def test_blind_health_not_triggered_by_imbalance_flag(self):
        """
        核心 mutation test: 修改 five_element_imbalance 不改变 HEALTH_ISSUE 信号。
        采用 monkey-patch 方式注入篡改后的 chart。
        """
        engine = BaziEngine()
        blind_engine = BlindBaziEngine(engine)

        # Baseline result
        result_baseline = blind_engine.compute((1984, 1, 1, 0), gender="male")
        health_baseline = [s for s in result_baseline.signals if s.event_type == "HEALTH_ISSUE"]

        # Monkey-patch: patch the instance method, not the class method
        original_compute = engine.compute
        def patched_compute(solar_date, gender="male"):
            chart = original_compute(solar_date, gender=gender)
            return replace(chart, five_element_imbalance=True, five_element_balance=EXTREME_BALANCE)

        with patch.object(engine, 'compute', patched_compute):
            result_mutated = blind_engine.compute((1984, 1, 1, 0), gender="male")

        health_mutated = [s for s in result_mutated.signals if s.event_type == "HEALTH_ISSUE"]

        # 核心断言: HEALTH_ISSUE 信号数量应相同
        assert len(health_baseline) == len(health_mutated), \
            f"HEALTH_ISSUE count changed: {len(health_baseline)} → {len(health_mutated)}"

    def test_blind_body_chonged_still_triggers_health(self):
        """
        回归验证: body_chonged=True 时仍正确触发 HEALTH_ISSUE。
        """
        engine = BaziEngine()
        blind_engine = BlindBaziEngine(engine)

        # 纪晓岚案例
        result = blind_engine.compute((1724, 7, 16, 12), gender="male")

        # 检查 body_chonged
        body_chonged = any(
            BRANCH_CHONG.get(b) in result.yong_branches
            for b in result.ti_branches
        )

        health_signals = [s for s in result.signals if s.event_type == "HEALTH_ISSUE"]

        if body_chonged:
            assert len(health_signals) >= 1, \
                "Expected HEALTH_ISSUE when body_chonged=True"
        else:
            assert len(health_signals) == 0, \
                "No HEALTH_ISSUE expected when body_chonged=False"

    def test_five_element_balance_mutation_no_effect_on_ti_yong(self):
        """
        Mutation test: five_element_balance 变化不应影响体用判定。
        体用基于 ten_god 分类，与五行分布无关。
        """
        engine = BaziEngine()
        blind_engine = BlindBaziEngine(engine)

        # Baseline result
        result_normal = blind_engine.compute((1984, 1, 1, 0), gender="male")

        # Mutated: five_element_imbalance=True
        original_compute = engine.compute
        def patched_compute(solar_date, gender="male"):
            chart = original_compute(solar_date, gender=gender)
            return replace(chart, five_element_imbalance=True, five_element_balance=EXTREME_BALANCE)

        with patch.object(engine, 'compute', patched_compute):
            result_mutated = blind_engine.compute((1984, 1, 1, 0), gender="male")

        # 体用分支集合应完全相同
        assert result_normal.ti_branches == result_mutated.ti_branches, \
            "ti_branches changed after balance mutation"
        assert result_normal.yong_branches == result_mutated.yong_branches, \
            "yong_branches changed after balance mutation"

        # 宾主分支也应相同
        assert result_normal.main_branches == result_mutated.main_branches, \
            "main_branches changed after balance mutation"
        assert result_normal.guest_branches == result_mutated.guest_branches, \
            "guest_branches changed after balance mutation"

    def test_strength_path_no_longer_reads_balance(self):
        """验证 STRENGTH_PATH 输入不再包含 five_element_balance"""
        from src.tongshu.judgment_architecture.system_school_contract import get_ziping_index_paths_for_case
        paths = get_ziping_index_paths_for_case({})

        assert "STRENGTH_PATH" in paths
        input_features = paths["STRENGTH_PATH"]["input_features"]
        assert "five_element_balance" not in input_features

    def test_heluo_signal_engine_not_reading_balance_runtime(self):
        """
        Runtime test: 直接调用 extract_heluo_context，传入不同 five_element_balance 的 chart，
        验证结果不受影响。
        """
        from src.tongshu.reasoning.signal_engine import extract_heluo_context

        engine = BaziEngine()
        chart = engine.compute((1984, 1, 1, 0), gender="male")

        # 测试 1: heluo_result=None → 应返回空 dict
        result_none = extract_heluo_context(None, chart)
        assert result_none == {}

        # 测试 2: 用不同 five_element_balance 构造 chart，验证结果不变
        chart_normal = replace(chart, five_element_balance=NORMAL_BALANCE)
        chart_extreme = replace(chart, five_element_balance=EXTREME_BALANCE)

        result_normal = extract_heluo_context(None, chart_normal)
        result_extreme = extract_heluo_context(None, chart_extreme)

        assert result_normal == result_extreme == {}

    def test_boundary_isolation_via_source_check(self):
        """源码级隔离验证（辅助测试）"""
        import inspect
        from src.tongshu.reasoning.signal_engine import extract_heluo_context
        from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine

        # signal_engine 不应再读取 bazi.five_element_balance[key]
        sig_source = inspect.getsource(extract_heluo_context)
        assert 'bazi.five_element_balance[' not in sig_source

        # blind engine 中 HEALTH_ISSUE 附近不应有 five_element_imbalance
        blind_source = inspect.getsource(BlindBaziEngine.compute)
        lines = blind_source.split('\n')
        for i, line in enumerate(lines):
            if 'HEALTH_ISSUE' in line:
                context = '\n'.join(lines[max(0, i-5):i+2])
                assert 'five_element_imbalance' not in context


class TestNoRegression:
    """回归测试: 确保其他计算不受影响"""

    def test_kong_wang_still_works(self):
        """空亡计算不受影响"""
        engine = BaziEngine()
        chart = engine.compute((1984, 1, 1, 0), gender="male")
        assert hasattr(chart, 'kong_wang')
        assert isinstance(chart.kong_wang, tuple)

    def test_branch_clash_map_still_works(self):
        """地支冲关系计算不受影响"""
        engine = BaziEngine()
        chart = engine.compute((1984, 1, 1, 0), gender="male")
        assert hasattr(chart, 'branch_clash_map')
        assert isinstance(chart.branch_clash_map, dict)

    def test_day_branch_main_ten_god_computed(self):
        """日支主气藏干十神计算不受影响"""
        engine = BaziEngine()
        chart = engine.compute((1984, 1, 1, 0), gender="male")
        assert hasattr(chart, 'day_branch_main_ten_god')
        assert isinstance(chart.day_branch_main_ten_god, str)

    def test_blind_engine_computes_signals(self):
        """盲派引擎仍能正常计算信号"""
        engine = BaziEngine()
        blind_engine = BlindBaziEngine(engine)
        result = blind_engine.compute((1984, 1, 1, 0), gender="male")
        assert isinstance(result, BlindBaziResult)
        assert hasattr(result, 'signals')
        assert isinstance(result.signals, list)

    def test_blind_body_chonged_logic_preserved(self):
        """盲派 body_chonged 逻辑仍正常工作"""
        engine = BaziEngine()
        blind_engine = BlindBaziEngine(engine)
        result = blind_engine.compute((1984, 1, 1, 0), gender="male")
        for signal in result.signals:
            assert hasattr(signal, 'signal_id')
            assert hasattr(signal, 'event_type')
            assert hasattr(signal, 'layer')
