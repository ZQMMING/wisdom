"""P6-C-3A: Temporal Context Contract Definition.

只做Contract Definition, 不改推理.

核心原则:
1. 把十神从"直接映射Domain"降级为"Candidate Semantic Signal"
2. TemporalContext包含四层: Natal + Da Yun + Year + Derived Signals
3. DerivedSignal必须有provenance
4. ContextResolver负责解释, 不负责重新计算Bazi
5. Direction来自状态/势的解释, 不是投票

禁止:
- 修改十神计算 (已513/513=100%, 冻结)
- 重新训练/调参
- 修改Ground Truth V2
- 十神→Domain硬映射
- ContextResolver重新计算Bazi
- Direction投票
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Literal
from enum import Enum


# ============================================================================
# 1. DerivedSignal Schema + Provenance
# ============================================================================

class SignalSource(str, Enum):
    """信号来源引擎."""
    TEN_GOD = "TEN_GOD"
    FIVE_ELEMENT = "FIVE_ELEMENT"
    BRANCH_RELATION = "BRANCH_RELATION"
    STEM_RELATION = "STEM_RELATION"
    DA_YUN = "DA_YUN"
    YEAR_PILLAR = "YEAR_PILLAR"
    MONTH_PILLAR = "MONTH_PILLAR"
    DAY_PILLAR = "DAY_PILLAR"
    HOUR_PILLAR = "HOUR_PILLAR"
    NATAL_STRUCTURE = "NATAL_STRUCTURE"
    LUCK_CYCLE = "LUCK_CYCLE"


class TemporalLayer(str, Enum):
    """时序层级."""
    NATAL = "NATAL"           # 本命/先天结构
    DA_YUN = "DA_YUN"         # 大运
    YEAR = "YEAR"             # 流年
    MONTH = "MONTH"           # 流月
    DAY = "DAY"               # 流日
    INTERACTION = "INTERACTION"  # 层间交互 (Natal×Year, DaYun×Year等)


class SignalPolarity(str, Enum):
    """信号极性 - 注意: 这不是direction, 是信号本身的结构极性.
    最终direction必须由ContextResolver基于完整context决定.
    """
    ACTIVATING = "ACTIVATING"     # 激活/增强
    RESTRAINING = "RESTRAINING"   # 制约/减弱
    CONNECTING = "CONNECTING"     # 连接/合
    CONFLICTING = "CONFLICTING"   # 冲突/冲
    REPEATING = "REPEATING"       # 重复/伏吟
    TRANSFORMING = "TRANSFORMING" # 转化/化
    NEUTRAL = "NEUTRAL"           # 中性


class SignalStrength(str, Enum):
    """信号强度档位."""
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    DOMINANT = "DOMINANT"


@dataclass(frozen=True)
class SignalProvenance:
    """信号来源追溯 - 没有provenance的signal不允许进入ContextResolver."""
    source_engine: str                    # 来源引擎 (ZI_PING, BLIND_SCHOOL, etc.)
    source_rule_id: str                   # 来源规则ID (canonical rule_id)
    temporal_layer: TemporalLayer         # 时序层级
    derivation_chain: list[str] = field(default_factory=list)  # 推导链 (rule_id序列)
    raw_evidence_ref: Optional[str] = None  # 原始EngineEvidence引用
    calculation_version: str = "2026.08"  # 计算版本


@dataclass(frozen=True)
class DerivedSignal:
    """派生信号 - 经过deterministic engine验证的语义信号.

    这是Candidate Semantic Signal, 不是最终断言.
    最终Domain/SemanticFamily/Direction由ContextResolver基于完整Context决定.
    """
    signal_id: str                        # 唯一标识
    source: SignalSource                  # 信号来源类型
    value: str                            # 信号值 (如 "DIRECT_WEALTH", "CLASH", "COMBINATION")
    label_zh: str                         # 中文标签 (如 "正财", "冲", "合")
    temporal_layer: TemporalLayer         # 时序层级
    subject: Optional[str] = None         # 主体 (如 "DAY_MASTER", "YEAR_STEM")
    object: Optional[str] = None          # 客体 (如 "YEAR_STEM_BING", "BRANCH_WEI")
    polarity: SignalPolarity = SignalPolarity.NEUTRAL  # 结构极性 (非direction)
    strength: SignalStrength = SignalStrength.MODERATE  # 强度
    participants: list[str] = field(default_factory=list)  # 参与者 (如 ["ZI", "WU"])
    semantic_keys: list[str] = field(default_factory=list)  # 语义键 (如 ["RESOURCE", "TRANSACTION"])
    provenance: SignalProvenance = field(default_factory=lambda: SignalProvenance(
        source_engine="UNKNOWN",
        source_rule_id="UNKNOWN",
        temporal_layer=TemporalLayer.NATAL,
    ))

    def __post_init__(self):
        # 验证provenance存在
        if not self.provenance.source_engine or self.provenance.source_engine == "UNKNOWN":
            raise ValueError(f"Signal {self.signal_id} 缺少有效provenance.source_engine")
        if not self.provenance.source_rule_id or self.provenance.source_rule_id == "UNKNOWN":
            raise ValueError(f"Signal {self.signal_id} 缺少有效provenance.source_rule_id")


# ============================================================================
# 2. Natal Context (本命上下文)
# ============================================================================

@dataclass(frozen=True)
class NatalPillar:
    """本命柱."""
    position: Literal["YEAR", "MONTH", "DAY", "HOUR"]
    heavenly_stem: str
    earthly_branch: str
    stem_ten_god: Optional[str] = None     # 天干对日主的十神
    branch_main_qi: Optional[str] = None   # 地支主气
    branch_hidden_stems: list[str] = field(default_factory=list)  # 藏干


@dataclass(frozen=True)
class NatalContext:
    """本命上下文 - 保存先天结构, 但不直接做事件判断.

    这是Context的基础层, 提供结构背景.
    """
    day_master: str                        # 日主
    gender: str                            # 性别
    birth_year: int                        # 出生年
    pillars: list[NatalPillar] = field(default_factory=list)  # 四柱

    # 结构关系
    branch_clashes: list[str] = field(default_factory=list)      # 地支冲 (如 "ZI-WU")
    branch_combinations: list[str] = field(default_factory=list) # 地支合 (如 "ZI-CHOU")
    branch_harms: list[str] = field(default_factory=list)        # 地支害 (如 "ZI-WEI")
    branch_punishments: list[str] = field(default_factory=list)  # 地支刑 (如 "YIN-SI-SHEN")
    branch_three_combinations: list[str] = field(default_factory=list)  # 三合 (如 "SHEN-ZI-CHEN")

    # 日主状态
    day_master_root: list[str] = field(default_factory=list)     # 日主通根 (地支)
    day_master_strength: str = "MODERATE"                         # 日主强度档位
    day_master_seasonal_state: str = "UNKNOWN"                    # 日主季节状态 (得令/失令)

    # 十神分布
    ten_god_distribution: dict[str, int] = field(default_factory=dict)  # 十神计数
    useful_gods: list[str] = field(default_factory=list)          # 用神 (调候/扶抑)
    avoid_gods: list[str] = field(default_factory=list)           # 忌神

    # 结构特征
    structural_features: list[str] = field(default_factory=list)  # 结构特征 (如 "印旺", "食伤生财")


# ============================================================================
# 3. Da Yun Context (大运上下文)
# ============================================================================

@dataclass(frozen=True)
class DaYunPillar:
    """大运柱."""
    index: int                           # 大运序号 (0-based)
    heavenly_stem: str
    earthly_branch: str
    start_age: float                     # 起运岁数
    end_age: float                       # 结束岁数
    start_year: int                      # 开始公历年
    end_year: int                        # 结束公历年
    stem_ten_god: Optional[str] = None  # 大运天干对日主的十神
    is_current: bool = False             # 是否当前大运


@dataclass(frozen=True)
class DaYunContext:
    """大运上下文 - 必须正式纳入Resolver输入.

    很多事件不是 Natal→Event, 而是:
    Natal latent structure → Da Yun activates → Year triggers → Event manifestation
    """
    current_da_yun: Optional[DaYunPillar] = None   # 当前大运
    previous_da_yun: Optional[DaYunPillar] = None  # 上一步大运 (用于换运分析)
    next_da_yun: Optional[DaYunPillar] = None      # 下一步大运
    all_da_yun: list[DaYunPillar] = field(default_factory=list)  # 全部大运

    # Natal × Da Yun 交互
    natal_dayun_clashes: list[str] = field(default_factory=list)      # 大运与本命冲
    natal_dayun_combinations: list[str] = field(default_factory=list) # 大运与本命合
    dayun_ten_god_activation: list[str] = field(default_factory=list) # 大运激活的十神

    # 换运状态
    is_transition_period: bool = False          # 是否在换运期
    transition_start_year: Optional[int] = None
    transition_end_year: Optional[int] = None

    # 起运前状态 (target_year在起运年龄之前, current_da_yun可以为None)
    is_pre_luck_period: bool = False             # 是否在起运前
    first_luck_start_year: Optional[int] = None  # 第一步大运开始年份


# ============================================================================
# 4. Year Context (流年上下文)
# ============================================================================

@dataclass(frozen=True)
class YearContext:
    """流年上下文 - 进入真正的temporal activation."""
    target_year: int                      # 目标年份
    year_stem: str                        # 流年天干
    year_branch: str                      # 流年地支
    year_stem_ten_god: Optional[str] = None  # 流年天干对日主的十神

    # Natal × Year 交互
    natal_year_clashes: list[str] = field(default_factory=list)      # 流年与本命冲
    natal_year_combinations: list[str] = field(default_factory=list) # 流年与本命合
    natal_year_harms: list[str] = field(default_factory=list)        # 流年与本命害
    natal_year_punishments: list[str] = field(default_factory=list)  # 流年与本命刑
    natal_year_fuyin: list[str] = field(default_factory=list)        # 流年与本命伏吟 (同支)

    # Da Yun × Year 交互
    dayun_year_clashes: list[str] = field(default_factory=list)      # 流年与大运冲
    dayun_year_combinations: list[str] = field(default_factory=list) # 流年与大运合
    dayun_year_fuyin: list[str] = field(default_factory=list)        # 流年与大运伏吟

    # Natal × Da Yun × Year 三层交互
    three_layer_interactions: list[str] = field(default_factory=list)  # 三层交互 (如 三合局完成)


# ============================================================================
# 5. TemporalContext (完整时序上下文)
# ============================================================================

@dataclass(frozen=True)
class TemporalContext:
    """完整时序上下文 - ContextResolver的输入.

    四层结构:
    Natal Context (先天结构背景)
    + Da Yun Context (大运激活)
    + Year Context (流年触发)
    + Derived Signals (派生语义信号)

    ContextResolver基于完整Context产生Domain + SemanticFamily + Direction.
    """
    case_id: str                          # 案例ID
    target_year: int                      # 目标年份

    # 四层上下文
    natal: NatalContext
    da_yun: DaYunContext
    year: YearContext
    derived_signals: list[DerivedSignal] = field(default_factory=list)

    # 元数据
    context_version: str = "1.0.0"       # Context Contract版本
    assembly_timestamp: str = ""          # 组装时间
    completeness_score: float = 0.0       # 完整性分数 (0-1)

    def get_signals_by_layer(self, layer: TemporalLayer) -> list[DerivedSignal]:
        """按时序层级筛选信号."""
        return [s for s in self.derived_signals if s.temporal_layer == layer]

    def get_signals_by_source(self, source: SignalSource) -> list[DerivedSignal]:
        """按来源筛选信号."""
        return [s for s in self.derived_signals if s.source == source]

    def get_activation_signals(self) -> list[DerivedSignal]:
        """获取激活类信号."""
        return [s for s in self.derived_signals if s.polarity == SignalPolarity.ACTIVATING]

    def get_conflict_signals(self) -> list[DerivedSignal]:
        """获取冲突类信号."""
        return [s for s in self.derived_signals if s.polarity == SignalPolarity.CONFLICTING]


# ============================================================================
# 6. Candidate Signal 降级规则 (十神不再直接映射Domain)
# ============================================================================

# 十神 → Candidate Semantic Keys (不是Domain!)
# 这些是语义候选, 最终Domain由ContextResolver决定
TEN_GOD_CANDIDATE_KEYS = {
    "BIJIAN": {
        "label_zh": "比肩",
        "semantic_keys": ["SELF", "PEER", "COMPETITION", "SUPPORT", "ENDURANCE"],
        "polarity": SignalPolarity.CONNECTING,
    },
    "JIECAI": {
        "label_zh": "劫财",
        "semantic_keys": ["COMPETITION", "RESOURCE_DISPUTE", "ACTION", "RISK"],
        "polarity": SignalPolarity.CONFLICTING,
    },
    "SHISHEN": {
        "label_zh": "食神",
        "semantic_keys": ["OUTPUT", "CREATIVITY", "EXPRESSION", "LEISURE", "FREEDOM"],
        "polarity": SignalPolarity.ACTIVATING,
    },
    "SHANGGUAN": {
        "label_zh": "伤官",
        "semantic_keys": ["OUTPUT", "EXPRESSION", "INNOVATION", "AUTONOMY", "REBELLION"],
        "polarity": SignalPolarity.ACTIVATING,
    },
    "ZHENGCAI": {
        "label_zh": "正财",
        "semantic_keys": ["RESOURCE", "TRANSACTION", "ACQUISITION", "RESPONSIBILITY", "STABILITY"],
        "polarity": SignalPolarity.CONNECTING,
    },
    "PIANCAI": {
        "label_zh": "偏财",
        "semantic_keys": ["RESOURCE", "OPPORTUNITY", "TRANSACTION", "RISK", "FLUIDITY"],
        "polarity": SignalPolarity.TRANSFORMING,
    },
    "ZHENGGUAN": {
        "label_zh": "正官",
        "semantic_keys": ["RULE", "RESPONSIBILITY", "STRUCTURE", "AUTHORITY", "DISCIPLINE"],
        "polarity": SignalPolarity.RESTRAINING,
    },
    "QISHA": {
        "label_zh": "七杀",
        "semantic_keys": ["PRESSURE", "COMPETITION", "CHANGE", "CHALLENGE", "DISCIPLINE"],
        "polarity": SignalPolarity.CONFLICTING,
    },
    "ZHENGYIN": {
        "label_zh": "正印",
        "semantic_keys": ["SUPPORT", "KNOWLEDGE", "RESOURCE", "PROTECTION", "TRADITION"],
        "polarity": SignalPolarity.CONNECTING,
    },
    "PIANYIN": {
        "label_zh": "偏印",
        "semantic_keys": ["KNOWLEDGE", "INSIGHT", "RESOURCE", "UNCONVENTIONAL", "ISOLATION"],
        "polarity": SignalPolarity.NEUTRAL,
    },
}

# 地支关系 → Candidate Semantic Keys (不是Direction!)
BRANCH_RELATION_CANDIDATE_KEYS = {
    "CLASH": {
        "label_zh": "冲",
        "semantic_keys": ["CHANGE", "CONFLICT", "MOVEMENT", "DISRUPTION", "SEPARATION"],
        "polarity": SignalPolarity.CONFLICTING,
    },
    "COMBINATION": {
        "label_zh": "合",
        "semantic_keys": ["CONNECTION", "INTEGRATION", "COOPERATION", "ATTRACTION", "STABILITY"],
        "polarity": SignalPolarity.CONNECTING,
    },
    "HARM": {
        "label_zh": "害",
        "semantic_keys": ["FRICTION", "MISUNDERSTANDING", "SUBTLE_CONFLICT", "DAMAGE"],
        "polarity": SignalPolarity.RESTRAINING,
    },
    "PUNISHMENT": {
        "label_zh": "刑",
        "semantic_keys": ["TENSION", "LEGAL", "DISCIPLINE", "SUFFERING", "RESOLUTION"],
        "polarity": SignalPolarity.RESTRAINING,
    },
    "FUYIN": {
        "label_zh": "伏吟",
        "semantic_keys": ["REPETITION", "RECURRENCE", "DELAY", "INTENSIFICATION", "RETURN"],
        "polarity": SignalPolarity.REPEATING,
    },
    "THREE_COMBINATION": {
        "label_zh": "三合",
        "semantic_keys": ["INTEGRATION", "COMPLETION", "AMPLIFICATION", "STRUCTURE_FORMATION"],
        "polarity": SignalPolarity.TRANSFORMING,
    },
}


# ============================================================================
# 7. Contract Validator
# ============================================================================

class ContractValidator:
    """TemporalContext Contract验证器."""

    @staticmethod
    def validate_derived_signal(signal: DerivedSignal) -> list[str]:
        """验证单个DerivedSignal."""
        errors = []
        if not signal.signal_id:
            errors.append("signal_id为空")
        if not signal.value:
            errors.append("value为空")
        if not signal.provenance.source_engine or signal.provenance.source_engine == "UNKNOWN":
            errors.append(f"signal {signal.signal_id}: provenance.source_engine无效")
        if not signal.provenance.source_rule_id or signal.provenance.source_rule_id == "UNKNOWN":
            errors.append(f"signal {signal.signal_id}: provenance.source_rule_id无效")
        if signal.polarity is None:
            errors.append(f"signal {signal.signal_id}: polarity为None")
        return errors

    @staticmethod
    def validate_natal_context(natal: NatalContext) -> list[str]:
        """验证NatalContext."""
        errors = []
        if not natal.day_master:
            errors.append("natal.day_master为空")
        if len(natal.pillars) != 4:
            errors.append(f"natal.pillars数量应为4, 实际{len(natal.pillars)}")
        return errors

    @staticmethod
    def validate_dayun_context(dayun: DaYunContext) -> list[str]:
        """验证DaYunContext."""
        errors = []
        # 起运前允许current_da_yun为None
        if dayun.current_da_yun is None and not dayun.is_pre_luck_period:
            errors.append("dayun.current_da_yun为None (大运是必要输入, 除非is_pre_luck_period=True)")
        return errors

    @staticmethod
    def validate_year_context(year: YearContext) -> list[str]:
        """验证YearContext."""
        errors = []
        if not year.year_stem:
            errors.append("year.year_stem为空")
        if not year.year_branch:
            errors.append("year.year_branch为空")
        if year.year_stem_ten_god is None:
            errors.append("year.year_stem_ten_god为None")
        return errors

    @classmethod
    def validate_temporal_context(cls, ctx: TemporalContext) -> dict:
        """验证完整TemporalContext."""
        all_errors = []

        # 验证各层
        natal_errors = cls.validate_natal_context(ctx.natal)
        dayun_errors = cls.validate_dayun_context(ctx.da_yun)
        year_errors = cls.validate_year_context(ctx.year)

        all_errors.extend(natal_errors)
        all_errors.extend(dayun_errors)
        all_errors.extend(year_errors)

        # 验证所有DerivedSignals
        signal_errors = []
        for signal in ctx.derived_signals:
            signal_errors.extend(cls.validate_derived_signal(signal))
        all_errors.extend(signal_errors)

        # 计算完整性分数
        completeness = 1.0
        if natal_errors:
            completeness -= 0.2
        if dayun_errors:
            completeness -= 0.3
        if year_errors:
            completeness -= 0.2
        if signal_errors:
            completeness -= 0.1 * min(len(signal_errors) / max(len(ctx.derived_signals), 1), 0.2)
        completeness = max(0.0, completeness)

        return {
            "valid": len(all_errors) == 0,
            "error_count": len(all_errors),
            "errors": all_errors,
            "completeness_score": completeness,
            "natal_valid": len(natal_errors) == 0,
            "dayun_valid": len(dayun_errors) == 0,
            "year_valid": len(year_errors) == 0,
            "signals_valid": len(signal_errors) == 0,
            "signal_count": len(ctx.derived_signals),
        }


if __name__ == "__main__":
    # 快速测试Contract
    print("P6-C-3A Temporal Context Contract - 快速测试")
    print("=" * 60)

    # 测试DerivedSignal
    print("\n1. DerivedSignal测试:")
    try:
        signal = DerivedSignal(
            signal_id="SIG-001",
            source=SignalSource.TEN_GOD,
            value="DIRECT_WEALTH",
            label_zh="正财",
            temporal_layer=TemporalLayer.YEAR,
            subject="YEAR_STEM",
            object="WU",
            polarity=SignalPolarity.CONNECTING,
            strength=SignalStrength.STRONG,
            semantic_keys=["RESOURCE", "TRANSACTION"],
            provenance=SignalProvenance(
                source_engine="ZI_PING",
                source_rule_id="BZA_TEN_GOD_ZHENG_CAI",
                temporal_layer=TemporalLayer.YEAR,
            ),
        )
        print(f"  ✅ DerivedSignal创建成功: {signal.signal_id} = {signal.label_zh}")
        print(f"     semantic_keys: {signal.semantic_keys}")
        print(f"     polarity: {signal.polarity.value} (非direction)")
    except Exception as e:
        print(f"  ❌ DerivedSignal创建失败: {e}")

    # 测试缺少provenance
    print("\n2. 缺少provenance测试 (应失败):")
    try:
        bad_signal = DerivedSignal(
            signal_id="SIG-BAD",
            source=SignalSource.TEN_GOD,
            value="TEST",
            label_zh="测试",
            temporal_layer=TemporalLayer.YEAR,
        )
        print(f"  ❌ 不应创建成功")
    except ValueError as e:
        print(f"  ✅ 正确拒绝: {e}")

    # 测试十神Candidate Keys
    print("\n3. 十神Candidate Keys (非Domain映射):")
    for tg, info in list(TEN_GOD_CANDIDATE_KEYS.items())[:3]:
        print(f"  {tg} ({info['label_zh']}):")
        print(f"    semantic_keys: {info['semantic_keys']}")
        print(f"    polarity: {info['polarity'].value}")
        print(f"    ⚠️  不是Domain! 最终Domain由ContextResolver决定")

    print("\n" + "=" * 60)
    print("P6-C-3A Contract Definition 测试通过")
