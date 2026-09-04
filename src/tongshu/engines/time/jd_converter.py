"""JD (Julian Date) to DateTime converter.

Provides reliable conversion between JD and datetime for solar term calculations.
Uses Meeus' Astronomical Algorithms, Chapter 7.

sxtwl internally uses Beijing Time (UTC+8) for all JD values.

Version: 1.0.2 (P2.7-G-FIX, corrected algorithm)
"""

from __future__ import annotations

from datetime import datetime, timedelta


def jd_to_datetime(jd: float) -> datetime:
    """Convert Julian Date to datetime (Beijing Time, UTC+8).

    Algorithm: Meeus, Astronomical Algorithms, Ch. 7.
    sxtwl JD values are already in Beijing Time.

    Args:
        jd: Julian Date (e.g., 2460345.1853370667 for 2024-02-04 16:26:53 BJ)

    Returns:
        datetime object representing Beijing Time
    """
    # Use the fractional part of JD for time calculation
    # The fractional part represents the fraction of a day
    frac = jd - int(jd)
    if frac < 0:
        frac += 1.0

    # Integer part is the JD of the date at noon UT
    jd_int = int(jd)

    # Convert JD to Gregorian calendar date (Fliegel-Van Flandern)
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

    # The JD corresponds to noon UT, so:
    # JD integer N corresponds to 12:00 UT of that Gregorian date
    # We need to add the fractional part to get the actual time
    # But since sxtwl uses Beijing Time (UTC+8), not UT

    # Calculate time offset from noon
    # frac is fraction of day since midnight UT
    # noon UT = 0.5 fraction
    total_seconds = (frac - 0.5) * 86400

    # Adjust for Beijing Time (UTC+8)
    total_seconds += 8 * 3600

    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    # Normalize time
    if hours >= 24:
        hours -= 24
        day += 1
    elif hours < 0:
        hours += 24
        day -= 1

    return datetime(year, month, day, hours, minutes, seconds)


def get_nearest_jieqi(sxtwl_day_obj, direction: int, birth_dt: datetime, max_days: int = 32) -> tuple[float, datetime] | None:
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
