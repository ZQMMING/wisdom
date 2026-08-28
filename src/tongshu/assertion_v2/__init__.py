"""P6 Assertion Layer V2 - 五引擎原生断言层.

核心原则:
1. 五大引擎各自拥有自己的原生断言层, 不共用统一断语模板
2. 断言层之后才进入统一Mapping / Cross-Engine聚合
3. 互补, 不比较; 各体系不能互相改写
4. 禁止: direction/polarity/pos/neg/confidence/vote/majority/SYSTEM_WEIGHTS
5. 每个NativeJudgment必须带provenance和mapping_hook
"""
from tongshu.assertion_v2.contract import (
    EngineName,
    ZiPingJudgmentType,
    BlindSchoolJudgmentType,
    ZiWeiJudgmentType,
    HeLuoJudgmentType,
    YiJingJudgmentType,
    ENGINE_JUDGMENT_TYPES,
    JudgmentProvenance,
    MappingHook,
    NativeJudgment,
    JudgmentLibrary,
    UnifiedMappingLayer,
    AssertionV2Validator,
)

__all__ = [
    "EngineName",
    "ZiPingJudgmentType",
    "BlindSchoolJudgmentType",
    "ZiWeiJudgmentType",
    "HeLuoJudgmentType",
    "YiJingJudgmentType",
    "ENGINE_JUDGMENT_TYPES",
    "JudgmentProvenance",
    "MappingHook",
    "NativeJudgment",
    "JudgmentLibrary",
    "UnifiedMappingLayer",
    "AssertionV2Validator",
]
