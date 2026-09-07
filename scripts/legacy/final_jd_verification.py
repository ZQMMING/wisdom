#!/usr/bin/env python3
"""
最终验证 - 确定 sxtwl JD 的时间基准
"""

import sxtwl
from datetime import datetime, timezone, timedelta

print("="*70)
print("sxtwl JD 时间基准最终验证")
print("="*70)

# 权威数据（新华网报道）
# 2024年立春：北京时间 2024-02-04 16:26:53
# 这意味着 UTC 时间应该是 2024-02-04 08:26:53

JD_EPOCH = 2451545.0
EPOCH_DT = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
BJ_TZ = timezone(timedelta(hours=8))

def jd_to_utc(jd):
    days = jd - JD_EPOCH
    return EPOCH_DT + timedelta(days=days)

# 测试 2024立春
year, month, day = 2024, 2, 4
day_obj = sxtwl.fromSolar(year, month, day)
jd = day_obj.getJieQiJD()

print(f"\n2024年立春")
print(f"sxtwl JD: {jd}")
print(f"sxtwl JD 整数部分: {int(jd)}")
print(f"sxtwl JD 小数部分: {jd - int(jd)}")

# 方法1: 标准JD→UTC
utc_dt = jd_to_utc(jd)
print(f"\n方法1 - 标准JD转换:")
print(f"  UTC:     {utc_dt.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  北京:    {utc_dt.astimezone(BJ_TZ).strftime('%Y-%m-%d %H:%M:%S')}")

# 方法2: 直接解读小数部分为时间
frac = jd - int(jd)
total_sec = frac * 86400
h = int(total_sec // 3600)
m = int((total_sec % 3600) // 60)
s = int(total_sec % 60)
direct_time = f"{h:02d}:{m:02d}:{s:02d}"
print(f"\n方法2 - 直接解读小数部分:")
print(f"  时间:    {direct_time}")

# 权威数据
print(f"\n权威数据（新华网）:")
print(f"  北京时间: 2024-02-04 16:26:53")
print(f"  UTC时间:  2024-02-04 08:26:53")

# 分析
print(f"\n{'='*70}")
print("分析:")
print(f"{'='*70}")

# 检查方法1的UTC是否匹配权威UTC
if utc_dt.strftime('%H:%M:%S') == '08:26:53':
    print("✅ 方法1匹配权威UTC！sxtwl JD = 标准儒略日")
elif utc_dt.strftime('%H:%M:%S') == '16:26:53':
    print("⚠️ 方法1得到16:26:53，这是北京时间而非UTC")
    print("   说明sxtwl JD的小数部分直接表示北京时间")

# 检查方法2
if direct_time == '16:26:53':
    print("✅ 方法2匹配！sxtwl JD小数部分 = 北京时间")
elif direct_time == '04:26:53':
    print("❌ 方法2不匹配（得到04:26:53）")

# 关键发现
print(f"\n关键观察:")
print(f"  整数部分 {int(jd)} 对应日期: 2024-02-04")
print(f"  小数部分 {frac:.6f} 对应时间: {direct_time} (直接解读)")
print(f"  标准转换UTC: {utc_dt.strftime('%H:%M:%S')}")

# 结论
if direct_time == '16:26:53':
    print(f"\n✅ 结论: sxtwl JD的小数部分直接表示北京时间（非标准JD）")
    print(f"   建议: 保持现有jd_to_datetime()逻辑，但修正注释说明")
elif utc_dt.strftime('%H:%M:%S') == '08:26:53':
    print(f"\n✅ 结论: sxtwl JD是标准儒略日，需要修正engine转换")
else:
    print(f"\n⚠️ 需要进一步调查")
