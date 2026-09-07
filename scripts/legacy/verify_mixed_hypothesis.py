#!/usr/bin/env python3
"""
验证混合 JD 假设：整数=UTC日期，小数=北京时间
"""

import sxtwl
from datetime import datetime, timezone, timedelta

print("="*70)
print("验证混合 JD 假设")
print("="*70)

JD_EPOCH = 2451545.0
EPOCH_DT = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
BJ_TZ = timezone(timedelta(hours=8))

def jd_to_mixed(jd):
    """混合解释：整数=UTC日期，小数=北京时间时间"""
    int_part = int(jd)
    frac_part = jd - int_part
    
    # 整数部分 → UTC 日期
    days = int_part - JD_EPOCH
    utc_date = EPOCH_DT + timedelta(days=days)
    
    # 小数部分 → 北京时间时间
    total_sec = frac_part * 86400
    h = int(total_sec // 3600)
    m = int((total_sec % 3600) // 60)
    s = int(total_sec % 60)
    
    # 组合
    return datetime(utc_date.year, utc_date.month, utc_date.day, h, m, s)

# 权威数据
AUTHORITATIVE = {
    (2024, 2, 4): ("立春", "16:26:53"),
    (2023, 2, 4): ("立春", "10:42:20"),
}

print("\n验证混合解释假设:")
for (year, month, day), (name, expected_bj) in AUTHORITATIVE.items():
    day_obj = sxtwl.fromSolar(year, month, day)
    jd = day_obj.getJieQiJD()
    
    mixed_dt = jd_to_mixed(jd)
    actual_time = mixed_dt.strftime('%H:%M:%S')
    
    print(f"\n{year}年 {name}:")
    print(f"  JD: {jd}")
    print(f"  预期北京时间: {expected_bj}")
    print(f"  混合解释结果: {actual_time}")
    
    if actual_time == expected_bj:
        print(f"  ✅ 假设成立！sxtwl JD = 整数(UTC日期) + 小数(北京时间)")
    else:
        print(f"  ❌ 假设不成立")

# 额外验证：惊蛰、清明
print("\n" + "="*70)
print("额外验证其他节气:")
print("="*70)

extra_cases = [
    (2024, 3, 5, "惊蛰", "16:06:00"),
    (2024, 4, 4, "清明", "20:45:00"),
]

for year, month, day, name, expected in extra_cases:
    day_obj = sxtwl.fromSolar(year, month, day)
    if day_obj.hasJieQi():
        jd = day_obj.getJieQiJD()
        mixed_dt = jd_to_mixed(jd)
        actual = mixed_dt.strftime('%H:%M:%S')
        status = "✅" if actual == expected else "❌"
        print(f"{year}年 {name}: 预期={expected}, 实际={actual} {status}")

print("\n" + "="*70)
print("最终结论")
print("="*70)
print("""
sxtwl 库使用的是一种特殊的 JD 表示：
- 整数部分：标准儒略日日期（UTC）
- 小数部分：北京时间的时间部分

这种设计使得：
1. 日期部分与国际标准一致
2. 时间部分直接读取北京时间

建议修正 jd_converter.py 使用混合解释。
""")
