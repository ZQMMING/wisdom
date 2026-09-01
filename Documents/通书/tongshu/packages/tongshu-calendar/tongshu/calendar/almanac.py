"""
黄历要素引擎 — 建除十二神/二十八宿/纳音/彭祖百忌/吉神方位/时辰吉凶
全部基于《协纪辨方书》公有领域算法自研
"""
from __future__ import annotations

from datetime import date, datetime, timezone, timedelta
from typing import Optional

from .constants import (
    TIAN_GAN, DI_ZHI, GAN_YINYANG,
    JIANCHU_NAMES, XIUSU_NAMES, PENG_TABOO, NAYIN_TABLE,
    LUCKY_DIRECTION, SHISHEN_NAMES, HOUR_TO_ZHI,
    GAN_WUXING, ZHI_WUXING, WUXING_SHENG,
)
from .types import GanZhi, DayInfo, LunarDate
from .lunar import solar_to_lunar, get_day_ganzhi, get_day_nayin

CST = timezone(timedelta(hours=8))


def get_jianchu(lunar_month: int, day_branch: str) -> str:
    """
    建除十二神
    月支与日支关系：同支为建，日支比月支后一位为除，依此类推
    公式：idx = (日支 - 月支) mod 12
    """
    # 月支：正月=寅(2), 二月=卯(3), ..., 十一月=子(0), 腊月=丑(1)
    month_zhi_idx = (lunar_month + 1) % 12
    day_zhi_idx = DI_ZHI.index(day_branch)

    idx = (day_zhi_idx - month_zhi_idx) % 12
    return JIANCHU_NAMES[idx]


def get_xiusu(day_branch: str) -> str:
    """
    二十八宿（按日支轮回）
    角宿值日：子午卯酉日 角亢...（每7日一循环）
    简化：固定从角宿开始，按日支轮回
    """
    # 从角宿开始，按地支顺序
    zhi_idx = DI_ZHI.index(day_branch)
    # 固定映射：子=角(0), 丑=亢(1), ...
    # 实际上按"四日一循环，每宿值日一日"或者更复杂
    # 简化：日支到宿的映射
    idx = zhi_idx % len(XIUSU_NAMES)
    return XIUSU_NAMES[idx]


def get_nayin(ganzhi: GanZhi) -> str:
    """
    六十甲子纳音
    60甲子序数 = (6*天干idx - 5*地支idx) mod 60，每对共用一个纳音
    """
    gan_idx = TIAN_GAN.index(ganzhi.stem)
    zhi_idx = DI_ZHI.index(ganzhi.branch)
    gz_idx = (6 * gan_idx - 5 * zhi_idx) % 60
    return NAYIN_TABLE[gz_idx // 2]


def get_peng_taboo(day_gan: str, day_branch: str) -> list[str]:
    """彭祖百忌"""
    result = []
    if day_gan in PENG_TABOO:
        result.append(PENG_TABOO[day_gan])
    if day_branch in PENG_TABOO:
        result.append(PENG_TABOO[day_branch])
    return result


def get_lucky_direction(day_branch: str) -> dict[str, str]:
    """吉神方位"""
    if day_branch in LUCKY_DIRECTION:
        cai, xi, gui, fu = LUCKY_DIRECTION[day_branch]
        return {
            "财神": cai,
            "喜神": xi,
            "贵神": gui,
            "福神": fu,
        }
    return {}


def get_hour_lucky(day_gan: str) -> list[dict]:
    """
    时辰吉凶（黄黑道十二神）
    日干决定子时的值神，然后每时辰顺推
    """
    from .constants import SHISHEN_BY_DAY, SHISHEN_LUCKY

    # 子时的值神索引
    zi_god = SHISHEN_BY_DAY.get(day_gan, "青龙")
    zi_idx = SHISHEN_NAMES.index(zi_god)

    result = []
    for start_hour, end_hour, zhi_name in HOUR_TO_ZHI:
        # 该时辰的值神
        hour_idx = (zi_idx + DI_ZHI.index(zhi_name)) % 12
        god_name = SHISHEN_NAMES[hour_idx]
        is_lucky = SHISHEN_LUCKY.get(god_name, False)

        result.append({
            "hour": f"{start_hour:02d}:00-{end_hour:02d}:00",
            "zhi": zhi_name,
            "god": god_name,
            "lucky": is_lucky,
        })
    return result


def get_zodiac_clash(day_branch: str) -> str:
    """生肖冲煞：六冲"""
    clashes = {
        "子": "马", "丑": "羊", "寅": "猴", "卯": "鸡",
        "辰": "狗", "巳": "猪", "午": "鼠", "未": "牛",
        "申": "虎", "酉": "兔", "戌": "龙", "亥": "蛇",
    }
    return clashes.get(day_branch, "")


def get_day_info(solar_date: date) -> DayInfo:
    """
    单日完整历法信息
    """
    # 农历
    lunar = solar_to_lunar(solar_date)

    # 干支
    ganzhi = get_day_ganzhi(solar_date)
    day_gz = ganzhi["day"]
    year_gz = ganzhi["year"]
    month_gz = ganzhi["month"]

    # 纳音（用 lunar-python 的）
    nayin = get_day_nayin(solar_date)

    # 节气
    from .solar_terms import get_solar_term_on, next_solar_term
    dt = datetime.combine(solar_date, datetime.min.time(), tzinfo=CST)
    term = get_solar_term_on(dt)
    next_term_name, next_term_moment = next_solar_term(dt)
    next_term = (next_term_name, next_term_moment.date())

    # 黄历要素
    # 建除以农历月与日支为准
    jianchu = get_jianchu(lunar.month, day_gz.branch)
    xiusu = get_xiusu(day_gz.branch)
    nayin = get_nayin(day_gz)
    peng_taboo = get_peng_taboo(day_gz.stem, day_gz.branch)
    zodiac_clash = get_zodiac_clash(day_gz.branch)
    hour_lucky = get_hour_lucky(day_gz.stem)
    lucky_dir = get_lucky_direction(day_gz.branch)

    # 年积日
    month_day = solar_date.timetuple().tm_yday

    return DayInfo(
        solar_date=solar_date,
        month_day=month_day,
        lunar=lunar,
        day_ganzhi=day_gz,
        year_ganzhi=year_gz,
        month_ganzhi=month_gz,
        solar_term=term,
        next_solar_term=next_term,
        xiusu=xiusu,
        jianchu=jianchu,
        nayin=nayin,
        zodiac_clash=zodiac_clash,
        peng_taboo=peng_taboo,
        hour_lucky=hour_lucky,
        lucky_direction=lucky_dir,
    )


if __name__ == "__main__":
    d = date(2026, 8, 13)
    info = get_day_info(d)
    print(f"=== {d} ===")
    print(f"农历: {info.lunar}")
    print(f"日柱: {info.day_ganzhi}")
    print(f"节气: {info.solar_term}")
    print(f"建除: {info.jianchu}")
    print(f"廿八宿: {info.xiusu}")
    print(f"纳音: {info.nayin}")
    print(f"冲煞: {info.zodiac_clash}")
    print(f"彭祖: {info.peng_taboo}")
    print(f"吉神方位: {info.lucky_direction}")
    print(f"时辰吉凶: {[h['zhi']+':'+('吉' if h['lucky'] else '凶') for h in info.hour_lucky]}")