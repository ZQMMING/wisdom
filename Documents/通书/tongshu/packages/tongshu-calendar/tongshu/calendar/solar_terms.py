"""
节气引擎 — 基于天文算法（ephem）自算
太阳黄经精确计算，无需任何外部数据表（商业安全）
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Optional

import ephem

from .constants import ALL_24_JIE_QI, JIEQI_LONGITUDES, JIE_NAMES

CST = timezone(timedelta(hours=8))


def _sun_longitude(date_ephem) -> float:
    """计算给定时刻的太阳视黄经（度）"""
    sun = ephem.Sun(date_ephem)
    ecl = ephem.Ecliptic(sun)
    return math.degrees(ecl.lon)


def _find_solar_term_moment(year: int, target_longitude: float) -> datetime:
    """
    通过二分搜索找到太阳黄经达到 target_longitude 的精确时刻
    返回 UTC datetime
    """
    ephem.epoch = '2000'

    # 粗略估算起点：春分(0°)约在3月20日，每15度约15.22天
    days_from_vernal = ((target_longitude - 0) % 360) / 360 * 365.25
    approx_day = 79 + days_from_vernal
    if approx_day > 365:
        approx_day -= 365

    start_jd = ephem.Date(f"{year}/1/1") + approx_day - 30
    end_jd = ephem.Date(f"{year}/1/1") + approx_day + 30

    for _ in range(64):
        mid_jd = (start_jd + end_jd) / 2
        lon = _sun_longitude(mid_jd)
        diff = (lon - target_longitude + 180) % 360 - 180
        if abs(diff) < 1e-8:
            break
        if diff < 0:
            start_jd = mid_jd
        else:
            end_jd = mid_jd

    # 用 ephem 的字符串格式转换，避免 datetime() 偏差
    import re
    dt_str = str(ephem.Date(mid_jd))
    m = re.match(r'(\d+)/(\d+)/(\d+) (\d+):(\d+):([\d.]+)', dt_str)
    if m:
        y, mo, d, h, mi = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))
        s = float(m.group(6))
        sec = int(s)
        usec = int((s - sec) * 1_000_000)
        utc_moment = datetime(y, mo, d, h, mi, sec, usec, tzinfo=timezone.utc)
    else:
        utc_moment = ephem.Date(mid_jd).datetime().replace(tzinfo=timezone.utc)
    return utc_moment


def get_jieqi_moment(year: int, jieqi_name: str) -> datetime:
    """获取指定年份某个节气的精确时刻（北京时间 UTC+8）"""
    target_lon = JIEQI_LONGITUDES[jieqi_name]
    utc_moment = _find_solar_term_moment(year, target_lon)
    return utc_moment.astimezone(CST)


def get_all_jieqi(year: int) -> dict[str, datetime]:
    """获取指定年份所有24节气时刻"""
    return {name: get_jieqi_moment(year, name) for name in ALL_24_JIE_QI}


def get_solar_term_on(date: datetime) -> Optional[str]:
    """
    返回指定日期当天的节气名（若有）
    注意：日期按北京时间整天判断
    """
    dt_cst = date if date.tzinfo else date.replace(tzinfo=CST)
    # 检查当年和上一年的节气（上年12月的节气可能落在1月）
    for y in (dt_cst.year, dt_cst.year - 1):
        for name, moment in get_all_jieqi(y).items():
            if moment.date() == dt_cst.date():
                return name
    return None


def next_solar_term(date: datetime) -> tuple[str, datetime]:
    """返回指定日期之后的第一个节气（含当天）"""
    dt_cst = date if date.tzinfo else date.replace(tzinfo=CST)
    all_terms: list[tuple[str, datetime]] = []
    for y in (dt_cst.year, dt_cst.year + 1):
        for name, moment in get_all_jieqi(y).items():
            all_terms.append((name, moment))
    all_terms.sort(key=lambda x: x[1])

    for name, moment in all_terms:
        if moment >= dt_cst:
            return name, moment
    return all_terms[-1]


def get_jie_list(year: int) -> list[tuple[str, datetime]]:
    """获取指定年份所有12个'节'（按时间排序）"""
    jie_list = [(name, get_jieqi_moment(year, name)) for name in JIE_NAMES]
    jie_list.sort(key=lambda x: x[1])
    return jie_list


if __name__ == "__main__":
    # 快速自检
    for y in (2024, 2026):
        print(f"=== {y} 立春 ===")
        print(f"  立春: {get_jieqi_moment(y, '立春')}")
        print(f"  冬至: {get_jieqi_moment(y, '冬至')}")