"""Bazi Adapter (P0-14) — CalculationContext → Existing BaziEngine.

适配层职责:把 TimeResolver/CalculationContext 的标准时间事实投影成 BaziEngine
的输入 tuple。**BaziEngine 本身不负责** timezone / longitude correction / EoT /
date boundary resolution —— 这些全部由上游(TimeResolver, T4)完成。

T5:八字 V1 使用「出生地当地真太阳时」,日界 = 23:00 子初换日
(22:59 → 前一日, 23:00 → 下一日),由 CalculationContext.bazi_view 承载
(effective_date 已换日)。本适配器禁止重写 bazi_engine;只做投影转发。

公共链(pipeline)保持原样:本适配器独立验证,不接入 pipeline,确保
Golden 20/20 不被公共链变化破坏。
"""

from __future__ import annotations

from typing import Literal

from .bazi_engine import BaziChart, BaziEngine
from .time_resolver import CalculationContext


class BaziAdapter:
    """把 CalculationContext 的八字视图送入现有 BaziEngine。"""

    def __init__(self, engine: BaziEngine | None = None):
        self._engine = engine or BaziEngine()

    @property
    def engine(self) -> BaziEngine:
        return self._engine

    def compute(
        self, ctx: CalculationContext, gender: Literal["male", "female"] = "male"
    ) -> BaziChart:
        """用 bazi_view(已 23:00 换日的 日+时)驱动现有引擎。

        bazi_view = (effective_date.y, m, d, effective_hour)。
        引擎收到已归一化日期;日柱由 sxtwl 按日期取,小时自动成为对应日期的时辰。

        V2.6 fix: 传 skip_late_zi=True, 因 TimeResolver 已完成 23:00 换日,
        避免 BaziEngine 内部再次换日导致双重换日(日柱多跳一天)。

        H18-FIX: 传递完整 solar_datetime，确保月柱边界检查精确到分钟。
        """
        view = ctx.bazi_view
        return self._engine.compute(
            view,
            gender=gender,
            skip_late_zi=True,
            birth_datetime=ctx.true_solar_datetime,
        )
