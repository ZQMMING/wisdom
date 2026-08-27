"""ComputeStage — 阶段 1-6（计算 + SIR 构造）。

职责：
    1. bazi / ziwei / huangli 三引擎计算
    2. 信号提取（Bazi/Ziwei 分轨，DECISION-002）
    3. Cross Analysis（Bazi + Ziwei，DECISION-003）
    4. atomic_claims 构造（含 mapping_refs 附加）
    5. SIR 构造（CanonicalComposer）
    6. SIR schema 校验（jsonschema Draft202012Validator）

设计：纯计算，无渲染、无校验、无审计。返回 ComputeResult。

Version: 1.0.0
Created: 2026-08-20 (Phase 2 / Step 3 C2)
Migrated from: pipeline.py:113-235（run() 阶段 1-6）
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone
import uuid
from pathlib import Path

from ..canonical.canonical_validator import validate_canonical
from ..canonical.composer import CanonicalComposer
from ..engines.bazi_adapter import BaziAdapter
from ..engines.bazi_engine import BaziEngine
from ..engines.heluo.canonical import HeluoCanonical
from ..engines.huangli_engine import HuangliEngine
from ..engines.time.calculation_context import CalculationContext
from ..engines.ziwei_adapter import ZiweiAdapter
from ..engines.ziwei_engine import ZiweiEngine
from ..reasoning.cross_analysis import CrossAnalyzer
from ..reasoning.mapping_registry import MappingRegistry
from ..reasoning.matcher import RuleMatcher
from ..reasoning.signal_engine import SignalEngine
from ..reasoning.theme_engine import ThemeEngine
from ..types import ComputeResult
from ..yi.adapter import YiAdapter, YiAdapterInput
from ..yi.interpreter import YiInterpretationEngine

log = logging.getLogger(__name__)

# BUG-P0-03: BaziEngine 输出的干支为英文（JIA/ZI），而 HeluoCanonical 需要中文
# （甲/子）。此映射只做符号转译，不参与任何河洛算法计算。
_STEM_CN = {
    "JIA": "甲", "YI": "乙", "BING": "丙", "DING": "丁", "WU": "戊",
    "JI": "己", "GENG": "庚", "XIN": "辛", "REN": "壬", "GUI": "癸",
}
_BRANCH_CN = {
    "ZI": "子", "CHOU": "丑", "YIN": "寅", "MAO": "卯", "CHEN": "辰", "SI": "巳",
    "WU": "午", "WEI": "未", "SHEN": "申", "YOU": "酉", "XU": "戌", "HAI": "亥",
}


class ComputeStage:
    """阶段 1-6: 纯计算 + SIR 构造。"""

    def __init__(
        self,
        bazi_engine: BaziEngine,
        ziwei_engine: ZiweiEngine,
        huangli_engine: HuangliEngine,
        signal_engine: SignalEngine,
        cross_analyzer: CrossAnalyzer,
        theme_engine: ThemeEngine,
        mapping_registry: MappingRegistry | None,
        composer: CanonicalComposer,
        schema_dir: Path,
        matcher: RuleMatcher,
        renderer_model_id: str,
        heluo_canonical: HeluoCanonical | None = None,
        yi_engine: YiInterpretationEngine | None = None,
    ) -> None:
        self.bazi_engine = bazi_engine
        self.ziwei_engine = ziwei_engine
        self.huangli_engine = huangli_engine
        self.signal_engine = signal_engine
        self.cross_analyzer = cross_analyzer
        self.theme_engine = theme_engine
        self.mapping_registry = mapping_registry
        self.composer = composer
        self.schema_dir = Path(schema_dir)
        self.matcher = matcher
        self._renderer_model_id = renderer_model_id
        # BUG-P0-03: 河洛 + 易经解释引擎接入主 Pipeline（可注入以支持测试）。
        self.heluo_canonical = heluo_canonical or HeluoCanonical()
        self.yi_engine = yi_engine or YiInterpretationEngine()
        # B-02: 时间政策 Adapter（封装 23:00 日界 / 阳→农历转换）
        self._bazi_adapter = BaziAdapter(bazi_engine)
        self._ziwei_adapter = ZiweiAdapter(ziwei_engine)

    def run(
        self,
        analysis_date: date,
        birth_date: tuple[int, int, int, int],
        gender: str,
        theme: str,
        request_id: str,
        trace_id: str,
        calc_context: CalculationContext | None = None,
    ) -> ComputeResult:
        """执行阶段 1-6 全流程：bazi+ziwei+huangli → signals → cross → claims → SIR → schema。"""

        # 1. Engine layer
        # B-02: calc_context 提供时经时间政策 Adapter 调用（23:00 日界 / 阳→农历）；
        # 无 calc_context 时保留直调以向后兼容。
        if calc_context is not None:
            effective_gender = calc_context.subject_gender or gender
            bazi_chart = self._bazi_adapter.compute(calc_context, gender=effective_gender)
            ziwei_chart = self._ziwei_adapter.compute(calc_context, gender=effective_gender)
            year, month, day, hour = calc_context.bazi_view
        else:
            bazi_birth = birth_date
            year, month, day, hour = bazi_birth
            effective_gender = gender
            bazi_chart = self.bazi_engine.compute(bazi_birth, gender=effective_gender)
            # P1-FIX: fallback(无 location) 也需阳历→农历再调 iztro。
            # 此前把阳历日期当农历直传，农历无 31 日等输入触发 iztro 崩溃（GOLDEN-016）。
            from lunar_python import Solar as _Solar
            _lunar = _Solar.fromYmdHms(year, month, day, hour, 0, 0).getLunar()
            ziwei_chart = self.ziwei_engine.compute(
                (_lunar.getYear(), _lunar.getMonth(), _lunar.getDay()),
                hour,
                gender=effective_gender,
            )
        huangli_day = self.huangli_engine.get_day(analysis_date)

        # 1b. 河洛理数 + 易经解释引擎（BUG-P0-03 接入主 Pipeline）。
        # 河洛计算 → YiAdapter 适配为 YiStructure → YiInterpretationEngine 解释。
        # 任何一步失败都降级为 None，不影响既有 bazi/ziwei/huangli 主链路。
        heluo_result, yi_structure, yi_interpretation = self._compute_heluo_yi(
            bazi_chart, gender
        )

        # 2. 信号提取（Bazi only - P1-C fix keeps Ziwei separate）
        signals = self.signal_engine.build(
            bazi_chart, ziwei_chart, huangli_day, gender=gender, heluo_result=heluo_result
        )

        # 2b. Ziwei signal extraction (separate from Bazi signals)
        zw_signal = self.ziwei_engine.extract_baseline_signal(ziwei_chart, 0)

        # 3. Cross Analysis (Bazi signals only, not mixed with Ziwei)
        bazi_signals = signals.get("BASELINE", []) + signals.get("CYCLE_CONTEXT", []) + signals.get("DAILY_ACTIVATION", [])
        ziwei_signals = [zw_signal] if zw_signal is not None else []
        cross_result = self.cross_analyzer.analyze(bazi_signals, ziwei_signals)

        # Add ziwei signal to BASELINE layer for SIR serialization (after Cross Analysis)
        # This keeps SIR complete without polluting the cross analysis input
        if zw_signal is not None:
            signals["BASELINE"].append(zw_signal)

        # 4. Generate atomic_claims from signals
        atomic_claims = self._build_atomic_claims(theme, signals)

        # 4b. V3.6 §18-21 词库标签层:附加 mapping_refs / modern_theme(DECISION 6
        # 语义边界:只加标签,绝不改写 USO 枚举 / rule_refs / evidence_refs)。
        if self.mapping_registry is not None:
            atomic_claims = self.mapping_registry.apply_to_claims(atomic_claims)

        # 5. Compose SIR
        # Lazy-init CanonicalComposer if not set (needs theme from run() params)
        if self.composer is None:
            self.composer = CanonicalComposer(
                theme=theme,
                engine_versions={
                    "bazi": "1.0.0",
                    "ziwei": "1.0.0",
                    "rules": "1.0.0",
                    "reasoning": "1.0.0",
                },
            )
        canonical = self.composer.compose(
            analysis_date=analysis_date,
            bazi=bazi_chart,
            ziwei=ziwei_chart,
            huangli=huangli_day,
            signals=signals,
            cross_result=cross_result,
            atomic_claims=atomic_claims,
            exclusions=[],
            meta_observability={
                "request_id": request_id,
                "trace_id": (trace_id if trace_id is not None else f"TRACE-{uuid.uuid4().hex[:10].upper()}"),
                "model_version": self._renderer_model_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        # 6. Validate canonical
        is_valid, errs = validate_canonical(canonical.to_dict(), self.schema_dir)
        if not is_valid:
            log.warning(f"Canonical validation failed: {errs}")
            # Per architecture: do not proceed with invalid SIR
            # For demo, log and continue

        return ComputeResult(
            bazi_chart=bazi_chart,
            ziwei_chart=ziwei_chart,
            huangli_day=huangli_day,
            signals=signals,
            cross_result=cross_result,
            atomic_claims=atomic_claims,
            canonical=canonical,
            canonical_schema_valid=is_valid,
            canonical_schema_errors=tuple(errs) if errs else (),
            computed_at=datetime.now(timezone.utc),
            heluo_result=heluo_result,
            yi_structure=yi_structure,
            yi_interpretation=yi_interpretation,
        )

    def _compute_heluo_yi(
        self,
        bazi_chart,
        gender: str,
    ) -> tuple:
        """河洛理数计算 + 易经解释（BUG-P0-03）。

        数据流：
            BaziChart(四柱干支) → HeluoCanonical.calculate()
                → HeluoResult(本命卦/元堂/后天卦)
                → YiAdapter.adapt() → YiStructure
                → YiInterpretationEngine.interpret() → YiInterpretation

        返回三元组 (heluo_result, yi_structure, yi_interpretation)。
        任一步失败都返回 (None, None, None)，绝不让河洛/易经错误中断既有主链路。
        """
        heluo_result = None
        yi_structure = None
        yi_interpretation = None
        try:
            bazi_cn = self._bazi_to_heluo_pillars(bazi_chart)
            birth_hour_cn = _BRANCH_CN.get(
                bazi_chart.hour_pillar.earthly_branch, "子"
            )
            heluo_result = self.heluo_canonical.calculate(
                bazi=bazi_cn,
                gender=gender,
                birth_hour=birth_hour_cn,
                era="zhong",
            )
            # 将河洛结果传入 YiAdapter（只消费 Contract 化字段，不重新计算河洛）
            yi_input = YiAdapterInput(
                heluo_prenatal_hexagram=heluo_result.prenatal.hexagram_name,
                heluo_postnatal_hexagram=heluo_result.postnatal.hexagram_name,
                heluo_yuantang_index=heluo_result.yuantang.yuantang_index,
                heluo_yuantang=heluo_result.yuantang.yuantang,
            )
            yi_structure = YiAdapter.adapt(yi_input)
            yi_interpretation = self.yi_engine.interpret(yi_structure)
        except Exception as exc:  # noqa: BLE001 — 河洛/易经降级，不中断主管道
            log.warning("Heluo/Yi integration failed (degraded, 不影响主链路): %s", exc)
        return heluo_result, yi_structure, yi_interpretation

    @staticmethod
    def _bazi_to_heluo_pillars(bazi_chart) -> list[tuple[str, str]]:
        """将 BaziChart 四柱干支转为河洛引擎所需的中文 (干, 支) 列表。

        仅做符号转译，不改动 V1.2 河洛算法。
        """
        return [
            (_STEM_CN[bazi_chart.year_pillar.heavenly_stem],
             _BRANCH_CN[bazi_chart.year_pillar.earthly_branch]),
            (_STEM_CN[bazi_chart.month_pillar.heavenly_stem],
             _BRANCH_CN[bazi_chart.month_pillar.earthly_branch]),
            (_STEM_CN[bazi_chart.day_pillar.heavenly_stem],
             _BRANCH_CN[bazi_chart.day_pillar.earthly_branch]),
            (_STEM_CN[bazi_chart.hour_pillar.heavenly_stem],
             _BRANCH_CN[bazi_chart.hour_pillar.earthly_branch]),
        ]

    def _build_atomic_claims(self, theme: str, signals: dict[str, list]) -> list[dict]:
        """Build atomic_claims from signals using theme frame.

        从 pipeline.py 迁出，保持原算法不变。
        """
        claims: list[dict] = []
        seq = 0
        for layer, sigs in signals.items():
            for sig in sigs:
                seq += 1
                claim_text = self.theme_engine.reframe_claim(
                    sig.ontology_type,
                    theme,
                    direction=sig.direction,
                    polarity=sig.polarity,
                ) or f"主体在 {theme} 主题上 {sig.ontology_type} 类信号{sig.polarity}。"

                claims.append({
                    "claim_id": f"AC-{sig.signal_id}",
                    "signal_type": sig.ontology_type,
                    "claim": claim_text,
                    "direction": sig.direction,
                    "strength": "MODERATE",
                    "source_layers": [layer],
                    "rule_refs": list(sig.rule_refs),
                    "evidence_refs": list(sig.evidence_refs),
                })
        return claims
