#!/usr/bin/env python3
"""
最终分析：sxtwl vs 新华网数据
"""

from datetime import datetime, timezone, timedelta

# 权威数据
XINHUA_2024_LICHUN = "2024-02-04 16:26:53"  # 新华网：北京时间
XINHUA_2023_LICHUN = "2023-02-04 10:42:20"  # 新华网：北京时间

# sxtwl输出
JD_2024_LICHUN = 2460345.1853370667
JD_2023_LICHUN = 2459979.946074724

JD_EPOCH = 2451545.0
EPOCH_DT = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
BJ_TZ = timezone(timedelta(hours=8))

def jd_to_utc(jd):
    days = jd - JD_EPOCH
    return EPOCH_DT + timedelta(days=days)

def jd_to_bj(jd):
    return jd_to_utc(jd).astimezone(BJ_TZ)

print("="*70)
print("sxtwl vs 新华网 数据对比")
print("="*70)

print("\n2024年立春:")
print(f"  新华网报道: {XINHUA_2024_LICHUN}")
print(f"  (说明: 新华网称为'北京时间')")

utc_2024 = jd_to_utc(JD_2024_LICHUN)
bj_2024 = jd_to_bj(JD_2024_LICHUN)

print(f"\n  sxtwl JD转换:")
print(f"    标准JD→UTC: {utc_2024.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"    标准JD→BJT: {bj_2024.strftime('%Y-%m-%d %H:%M:%S')}")

print(f"\n  对比分析:")
if utc_2024.strftime('%Y-%m-%d %H:%M:%S') == XINHUA_2024_LICHUN:
    print(f"    ✅ sxtwl标准JD转换 = 新华网'北京时间'")
    print(f"    ⚠️ 结论: 新华网的'北京时间16:26'实际上是UTC时间!")
else:
    print(f"    ❌ 不匹配")

print("\n" + "="*70)
print("关键发现")
print("="*70)
print("""
1. sxtwl使用标准儒略日格式
   - 整数部分 = UTC日期
   - 小数部分 = UTC时间

2. 新华网报道的"北京时间16:26:53"
   - 实际上是UTC时间 16:26:53
   - 正确的北京时间应该是 00:26:53 (次日)

3. 这解释了测试中的矛盾：
   - 测试期望值基于新华网报道
   - 但新华网可能误标了时区
   - 或者sxtwl的输出有特殊含义
""")

# 验证更多节气
print("\n" + "="*70)
print("额外验证：其他节气")
print("="*70)

# 从sxtwl获取更多节气
import sxtwl

test_cases = [
    (2024, 2, 4, "立春"),
    (2024, 3, 5, "惊蛰"),
    (2024, 4, 4, "清明"),
    (2024, 5, 5, "立夏"),
]

for year, month, day, name in test_cases:
    day_obj = sxtwl.fromSolar(year, month, day)
    if day_obj.hasJieQi():
        jd = day_obj.getJieQiJD()
        utc_dt = jd_to_utc(jd)
        bj_dt = jd_to_bj(jd)
        
        print(f"\n{name} {year}:")
        print(f"  sxtwl JD: {jd}")
        print(f"  UTC:      {utc_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  BJT:      {bj_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 检查是否为常见时间
        time_str = utc_dt.strftime('%H:%M:%S')
        if time_str in ["16:26:53", "10:42:20"]:
            print(f"  ⚠️ 与新华网报道一致")
