#!/usr/bin/env python3
"""
分析新华网数据与sxtwl输出的矛盾
"""

import sxtwl
from datetime import datetime, timezone, timedelta

print("="*70)
print("新华网 vs sxtwl 时间对比分析")
print("="*70)

JD_EPOCH = 2451545.0
EPOCH_DT = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
BJ_TZ = timezone(timedelta(hours=8))

def jd_to_utc(jd):
    days = jd - JD_EPOCH
    return EPOCH_DT + timedelta(days=days)

def jd_to_bj_from_utc(jd):
    return jd_to_utc(jd).astimezone(BJ_TZ)

# 新华网报道的2024年立春时间
# "北京时间2月4日16时27分"
XINHUA_BJ = datetime(2024, 2, 4, 16, 26, 53)
XINHUA_UTC = XINHUA_BJ - timedelta(hours=8)

print(f"\n新华网报道:")
print(f"  北京时间: {XINHUA_BJ.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  UTC时间:  {XINHUA_UTC.strftime('%Y-%m-%d %H:%M:%S')}")

# sxtwl输出
day_obj = sxtwl.fromSolar(2024, 2, 4)
jd = day_obj.getJieQiJD()

print(f"\nsxtwl输出:")
print(f"  JD: {jd}")

utc_from_jd = jd_to_utc(jd)
bj_from_jd = jd_to_bj_from_utc(jd)

print(f"  标准JD→UTC: {utc_from_jd.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  标准JD→BJT: {bj_from_jd.strftime('%Y-%m-%d %H:%M:%S')}")

# 分析
print(f"\n{'='*70}")
print("矛盾分析")
print("="*70)

if abs(utc_from_jd - XINHUA_BJ).total_seconds() < 10:
    print("✅ 匹配: sxtwl JD 小数部分 = 北京时间")
    print("   即: JD的小数部分直接表示北京时间时间")
elif abs(bj_from_jd - XINHUA_BJ).total_seconds() < 10:
    print("✅ 匹配: sxtwl JD 是标准儒略日，输出北京时间")
    print("   即: 标准JD转换后得到北京时间")
else:
    print("❌ 不匹配任何情况")
    
    # 计算差值
    diff_utc = utc_from_jd - XINHUA_BJ
    diff_bj = bj_from_jd - XINHUA_BJ
    
    print(f"\n差值分析:")
    print(f"  sxtwl UTC - 新华网BJ: {diff_utc}")
    print(f"  sxtwl BJT - 新华网BJ: {diff_bj}")
    
    # 如果差值是+8小时，说明sxtwl输出的是UTC
    if abs(diff_bj.total_seconds() - 8*3600) < 10:
        print(f"\n⚠️ 假设: sxtwl输出UTC时间，但新华网报道的是UTC时间")
        print(f"   即：新华网'北京时间16:26'实际是UTC时间")
    elif abs(diff_utc.total_seconds() + 8*3600) < 10:
        print(f"\n⚠️ 假设: sxtwl输出北京时间")
        print(f"   即：JD小数部分直接表示北京时间")

# 额外测试：2023年立春
print(f"\n{'='*70}")
print("额外验证：2023年立春")
print("="*70)

XINHUA_2023_BJ = datetime(2023, 2, 4, 10, 42, 20)
XINHUA_2023_UTC = XINHUA_2023_BJ - timedelta(hours=8)

print(f"\n新华网报道:")
print(f"  北京时间: {XINHUA_2023_BJ.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  UTC时间:  {XINHUA_2023_UTC.strftime('%Y-%m-%d %H:%M:%S')}")

day_obj_2023 = sxtwl.fromSolar(2023, 2, 4)
jd_2023 = day_obj_2023.getJieQiJD()

print(f"\nsxtwl输出:")
print(f"  JD: {jd_2023}")

utc_2023 = jd_to_utc(jd_2023)
bj_2023 = jd_to_bj_from_utc(jd_2023)

print(f"  标准JD→UTC: {utc_2023.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  标准JD→BJT: {bj_2023.strftime('%Y-%m-%d %H:%M:%S')}")

# 检查匹配
if abs(utc_2023 - XINHUA_2023_BJ).total_seconds() < 10:
    print(f"\n✅ 匹配: sxtwl JD 小数部分 = 北京时间")
elif abs(bj_2023 - XINHUA_2023_BJ).total_seconds() < 10:
    print(f"\n✅ 匹配: sxtwl JD 是标准儒略日")
else:
    diff = bj_2023 - XINHUA_2023_BJ
    print(f"\n❌ 不匹配，差值: {diff}")
