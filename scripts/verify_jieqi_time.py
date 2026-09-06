#!/usr/bin/env python3
"""
节气时间 Authority Verification Script
验证 sxtwl 返回的时间基准
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import sxtwl
from datetime import datetime, timezone, timedelta


def jd_to_datetime(jd: float) -> datetime:
    """Convert JD to Beijing Time datetime (from jd_converter.py)"""
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

    total_seconds = frac * 86400.0
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    return datetime(year, month, day, hours, minutes, seconds)


def analyze_jieqi(year: int, month: int, day: int, name: str):
    """Analyze a specific solar term date"""
    print(f"\n{'='*60}")
    print(f"分析: {name} ({year}-{month:02d}-{day:02d})")
    print(f"{'='*60}")
    
    day_obj = sxtwl.fromSolar(year, month, day)
    
    print(f"hasJieQi: {day_obj.hasJieQi()}")
    
    if day_obj.hasJieQi():
        jd = day_obj.getJieQiJD()
        print(f"sxtwl JD: {jd}")
        
        # Method 1: Convert JD to UTC using standard formula
        # JD 2451545.0 = 2000-01-01 12:00:00 UTC
        jd_epoch = 2451545.0
        dt_epoch = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        days_diff = jd - jd_epoch
        utc_dt = dt_epoch + timedelta(days=days_diff)
        print(f"\nStandard JD→UTC conversion:")
        print(f"  UTC time: {utc_dt}")
        
        # Convert to Beijing time
        beijing_tz = timezone(timedelta(hours=8))
        beijing_dt = utc_dt.astimezone(beijing_tz)
        print(f"  Beijing time: {beijing_dt}")
        
        # Method 2: Use engine's jd_to_datetime (assumes Beijing Time)
        from tongshu.engines.time.jd_converter import jd_to_datetime as engine_jd_to_datetime
        engine_dt = engine_jd_to_datetime(jd)
        print(f"\nEngine jd_to_datetime (assumes Beijing):")
        print(f"  Beijing time: {engine_dt}")
        
        # Check if there's an 8-hour offset
        if utc_dt.tzinfo is None:
            utc_dt = utc_dt.replace(tzinfo=timezone.utc)
        beijing_from_standard = utc_dt.astimezone(beijing_tz)
        
        print(f"\nComparison:")
        print(f"  Standard JD→UTC→BJT: {beijing_from_standard}")
        print(f"  Engine BJT direct:    {engine_dt}")
        
        if beijing_from_standard.hour == engine_dt.hour and beijing_from_standard.minute == engine_dt.minute:
            print(f"  ✅ MATCH: Engine correctly interprets JD as Beijing Time")
        else:
            print(f"  ❌ MISMATCH: 8-hour offset detected!")
            print(f"  Difference: {engine_dt - beijing_from_standard.replace(tzinfo=None)}")
        
        # Get solar term name if possible
        jieqi_type = day_obj.getJieQi()
        print(f"\nJieQi type index: {jieqi_type}")
        
        return {
            "jd": jd,
            "utc": utc_dt,
            "beijing_standard": beijing_from_standard,
            "beijing_engine": engine_dt,
            "match": beijing_from_standard.hour == engine_dt.hour,
        }
    
    return None


def main():
    print("="*60)
    print("节气时间 Authority Verification")
    print("="*60)
    
    # Test cases: LiChun (立春), JingZhe (惊蛰), QingMing (清明) for 2024
    test_cases = [
        (2024, 2, 4, "立春 LiChun 2024"),
        (2024, 3, 5, "惊蛰 JingZhe 2024"),
        (2024, 4, 4, "清明 QingMing 2024"),
        (2024, 5, 5, "立夏 LiXia 2024"),
        (2023, 2, 4, "立春 LiChun 2023"),
    ]
    
    results = []
    for year, month, day, name in test_cases:
        result = analyze_jieqi(year, month, day, name)
        if result:
            results.append(result)
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for r in results:
        status = "✅" if r["match"] else "❌"
        print(f"{status} JD={r['jd']:.6f}")
        print(f"   UTC: {r['utc']}")
        print(f"   BJT (std): {r['beijing_standard']}")
        print(f"   BJT (eng): {r['beijing_engine']}")
    
    # Conclusion
    print(f"\n{'='*60}")
    all_match = all(r["match"] for r in results)
    if all_match:
        print("✅ CONCLUSION: sxtwl stores节气时刻 in Beijing Time (UTC+8)")
        print("   Engine's jd_to_datetime is CORRECT")
    else:
        print("❌ CONCLUSION: Time zone mismatch detected!")
        print("   Need to investigate further")
    print(f"{'='*60}")
    
    return 0 if all_match else 1


if __name__ == "__main__":
    sys.exit(main())
