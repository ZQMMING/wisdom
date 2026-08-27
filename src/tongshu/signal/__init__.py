"""
Signal Module (Phase 3)

Exports:
  - CanonicalSignal, SignalTemporalScope
  - CanonicalSignalValidator
  - SignalNormalizer, NormalizationResult, NormalizationStatus
  - All engine adapters
  - CanonicalSignalAggregator
"""
from .canonical_signal import (
    CanonicalSignal,
    SignalTemporalScope,
    CanonicalSignalValidator,
    validate_canonical_signal_schema,
)
from .normalizer import (
    SignalNormalizer,
    NormalizationResult,
    NormalizationStatus,
)
from .adapters import (
    BaseAdapter,
    AdapterContext,
    BaziAdapter,
    HeluoAdapter,
    ZiweiAdapter,
    HuangliAdapter,
    KnowledgeAdapter,
    get_adapter,
    adapt,
    ADAPTER_REGISTRY,
)
from .aggregator import (
    SignalGroup,
    CanonicalSignalAggregator,
)

__all__ = [
    # Canonical Signal
    'CanonicalSignal',
    'SignalTemporalScope',
    'CanonicalSignalValidator',
    'validate_canonical_signal_schema',
    # Normalizer
    'SignalNormalizer',
    'NormalizationResult',
    'NormalizationStatus',
    # Adapters
    'BaseAdapter',
    'AdapterContext',
    'BaziAdapter',
    'HeluoAdapter',
    'ZiweiAdapter',
    'HuangliAdapter',
    'KnowledgeAdapter',
    'get_adapter',
    'adapt',
    'ADAPTER_REGISTRY',
    # Aggregator
    'SignalGroup',
    'CanonicalSignalAggregator',
]
