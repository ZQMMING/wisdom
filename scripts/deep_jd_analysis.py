#!/usr/bin/env python3
"""
深入分析 sxtwl JD 时间基准问题
"""

import sxtwl
from datetime import datetime, timezone, timedelta

print("="*60)
print("sxtwl 节气时间基准深度分析")
print("="*60)

# 权威数据源（新华网/中国天文台）:
# 2024年立春: 北京时间 2月4日 16:26:53
# 2023年立春: 北京时间 2月4日 10:42:20

test_cases = [
    # (年, 月, 日, 权威北京时间, 描述)
    (2024, 2, 4, "16:26:53", "立春 2024"),
    (2023, 2, 4, "10:42:20", "立春 2023"),
    (2024, 3, 5, "16:06:00", "惊蛰 2024 (约)"),
    (2024, 4, 4, "20:45:00", "清明 2024 (约)"),
]

for year, month, day, expected_time, desc in test_cases:
    print(f"\n{'─'*60}")
    print(f"测试: {desc} ({year}-{month:02d}-{day:02d})")
    print(f"预期北京时间: {expected_time}")
    
    day_obj = sxtwl.fromSolar(year, month, day)
    
    if day_obj.hasJieQi():
        jd = day_obj.getJieQiJD()
        print(f"sxtwl JD: {jd}")
        
        # Method A: 直接解读为北京时间
        frac = jd - int(jd)
        total_sec = frac * 86400
        h = int(total_sec // 3600)
        m = int((total_sec % 3600) // 60)
        s = int(total_sec % 60)
        method_a = f"{h:02d}:{m:02d}:{s:02d}"
        print(f"Method A (直接解读): {method_a}")
        
        # Method B: 标准JD→UTC→BJT
        jd_epoch = 2451545.0
        dt_epoch = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        days_diff = jd - jd_epoch
        utc_dt = dt_epoch + timedelta(days=days_diff)
        beijing_tz = timezone(timedelta(hours=8))
        bj_dt = utc_dt.astimezone(beijing_tz)
        method_b = bj_dt.strftime("%H:%M:%S")
        method_b_date = bj_dt.strftime("%Y-%m-%d")
        print(f"Method B (标准转换): {method_b_date} {method_b}")
        
        # Method C: 假设sxtwl JD是UTC时间
        method_c = utc_dt.strftime("%H:%M:%S")
        method_c_date = utc_dt.strftime("%Y-%m-%d")
        print(f"Method C (假设UTC): {method_c_date} {method_c}")
        
        # 分析
        print(f"\n分析:")
        if method_a == expected_time:
            print(f"  ✅ Method A 匹配！sxtwl JD 小数部分 = 北京时间")
        elif method_b == expected_time:
            print(f"  ✅ Method B 匹配！sxtwl JD = UTC时间")
        elif method_c == expected_time:
            print(f"  ✅ Method C 匹配！sxtwl JD = UTC时间（与B相同）")
        else:
            print(f"  ❌ 无匹配，需要进一步调查")
            print(f"     预期: {expected_time}, A: {method_a}, B: {method_b}, C: {method_c}")

print("\n" + "="*60)
print("结论")
print("="*60)
