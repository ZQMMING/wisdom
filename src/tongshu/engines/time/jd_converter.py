"""JD (Julian Date) to DateTime converter.

Provides reliable conversion between JD and datetime for solar term calculations.
Uses Meeus' Astronomical Algorithms, Chapter 7.

IMPORTANT: sxtwl's JD values need adjustment:
    - sxtwl stores节气时刻 in a custom JD system
    - To convert: subtract 1/3 from sxtwl's JD, then apply standard JD→UTC algorithm
    - Result is UTC time; add 8 hours for Beijing Time

Version: 1.0.5 (P2.7-H18-P0: Correct sxtwl JD offset)
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta


def jd_to_datetime(jd: float) -> datetime:
    """Convert Julian Date to datetime (Beijing Time, UTC+8).

    Algorithm: Meeus, Astronomical Algorithms, Ch. 7.

    sxtwl internally stores节气时刻 with a custom JD offset.
    The conversion requires:
        1. Subtract 1/3 from sxtwl's JD (sxtwl JD = standard JD + 1/3)
        2. Apply standard JD → UTC conversion
        3. Convert UTC to Beijing Time (UTC+8)

    Args:
        jd: Julian Date from sxtwl.getJieQiJD()

    Returns:
        datetime object representing Beijing Time
    """
    # sxtwl JD offset correction
    standard_jd = jd - 1/3

    # Standard JD to UTC conversion (Meeus algorithm)
    standard_jd += 0.5  # JD starts at noon UTC
    Z = int(standard_jd)
    F = standard_jd - Z

    if Z < 2299161:
        A = Z
    else:
        alpha = int((Z - 1867216.25) / 36524.25)
        A = Z + 1 + alpha - int(alpha / 4)

    B = A + 1524
    C = int((B - 122.1) / 365.25)
    D = int(365.25 * C)
    E = int((B - D) / 30.6001)

    day = B - D - int(30.6001 * E) + F
    month = E - 1 if E < 14 else E - 13
    year = C - 4716 if month > 2 else C - 4715

    day_frac = day - int(day)
    hours = int(day_frac * 24)
    minutes = int((day_frac * 24 - hours) * 60)
    seconds = int((day_frac * 1440 - hours * 60 - minutes) * 60)

    # Result is UTC, convert to Beijing Time
    utc_dt = datetime(year, month, int(day), hours, minutes, seconds, tzinfo=timezone.utc)
    beijing_tz = timezone(timedelta(hours=8))
    return utc_dt.astimezone(beijing_tz)


def get_nearest_jieqi(
    sxtwl_day_obj, direction: int, birth_dt: datetime, max_days: int = 32
) -> tuple[float, datetime] | None:
    """Find the nearest Jieqi (节) datetime relative to birth time.

    Args:
        sxtwl_day_obj: sxtwl Day object for testing
        direction: +1 for forward (顺排), -1 for backward (逆排)
        birth_dt: Birth datetime (Beijing Time, timezone-aware)
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
