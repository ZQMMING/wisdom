"""
P0-③ Legacy Signal Adapter — 基础层 Signal 到 CanonicalSignal 的适配器

【职责】仅做字段转换，不重新实现引擎逻辑
【原则】Adapter can only convert, NOT re-implement engine logic
【唯一生产标准】CanonicalSignal（规范层）

转换映射：
  Signal (reasoning/signal_engine.py) → CanonicalSignal (signal/canonical_signal.py)
  - signal_id → signal_id（直接映射）
  - ontology_type → event_type（不在CANONICAL_EVENT_TYPES中则用UNKNOWN）
  - direction → direction（POSITIVE/NEGATIVE/CHANGE/NEUTRAL/UNKNOWN）
  - strength(str) → strength(float 0.0-1.0)（moderate→0.5, strong→0.8, weak→0.3）
  - layer → layer（BASELINE/CYCLE_CONTEXT/DAILY_ACTIVATION）
  - rule_refs → rule_refs（直接映射）
  - evidence_refs → evidence_refs（直接映射）
  - source_engine → 默认 Bazi（SignalEngine主要处理八字）
  - domain → 默认 LIFE_EVENT（无法从ontology_type推断时）
  - temporal_scope → 默认 SignalTemporalScope()
  - extracted_at → 当前时间
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from tongshu.signal.canonical_signal import (
    CanonicalSignal,
    SignalTemporalScope,
    CANONICAL_EVENT_TYPES,
)
from tongshu.spec.canonical_signal import SourceEngine, SignalLayer
from tongshu.spec.event_ontology_v1 import Domain, EventDirection


# ============================================================
# 字段映射表
# ============================================================

# Signal.strength (字符串) → CanonicalSignal.strength (浮点数 0.0-1.0)
_STRENGTH_MAP = {
    "very_strong": 0.9,
    "strong": 0.8,
    "moderate": 0.5,
    "weak": 0.3,
    "very_weak": 0.1,
    "none": 0.0,
}

# Signal.direction → EventDirection
_DIRECTION_MAP = {
    "positive": EventDirection.POSITIVE,
    "beneficial": EventDirection.POSITIVE,
    "favorable": EventDirection.POSITIVE,
    "negative": EventDirection.NEGATIVE,
    "harmful": EventDirection.NEGATIVE,
    "unfavorable": EventDirection.NEGATIVE,
    "change": EventDirection.CHANGE,
    "transform": EventDirection.CHANGE,
    "neutral": EventDirection.NEUTRAL,
    "mixed": EventDirection.NEUTRAL,
}

# Signal.layer → SignalLayer
_LAYER_MAP = {
    "BASELINE": SignalLayer.BASELINE,
    "CYCLE_CONTEXT": SignalLayer.CYCLE_CONTEXT,
    "DAILY_ACTIVATION": SignalLayer.DAILY_ACTIVATION,
}


# ============================================================
# 适配器函数
# ============================================================

def legacy_signal_to_canonical(
    signal,
    source_engine: SourceEngine = SourceEngine.BAZI,
    domain: Domain = Domain.LIFE_EVENT,
    temporal_scope: Optional[SignalTemporalScope] = None,
) -> CanonicalSignal:
    """将基础层 Signal 转换为 CanonicalSignal（唯一生产标准）。

    Args:
        signal: 基础层 Signal 对象（reasoning/signal_engine.py）
        source_engine: 来源引擎，默认 Bazi
        domain: 事件域，默认 LIFE_EVENT
        temporal_scope: 时间范围，默认空 SignalTemporalScope

    Returns:
        CanonicalSignal 对象

    Note:
        本函数仅做字段转换，不重新实现引擎逻辑。
        无法精确映射的字段使用默认值或 UNKNOWN。
    """
    # event_type: ontology_type → event_type，不在标准列表中则用 UNKNOWN
    event_type = signal.ontology_type if signal.ontology_type in CANONICAL_EVENT_TYPES else "UNKNOWN"

    # direction: 字符串 → EventDirection 枚举
    direction = _DIRECTION_MAP.get(
        getattr(signal, "direction", "").lower(),
        EventDirection.UNKNOWN,
    )

    # strength: 字符串 → 浮点数 0.0-1.0
    strength_str = getattr(signal, "strength", "moderate").lower()
    strength = _STRENGTH_MAP.get(strength_str, 0.5)
    strength = max(0.0, min(1.0, strength))  # 确保在范围内

    # layer: 字符串 → SignalLayer 枚举
    layer_str = getattr(signal, "layer", "BASELINE").upper()
    layer = _LAYER_MAP.get(layer_str, SignalLayer.BASELINE)

    # temporal_scope: 默认空
    if temporal_scope is None:
        temporal_scope = SignalTemporalScope()

    return CanonicalSignal(
        signal_id=signal.signal_id,
        source_engine=source_engine,
        event_type=event_type,
        domain=domain,
        direction=direction,
        strength=strength,
        temporal_scope=temporal_scope,
        evidence_refs=list(getattr(signal, "evidence_refs", [])),
        rule_refs=list(getattr(signal, "rule_refs", [])),
        layer=layer,
        extracted_at=datetime.now().isoformat(),
    )


def legacy_signals_to_canonical(
    signals: list,
    source_engine: SourceEngine = SourceEngine.BAZI,
    domain: Domain = Domain.LIFE_EVENT,
) -> list[CanonicalSignal]:
    """批量将基础层 Signal 列表转换为 CanonicalSignal 列表。

    Args:
        signals: 基础层 Signal 对象列表
        source_engine: 来源引擎，默认 Bazi
        domain: 事件域，默认 LIFE_EVENT

    Returns:
        CanonicalSignal 对象列表
    """
    return [
        legacy_signal_to_canonical(s, source_engine=source_engine, domain=domain)
        for s in signals
    ]


# ============================================================
# SignalEngine 便捷方法（monkey-patch 风格）
# ============================================================

def add_canonical_conversion_to_signal_engine():
    """给基础层 Signal 类添加 to_canonical() 方法。

    调用此函数后，可以直接使用：
        signal.to_canonical() → CanonicalSignal

    注意：这是运行时 monkey-patch，不修改原始类定义文件。
    推荐在应用启动时调用一次。
    """
    from tongshu.reasoning.signal_engine import Signal as _LegacySignal

    if not hasattr(_LegacySignal, "to_canonical"):
        def to_canonical(self, source_engine=SourceEngine.BAZI, domain=Domain.LIFE_EVENT):
            return legacy_signal_to_canonical(self, source_engine=source_engine, domain=domain)
        _LegacySignal.to_canonical = to_canonical
