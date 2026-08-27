"""Ziwei Adapter (P0-14) — Policy RATIFIED.

P0-14 行为验证已完成，政策已冻结。

关键决策:
- DECISION-001: 八字使用阳历(solar)，紫微使用阴历(lunar)
- DECISION-002: 晚子时不换日，使用原日期四柱
- DECISION-003: time_index_from_hour 标准映射
- DECISION-004: 通过 earthlyBranchOfSoulPalace 查找命宫

架构:
    CalculationContext
        ↓
    SolarDate (阳历，用户输入)
        ↓
    LunarDate (阴历，转换为农历)
        ↓
    ZiweiEngine (调用 iztro byLunar)
"""

from __future__ import annotations

from typing import Literal, Optional

from lunar_python import Solar

from .time_resolver import CalculationContext
from .ziwei_engine import ZiweiChart, ZiweiEngine


class ZiweiCalculationPolicy:
    """Ziwei 时间政策 (P0-14 已裁定,已冻结)"""

    SPEC_DECISION_PENDING = "SPEC_DECISION_PENDING"
    RATIFIED = "RATIFIED"

    RATIFIED_VERSION = "P0-14-v1"
    RATIFIED_DATE = "2026-08-21"

    def __init__(self) -> None:
        self.status: str = self.RATIFIED  # 已冻结
        self.date_source: str = "lunar"  # 紫微使用农历
        self.late_zi_handling: str = "same_day"  # 与iztro一致
        self.time_index_fn: str = "standard"
        self.ratified_policy_version: str = self.RATIFIED_VERSION

    @property
    def is_pending(self) -> bool:
        return False  # 已冻结，不再 pending

    @property
    def is_ratified(self) -> bool:
        return self.status == self.RATIFIED

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "date_source": self.date_source,
            "late_zi_handling": self.late_zi_handling,
            "time_index_fn": self.time_index_fn,
            "ratified_policy_version": self.ratified_policy_version,
            "ratified_date": self.RATIFIED_DATE,
        }


class ZiweiAdapter:
    """Ziwei 适配层 (P0-14 RATIFIED)
    
    关键: 将阳历转换为农历后传入紫微引擎。
    """

    def __init__(
        self,
        engine: ZiweiEngine,
        policy: Optional[ZiweiCalculationPolicy] = None,
    ) -> None:
        self._engine = engine
        self._policy = policy or ZiweiCalculationPolicy()

    @property
    def policy(self) -> ZiweiCalculationPolicy:
        return self._policy

    def compute(self, ctx: CalculationContext, gender: Literal["male", "female"] = "male") -> ZiweiChart:
        """根据已冻结的政策执行紫微计算
        
        流程:
        1. 从 ctx 获取阳历日期和时间
        2. 转换为农历
        3. 调用引擎计算
        """
        if self._policy.is_pending:
            raise RuntimeError(
                "Ziwei Calculation Policy 状态 = SPEC_DECISION_PENDING: "
                "尚未完成 P0-14 行为验证，禁止执行。"
            )

        # 从 CalculationContext 提取阳历信息
        solar_dt = ctx.true_solar_datetime
        year, month, day = solar_dt.year, solar_dt.month, solar_dt.day
        hour = solar_dt.hour

        # 阳历 → 农历转换
        solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        lunar = solar.getLunar()
        
        lunar_year = lunar.getYear()
        lunar_month = lunar.getMonth()
        lunar_day = lunar.getDay()
        
        # 紫微使用农历，但时柱仍用阳历的时辰
        # 注意: 紫微时柱有时也用农历，这里保持与时辰表一致
        lunar_date = (lunar_year, lunar_month, lunar_day)
        
        # 调用引擎 (内部会使用 byLunar)
        return self._engine.compute(lunar_date, hour, gender)
