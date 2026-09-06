"""P6-C-3B: Context Assembly.

严格按P6-C-3A已冻结的Contract做Context Assembly.
不回头修改Semantic/Assertion架构.

核心目标:
Natal + DaYun + Year + DerivedSignals → TemporalContext
对513 events做完整组装, Context completeness = 100%

禁止:
- 不修改十神计算
- 不改变V2 Baseline
- 不改变Ground Truth
- 不做direction
- 不做吉凶判断
- 不做十神→Domain
- 不做跨体系投票
- 不调precision/F1参数
- 不让LLM参与
"""
from __future__ import annotations
import json
import sys
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
sys.path.insert(0, "src")

from tongshu.reasoning.temporal_context_contract import (
    TemporalContext, NatalContext, DaYunContext, YearContext,
    DerivedSignal, SignalProvenance, SignalSource, TemporalLayer,
    SignalPolarity, SignalStrength, NatalPillar, DaYunPillar,
    TEN_GOD_CANDIDATE_KEYS, BRANCH_RELATION_CANDIDATE_KEYS,
    ContractValidator,
)


HEAVENLY_STEMS = ["JIA", "YI", "BING", "DING", "WU", "JI", "GENG", "XIN", "REN", "GUI"]
EARTHLY_BRANCHES = ["ZI", "CHOU", "YIN", "MAO", "CHEN", "SI", "WU", "WEI", "SHEN", "YOU", "XU", "HAI"]


class ContextAssembler:
    """Context Assembler - 把Natal + DaYun + Year + DerivedSignals组装成TemporalContext.

    P0-1-C-FIX-2: ZIPING 不再计算确定性的 BAZI 事实.
    - Ten-God: consumed from chart.*.stem_ten_god
    - Branch Relations: consumed from chart.branch_*_map
    - Year Pillar: consumed from BAZI/Temporal Engine
    - DaYun: consumed from chart.luck_pillars
    """

    def __init__(self):
        # P0-1-C-FIX-2: No bazi_engine dependency - ZIPING only consumes
        pass

    def assemble_natal_context(self, chart, birth_year: int, gender: str) -> NatalContext:
        """组装NatalContext."""

        # 四柱 - 直接消费 BAZI 字段
        pillars = [
            NatalPillar(
                position="YEAR",
                heavenly_stem=chart.year_pillar.heavenly_stem,
                earthly_branch=chart.year_pillar.earthly_branch,
                stem_ten_god=chart.year_pillar.stem_ten_god,
            ),
            NatalPillar(
                position="MONTH",
                heavenly_stem=chart.month_pillar.heavenly_stem,
                earthly_branch=chart.month_pillar.earthly_branch,
                stem_ten_god=chart.month_pillar.stem_ten_god,
            ),
            NatalPillar(
                position="DAY",
                heavenly_stem=chart.day_pillar.heavenly_stem,
                earthly_branch=chart.day_pillar.earthly_branch,
                stem_ten_god=chart.day_pillar.stem_ten_god,
            ),
            NatalPillar(
                position="HOUR",
                heavenly_stem=chart.hour_pillar.heavenly_stem,
                earthly_branch=chart.hour_pillar.earthly_branch,
                stem_ten_god=chart.hour_pillar.stem_ten_god,
            ),
        ]

        branches = [p.earthly_branch for p in pillars]

        # P0-1-C-FIX-2: Branch relations - 消费 BAZI fields, no re-calculation
        branch_clashes = list(getattr(chart, 'branch_clash_map', {}).keys())
        branch_combinations = list(getattr(chart, 'branch_he_map', {}).keys())
        branch_harms = list(getattr(chart, 'branch_harm_map', {}).keys())
        branch_punishments = []  # TODO: add branch_sanxing_map to BAZI
        branch_three_combinations = list(getattr(chart, 'branch_sanhe_map', {}).keys())

        # 十神分布
        ten_god_distribution = {}
        for p in pillars:
            if p.stem_ten_god and p.stem_ten_god != "DAY_MASTER":
                ten_god_distribution[p.stem_ten_god] = ten_god_distribution.get(p.stem_ten_god, 0) + 1

        # P0 修复: fail-closed，缺失时报错而非静默使用默认值
        _dm_strength = getattr(chart, 'day_master_strength', None)
        if _dm_strength is None:
            raise ValueError(
                f"day_master_strength 未计算。"
                f"日主强度是辨证核心，必须在 BaziEngine 中计算或明确标记为 MISSING。"
                f"当前日主: {chart.day_master}"
            )

        return NatalContext(
            day_master=chart.day_master,
            gender=gender,
            birth_year=birth_year,
            pillars=pillars,
            branch_clashes=branch_clashes,
            branch_combinations=branch_combinations,
            branch_harms=branch_harms,
            branch_punishments=branch_punishments,
            branch_three_combinations=branch_three_combinations,
            day_master_strength=_dm_strength,
            ten_god_distribution=ten_god_distribution,
            structural_features=getattr(chart, 'structural_features', []),
        )

    def assemble_dayun_context(self, chart, natal: NatalContext, target_year: int) -> DaYunContext:
        """组装DaYunContext - 消费 BAZI 已有大运列表."""
        start_age = getattr(chart, 'start_age', 0.0)

        # 消费 BAZI 已有大运列表 (不重新计算)
        da_yun_pillars = []
        for luck in chart.luck_pillars:
            pillar_start_age = getattr(luck, 'start_age', None)
            if pillar_start_age is None:
                pillar_start_age = start_age + len(da_yun_pillars) * 10
            pillar_end_age = pillar_start_age + 10
            pillar_start_year = natal.birth_year + int(pillar_start_age)
            pillar_end_year = natal.birth_year + int(pillar_end_age)
            is_current = pillar_start_year <= target_year < pillar_end_year

            da_yun_pillars.append(DaYunPillar(
                index=len(da_yun_pillars),
                heavenly_stem=luck.heavenly_stem,
                earthly_branch=luck.earthly_branch,
                start_age=pillar_start_age,
                end_age=pillar_end_age,
                start_year=pillar_start_year,
                end_year=pillar_end_year,
                stem_ten_god=getattr(luck, 'stem_ten_god', ''),  # 消费 BAZI 字段
                is_current=is_current,
            ))

        current = next((p for p in da_yun_pillars if p.is_current), None)
        current_idx = da_yun_pillars.index(current) if current else 0
        previous = da_yun_pillars[current_idx - 1] if current_idx > 0 else None
        next_dy = da_yun_pillars[current_idx + 1] if current_idx + 1 < len(da_yun_pillars) else None

        # 起运前判断
        first_luck_start_year = natal.birth_year + int(start_age) if da_yun_pillars else None
        is_pre_luck = target_year < first_luck_start_year if first_luck_start_year else False

        # P0-1-C-FIX-2: Natal × Da Yun 交互 - 消费 BAZI branch_clash_map, tidak re-calculate
        natal_branches = [p.earthly_branch for p in natal.pillars]
        natal_dayun_clashes = []
        natal_dayun_combinations = []
        natal_dayun_harms = []

        if current:
            dy_branch = current.earthly_branch
            # Use BAZI branch_clash_map
            clash_map = getattr(chart, 'branch_clash_map', {})
            for key, branches in clash_map.items():
                if dy_branch in branches:
                    other = [b for b in branches if b != dy_branch][0] if len(branches) > 1 else None
                    if other and other in natal_branches:
                        natal_dayun_clashes.append(f"{dy_branch}-{other}")

            # Use BAZI branch_he_map
            he_map = getattr(chart, 'branch_he_map', {})
            for key, data in he_map.items():
                if isinstance(data, list) and dy_branch in data:
                    other = [b for b in data if b != dy_branch][:1]
                    if other and other[0] in natal_branches:
                        natal_dayun_combinations.append(f"{dy_branch}-{other[0]}")

            # Use BAZI branch_harm_map
            harm_map = getattr(chart, 'branch_harm_map', {})
            for key, branches in harm_map.items():
                if dy_branch in branches:
                    other = [b for b in branches if b != dy_branch][0] if len(branches) > 1 else None
                    if other and other in natal_branches:
                        natal_dayun_harms.append(f"{dy_branch}-{other}")

        # 换运期
        is_transition = False
        transition_start = None
        transition_end = None
        if current:
            # 换运期前后2年
            if abs(target_year - current.start_year) <= 2:
                is_transition = True
                transition_start = current.start_year - 2
                transition_end = current.start_year + 2

        return DaYunContext(
            current_da_yun=current,
            previous_da_yun=previous,
            next_da_yun=next_dy,
            all_da_yun=da_yun_pillars,
            natal_dayun_clashes=natal_dayun_clashes,
            natal_dayun_combinations=natal_dayun_combinations,
            natal_dayun_harms=natal_dayun_harms,
            is_transition_period=is_transition,
            transition_start_year=transition_start,
            transition_end_year=transition_end,
            is_pre_luck_period=is_pre_luck,
            first_luck_start_year=first_luck_start_year,
        )

    def assemble_year_context(self, natal: NatalContext, dayun: DaYunContext,
                               chart, target_year: int) -> YearContext:
        """组装YearContext - 流年干支由 BAZI/Temporal Engine 提供，此处仅消费.

        P0-1-C-FIX-2: ZIPING 不再计算流年干支.
        P0-1-C-FIX-3: 强制 fail-closed，year_pillar 缺失时直接报错.
        TODO: Phase 2 (BOT-TIME) - implement proper temporal engine.
        """
        # P0-1-C: 流年干支应由 BAZI/Temporal Engine 计算
        # 当前 consuming chart.year_pillar
        # TODO: Replace with TemporalContext.target_year_pillar after Phase 2
        year_pillar = getattr(chart, 'year_pillar', None)

        # P0-1-C-FIX-3: 强制要求 year_pillar 存在，不允许 fallback 计算
        if year_pillar is None:
            raise ValueError(
                "chart.year_pillar 不能为 None。\n"
                "流年干支是确定性事实，必须由 BAZI/Temporal Engine 计算后传入。\n"
                "ZIPING 不拥有 Year Pillar 的计算权。"
            )

        year_stem = year_pillar.heavenly_stem
        year_branch = year_pillar.earthly_branch
        year_stem_ten_god = year_pillar.stem_ten_god

        natal_branches = [p.earthly_branch for p in natal.pillars]

        # P0-1-C-FIX-2: Natal × Year 交互 - 消费 BAZI branch_clash_map, tidak re-calculate
        natal_year_clashes = []
        natal_year_combinations = []
        natal_year_harms = []
        natal_year_fuyin = []

        # Use BAZI branch_clash_map for natal-year clashes
        clash_map = getattr(chart, 'branch_clash_map', {})
        for key, branches in clash_map.items():
            if year_branch in branches:
                other = [b for b in branches if b != year_branch][0] if len(branches) > 1 else None
                if other and other in natal_branches:
                    natal_year_clashes.append(f"{year_branch}-{other}")

        # Use BAZI branch_he_map for combinations
        he_map = getattr(chart, 'branch_he_map', {})
        for key, data in he_map.items():
            if isinstance(data, list) and year_branch in data:
                other = [b for b in data if b != year_branch][:1]
                if other and other[0] in natal_branches:
                    natal_year_combinations.append(f"{year_branch}-{other[0]}")

        # Use BAZI branch_harm_map for harms
        harm_map = getattr(chart, 'branch_harm_map', {})
        for key, branches in harm_map.items():
            if year_branch in branches:
                other = [b for b in branches if b != year_branch][0] if len(branches) > 1 else None
                if other and other in natal_branches:
                    natal_year_harms.append(f"{year_branch}-{other}")

        # Fuyin (same branch)
        natal_year_fuyin = [f"{year_branch}-{nb}" for nb in natal_branches if nb == year_branch]

        # P0-1-C-FIX-2: Da Yun × Year 交互 - 消费 BAZI branch relations
        dayun_year_clashes = []
        dayun_year_combinations = []
        dayun_year_harms = []
        dayun_year_fuyin = []

        if dayun.current_da_yun:
            dy_branch = dayun.current_da_yun.earthly_branch

            # Use BAZI branch_clash_map
            for key, branches in clash_map.items():
                if year_branch in branches:
                    other = [b for b in branches if b != year_branch][0] if len(branches) > 1 else None
                    if other == dy_branch:
                        dayun_year_clashes.append(f"{year_branch}-{dy_branch}")

            # Use BAZI branch_he_map
            for key, data in he_map.items():
                if isinstance(data, list) and year_branch in data:
                    other = [b for b in data if b != year_branch][:1]
                    if other and other[0] == dy_branch:
                        dayun_year_combinations.append(f"{year_branch}-{dy_branch}")

            # Use BAZI branch_harm_map
            for key, branches in harm_map.items():
                if year_branch in branches:
                    other = [b for b in branches if b != year_branch][0] if len(branches) > 1 else None
                    if other == dy_branch:
                        dayun_year_harms.append(f"{year_branch}-{dy_branch}")

            # Fuyin
            if year_branch == dy_branch:
                dayun_year_fuyin.append(f"{year_branch}-{dy_branch}")

        # P0-1-C-FIX-2: Three-layer interactions - 消费 BAZI branch_sanhe_map
        three_layer_interactions = []
        all_branches = natal_branches + [year_branch]
        if dayun.current_da_yun:
            all_branches.append(dayun.current_da_yun.earthly_branch)

        # Use BAZI branch_sanhe_map for three combinations
        sanhe_map = getattr(chart, 'branch_sanhe_map', {})
        for key, data in sanhe_map.items():
            if isinstance(data, list) and len(data) >= 3:
                if all(b in all_branches for b in data[:3]):
                    three_layer_interactions.append(f"THREE_COMBINATION:{'-'.join(data[:3])}")

        return YearContext(
            target_year=target_year,
            year_stem=year_stem,
            year_branch=year_branch,
            year_stem_ten_god=year_stem_ten_god,
            natal_year_clashes=natal_year_clashes,
            natal_year_combinations=natal_year_combinations,
            natal_year_harms=natal_year_harms,
            natal_year_fuyin=natal_year_fuyin,
            dayun_year_clashes=dayun_year_clashes,
            dayun_year_combinations=dayun_year_combinations,
            dayun_year_harms=dayun_year_harms,
            dayun_year_fuyin=dayun_year_fuyin,
            three_layer_interactions=three_layer_interactions,
        )

    def generate_derived_signals(self, natal: NatalContext, dayun: DaYunContext,
                                   year: YearContext, case_id: str,
                                   target_year: int) -> list[DerivedSignal]:
        """生成DerivedSignals - 带provenance."""
        signals = []
        signal_counter = 0

        def make_signal_id():
            nonlocal signal_counter
            signal_counter += 1
            return f"{case_id}-{target_year}-SIG{signal_counter:03d}"

        # 1. 流年十神信号
        tg = year.year_stem_ten_god
        if tg in TEN_GOD_CANDIDATE_KEYS:
            info = TEN_GOD_CANDIDATE_KEYS[tg]
            signals.append(DerivedSignal(
                signal_id=make_signal_id(),
                source=SignalSource.TEN_GOD,
                value=tg,
                label_zh=info["label_zh"],
                temporal_layer=TemporalLayer.YEAR,
                subject="YEAR_STEM",
                object=year.year_stem,
                polarity=info["polarity"],
                strength=SignalStrength.MODERATE,
                semantic_keys=info["semantic_keys"],
                provenance=SignalProvenance(
                    source_engine="ZI_PING",
                    source_rule_id=f"BZA_TEN_GOD_{tg.upper()}",
                    temporal_layer=TemporalLayer.YEAR,
                    derivation_chain=["YEAR_STEM_CALCULATION", "TEN_GOD_DERIVATION"],
                ),
            ))

        # 2. 流年与本命冲
        for clash in year.natal_year_clashes:
            signals.append(DerivedSignal(
                signal_id=make_signal_id(),
                source=SignalSource.BRANCH_RELATION,
                value="CLASH",
                label_zh="冲",
                temporal_layer=TemporalLayer.INTERACTION,
                subject="YEAR_BRANCH",
                object=clash.split("-")[1],
                polarity=SignalPolarity.CONFLICTING,
                strength=SignalStrength.STRONG,
                participants=clash.split("-"),
                semantic_keys=BRANCH_RELATION_CANDIDATE_KEYS["CLASH"]["semantic_keys"],
                provenance=SignalProvenance(
                    source_engine="ZI_PING",
                    source_rule_id="BZA_BRANCH_CLASH",
                    temporal_layer=TemporalLayer.INTERACTION,
                    derivation_chain=["YEAR_BRANCH_CALCULATION", "BRANCH_CLASH_DETECTION"],
                ),
            ))

        # 3. 流年与本命合
        for combo in year.natal_year_combinations:
            signals.append(DerivedSignal(
                signal_id=make_signal_id(),
                source=SignalSource.BRANCH_RELATION,
                value="COMBINATION",
                label_zh="合",
                temporal_layer=TemporalLayer.INTERACTION,
                subject="YEAR_BRANCH",
                object=combo.split("-")[1],
                polarity=SignalPolarity.CONNECTING,
                strength=SignalStrength.MODERATE,
                participants=combo.split("-"),
                semantic_keys=BRANCH_RELATION_CANDIDATE_KEYS["COMBINATION"]["semantic_keys"],
                provenance=SignalProvenance(
                    source_engine="ZI_PING",
                    source_rule_id="BZA_BRANCH_COMBINATION",
                    temporal_layer=TemporalLayer.INTERACTION,
                    derivation_chain=["YEAR_BRANCH_CALCULATION", "BRANCH_COMBINATION_DETECTION"],
                ),
            ))

        # 4. 流年与本命伏吟
        for fuyin in year.natal_year_fuyin:
            signals.append(DerivedSignal(
                signal_id=make_signal_id(),
                source=SignalSource.BRANCH_RELATION,
                value="FUYIN",
                label_zh="伏吟",
                temporal_layer=TemporalLayer.INTERACTION,
                subject="YEAR_BRANCH",
                object=fuyin.split("-")[1],
                polarity=SignalPolarity.REPEATING,
                strength=SignalStrength.MODERATE,
                participants=fuyin.split("-"),
                semantic_keys=BRANCH_RELATION_CANDIDATE_KEYS["FUYIN"]["semantic_keys"],
                provenance=SignalProvenance(
                    source_engine="ZI_PING",
                    source_rule_id="BZA_BRANCH_FUYIN",
                    temporal_layer=TemporalLayer.INTERACTION,
                    derivation_chain=["YEAR_BRANCH_CALCULATION", "BRANCH_FUYIN_DETECTION"],
                ),
            ))

        # 5. 大运十神信号
        if dayun.current_da_yun and dayun.current_da_yun.stem_ten_god:
            dy_tg = dayun.current_da_yun.stem_ten_god
            if dy_tg in TEN_GOD_CANDIDATE_KEYS:
                info = TEN_GOD_CANDIDATE_KEYS[dy_tg]
                signals.append(DerivedSignal(
                    signal_id=make_signal_id(),
                    source=SignalSource.DA_YUN,
                    value=dy_tg,
                    label_zh=f"大运{info['label_zh']}",
                    temporal_layer=TemporalLayer.DA_YUN,
                    subject="DAYUN_STEM",
                    object=dayun.current_da_yun.heavenly_stem,
                    polarity=info["polarity"],
                    strength=SignalStrength.STRONG,
                    semantic_keys=info["semantic_keys"],
                    provenance=SignalProvenance(
                        source_engine="ZI_PING",
                        source_rule_id=f"BZA_DAYUN_TEN_GOD_{dy_tg.upper()}",
                        temporal_layer=TemporalLayer.DA_YUN,
                        derivation_chain=["DAYUN_CALCULATION", "TEN_GOD_DERIVATION"],
                    ),
                ))

        # 6. 三层交互 (三合局)
        for interaction in year.three_layer_interactions:
            signals.append(DerivedSignal(
                signal_id=make_signal_id(),
                source=SignalSource.BRANCH_RELATION,
                value="THREE_COMBINATION",
                label_zh="三合",
                temporal_layer=TemporalLayer.INTERACTION,
                subject="THREE_LAYER",
                object=interaction,
                polarity=SignalPolarity.TRANSFORMING,
                strength=SignalStrength.DOMINANT,
                participants=interaction.replace("THREE_COMBINATION:", "").split("-"),
                semantic_keys=BRANCH_RELATION_CANDIDATE_KEYS["THREE_COMBINATION"]["semantic_keys"],
                provenance=SignalProvenance(
                    source_engine="ZI_PING",
                    source_rule_id="BZA_THREE_COMBINATION",
                    temporal_layer=TemporalLayer.INTERACTION,
                    derivation_chain=["NATAL_BRANCHES", "DAYUN_BRANCH", "YEAR_BRANCH", "THREE_COMBINATION_DETECTION"],
                ),
            ))

        return signals

    def assemble(self, case_id: str, chart, gender: str,
                 target_year: int) -> TemporalContext:
        """完整组装TemporalContext.

        注意: chart 必须由外部提供（如 ComputeStage），不得在 ZIPING 内重新排盘。
        """
        # 0. 直接使用传入的 chart，禁止重新排盘
        assert chart is not None, "chart 不能为 None，必须由 BAZI Engine 计算后传入"

        # 从 Frozen Chart 获取 birth_year（禁止重新接收出生信息）
        birth_year = chart.birth_datetime.year if chart.birth_datetime else None
        assert birth_year is not None, "birth_year 必须从 chart.birth_datetime 获取"

        # 1. Natal
        natal = self.assemble_natal_context(chart, birth_year, gender)

        # 2. Da Yun
        dayun = self.assemble_dayun_context(chart, natal, target_year)

        # 3. Year
        year = self.assemble_year_context(natal, dayun, chart, target_year)

        # 4. Derived Signals
        derived_signals = self.generate_derived_signals(natal, dayun, year, case_id, target_year)

        # 5. 组装
        ctx = TemporalContext(
            case_id=case_id,
            target_year=target_year,
            natal=natal,
            da_yun=dayun,
            year=year,
            derived_signals=derived_signals,
            context_version="1.0.0",
            assembly_timestamp=datetime.now().isoformat(),
        )

        # 6. 计算completeness_score (frozen dataclass需要用object.__setattr__)
        validation = ContractValidator.validate_temporal_context(ctx)
        object.__setattr__(ctx, 'completeness_score', validation["completeness_score"])

        return ctx


if __name__ == "__main__":
    # 快速测试
    print("P6-C-3B Context Assembler - 快速测试")
    print("=" * 60)

    # 先调用 BaziEngine 计算 chart
    from tongshu.engines.bazi_engine import canonical_bazi_engine
    chart = canonical_bazi_engine.compute((1983, 11, 3, 12), "male")

    assembler = ContextAssembler()

    # 测试1983案例 - 传入已计算的 chart
    ctx = assembler.assemble(
        case_id="TEST-001",
        chart=chart,
        gender="male",
        target_year=2026,
    )

    print(f"\nCase: {ctx.case_id}, Target Year: {ctx.target_year}")
    print(f"Day Master: {ctx.natal.day_master}")
    print(f"Current Da Yun: {ctx.da_yun.current_da_yun.heavenly_stem if ctx.da_yun.current_da_yun else 'None'}")
    print(f"Year Pillar: {ctx.year.year_stem}{ctx.year.year_branch}")
    print(f"Year Ten God: {ctx.year.year_stem_ten_god}")
    print(f"Derived Signals: {len(ctx.derived_signals)}")
    print(f"Completeness Score: {ctx.completeness_score}")

    # 验证
    validation = ContractValidator.validate_temporal_context(ctx)
    print(f"\nValidation: valid={validation['valid']}, errors={validation['error_count']}")
    if validation['errors']:
        for e in validation['errors'][:5]:
            print(f"  - {e}")

    # 打印signals
    print(f"\nDerived Signals:")
    for sig in ctx.derived_signals:
        print(f"  {sig.signal_id}: {sig.label_zh} ({sig.value}) layer={sig.temporal_layer.value} polarity={sig.polarity.value}")
        print(f"    semantic_keys: {sig.semantic_keys}")
        print(f"    provenance: {sig.provenance.source_engine}/{sig.provenance.source_rule_id}")
