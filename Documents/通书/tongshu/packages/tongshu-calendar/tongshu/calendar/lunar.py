"""
农历引擎 — 基于 lunar-python（MIT，6tail）
lunar-python 使用天文算法自算，不是 HKO 数据表，商业安全
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Optional

from lunar_python import Solar

from .types import LunarDate, GanZhi
from .constants import TIAN_GAN, DI_ZHI

CST = timezone(timedelta(hours=8))


def solar_to_lunar(solar_date: date) -> LunarDate:
    """
    公历日期 → 农历日期
    使用 lunar-python 引擎（MIT, 6tail）
    lunar-python 闰月以负数表示月份（如 -2 = 闰二月）
    """
    s = Solar.fromYmd(solar_date.year, solar_date.month, solar_date.day)
    l = s.getLunar()
    raw_month = l.getMonth()
    return LunarDate(
        year=l.getYear(),
        month=abs(raw_month),
        day=l.getDay(),
        is_leap=(raw_month < 0),
    )


def lunar_to_solar(lunar: LunarDate) -> date:
    """
    农历日期 → 公历日期
    lunar-python 的 fromYmd 不支持闰月参数，用 Solar 反向查找
    """
    # 从公历日期构建 Lunar，然后检查是否匹配
    from lunar_python import Lunar
    # 遍历该月可能的范围（29-30天）
    # 用 Solar 到 Lunar 的转换来反向查找
    # 先尝试直接用 Lunar.fromYmd
    try:
        l = Lunar.fromYmd(lunar.year, lunar.month, lunar.day)
        s = l.getSolar()
        # 验证是否匹配
        check = solar_to_lunar(date(s.getYear(), s.getMonth(), s.getDay()))
        if check == lunar:
            return date(s.getYear(), s.getMonth(), s.getDay())
    except Exception:
        pass

    # 如果 Lunar.fromYmd 不匹配（如闰月），用 Solar 试探
    # 从该月1号开始试探（大约在公历的20号左右）
    for month_offset in range(1, 13):
        for day in range(1, 32):
            try:
                test_date = date(lunar.year, month_offset, day)
                check = solar_to_lunar(test_date)
                if check == lunar:
                    return test_date
            except (ValueError, OverflowError):
                continue
    raise ValueError(f"无法将 {lunar} 转换为公历日期")


def get_lunar_month_name(month: int, is_leap: bool = False) -> str:
    """农历月份中文名"""
    names = ["", "正月", "二月", "三月", "四月", "五月", "六月",
             "七月", "八月", "九月", "十月", "冬月", "腊月"]
    prefix = "闰" if is_leap else ""
    return prefix + names[month] if 1 <= month <= 12 else ""


def get_lunar_day_name(day: int) -> str:
    """农历日中文名"""
    stems = ["初", "十", "廿", "三十"]
    digits = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
    if day == 10:
        return "初十"
    if day == 20:
        return "二十"
    if day == 30:
        return "三十"
    tens = day // 10
    ones = day % 10
    if tens == 0:
        return f"初{digits[ones]}"
    elif tens == 1:
        return f"十{digits[ones]}"
    elif tens == 2:
        return f"廿{digits[ones]}"
    return str(day)


def get_lunar_year_name(year: int) -> str:
    """农历年干支"""
    gan_idx = (year - 4) % 10
    zhi_idx = (year - 4) % 12
    return TIAN_GAN[gan_idx] + DI_ZHI[zhi_idx]


def get_day_ganzhi(solar_date: date, hour: int = 0, minute: int = 0) -> dict[str, GanZhi]:
    """
    获取日期的四柱干支
    使用 lunar-python 的八字计算
    hour/minute 用于时柱（默认子时）

    晚子时规则（23:00-23:59）：日柱用次日，时柱仍为子时
    """
    # 晚子时：23:00 后日柱算下一天（传统八字排盘法）
    if hour == 23:
        day_date = solar_date + timedelta(days=1)
    else:
        day_date = solar_date

    # 但 lunar-python 需要按原始时刻算 baZi（它内部有子时轮换）
    s = Solar.fromYmdHms(solar_date.year, solar_date.month, solar_date.day, hour, minute, 0)
    l = s.getLunar()
    bazi = l.getBaZi()  # ["丙午", "丙申", "己未", "甲子"]

    # 手动修正日柱（晚子时）
    if hour == 23:
        bazi[2] = Solar.fromYmd(day_date.year, day_date.month, day_date.day).getLunar().getBaZi()[2]

    return {
        "year": GanZhi(stem=bazi[0][0], branch=bazi[0][1]),
        "month": GanZhi(stem=bazi[1][0], branch=bazi[1][1]),
        "day": GanZhi(stem=bazi[2][0], branch=bazi[2][1]),
        "hour": GanZhi(stem=bazi[3][0], branch=bazi[3][1]),
    }


def get_nayin(solar_date: date) -> list[str]:
    """获取日柱纳音（年柱, 月柱, 日柱, 时柱）"""
    s = Solar.fromYmd(solar_date.year, solar_date.month, solar_date.day)
    l = s.getLunar()
    return l.getBaZiNaYin()


def get_day_nayin(solar_date: date) -> str:
    """获取日柱纳音"""
    return get_nayin(solar_date)[2]


if __name__ == "__main__":
    # 自检
    d = date(2026, 8, 13)
    ld = solar_to_lunar(d)
    print(f"{d} → {ld}")
    gz = get_day_ganzhi(d)
    for k, v in gz.items():
        print(f"  {k}: {v}")
    print(f"  纳音: {get_nayin(d)}")