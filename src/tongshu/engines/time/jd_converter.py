"""JD (Julian Date) to DateTime converter.

Provides reliable conversion between JD and datetime for solar term calculations.
Uses Meeus' Astronomical Algorithms, Chapter 7.

IMPORTANT: sxtwl's JD values represent Beijing Time (UTC+8), not UT.
The fractional part of JD represents time from noon UT, so we need to:
1. Convert fractional JD to time of day in UT
2. Add 8 hours to get Beijing Time

Version: 1.0.3 (P2.7-H17-P0: Fixed timezone handling)
"""

from __future__ import annotations

from datetime import datetime, timedelta


def jd_to_datetime(jd: float) -> datetime:
    """Convert Julian Date to datetime (Beijing Time, UTC+8).

    Algorithm: Meeus, Astronomical Algorithms, Ch. 7.

    sxtwl internally stores节气时刻 in Beijing Time (UTC+8).
    JD fractional part represents time from noon UT.

    Args:
        jd: Julian Date (e.g., 2460345.1853370667 for 2024-02-04 04:26:53 BJ)

    Returns:
        datetime object representing Beijing Time
    """
    # Step 1: Extract date from JD integer part
    jd_int = int(jd)
    frac = jd - jd_int
    if frac < 0:
        frac += 1.0
        jd_int -= 1

    # Fliegel-Van Flandern algorithm to convert JD to Gregorian date
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

    # Step 2: Convert fractional JD to time
    # JD fractional part is time from noon UT
    # frac = 0.0 → 00:00 UT (midnight)
    # frac = 0.5 → 12:00 UT (noon)
    # frac = 1.0 → 24:00 UT (= 00:00 next day)

    # Convert fraction to seconds from noon UT
    seconds_from_noon_ut = frac * 86400.0

    # Adjust to seconds from midnight UT
    seconds_from_midnight_ut = seconds_from_noon_ut - 43200.0  # 12 hours = 43200 seconds

    # Handle day wraparound
    if seconds_from_midnight_ut < 0:
        seconds_from_midnight_ut += 86400.0
        day -= 1
    elif seconds_from_midnight_ut >= 86400.0:
        seconds_from_midnight_ut -= 86400.0
        day += 1

    # Convert to hours, minutes, seconds
    hours = int(seconds_from_midnight_ut // 3600)
    minutes = int((seconds_from_midnight_ut % 3600) // 60)
    seconds = int(seconds_from_midnight_ut % 60)

    # Step 3: Add 8 hours for Beijing Time (UTC+8)
    hours += 8
    if hours >= 24:
        hours -= 24
        day += 1
    elif hours < 0:
        hours += 24
        day -= 1

    return datetime(year, month, day, hours, minutes, seconds)


def get_nearest_jieqi(
    sxtwl_day_obj, direction: int, birth_dt: datetime, max_days: int = 32
) -> tuple[float, datetime] | None:
    """Find the nearest Jieqi (节) datetime relative to birth time.

    Args:
        sxtwl_day_obj: sxtwl Day object for testing
        direction: +1 for forward (顺排), -1 for backward (逆排)
        birth_dt: Birth datetime (Beijing Time)
        max_days: Maximum search range

    Returns:
        Tuple of (jd_of_jieqi, jieqi_dt) or None
    """
    import sxtwl

    for i in range(1, max_days + 1):
        if direction == +1:
            test_dt = birth_dt + timedelta(days=i)
        else:
            test_dt = birth_dt - timedelta(days=i)

        day_obj = sxtwl.fromSolar(test_dt.year, test_dt.month, test_dt.day)

        if day_obj.hasJieQi():
            jieqi_jd = day_obj.getJieQiJD()
            jieqi_dt = jd_to_datetime(jieqi_jd)
            return jieqi_jd, jieqi_dt

    return None
