#!/usr/bin/env python3
"""
Debug JD conversion to understand the root cause
"""

import sxtwl
from datetime import datetime, timezone, timedelta

# 2024 LiChun (立春) - Authoritative: 2024-02-04 16:26:53 Beijing Time
year, month, day = 2024, 2, 4
day_obj = sxtwl.fromSolar(year, month, day)

print("="*60)
print("sxtwl JD Debug Analysis")
print("="*60)

if day_obj.hasJieQi():
    jd = day_obj.getJieQiJD()
    print(f"sxtwl JD: {jd}")
    print(f"JD integer part: {int(jd)}")
    print(f"JD fractional part: {jd - int(jd)}")
    
    # Method 1: Direct interpretation (what engine does)
    frac = jd - int(jd)
    seconds = frac * 86400
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    print(f"\nMethod 1 - Direct (assumes JD frac = Beijing Time):")
    print(f"  Time: {hours:02d}:{minutes:02d}:{secs:02d}")
    
    # Method 2: Standard JD to UTC conversion
    # JD 2451545.0 = 2000-01-01 12:00:00 UTC
    jd_epoch = 2451545.0
    dt_epoch = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    days_diff = jd - jd_epoch
    utc_dt = dt_epoch + timedelta(days=days_diff)
    print(f"\nMethod 2 - Standard JD to UTC:")
    print(f"  UTC time: {utc_dt}")
    
    # Convert UTC to Beijing
    beijing_tz = timezone(timedelta(hours=8))
    bj_dt = utc_dt.astimezone(beijing_tz)
    print(f"  Beijing time: {bj_dt}")
    
    # Expected from authoritative source
    expected_bj = datetime(2024, 2, 4, 16, 26, 53)
    print(f"\nExpected (authoritative): {expected_bj}")
    
    print(f"\nComparison:")
    print(f"  Method 1 vs Expected: {'✅' if hours == 16 and minutes == 26 else '❌'}")
    print(f"  Method 2 vs Expected: {'✅' if bj_dt.hour == 16 and bj_dt.minute == 26 else '❌'}")
    
    # Let's also check what the correct JD should be
    # If expected is 2024-02-04 16:26:53 Beijing = 2024-02-04 08:26:53 UTC
    expected_utc = datetime(2024, 2, 4, 8, 26, 53, tzinfo=timezone.utc)
    days_from_epoch = (expected_utc - dt_epoch).total_seconds() / 86400
    correct_jd = jd_epoch + days_from_epoch
    print(f"\nCorrect JD for expected time: {correct_jd}")
    print(f"sxtwl JD:                      {jd}")
    print(f"JD difference:                 {jd - correct_jd}")
