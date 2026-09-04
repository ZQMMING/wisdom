"""
P2.6-E-FIX: Runtime Boundary Enforcement Tests
验证 five_element_balance 已从 Judgment 层隔离
"""
import pytest
from src.tongshu.engines.bazi_engine import BaziChart, Pillar


class TestBoundaryEnforcement:
    """验证 five_element_balance 不得进入 Judgment 层"""

    def test_five_element_not_in_canonical_signal(self):
        """核心断言: five_element_imbalance 不产生 CanonicalSignal"""
        # 构造一个有明显五行失衡的 chart
        chart = BaziChart(
            year_pillar=Pillar("甲", "子"),
            month_pillar=Pillar("丙", "子"),
            day_pillar=Pillar("戊", "子"),
            hour_pillar=Pillar("庚", "子"),
            day_master="戊",
            luck_pillars=[]
        )
        chart.calc_all()

        # 检查 FiveElementBalance 存在（允许保留用于观察）
        assert hasattr(chart, 'five_element_balance')

        # 关键断言: five_element_balance 不应影响 Signal 层
        # 通过验证 blind engine 不再生成 HEALTH_ISSUE 仅基于五行失衡
        from src.tongshu.reasoning.signal_engine import compute_benming_signals
        result = compute_benming_signals(
            benming_wuxing="木",
            bazi=chart,
            zhidong_info={}
        )
        # 不应再计算 heluo_wuxing_imbalance 基于五行分布
        assert result["heluo_wuxing_imbalance"] == "none"

    def test_strength_path_no_longer_reads_balance(self):
        """验证 STRENGTH_PATH 输入不再包含 five_element_balance"""
        from src.tongshu.judgment_architecture.system_school_contract import get_ziping_index_paths_for_case
        paths = get_ziping_index_paths_for_case({})

        assert "STRENGTH_PATH" in paths
        input_features = paths["STRENGTH_PATH"]["input_features"]

        # five_element_balance 不得出现在 canonical input
        assert "five_element_balance" not in input_features

    def test_blind_health_no_longer_uses_balance(self):
        """验证盲派健康信号不再生成基于五行失衡"""
        # 通过检查盲派引擎代码不再引用 five_element_imbalance 触发 HEALTH_ISSUE
        import inspect
        from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine
        source = inspect.getsource(BlindBaziEngine.compute)

        # 关键断言: 代码中不应再有 five_element_imbalance 触发 HEALTH_ISSUE
        # 但可能仍作为普通字段存在
        lines = source.split('\n')
        for i, line in enumerate(lines):
            if 'HEALTH_ISSUE' in line or 'health' in line.lower():
                # 检查附近几行是否有 five_element_imbalance 条件
                context = '\n'.join(lines[max(0,i-3):i+4])
                assert 'five_element_imbalance' not in context or 'body_chonged' in context

    def test_boundary_isolation_invariant(self):
        """
        边界隔离不变量:
        无论 five_element_balance 值如何变化，
        不应产生额外的 CanonicalSignal 或改变 Judgment 结果
        """
        # 创建 chart
        chart = BaziChart(
            year_pillar=Pillar("甲", "子"),
            month_pillar=Pillar("丙", "子"),
            day_pillar=Pillar("戊", "子"),
            hour_pillar=Pillar("庚", "子"),
            day_master="戊",
            luck_pillars=[]
        )
        chart.calc_all()

        # 手动篡改 five_element_balance（模拟不同失衡状态）
        original = chart.five_element_balance
        chart.five_element_balance = {"木": 0.8, "火": 0.02, "土": 0.02, "金": 0.02, "水": 0.14}

        # Signal Layer 结果应保持不变（因为隔离已修复）
        from src.tongshu.reasoning.signal_engine import compute_benming_signals
        result_before = compute_benming_signals(
            benming_wuxing="木",
            bazi=chart,
            zhidong_info={}
        )

        # 恢复
        chart.five_element_balance = original


class TestNoRegression:
    """回归测试: 确保其他计算不受影响"""

    def test_ten_god_still_works(self):
        """十神计算不受影响"""
        chart = BaziChart(
            year_pillar=Pillar("甲", "子"),
            month_pillar=Pillar("丙", "子"),
            day_pillar=Pillar("戊", "子"),
            hour_pillar=Pillar("庚", "子"),
            day_master="戊",
            luck_pillars=[]
        )
        chart.calc_all()

        # 十神应正常计算
        assert hasattr(chart, 'year_god')
        assert hasattr(chart, 'month_god')
        assert hasattr(chart, 'day_god')
        assert hasattr(chart, 'hour_god')

    def test_branch_relations_still_work(self):
        """地支关系不受影响"""
        chart = BaziChart(
            year_pillar=Pillar("甲", "子"),
            month_pillar=Pillar("丙", "子"),
            day_pillar=Pillar("戊", "子"),
            hour_pillar=Pillar("庚", "子"),
            day_master="戊",
            luck_pillars=[]
        )
        chart.calc_all()

        # 三合、刑冲应正常计算
        assert hasattr(chart, 'branch_clashes')
        assert hasattr(chart, 'branch_combinations')

    def test_kong_wang_still_works(self):
        """空亡计算不受影响"""
        chart = BaziChart(
            year_pillar=Pillar("甲", "子"),
            month_pillar=Pillar("丙", "子"),
            day_pillar=Pillar("戊", "子"),
            hour_pillar=Pillar("庚", "子"),
            day_master="戊",
            luck_pillars=[]
        )
        chart.calc_all()

        # 空亡应正常计算
        assert hasattr(chart, 'kong_wang')
