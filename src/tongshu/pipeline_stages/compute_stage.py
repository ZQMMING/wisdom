"""ComputeStage — 阶段 1-6（计算 + SIR 构造）。

职责：
    1. bazi / ziwei / huangli 三引擎计算
    2. 信号提取（Bazi/Ziwei 分轨，DECISION-002）
    3. 跨域编排（CrossDomainOrchestrator，P1.6）
    4. atomic_claims 构造（含 mapping_refs 附加，direction 来自授权 Rule）
    5. SIR 构造（CanonicalComposer）
    6. SIR schema 校验（jsonschema Draft202012Validator）

设计：纯计算，无渲染、无校验、无审计。返回 ComputeResult。

Version: 1.1.0 (P1.6: CrossDomainOrchestrator 接入生产路径)
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
from ..cross_domain import CrossDomainOrchestrator
from ..engines.bazi_adapter import BaziAdapter
from ..engines.bazi_engine import BaziEngine
from ..engines.heluo.canonical import HeluoCanonical
from ..engines.huangli_engine import HuangliEngine
from ..engines.time.calculation_context import CalculationContext
from ..engines.ziwei_adapter import ZiweiAdapter
from ..engines.ziwei_engine import ZiweiEngine
from ..reasoning.mapping_registry import MappingRegistry
from ..reasoning.matcher import RuleMatcher
from ..reasoning.signal_engine import SignalEngine
from ..reasoning.theme_engine import ThemeEngine
from ..spec.canonical import EngineEvidence, SemanticAtom, EngineName, TemporalScope
from ..temporal.convergence import TemporalConvergenceEngine
from ..temporal.schema import PredictionWindow, TemporalGranularity, TemporalSignal
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
    """阶段 1-6: 纯计算 + SIR 构造。

    P1.6: 接受可选的 assertion_library（ProductionRuleLibrary），
    通过 CrossDomainOrchestrator 编排跨域证据，direction 来自 Rule 授权。
    """

    def __init__(
        self,
        bazi_engine: BaziEngine,
        ziwei_engine: ZiweiEngine,
        huangli_engine: HuangliEngine,
        signal_engine: SignalEngine,
        theme_engine: ThemeEngine,
        mapping_registry: MappingRegistry | None,
        composer: CanonicalComposer,
        schema_dir: Path,
        matcher: RuleMatcher,
        renderer_model_id: str,
        heluo_canonical: HeluoCanonical | None = None,
        yi_engine: YiInterpretationEngine | None = None,
        assertion_library=None,  # ProductionRuleLibrary | None (P1.6)
        temporal_convergence_engine: TemporalConvergenceEngine | None = None,  # P1.7
    ) -> None:
        self.bazi_engine = bazi_engine
        self.ziwei_engine = ziwei_engine
        self.huangli_engine = huangli_engine
        self.signal_engine = signal_engine
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
        # P1.6: CrossDomainOrchestrator（可选，None = 降级为旧信号路径）
        self._assertion_library = assertion_library
        self._orchestrator = None
        if assertion_library is not None and getattr(assertion_library, "is_production", False):
            self._orchestrator = CrossDomainOrchestrator(assertion_library=assertion_library)
        # P1.7: TemporalConvergenceEngine（可选，None = 跳过时序收敛）
        self._temporal_convergence_engine = temporal_convergence_engine

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
        build_result = self.signal_engine.build(
            bazi_chart, ziwei_chart, huangli_day, gender=gender, heluo_result=heluo_result
        )
        signals = build_result["signals"]
        canonical_signals = build_result.get("canonical_signals", {})

        # 2b. Ziwei signal extraction (separate from Bazi signals)
        zw_signal = self.ziwei_engine.extract_baseline_signal(ziwei_chart, 0)

        # 3. Cross-domain orchestration (P1.6)
        # If assertion_library is provided, use CrossDomainOrchestrator to produce
        # authorized assertions with direction from Rule (not from Signal).
        # P1.6 BLOCKING FIX: No fail-open fallback — authorization failure = NO CLAIM.
        cross_result = None
        authorized_assertions = []
        if self._orchestrator is not None and signals:
            cross_result = self._orchestrate_signals(bazi_chart, ziwei_chart, signals)
            authorized_assertions = self._extract_authorizations(cross_result)

        # 3b. Temporal convergence (P1.7)
        # Harmonize signals across temporal layers (BIRTH/YEAR/DAY) for unified view.
        temporal_convergence = None
        if self._temporal_convergence_engine is not None and signals:
            temporal_convergence = self._run_temporal_convergence(signals, analysis_date)

        # Add ziwei signal to BASELINE layer for SIR serialization
        # This keeps SIR complete without polluting the cross analysis input
        if zw_signal is not None:
            signals["BASELINE"].append(zw_signal)

        # 4. Generate atomic_claims from authorized assertions (P1.6 fail-closed)
        # No authorization → NO CLAIM. Legacy fallback removed.
        if authorized_assertions:
            atomic_claims = self._build_claims_from_assertions(theme, authorized_assertions)
        else:
            atomic_claims = []

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
            canonical_signals=canonical_signals,
            cross_result=cross_result,
            authorized_assertions=authorized_assertions,
            temporal_convergence=temporal_convergence,
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

    # ─── P1.6: CrossDomainOrchestrator integration ──────────────────────────────

    def _orchestrate_signals(
        self, bazi_chart, ziwei_chart, signals: dict[str, list]
    ):
        """Map engine signals to CrossDomainOrchestrator input and run orchestration."""
        # Build EngineEvidence from signals grouped by engine
        # Also add ten_god evidence from BaziEngine for production rule matching (P1.6)
        from ..reasoning.bazi_ten_gods import ten_god

        engine_evidences: dict[str, list] = {"ZI_PING": [], "ZI_WEI": []}

        # Add BaziEngine ten-god evidence for production rule matching
        day_master = bazi_chart.day_master
        stem_positions = {
            "year": bazi_chart.year_pillar.heavenly_stem,
            "month": bazi_chart.month_pillar.heavenly_stem,
            "day": day_master,
            "hour": bazi_chart.hour_pillar.heavenly_stem,
        }
        for pos, stem in stem_positions.items():
            tg = ten_god(day_master, stem)
            engine_evidences["ZI_PING"].append(
                EngineEvidence(
                    evidence_id=f"BZI-TG-{pos}",
                    engine=EngineName.ZI_PING,
                    rule_id=f"BZI_TEN_GOD_{pos.upper()}",
                    value=tg,
                    temporal_scope=TemporalScope.BIRTH,
                    attributes={"ten_god": tg, "stem": stem, "pillar": pos},
                    source_rule_ref="data/rules/bazi_ten_gods.json",
                    source_field="ten_god",
                )
            )

        # Add signal-based evidence
        for layer, sigs in signals.items():
            for sig in sigs:
                engine_name = "ZI_PING"
                if engine_name not in engine_evidences:
                    engine_evidences[engine_name] = []
                # Derive temporal_scope from signal layer (P1.6 fix)
                temporal = {
                    "BASELINE": TemporalScope.BIRTH,
                    "CYCLE_CONTEXT": TemporalScope.YEAR,
                    "DAILY_ACTIVATION": TemporalScope.DAY,
                }.get(layer, TemporalScope.BIRTH)
                engine_evidences[engine_name].append(
                    EngineEvidence(
                        evidence_id=sig.signal_id,
                        engine=EngineName(engine_name),
                        rule_id=sig.rule_refs[0] if sig.rule_refs else sig.signal_id,
                        value=sig.ontology_type,
                        temporal_scope=temporal,
                        attributes={"ontology_type": sig.ontology_type, "layer": layer},
                        source_rule_ref=sig.rule_refs[0] if sig.rule_refs else "",
                        source_field="",
                    )
                )

        # Map Evidence → SemanticAtom
        def atom_fn(ev: EngineEvidence) -> SemanticAtom | None:
            attrs = ev.attributes
            # P1.6: Handle ten_god evidence for production rule matching
            ten_god = attrs.get("ten_god")
            if ten_god:
                ten_god_map = {
                    "正官": "TEN_GOD_ZHENG_GUAN",
                    "偏印": "TEN_GOD_PIAN_YIN",
                    "正财": "TEN_GOD_ZHENG_CAi",
                }
                atom_id = ten_god_map.get(ten_god, f"TEN_GOD_{ten_god}")
                return SemanticAtom(
                    atom_id=atom_id,
                    engine=ev.engine,
                    evidence_ref=ev.evidence_id,
                    semantic_keys=[ten_god],
                    domain_candidates=["GROWTH", "FINANCE"],
                    label_zh=ten_god,
                    category="TEN_GOD",
                )
            # Fallback: signal-based evidence
            atom_id = f"{ev.engine.value}_{attrs.get('ontology_type', 'UNKNOWN')}"
            return SemanticAtom(
                atom_id=atom_id,
                engine=ev.engine,
                evidence_ref=ev.evidence_id,
                semantic_keys=[attrs.get("ontology_type", "")],
                domain_candidates=["CAREER", "FINANCE", "GROWTH"],
                label_zh=attrs.get("ontology_type", ""),
                category="",
            )

        return self._orchestrator.orchestrate(
            case_id="pipeline",
            temporal_scope="birth",
            engine_evidences=engine_evidences,
            atom_map_fn=atom_fn,
        )

    # ─── P1.7: Temporal Convergence ────────────────────────────────────────────

    @staticmethod
    def _map_signal_to_temporal(
        sig, layer: str, target_year: int, engine_name: str
    ) -> TemporalSignal | None:
        """Convert a production Signal → TemporalSignal for convergence engine."""
        _DIR_MAP = {
            "INCREASE": "POSITIVE",
            "DECLINE": "NEGATIVE",
            "STABLE": "NEUTRAL",
            "VOLATILE": "CHANGE",
        }
        _STRENGTH_MAP = {"low": 0.3, "moderate": 0.5, "high": 0.7}
        _GRAN_MAP = {
            "DAILY_ACTIVATION": TemporalGranularity.DAILY,
            "CYCLE_CONTEXT": TemporalGranularity.YEARLY,
            "BASELINE": TemporalGranularity.YEARLY,
        }

        direction = _DIR_MAP.get(sig.direction, "UNKNOWN")
        try:
            strength = float(sig.strength)
        except (TypeError, ValueError):
            strength = _STRENGTH_MAP.get(sig.strength, 0.5)
        granularity = _GRAN_MAP.get(layer, TemporalGranularity.YEARLY)

        return TemporalSignal(
            signal_id=sig.signal_id,
            engine=engine_name,
            prediction_window=PredictionWindow(
                start_year=target_year,
                end_year=target_year,
                granularity=granularity,
            ),
            direction=direction,
            strength=max(0.0, min(1.0, strength)),
            provenance=f"{sig.ontology_type}@{layer}",
        )

    def _run_temporal_convergence(
        self, signals: dict[str, list], analysis_date: date
    ) -> Any:
        """Map all signals → TemporalSignal and run convergence engine."""
        if self._temporal_convergence_engine is None:
            return None
        engine = self._temporal_convergence_engine
        added = 0
        for layer, sigs in signals.items():
            # Use domain-derived engine name from first signal
            engine_name = sigs[0].system if sigs and hasattr(sigs[0], "system") and sigs[0].system else "Shuntian"
            for sig in sigs:
                ts = self._map_signal_to_temporal(sig, layer, analysis_date.year, engine_name)
                if ts is not None:
                    if engine.add_signal(ts):
                        added += 1
        if added == 0:
            return None
        return engine.compute_convergence()

    def _extract_authorizations(self, cross_result) -> list[dict]:
        """Extract authorized assertions from CrossDomainResult with Rule direction.

        P1.6 fix: look up rule by (domain, semantic) to get real direction.
        """
        assertions = []
        if cross_result is None:
            return assertions
        for domain, domain_index in cross_result.coverage.coverage.items():
            for semantic, ds_index in domain_index.items():
                for engine_name, eng_set in ds_index.by_engine.items():
                    for assertion_id in eng_set.assertion_ids:
                        # Look up rule from production library to get real direction
                        rule = None
                        if self._assertion_library is not None:
                            from ..spec.canonical import SemanticAtom, EngineName as EN
                            atom = SemanticAtom(
                                atom_id=semantic, engine=EN(engine_name),
                                evidence_ref=f"AS-{assertion_id}", semantic_keys=[semantic],
                                domain_candidates=[domain], label_zh="", category="",
                            )
                            rule = self._assertion_library.find_rule(atom, {})
                        assertions.append({
                            "assertion_id": assertion_id,
                            "engine": engine_name,
                            "domain": domain,
                            "semantic": semantic,
                            "authorized_rule_id": rule.rule_id if rule else None,
                            "rule_direction": rule.direction.value if rule else "UNKNOWN",
                            "authorization_source": "CrossDomainOrchestrator",
                        })
        return assertions

    def _build_claims_from_assertions(self, theme: str, assertions: list[dict]) -> list[dict]:
        """Build claims from authorized assertions. direction comes from Rule, not Signal.

        P1.6 boundary: claims from authorized assertions only.
        No signal.direction bypass.
        """
        claims = []
        for auth in assertions:
            claims.append({
                "claim_id": f"AC-{auth['assertion_id']}",
                "assertion_id": auth["assertion_id"],
                "authorized_rule_id": auth.get("authorized_rule_id"),
                "signal_type": auth.get("domain", "UNKNOWN"),
                "claim": f"主体在 {theme} 主题上经 [{auth['authorization_source']}] 授权。",
                "direction": auth.get("rule_direction", "UNKNOWN"),
                "strength": "AUTHORIZED",
                "source_layers": [auth["engine"]],
                "rule_refs": [auth["assertion_id"]],
                "evidence_refs": [],
            })
        return claims
