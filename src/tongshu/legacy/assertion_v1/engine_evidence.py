# -*- coding: utf-8 -*-
"""P0 EngineEvidence 统一证据契约 (ARCHITECTURE_V13_FINAL §三).

铁律:
- EngineEvidence 只承载【纯事实】, 不含 polarity / direction / 吉凶判断.
- 五行/十神/星曜/卦象本身没有绝对吉凶, 方向在 Assertion 层之后才产生.
- rule_id 稳定不变, 用于 Golden Case 反查追踪.
- 所有引擎必须适配此契约, 不改各引擎内部计算逻辑.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EngineName(str, Enum):
    """引擎名称(冻结, P0后不随意新增)."""
    ZI_PING = "ZI_PING"           # 子平八字: 旺衰/格局/用神
    BLIND_SCHOOL = "BLIND_SCHOOL"  # 盲派: 做功/宾主体用/应期
    ZI_WEI = "ZI_WEI"             # 紫微斗数: 星曜/宫位/四化
    HE_LUO = "HE_LUO"             # 河洛理数: 先天/后天/元堂/流年卦
    YI_JING = "YI_JING"           # 易经: 卦辞/爻辞/人间道/决策


class TemporalScope(str, Enum):
    """时间范围(冻结)."""
    BIRTH = "birth"      # 先天结构(本命)
    YEAR = "year"        # 流年
    MONTH = "month"      # 流月
    DAY = "day"          # 流日
    HOUR = "hour"        # 流时


@dataclass(frozen=True)
class EngineEvidence:
    """统一引擎证据 — 纯事实, 无 polarity/direction.

    示例(正确):
        EngineEvidence(
            engine=EngineName.ZI_PING,
            rule_id="TEN_GOD_SHANG_GUAN",
            value="丙",
            temporal_scope=TemporalScope.YEAR,
            attributes={"ten_god": "伤官", "element": "火", "stem": "丙"},
        )

    禁止(错误):
        {"value": "伤官", "polarity": "positive"}  # polarity已废除
    """
    engine: EngineName
    rule_id: str                          # 规则ID, 稳定不变, 用于反查追踪
    value: Any                            # 原始计算值(纯事实)
    temporal_scope: TemporalScope         # 时间范围
    attributes: dict[str, Any] = field(default_factory=dict)  # 附加属性

    def to_dict(self) -> dict:
        return {
            "engine": self.engine.value,
            "rule_id": self.rule_id,
            "value": self.value,
            "temporal_scope": self.temporal_scope.value,
            "attributes": dict(self.attributes),
        }


class BaseEngineAdapter(ABC):
    """引擎适配器基类.

    每个引擎实现一个 Adapter, 将引擎内部计算结果转换为 EngineEvidence 列表.
    不改引擎内部逻辑, 只做输出适配.
    """
    engine_name: EngineName

    @abstractmethod
    def produce_evidence(
        self,
        inp: Any,
        chart: Any,
        context: dict | None = None,
    ) -> list[EngineEvidence]:
        """产出该引擎的统一证据列表.

        Args:
            inp: AssertionInput 或兼容的输入
            chart: 排盘结果
            context: 上下文字典(birth/bazi/gender/focus_years等)

        Returns:
            EngineEvidence 列表, 每条都是纯事实, 不含方向判断
        """
        ...


__all__ = [
    "EngineName",
    "TemporalScope",
    "EngineEvidence",
    "BaseEngineAdapter",
]
