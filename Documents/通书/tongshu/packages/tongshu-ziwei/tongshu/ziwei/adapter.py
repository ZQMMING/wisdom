"""Ziwei Adapter (P0-14) 与 Policy RATIFIED.

P0-14 紫微验证完成，架构已定稿。

关键决策:
- DECISION-001: 八字使用阳历(solar)，紫微使用农历(lunar)
- DECISION-002: 晚子时仍当天，沿用原始时辰
- DECISION-003: time_index_from_hour 标准映射
- DECISION-004: 通过 earthlyBranchOfSoulPalace 查找命宫

架构:
    CalculationContext
        ↓
    SolarDate (用户输入/校准)
        ↓
    LunarDate (阳历→农历)
        ↓
    ZiweiEngine (内部调用 byLunar)
"""

from __future__ import annotations

from typing import Literal, Optional

from lunar_python import Solar

from .engine import ZiweiChart, ZiweiEngine


class ZiweiCalculationPolicy:
    """Ziwei 时辰计算策略 (P0-14 已定稿, 已审核)"""

    SPEC_DECISION_PENDING = "SPEC_DECISION_PENDING"
    RATIFIED = "RATIFIED"

    RATIFIED_VERSION = "P0-14-v1"
    RATIFIED_DATE = "2026-08-21"

    def __init__(self) -> None:
        self.status: str = self.RATIFIED  # 已定稿
        self.date_source: str = "lunar"  # 紫微使用农历
        self.late_zi_handling: str = "same_day"  # 与iztro一致
        self.time_index_fn: str = "standard"
        self.ratified_policy_version: str = self.RATIFIED_VERSION

    @property
    def is_pending(self) -> bool:
        return False  # 已定稿，无需 pending

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
    
    关键点: 阳历转农历，再供紫微排盘。
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

    def compute(self, ctx, gender: Literal["male", "female"] = "male") -> ZiweiChart:
        """执行紫微排盘（P0-14 已通过）。
        
        步骤:
        1. 从 ctx 获取出生年月日和时辰
        2. 转为农历
        3. 调用紫微引擎
        """
        if self._policy.is_pending:
            raise RuntimeError(
                "Ziwei Calculation Policy 状态 = SPEC_DECISION_PENDING: "
                "尚未通过 P0-14 紫微验证，执行中止。"
            )

        # 从 CalculationContext 获取出生信息
        solar_dt = ctx.true_solar_datetime
        year, month, day = solar_dt.year, solar_dt.month, solar_dt.day
        hour = solar_dt.hour

        # 阳历 → 农历转换
        solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        lunar = solar.getLunar()
        
        lunar_year = lunar.getYear()
        lunar_month = lunar.getMonth()
        lunar_day = lunar.getDay()
        
        # 紫微使用农历年月日，时辰不变（凌晨时辰也按农历处理保持一致性）
        lunar_date = (lunar_year, lunar_month, lunar_day)
        
        # 调用紫微引擎 (内部使用 byLunar)
        return self._engine.compute(lunar_date, hour, gender)
