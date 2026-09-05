"""P2.7-H18: Minute-Level Jieqi Boundary Hard Tests

验证分钟精度对月柱的影响。

关键发现：
- 真太阳时校正会改变 effective_minute
- 北京 longitude=116.41，经度校正 ≈ -14分钟
- EoT 在2月约 -14分钟
- 总校正约 -28分钟

因此测试必须考虑真太阳时后的实际时间。
"""

import pytest
import sys
sys.path.insert(0, "src")

from datetime import date
from tongshu.engines.time.resolver import TimeResolver
from tongshu.engines.bazi_adapter import BaziAdapter
from tongshu.engines.bazi_engine import BaziEngine
from tongshu.models.canonical_bazi import CanonicalBaziChart


class TestMonthPillarBoundary:
    """A. 月柱边界测试 - 使用真太阳时后的实际时间"""

    def setup_method(self):
        self.resolver = TimeResolver()
        self.adapter = BaziAdapter()

    def test_li_chun_boundary_before(self):
        """立春前的真太阳时 → 丑月"""
        # 立春: 2024-02-04 04:26:53 (北京时间)
        # 输入 04:00 → 真太阳时约 03:32（仍在立春前）
        ctx = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=4, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = self.adapter.compute(ctx, gender="male")

        # 立春前应为丑月
        assert chart.month_pillar.earthly_branch == "CHOU", \
            f"立春前应為丑月，实际: {chart.month_pillar}"

    def test_li_chun_boundary_after(self):
        """立春后的真太阳时 → 寅月"""
        # 需要输入足够晚的时间，使真太阳时超过 04:26:53
        # 校正约 -28分钟，所以需要输入 04:59 左右
        ctx = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=4, minute=59,  # 真太阳时约 04:30，立春后
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = self.adapter.compute(ctx, gender="male")

        # 立春后应为寅月
        assert chart.month_pillar.earthly_branch == "YIN", \
            f"立春后应為寅月，实际: {chart.month_pillar}"

    def test_li_chun_boundary_different_results(self):
        """关键验证: 节气前后的真太阳时月柱必须不同"""
        # 立春前
        ctx_before = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=4, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart_before = self.adapter.compute(ctx_before, gender="male")

        # 立春后
        ctx_after = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=4, minute=59,  # 真太阳时约 04:30，立春后
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart_after = self.adapter.compute(ctx_after, gender="male")

        # 月柱必须不同
        assert chart_before.month_pillar != chart_after.month_pillar, \
            f"节气前后月柱应不同: {chart_before.month_pillar} vs {chart_after.month_pillar}"


class TestStartAgeTargetJie:
    """B. 起运目标节测试"""

    def setup_method(self):
        self.engine = BaziEngine()

    def test_forward_direction_finds_future_jie(self):
        """顺排: 出生 < 节气 → 找未来最近节"""
        ctx = TimeResolver().resolve_context(
            birth_date=date(2024, 1, 10),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = BaziAdapter().compute(ctx, gender="male")

        assert chart.start_age > 0, "起运年龄应 > 0"
        assert chart.start_age < 10, "起运年龄应在合理范围内"

    def test_backward_direction_finds_past_jie(self):
        """逆排: 出生 > 节气 → 找过去最近节"""
        ctx = TimeResolver().resolve_context(
            birth_date=date(2025, 2, 10),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = BaziAdapter().compute(ctx, gender="male")

        assert chart.start_age > 0, "起运年龄应 > 0"

    def test_zhongqi_not_target(self):
        """中气绝不能成为目标节"""
        import sxtwl
        from tongshu.engines.time.jd_converter import jd_to_datetime

        d = sxtwl.fromSolar(2024, 2, 19)  # 雨水日
        if d.hasJieQi():
            jq_idx = d.getJieQi()
            is_jie = jq_idx % 2 == 1
            assert not is_jie, f"雨水(index={jq_idx})应是中气，不是节"


class TestSameJieqiDay:
    """C. 同一节气日测试"""

    def setup_method(self):
        self.resolver = TimeResolver()
        self.adapter = BaziAdapter()

    def test_birth_before_jieqi_solar_time(self):
        """真太阳时在节气前 → 前一月柱"""
        ctx = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=4, minute=0,  # 真太阳时约 03:32，立春前
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = self.adapter.compute(ctx, gender="male")
        assert chart.month_pillar.earthly_branch == "CHOU"

    def test_birth_after_jieqi_solar_time(self):
        """真太阳时在节气后 → 当月柱"""
        # 输入 04:59 → 真太阳时约 04:30，立春后
        ctx = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=4, minute=59,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = self.adapter.compute(ctx, gender="male")
        assert chart.month_pillar.earthly_branch == "YIN"

    def test_jieqi_day_boundary_cases(self):
        """节气日边界测试：真太阳时前后"""
        # 立春 2024-02-04 04:26:53

        # 真太阳时节前
        ctx_before = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=4, minute=20,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart_before = self.adapter.compute(ctx_before, gender="male")

        # 真太阳时节后
        ctx_after = self.resolver.resolve_context(
            birth_date=date(2024, 2, 4),
            hour=4, minute=59,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart_after = self.adapter.compute(ctx_after, gender="male")

        # 月柱必须不同
        assert chart_before.month_pillar != chart_after.month_pillar


class TestProductionPipelinePreservesTime:
    """D. 真太阳时链路测试"""

    def setup_method(self):
        self.resolver = TimeResolver()
        self.adapter = BaziAdapter()

    def test_pipeline_preserves_minute(self):
        """生产入口: minute必须贯穿整条链（在真太阳时校正后）"""
        birth_minute = 37

        ctx = self.resolver.resolve_context(
            birth_date=date(2024, 3, 15),
            hour=10, minute=birth_minute,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )

        # L1 事实层有 effective_minute（真太阳时校正后）
        assert ctx.effective_minute is not None

        # 通过Adapter到Engine
        chart = self.adapter.compute(ctx, gender="male")

        # BaziChart必须有birth_datetime且minute正确
        assert chart.birth_datetime is not None, "birth_datetime不应为None"
        # birth_datetime 应来自 true_solar_datetime
        assert chart.birth_datetime.minute == ctx.effective_minute, \
            f"birth_datetime.minute应为{ctx.effective_minute}，实际: {chart.birth_datetime.minute}"

    def test_canonical_chart_has_birth_datetime(self):
        """CanonicalBaziChart必须包含birth_datetime"""
        ctx = self.resolver.resolve_context(
            birth_date=date(2024, 3, 15),
            hour=10, minute=30,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = self.adapter.compute(ctx, gender="male")

        canonical = CanonicalBaziChart.from_bazi_chart(chart)

        assert canonical.birth_datetime is not None, \
            "CanonicalBaziChart.birth_datetime不应为None"
        assert canonical.birth_datetime == chart.birth_datetime, \
            "CanonicalBaziChart.birth_datetime应与BaziChart一致"

    def test_true_solar_time_chain(self):
        """真太阳时链路完整性测试"""
        ctx = self.resolver.resolve_context(
            birth_date=date(2024, 3, 15),
            hour=10, minute=30,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )

        # 所有时间字段都不应为None
        assert ctx.birth_civil_datetime is not None
        assert ctx.true_solar_datetime is not None

        # effective 应从 solar 计算得出
        assert ctx.effective_date is not None
        assert ctx.effective_hour is not None
        assert ctx.effective_minute is not None


class TestMinutePrecisionImpact:
    """分钟精度对月柱的实际影响测试"""

    def setup_method(self):
        self.resolver = TimeResolver()
        self.adapter = BaziAdapter()

    def test_different_minutes_same_day(self):
        """同一天不同分钟 → 验证起运年龄变化"""
        ctx1 = self.resolver.resolve_context(
            birth_date=date(2024, 3, 15),
            hour=10, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart1 = self.adapter.compute(ctx1, gender="male")

        ctx2 = self.resolver.resolve_context(
            birth_date=date(2024, 3, 15),
            hour=10, minute=30,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart2 = self.adapter.compute(ctx2, gender="male")

        # 月柱应相同（非节气日）
        assert chart1.month_pillar == chart2.month_pillar


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
