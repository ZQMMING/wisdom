"""Z76: 流日参数与来源契约（第一阶段）

原则（用户铁律）：
1. 先做"流日计算与来源契约"，再做规则接入。
2. 流日四化天干来源未在《飞星秘仪》查到原文 → 不反套流月规则，标 UNRESOLVED。
3. 南北派继续绝对隔离，不投票不互补。
4. 本模块只回答机器层面：
   给定 natal_chart + flow_year + flow_month + flow_day（阳历日），
   唯一确定 flow_day_gan / flow_day_zhi / day_position / applicable_method。
   不接 Rule/Evidence/Assertion。

已钉边界（对照现有层）：
- 流年四化：北派钦天 = 流年命宫宫干（非流年干支本身），已由 QTN-CMB-016 钉住。
- 流月四化：《飞星秘仪》"流月四化飛曜天干：一律用本命盤天干，不可另取用"，
  已由 QTN-CMB-054 钉住。
- 流日四化天干：《飞星秘仪》原文未检索到流日四化天干的明确讲法。
  iztro 默认 daily.mutagen 用流日干支（阳历日天干），但这不是钦天口径。
  → 本阶段不假设、不反套，标 UNRESOLVED，等原典取证。
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class FlowDayContract:
    """流日参数契约——给定 natal + 阳历日，唯一确定流日定位。

    本结构不做吉凶判断，只钉"这一天在盘上是什么、为什么这样取"。
    """
    flow_day_date: str            # 阳历日 "YYYY-MM-DD"
    flow_day_gan: str             # 流日天干（iztro daily.heavenlyStem）
    flow_day_zhi: str             # 流日地支（iztro daily.earthlyBranch）
    flow_day_mutagen: list        # 流日四化 [禄,权,科,忌]（iztro 计算）
    day_position_palace: str      # 流日地支落本命盘哪个宫名
    source_of_gan: str            # 天干来源说明
    source_of_zhi: str            # 地支来源说明
    applicable_sect: list         # 本阶段允许进入的派别（默认空=不接规则）
    sihua_gan_source: str         # 流日四化天干来源契约状态
    notes: str = ""


def resolve_flow_day(chart, flow_day: tuple[int, int, int]) -> FlowDayContract:
    """解析流日参数契约。

    参数：
        chart: ZiweiChart（本命盘，需含 palaces 地支映射）
        flow_day: (年, 月, 日) 阳历日

    返回：FlowDayContract
    """
    from ...ziwei_engine import ZiweiEngine
    import subprocess, json

    y, mo, d = flow_day
    engine = ZiweiEngine()

    # 调 iztro 拿 daily 层（含流日干支+四化）
    # 需要出生农历日期——从 chart.birth_year 反推不了农历，
    # 但 flow_day_mutagen 已经接受阳历日参数，直接复用。
    # 这里多取一步：拿 daily.heavenlyStem/earthlyBranch
    # （flow_day_mutagen 只返回 mutagen，我们要干支本身）
    # 用 chart 里没有的 birth lunar——调用方应传入。
    # 本阶段：先用 flow_day_mutagen 拿四化，干支由调用方提供或 iztro 直接返回。
    raise NotImplementedError(
        "Z76第一阶段：resolve_flow_day 需要调用方提供出生农历日期才能调 iztro daily。"
        "本模块只钉契约设计，实际跑通留待接入 full_chart(flow_day=...) 时实现。"
    )
