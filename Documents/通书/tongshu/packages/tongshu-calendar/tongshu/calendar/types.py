# 历法引擎核心类型定义
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Optional

# ============================================================
# 原始类型
# ============================================================

@dataclass(frozen=True)
class LunarDate:
    """农历日期"""
    year: int          # 农历年（如 2026）
    month: int         # 农历月（1-12）
    day: int           # 农历日（1-30）
    is_leap: bool = False  # 是否闰月

    @property
    def month_display(self) -> str:
        return f"闰{self.month}月" if self.is_leap else f"{self.month}月"

    def __repr__(self) -> str:
        return f"{self.year}年{self.month_display}{self.day}日"


@dataclass(frozen=True)
class GanZhi:
    """干支"""
    stem: str    # 天干（甲-癸）
    branch: str  # 地支（子-亥）

    @property
    def full(self) -> str:
        return self.stem + self.branch

    def __repr__(self) -> str:
        return self.full


@dataclass(frozen=True)
class SolarTerm:
    """节气"""
    name: str          # 中文名
    moment: datetime   # 精确时刻（UTC+8 北京时间）
    is_major: bool     # True=中气, False=节气

    @property
    def month_solar_term(self) -> Optional[str]:
        """返回该节气对应的月气（如 立春→寅月）"""
        return _SOLAR_TERM_TO_MONTH.get(self.name)


_SOLAR_TERM_TO_MONTH = {
    "立春": "寅", "雨水": "寅",
    "惊蛰": "卯", "春分": "卯",
    "清明": "辰", "谷雨": "辰",
    "立夏": "巳", "小满": "巳",
    "芒种": "午", "夏至": "午",
    "小暑": "未", "大暑": "未",
    "立秋": "申", "处暑": "申",
    "白露": "酉", "秋分": "酉",
    "寒露": "戌", "霜降": "戌",
    "立冬": "亥", "小雪": "亥",
    "大雪": "子", "冬至": "子",
    "小寒": "丑", "大寒": "丑",
}


# ============================================================
# 输出类型
# ============================================================

@dataclass
class DayInfo:
    """单日完整历法信息"""
    # 日期
    solar_date: date
    month_day: int          # 年积日（1-365/366）

    # 农历
    lunar: LunarDate

    # 干支（日柱，含年柱月柱时柱）
    day_ganzhi: GanZhi
    year_ganzhi: GanZhi
    month_ganzhi: GanZhi

    # 节气
    solar_term: Optional[str] = None
    next_solar_term: Optional[tuple[str, date]] = None

    # 黄历要素
    xiusu: str = ""            # 二十八宿
    jianchu: str = ""          # 建除十二神
    nayin: str = ""            # 纳音
    zodiac_clash: str = ""     # 冲煞
    peng_taboo: list[str] = field(default_factory=list)
    hour_lucky: list[dict] = field(default_factory=list)
    lucky_gods: list[str] = field(default_factory=list)
    unlucky_gods: list[str] = field(default_factory=list)
    lucky_direction: dict[str, str] = field(default_factory=dict)


@dataclass
class DailyOutput:
    """每日输出（API 响应）"""
    date: str
    lunar: str
    ganzhi: dict
    solar_term: Optional[str]
    moduls: list[dict]
    personal: Optional[dict] = None
    disclaimer: str = "Der Inhalt dient nur der Unterhaltung."