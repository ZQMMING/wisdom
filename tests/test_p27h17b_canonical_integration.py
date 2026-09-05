"""P2.7-H17-B: Canonical Bazi Integration Tests

Tests for H17-B: CanonicalBaziChart → HeluoAdapter → FrozenHeluoState integration.

Architecture:
  BaziEngine → BaziChart → CanonicalBaziChart → HeluoCanonical.calculate()

Contract:
  - Heluo MUST NOT recompute four pillars
  - Heluo consumes only CanonicalBaziChart (authoritative upstream)
  - Adapter does field mapping only, no re-calculation
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from tongshu.models.canonical_bazi import CanonicalBaziChart
    from tongshu.engines.bazi_engine import BaziChart

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.engines.bazi_adapter import BaziAdapter
from tongshu.engines.time.resolver import TimeResolver
from tongshu.models.canonical_bazi import CanonicalBaziChart
from tongshu.engines.heluo import HeluoCanonical, HeluoResult
from tongshu.signal.adapters.heluo_adapter import HeluoAdapter


class TestCanonicalBaziChart:
    """Test CanonicalBaziChart creation and properties."""

    def test_from_bazi_chart_jixiaolan(self):
        """纪晓岚案例：BaziChart → CanonicalBaziChart."""
        resolver = TimeResolver()
        adapter = BaziAdapter()

        ctx = resolver.resolve_context(
            birth_date=date(1724, 7, 16),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = adapter.compute(ctx, gender="male")

        # Create CanonicalBaziChart
        canonical = CanonicalBaziChart.from_bazi_chart(chart)

        # Verify fields (纪晓岚: 甲辰 辛未 戊辰 戊午)
        assert canonical.year_pillar.heavenly_stem == "JIA"
        assert canonical.year_pillar.earthly_branch == "CHEN"
        assert canonical.month_pillar.heavenly_stem == "XIN"
        assert canonical.month_pillar.earthly_branch == "WEI"
        assert canonical.day_pillar.heavenly_stem == "WU"  # 戊
        assert canonical.day_pillar.earthly_branch == "CHEN"  # 辰
        assert canonical.hour_pillar.heavenly_stem == "WU"  # 戊
        assert canonical.hour_pillar.earthly_branch == "WU"  # 午
        assert canonical.day_master == "WU"
        assert canonical.gender == "male"
        assert canonical.start_age > 0

    def test_from_bazi_chart_su_shi(self):
        """苏轼案例：BaziChart → CanonicalBaziChart."""
        resolver = TimeResolver()
        adapter = BaziAdapter()

        ctx = resolver.resolve_context(
            birth_date=date(1037, 1, 8),
            hour=6, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = adapter.compute(ctx, gender="male")

        canonical = CanonicalBaziChart.from_bazi_chart(chart)

        assert canonical.day_master == "GUI"
        assert canonical.gender == "male"

    def test_bazi_property(self):
        """CanonicalBaziChart.bazi property returns correct list."""
        resolver = TimeResolver()
        adapter = BaziAdapter()

        ctx = resolver.resolve_context(
            birth_date=date(1724, 7, 16),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = adapter.compute(ctx, gender="male")
        canonical = CanonicalBaziChart.from_bazi_chart(chart)

        bazi = canonical.bazi
        assert len(bazi) == 4
        assert bazi[0] == ("JIA", "CHEN")  # 年柱
        assert bazi[1] == ("XIN", "WEI")   # 月柱
        assert bazi[2] == ("WU", "CHEN")   # 日柱（戊辰）
        assert bazi[3] == ("WU", "WU")     # 时柱（戊午）

    def test_birth_hour_property(self):
        """CanonicalBaziChart.birth_hour returns correct hour branch."""
        resolver = TimeResolver()
        adapter = BaziAdapter()

        ctx = resolver.resolve_context(
            birth_date=date(1724, 7, 16),
            hour=12, minute=0,  # 午时
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = adapter.compute(ctx, gender="male")
        canonical = CanonicalBaziChart.from_bazi_chart(chart)

        assert canonical.birth_hour == "WU"


class TestHeluoCanonicalWithCanonicalBazi:
    """Test HeluoCanonical.calculate() with CanonicalBaziChart input."""

    def setup_method(self):
        self.canonical = HeluoCanonical()

    def test_golden_case_jixiaolan_via_canonical(self):
        """纪晓岚 Golden Case via CanonicalBaziChart."""
        resolver = TimeResolver()
        adapter = BaziAdapter()

        ctx = resolver.resolve_context(
            birth_date=date(1724, 7, 16),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = adapter.compute(ctx, gender="male")
        canonical = CanonicalBaziChart.from_bazi_chart(chart)

        # Calculate via new interface
        result = self.canonical.calculate(
            canonical_bazi=canonical,
            era="zhong",
            birth_year=1724,
        )

        # Verify expected results (纪晓岚: 风地观 → 六四 → 天雷无妄)
        assert result.prenatal.hexagram_name == "风地观"
        assert result.yuantang.yuantang == "六四"
        assert result.postnatal.hexagram_name == "天雷无妄"

    def test_su_shi_via_canonical(self):
        """苏轼案例 via CanonicalBaziChart."""
        resolver = TimeResolver()
        adapter = BaziAdapter()

        ctx = resolver.resolve_context(
            birth_date=date(1037, 1, 8),
            hour=6, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = adapter.compute(ctx, gender="male")
        canonical = CanonicalBaziChart.from_bazi_chart(chart)

        result = self.canonical.calculate(
            canonical_bazi=canonical,
            era="zhong",
            birth_year=1037,
        )

        # Should produce valid result without errors
        assert result is not None
        assert result.prenatal is not None
        assert result.postnatal is not None

    def test_canonical_is_read_only(self):
        """CanonicalBaziChart should be immutable (frozen)."""
        resolver = TimeResolver()
        adapter = BaziAdapter()

        ctx = resolver.resolve_context(
            birth_date=date(1724, 7, 16),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = adapter.compute(ctx, gender="male")
        canonical = CanonicalBaziChart.from_bazi_chart(chart)

        # Try to modify (should fail because frozen=True)
        with pytest.raises(Exception):  # dataclasses.FrozenInstanceError
            canonical.year_pillar = None


class TestHeluoAdapter:
    """Test HeluoAdapter BaziChart → CanonicalSignal conversion."""

    def test_from_bazi_chart_jixiaolan(self):
        """纪晓岚案例：BaziChart → HeluoAdapter → CanonicalSignal."""
        resolver = TimeResolver()
        adapter = BaziAdapter()

        ctx = resolver.resolve_context(
            birth_date=date(1724, 7, 16),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = adapter.compute(ctx, gender="male")

        # Convert via adapter
        signal = HeluoAdapter.from_bazi_chart(chart, era="zhong")

        # Verify signal structure
        assert signal is not None
        assert signal.signal_id.startswith("HELUO_")
        assert signal.source_engine == "Heluo"


class TestIntegration:
    """Integration tests: end-to-end flow from BirthInput to HeluoResult."""

    def test_full_pipeline_jixiaolan(self):
        """完整生产链：BirthInput → BaziAdapter → BaziChart → CanonicalBaziChart → HeluoCanonical."""
        resolver = TimeResolver()
        bazi_adapter = BaziAdapter()
        heluo_canonical = HeluoCanonical()

        # Step 1: BirthInput → BaziChart
        ctx = resolver.resolve_context(
            birth_date=date(1724, 7, 16),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = bazi_adapter.compute(ctx, gender="male")

        # Step 2: BaziChart → CanonicalBaziChart
        canonical = CanonicalBaziChart.from_bazi_chart(chart)

        # Step 3: CanonicalBaziChart → HeluoResult
        result = heluo_canonical.calculate(
            canonical_bazi=canonical,
            era="zhong",
            birth_year=1724,
        )

        # Verify full pipeline
        assert chart.start_age > 0
        assert canonical.day_master == chart.day_master
        assert result.prenatal.hexagram_name == "地天泰"
        assert result.postnatal.hexagram_name == "天雷无妄"

    def test_full_pipeline_su_shi(self):
        """苏轼案例：完整生产链验证."""
        resolver = TimeResolver()
        bazi_adapter = BaziAdapter()
        heluo_canonical = HeluoCanonical()

        ctx = resolver.resolve_context(
            birth_date=date(1037, 1, 8),
            hour=6, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = bazi_adapter.compute(ctx, gender="male")
        canonical = CanonicalBaziChart.from_bazi_chart(chart)
        result = heluo_canonical.calculate(
            canonical_bazi=canonical,
            era="zhong",
            birth_year=1037,
        )

        assert result is not None
        assert result.prenatal is not None
        assert result.postnatal is not None


class TestNoDuplicateCalculation:
    """Verify Heluo does NOT recompute four pillars."""

    def test_heluo_consumes_canonical_only(self):
        """Heluo.calculate() should only read from CanonicalBaziChart, not compute."""
        # This test verifies the architecture contract:
        # Heluo should NOT have its own calculate_year_pillar, etc.
        import inspect
        from tongshu.engines.heluo import HeluoCanonical

        canonical_source = inspect.getsource(HeluoCanonical.calculate)

        # Should NOT contain these patterns (duplicate calculation)
        forbidden_patterns = [
            "calculate_year_pillar",
            "calculate_month_pillar",
            "calculate_day_pillar",
            "calculate_hour_pillar",
            "sxtwl.fromSolar",  # No direct sxtwl calls in calculate()
        ]

        for pattern in forbidden_patterns:
            assert pattern not in canonical_source, \
                f"Heluo.calculate() should not contain '{pattern}' — duplicate calculation detected!"

    def test_canonical_bazi_not_modified_by_heluo(self):
        """Heluo should not modify CanonicalBaziChart (read-only contract)."""
        resolver = TimeResolver()
        adapter = BaziAdapter()

        ctx = resolver.resolve_context(
            birth_date=date(1724, 7, 16),
            hour=12, minute=0,
            timezone=None, location="beijing",
            apparent_solar=True, gender="male",
        )
        chart = adapter.compute(ctx, gender="male")
        canonical_before = CanonicalBaziChart.from_bazi_chart(chart)

        # Calculate Heluo
        heluo = HeluoCanonical()
        result = heluo.calculate(
            canonical_bazi=canonical_before,
            era="zhong",
            birth_year=1724,
        )

        # CanonicalBaziChart should be unchanged (frozen)
        canonical_after = CanonicalBaziChart.from_bazi_chart(chart)
        assert canonical_before == canonical_after


class TestBoundaryCases:
    """Boundary case tests for CanonicalBaziChart integration."""

    def test_different_genders(self):
        """Test both male and female cases."""
        resolver = TimeResolver()
        adapter = BaziAdapter()
        heluo = HeluoCanonical()

        for gender in ["male", "female"]:
            ctx = resolver.resolve_context(
                birth_date=date(1724, 7, 16),
                hour=12, minute=0,
                timezone=None, location="beijing",
                apparent_solar=True, gender=gender,
            )
            chart = adapter.compute(ctx, gender=gender)
            canonical = CanonicalBaziChart.from_bazi_chart(chart)
            result = heluo.calculate(
                canonical_bazi=canonical,
                era="zhong",
                birth_year=1724,
            )
            assert result is not None
            assert result.prenatal is not None

    def test_different_hours(self):
        """Test different birth hours."""
        resolver = TimeResolver()
        adapter = BaziAdapter()
        heluo = HeluoCanonical()

        for hour in [1, 5, 11, 17, 23]:
            ctx = resolver.resolve_context(
                birth_date=date(1724, 7, 16),
                hour=hour, minute=0,
                timezone=None, location="beijing",
                apparent_solar=True, gender="male",
            )
            chart = adapter.compute(ctx, gender="male")
            canonical = CanonicalBaziChart.from_bazi_chart(chart)
            result = heluo.calculate(
                canonical_bazi=canonical,
                era="zhong",
                birth_year=1724,
            )
            assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
