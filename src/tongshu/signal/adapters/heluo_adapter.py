"""HeluoAdapter — BaziChart to Heluo canonical conversion.

H17-B Contract:
  - Adapters only CONVERT, do NOT re-implement engine logic
  - HeluoAdapter maps BaziChart → CanonicalBaziChart → HeluoResult
  - Evidence provenance must be preserved
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from tongshu.engines.bazi_engine import BaziChart
from tongshu.models.canonical_bazi import CanonicalBaziChart
from tongshu.signal.adapters import BaseAdapter, AdapterContext
from tongshu.signal.canonical_signal import CanonicalSignal, SourceEngine


# 天干英文→中文映射（用于 Heluo 计算）
STEM_EN_TO_CN = {
    "JIA": "甲", "YI": "乙", "BING": "丙", "DING": "丁", "WU": "戊",
    "JI": "己", "GENG": "庚", "XIN": "辛", "REN": "壬", "GUI": "癸",
}

# 地支英文→中文映射
BRANCH_EN_TO_CN = {
    "ZI": "子", "CHOU": "丑", "YIN": "寅", "MAO": "卯", "CHEN": "辰", "SI": "巳",
    "WU": "午", "WEI": "未", "SHEN": "申", "YOU": "酉", "XU": "戌", "HAI": "亥",
}


@dataclass
class HeluoAdapter(BaseAdapter):
    """Adapter for Heluo engine — converts BaziChart to Heluo canonical output.

    Contract:
      - Does NOT recompute four pillars (consumes CanonicalBaziChart)
      - Only does field mapping and contract validation
      - Preserves evidence provenance
    """

    engine_name = "Heluo"
    canonical_engine = SourceEngine.HELUO

    @classmethod
    def adapt(
        cls,
        engine_output: Dict[str, Any],
        context: AdapterContext = None,
    ) -> CanonicalSignal:
        """
        Convert Heluo output to CanonicalSignal.

        Expected engine_output format:
          {
            'gua': str,
            'yao': int,
            'position': str,
            'shi': str,
            'strength': float,
            'temporal_scope': dict
          }
        """
        # Extract parameters
        gua = engine_output.get('gua', '')
        yao = engine_output.get('yao', 1)
        position = engine_output.get('position', '')
        shi = engine_output.get('shi', '')
        temporal_scope = engine_output.get('temporal_scope')

        # Normalize
        result = cls._normalize_heluo(
            gua=gua,
            yao=yao,
            position=position,
            shi=shi,
        )

        # Validate
        if not cls.validate_output(result):
            raise ValueError(f"Heluo adapter: {result.rejection_reason}")

        return cls.build_signal(
            signal_id=engine_output.get('signal_id', 'HELUO_001'),
            result=result,
            temporal_scope=temporal_scope,
            evidence_refs=context.evidence_refs if context else [],
            rule_refs=context.rule_refs if context else [],
            extracted_at=engine_output.get('extracted_at', ''),
        )

    @classmethod
    def from_bazi_chart(cls, chart: BaziChart, era: str = "zhong") -> CanonicalSignal:
        """
        Convert BaziChart directly to Heluo CanonicalSignal.

        This is the canonical path for H17-B:
          BaziChart → CanonicalBaziChart → HeluoCanonical.calculate() → CanonicalSignal

        Args:
            chart: BaziChart from BaziEngine.compute()
            era: 三元 (shang/zhong/xia)

        Returns:
            CanonicalSignal with Heluo hexagram result
        """
        # Step 1: Create CanonicalBaziChart (authoritative upstream)
        canonical_bazi = CanonicalBaziChart.from_bazi_chart(chart)

        # Step 2: Compute Heluo result (no re-computation of four pillars)
        # Convert English codes to Chinese for Heluo
        stem_map = STEM_EN_TO_CN
        branch_map = BRANCH_EN_TO_CN
        bazi_cn = [
            (stem_map[p.heavenly_stem], branch_map[p.earthly_branch])
            for p in [canonical_bazi.year_pillar, canonical_bazi.month_pillar,
                      canonical_bazi.day_pillar, canonical_bazi.hour_pillar]
        ]
        birth_hour_cn = branch_map.get(canonical_bazi.birth_hour, canonical_bazi.birth_hour)

        try:
            from tongshu.engines.heluo import HeluoCanonical
            heluo_canonical = HeluoCanonical()
            heluo_result = heluo_canonical.calculate(
                bazi=bazi_cn,
                gender=canonical_bazi.gender,
                birth_hour=birth_hour_cn,
                era=era,
                birth_year=1724,
            )
        except Exception as e:
            # Return error signal
            return cls._build_error_signal(
                signal_id=f"HELUO_ERROR_{chart.day_master}",
                error=str(e),
            )

        # Step 3: Build CanonicalSignal from HeluoResult
        return cls._result_to_signal(heluo_result, canonical_bazi)

    @classmethod
    def _result_to_signal(cls, heluo_result, canonical_bazi: CanonicalBaziChart) -> CanonicalSignal:
        """Convert HeluoResult to CanonicalSignal."""
        from tongshu.signal.normalizer import SignalNormalizer, NormalizationStatus

        # Extract key fields from HeluoResult
        gua = heluo_result.postnatal.hexagram_name
        yao = heluo_result.yuantang.yuantang
        position = heluo_result.yuantang.yao_position
        shi = canonical_bazi.birth_hour

        # Normalize
        normalization = SignalNormalizer.normalize_heluo(
            gua=gua,
            yao=yao,
            position=position,
            shi=shi,
        )

        if normalization.status != NormalizationStatus.SUCCESS:
            return cls._build_error_signal(
                signal_id="HELUO_001",
                error=normalization.rejection_reason,
            )

        # Build signal
        signal_id = f"HELUO_{canonical_bazi.day_master}_{canonical_bazi.gender}"

        return cls.build_signal(
            signal_id=signal_id,
            result=normalization,
            temporal_scope={
                "birth_year": canonical_bazi.start_age,
                "era": "zhong",
            },
        )

    @classmethod
    def _normalize_heluo(cls, gua: str, yao: int, position: str, shi: str) -> Any:
        """Normalize Heluo output."""
        from tongshu.signal.normalizer import SignalNormalizer
        return SignalNormalizer.normalize_heluo(
            gua=gua,
            yao=yao,
            position=position,
            shi=shi,
        )

    @classmethod
    def _build_error_signal(cls, signal_id: str, error: str) -> CanonicalSignal:
        """Build error CanonicalSignal."""
        from tongshu.signal.canonical_signal import CanonicalSignal, SignalLayer
        from tongshu.signal.normalizer import NormalizationResult, NormalizationStatus

        # Get REJECTED status (closest to ERROR)
        error_status = NormalizationStatus.REJECTED

        result = NormalizationResult(
            status=error_status,
            rejection_reason=error,
        )

        return CanonicalSignal(
            signal_id=signal_id,
            layer=SignalLayer.ERROR,
            source_engine=cls.canonical_engine,
            result=result,
        )
