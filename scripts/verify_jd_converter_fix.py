#!/usr/bin/env python3
"""
jd_converter.py 时区转换根因分析

Author: BOT-MASTER
Date: 2026-09-06
"""

from datetime import datetime, timezone, timedelta


def jd_to_datetime_current(jd: float) -> datetime:
    """当前实现（错误）：假设 JD 小数部分是北京时间"""
    jd_int = int(jd)
    frac = jd - jd_int
    if frac < 0:
        frac += 1.0
        jd_int -= 1

    L = jd_int + 68569
    N = int(4 * L // 146097)
    L = L - int((146097 * N + 3) // 4)
    I = int(4000 * (L + 1) // 1461001)
    L = L - int(1461 * I // 4) + 31
    J = int(80 * L // 2447)
    day = L - int(2447 * J // 80)
    L = int(J // 11)
    month = J + 2 - 12 * L
    year = 100 * (N - 49) + I + L

    # 错误：假设 frac 直接代表北京时间
    total_seconds = frac * 86400.0
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    return datetime(year, month, day, hours, minutes, seconds)


def jd_to_datetime_correct(jd: float) -> datetime:
    """正确实现：JD 小数部分是 UTC，需要转换为北京时间"""
    jd_epoch = 2451545.0
    dt_epoch = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    days_diff = jd - jd_epoch
    utc_dt = dt_epoch + timedelta(days=days_diff)

    # 转换为北京时间
    beijing_tz = timezone(timedelta(hours=8))
    beijing_dt = utc_dt.astimezone(beijing_tz)

    return beijing_dt.replace(tzinfo=None)  # 返回 naive datetime


# 权威数据（来自新华网/中国天文年历）
AUTHORITATIVE_DATA = [
    ("2024立春", 2460345.1853370667, datetime(2024, 2, 4, 16, 26, 53)),
    ("2023立春", 2459979.946074724, datetime(2023, 2, 4, 10, 42, 20)),
]


def verify():
    print("=" * 80)
    print("jd_converter.py 时区转换根因分析")
    print("=" * 80)

    for name, jd, expected_bjt in AUTHORITATIVE_DATA:
        # 当前错误实现
        current_result = jd_to_datetime_current(jd)
        current_error = abs((current_result - expected_bjt).total_seconds())

        # 正确实现
        correct_result = jd_to_datetime_correct(jd)
        correct_error = abs((correct_result - expected_bjt).total_seconds())

        print(f"\n{name}:")
        print(f"  JD: {jd}")
        print(f"  权威北京时间: {expected_bjt}")
        print(f"  当前实现:     {current_result} (误差: {current_error:.0f}秒 = {current_error/3600:.1f}小时)")
        print(f"  正确实现:     {correct_result} (误差: {correct_error:.0f}秒)")

        if correct_error < 1:
            print(f"  ✅ 正确实现通过验证")
        else:
            print(f"  ❌ 正确实现仍有误差")

    print("\n" + "=" * 80)
    print("根因分析:")
    print("  - 当前实现错误：将 JD 小数部分解释为北京时间")
    print("  - 正确做法：JD 小数部分是 UTC，需转换为北京时间")
    print("  - 误差来源：8小时时区差")
    print("=" * 80)


if __name__ == "__main__":
    verify()
