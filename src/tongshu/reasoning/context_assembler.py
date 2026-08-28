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
from tongshu.engines.bazi_engine import BaziEngine


# 地支冲/合/害/刑/三合 映射
BRANCH_CLASH = {
    "ZI": "WU", "WU": "ZI",
    "CHOU": "WEI", "WEI": "CHOU",
    "YIN": "SHEN", "SHEN": "YIN",
    "MAO": "YOU", "YOU": "MAO",
    "CHEN": "XU", "XU": "CHEN",
    "SI": "HAI", "HAI": "SI",
}

BRANCH_COMBINATION = {
    "ZI": "CHOU", "CHOU": "ZI",
    "YIN": "HAI", "HAI": "YIN",
    "MAO": "XU", "XU": "MAO",
    "CHEN": "YOU", "YOU": "CHEN",
    "SI": "SHEN", "SHEN": "SI",
    "WU": "WEI", "WEI": "WU",
}

BRANCH_HARM = {
    "ZI": "WEI", "WEI": "ZI",
    "CHOU": "WU", "WU": "CHOU",
    "YIN": "SI", "SI": "YIN",
    "MAO": "CHEN", "CHEN": "MAO",
    "SHEN": "HAI", "HAI": "SHEN",
    "YOU": "XU", "XU": "YOU",
}

BRANCH_PUNISHMENT = {
    "YIN": "SI", "SI": "SHEN", "SHEN": "YIN",  # 无恩之刑
    "CHOU": "XU", "XU": "WEI", "WEI": "CHOU",  # 恃势之刑
    "ZI": "MAO", "MAO": "ZI",  # 无礼之刑
    "CHEN": "CHEN", "WU": "WU", "YOU": "YOU", "HAI": "HAI",  # 自刑
}

THREE_COMBINATION = {
    "SHEN": ("SHEN", "ZI", "CHEN"), "ZI": ("SHEN", "ZI", "CHEN"), "CHEN": ("SHEN", "ZI", "CHEN"),
    "HAI": ("HAI", "MAO", "WEI"), "MAO": ("HAI", "MAO", "WEI"), "WEI": ("HAI", "MAO", "WEI"),
    "YIN": ("YIN", "WU", "XU"), "WU": ("YIN", "WU", "XU"), "XU": ("YIN", "WU", "XU"),
    "SI": ("SI", "YOU", "CHOU"), "YOU": ("SI", "YOU", "CHOU"), "CHOU": ("SI", "YOU", "CHOU"),
}

# 天干五行
STEM_ELEMENT = {
    "JIA": "WOOD", "YI": "WOOD",
    "BING": "FIRE", "DING": "FIRE",
    "WU": "EARTH", "JI": "EARTH",
    "GENG": "METAL", "XIN": "METAL",
    "REN": "WATER", "GUI": "WATER",
}

# 地支五行
BRANCH_ELEMENT = {
    "YIN": "WOOD", "MAO": "WOOD",
    "SI": "FIRE", "WU": "FIRE",
    "CHEN": "EARTH", "XU": "EARTH", "CHOU": "EARTH", "WEI": "EARTH",
    "SHEN": "METAL", "YOU": "METAL",
    "HAI": "WATER", "ZI": "WATER",
}

# 天干数 (河图洛书)
STEM_NUMBER = {
    "JIA": 1, "YI": 2, "BING": 3, "DING": 4,
    "WU": 5, "JI": 6, "GENG": 7, "XIN": 8,
    "REN": 9, "GUI": 10,
}

HEAVENLY_STEMS = ["JIA", "YI", "BING", "DING", "WU", "JI", "GENG", "XIN", "REN", "GUI"]
EARTHLY_BRANCHES = ["ZI", "CHOU", "YIN", "MAO", "CHEN", "SI", "WU", "WEI", "SHEN", "YOU", "XU", "HAI"]


def compute_year_pillar(year: int) -> tuple[str, str]:
    """计算流年干支 (1984甲子年基准)."""
    base_year = 1984
    offset = year - base_year
    stem_idx = offset % 10
    branch_idx = offset % 12
    return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]


def compute_ten_god(day_master: str, other_stem: str) -> str:
    """计算十神."""
    from tongshu.reasoning.temporal_context_contract import TEN_GOD_CANDIDATE_KEYS
    # 简化: 用已知的十神映射
    # 这里直接从BaziEngine的逻辑推导
    dm_element = STEM_ELEMENT[day_master]
    other_element = STEM_ELEMENT[other_stem]
    dm_yin_yang = STEM_NUMBER[day_master] % 2  # 1=阳, 0=阴
    other_yin_yang = STEM_NUMBER[other_stem] % 2

    # 五行生克关系
    element_generate = {"WOOD": "FIRE", "FIRE": "EARTH", "EARTH": "METAL", "METAL": "WATER", "WATER": "WOOD"}
    element_control = {"WOOD": "EARTH", "EARTH": "WATER", "WATER": "FIRE", "FIRE": "METAL", "METAL": "WOOD"}

    if dm_element == other_element:
        # 同我者: 比劫
        if dm_yin_yang == other_yin_yang:
            return "BIJIAN"
        else:
            return "JIECAI"
    elif element_generate[dm_element] == other_element:
        # 我生者: 食伤
        if dm_yin_yang == other_yin_yang:
            return "SHISHEN"
        else:
            return "SHANGGUAN"
    elif element_control[dm_element] == other_element:
        # 我克者: 财
        if dm_yin_yang == other_yin_yang:
            return "PIANCAI"
        else:
            return "ZHENGCAI"
    elif element_control[other_element] == dm_element:
        # 克我者: 官杀
        if dm_yin_yang == other_yin_yang:
            return "QISHA"
        else:
            return "ZHENGGUAN"
    elif element_generate[other_element] == dm_element:
        # 生我者: 印
        if dm_yin_yang == other_yin_yang:
            return "PIANYIN"
        else:
            return "ZHENGYIN"
    return "UNKNOWN"


class ContextAssembler:
    """Context Assembler - 把Natal + DaYun + Year + DerivedSignals组装成TemporalContext."""

    def __init__(self):
        self.bazi_engine = BaziEngine()

    def assemble_natal_context(self, chart, birth_year: int, gender: str) -> NatalContext:
        """组装NatalContext."""

        # 四柱
        pillars = [
            NatalPillar(
                position="YEAR",
                heavenly_stem=chart.year_pillar.heavenly_stem,
                earthly_branch=chart.year_pillar.earthly_branch,
                stem_ten_god=compute_ten_god(chart.day_master, chart.year_pillar.heavenly_stem),
            ),
            NatalPillar(
                position="MONTH",
                heavenly_stem=chart.month_pillar.heavenly_stem,
                earthly_branch=chart.month_pillar.earthly_branch,
                stem_ten_god=compute_ten_god(chart.day_master, chart.month_pillar.heavenly_stem),
            ),
            NatalPillar(
                position="DAY",
                heavenly_stem=chart.day_pillar.heavenly_stem,
                earthly_branch=chart.day_pillar.earthly_branch,
                stem_ten_god="DAY_MASTER",
            ),
            NatalPillar(
                position="HOUR",
                heavenly_stem=chart.hour_pillar.heavenly_stem,
                earthly_branch=chart.hour_pillar.earthly_branch,
                stem_ten_god=compute_ten_god(chart.day_master, chart.hour_pillar.heavenly_stem),
            ),
        ]

        branches = [p.earthly_branch for p in pillars]

        # 地支关系
        branch_clashes = []
        branch_combinations = []
        branch_harms = []
        branch_punishments = []
        branch_three_combinations = []

        for i, b1 in enumerate(branches):
            for j, b2 in enumerate(branches):
                if i >= j:
                    continue
                pair = f"{b1}-{b2}"
                if BRANCH_CLASH.get(b1) == b2:
                    branch_clashes.append(pair)
                if BRANCH_COMBINATION.get(b1) == b2:
                    branch_combinations.append(pair)
                if BRANCH_HARM.get(b1) == b2:
                    branch_harms.append(pair)

        # 三合
        for combo in set(THREE_COMBINATION.values()):
            if all(b in branches for b in combo):
                branch_three_combinations.append("-".join(combo))

        # 十神分布
        ten_god_distribution = {}
        for p in pillars:
            if p.stem_ten_god and p.stem_ten_god != "DAY_MASTER":
                ten_god_distribution[p.stem_ten_god] = ten_god_distribution.get(p.stem_ten_god, 0) + 1

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
            day_master_strength=getattr(chart, 'day_master_strength', 'MODERATE'),
            ten_god_distribution=ten_god_distribution,
            structural_features=getattr(chart, 'structural_features', []),
        )

    def assemble_dayun_context(self, chart, natal: NatalContext, target_year: int) -> DaYunContext:
        """组装DaYunContext."""
        # 自己计算大运 (不依赖chart.luck_pillars数量)
        # 阳男阴女顺排, 阴男阳女逆排
        year_stem = natal.pillars[0].heavenly_stem  # 年干
        is_yang_year = STEM_NUMBER[year_stem] % 2 == 1  # 阳年
        is_male = natal.gender == "male"

        # 顺排: 阳男/阴女; 逆排: 阴男/阳女
        is_forward = (is_yang_year and is_male) or (not is_yang_year and not is_male)

        # 从月柱开始
        month_stem = natal.pillars[1].heavenly_stem
        month_branch = natal.pillars[1].earthly_branch
        month_stem_idx = HEAVENLY_STEMS.index(month_stem)
        month_branch_idx = EARTHLY_BRANCHES.index(month_branch)

        start_age = getattr(chart, 'start_age', 0.0)

        # 计算12个大运 (覆盖到120岁, 避免target_year超出范围)
        da_yun_pillars = []
        for i in range(12):
            if is_forward:
                stem_idx = (month_stem_idx + 1 + i) % 10
                branch_idx = (month_branch_idx + 1 + i) % 12
            else:
                stem_idx = (month_stem_idx - 1 - i) % 10
                branch_idx = (month_branch_idx - 1 - i) % 12

            stem = HEAVENLY_STEMS[stem_idx]
            branch = EARTHLY_BRANCHES[branch_idx]

            pillar_start_age = start_age + i * 10
            pillar_end_age = pillar_start_age + 10
            pillar_start_year = natal.birth_year + int(pillar_start_age)
            pillar_end_year = natal.birth_year + int(pillar_end_age)

            is_current = pillar_start_year <= target_year < pillar_end_year

            da_yun_pillars.append(DaYunPillar(
                index=i,
                heavenly_stem=stem,
                earthly_branch=branch,
                start_age=pillar_start_age,
                end_age=pillar_end_age,
                start_year=pillar_start_year,
                end_year=pillar_end_year,
                stem_ten_god=compute_ten_god(natal.day_master, stem),
                is_current=is_current,
            ))

        current = next((p for p in da_yun_pillars if p.is_current), None)
        current_idx = da_yun_pillars.index(current) if current else 0
        previous = da_yun_pillars[current_idx - 1] if current_idx > 0 else None
        next_dy = da_yun_pillars[current_idx + 1] if current_idx + 1 < len(da_yun_pillars) else None

        # 起运前判断
        first_luck_start_year = natal.birth_year + int(start_age) if da_yun_pillars else None
        is_pre_luck = target_year < first_luck_start_year if first_luck_start_year else False

        # Natal × Da Yun 交互
        natal_branches = [p.earthly_branch for p in natal.pillars]
        natal_dayun_clashes = []
        natal_dayun_combinations = []

        if current:
            for nb in natal_branches:
                if BRANCH_CLASH.get(current.earthly_branch) == nb:
                    natal_dayun_clashes.append(f"{current.earthly_branch}-{nb}")
                if BRANCH_COMBINATION.get(current.earthly_branch) == nb:
                    natal_dayun_combinations.append(f"{current.earthly_branch}-{nb}")

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
            is_transition_period=is_transition,
            transition_start_year=transition_start,
            transition_end_year=transition_end,
            is_pre_luck_period=is_pre_luck,
            first_luck_start_year=first_luck_start_year,
        )

    def assemble_year_context(self, natal: NatalContext, dayun: DaYunContext,
                               target_year: int) -> YearContext:
        """组装YearContext."""
        year_stem, year_branch = compute_year_pillar(target_year)
        year_stem_ten_god = compute_ten_god(natal.day_master, year_stem)

        natal_branches = [p.earthly_branch for p in natal.pillars]

        # Natal × Year 交互
        natal_year_clashes = []
        natal_year_combinations = []
        natal_year_harms = []
        natal_year_fuyin = []

        for nb in natal_branches:
            if BRANCH_CLASH.get(year_branch) == nb:
                natal_year_clashes.append(f"{year_branch}-{nb}")
            if BRANCH_COMBINATION.get(year_branch) == nb:
                natal_year_combinations.append(f"{year_branch}-{nb}")
            if BRANCH_HARM.get(year_branch) == nb:
                natal_year_harms.append(f"{year_branch}-{nb}")
            if year_branch == nb:
                natal_year_fuyin.append(f"{year_branch}-{nb}")

        # Da Yun × Year 交互
        dayun_year_clashes = []
        dayun_year_combinations = []
        dayun_year_fuyin = []

        if dayun.current_da_yun:
            dy_branch = dayun.current_da_yun.earthly_branch
            if BRANCH_CLASH.get(year_branch) == dy_branch:
                dayun_year_clashes.append(f"{year_branch}-{dy_branch}")
            if BRANCH_COMBINATION.get(year_branch) == dy_branch:
                dayun_year_combinations.append(f"{year_branch}-{dy_branch}")
            if year_branch == dy_branch:
                dayun_year_fuyin.append(f"{year_branch}-{dy_branch}")

        # 三层交互 (三合局完成等)
        three_layer_interactions = []
        all_branches = natal_branches + [year_branch]
        if dayun.current_da_yun:
            all_branches.append(dayun.current_da_yun.earthly_branch)

        for combo in set(THREE_COMBINATION.values()):
            if all(b in all_branches for b in combo):
                three_layer_interactions.append(f"THREE_COMBINATION:{'-'.join(combo)}")

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

    def assemble(self, case_id: str, birth_year: int, birth_month: int,
                 birth_day: int, birth_hour: int, gender: str,
                 target_year: int) -> TemporalContext:
        """完整组装TemporalContext."""
        # 0. 只调用一次BaziEngine
        chart = self.bazi_engine.compute((birth_year, birth_month, birth_day, birth_hour), gender)

        # 1. Natal
        natal = self.assemble_natal_context(chart, birth_year, gender)

        # 2. Da Yun
        dayun = self.assemble_dayun_context(chart, natal, target_year)

        # 3. Year
        year = self.assemble_year_context(natal, dayun, target_year)

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

    assembler = ContextAssembler()

    # 测试1983案例
    ctx = assembler.assemble(
        case_id="TEST-001",
        birth_year=1983,
        birth_month=11,
        birth_day=3,
        birth_hour=12,
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
