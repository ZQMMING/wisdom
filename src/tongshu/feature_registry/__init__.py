"""P6-C-3C-1 Feature Registry - 五引擎计算特征注册表."""
from tongshu.feature_registry.contract import (
    FeatureNamespace, FeatureValueType, FeatureScope,
    FeatureDefinition, Feature, FeatureMapStatus, FeatureMapResult,
    FeatureRegistry, BaseFeatureAdapter,
)
from tongshu.feature_registry.adapters.zi_ping_adapter import ZiPingFeatureAdapter
from tongshu.feature_registry.adapters.zi_wei_adapter import ZiWeiFeatureAdapter
from tongshu.feature_registry.adapters.he_luo_adapter import HeLuoFeatureAdapter
from tongshu.feature_registry.adapters.yi_jing_adapter import YiJingFeatureAdapter
from tongshu.feature_registry.adapters.blind_school_adapter import BlindSchoolFeatureAdapter

__all__ = [
    "FeatureNamespace", "FeatureValueType", "FeatureScope",
    "FeatureDefinition", "Feature", "FeatureMapStatus", "FeatureMapResult",
    "FeatureRegistry", "BaseFeatureAdapter",
    "ZiPingFeatureAdapter", "ZiWeiFeatureAdapter", "HeLuoFeatureAdapter",
    "YiJingFeatureAdapter", "BlindSchoolFeatureAdapter",
]
