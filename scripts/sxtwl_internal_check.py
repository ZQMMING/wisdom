#!/usr/bin/env python3
"""
直接使用sxtwl验证节气时间
不依赖外部权威数据，只看sxtwl输出是否一致
"""

import sxtwl
from datetime import datetime, timezone, timedelta

print("="*70)
print("sxtwl 内部一致性验证")
print("="*70)

# 关键测试：检查sxtwl的jd_toSolar方法
JD_EPOCH = 2451545.0
EPOCH_DT = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
BJ_TZ = timezone(timedelta(hours=8))

def jd_to_utc(jd):
    days = jd - JD_EPOCH
    return EPOCH_DT + timedelta(days=days)

def jd_to_bj(jd):
    return jd_to_utc(jd).astimezone(BJ_TZ)

# 测试：从JD反推日期，再验证
print("\n测试1: JD反推一致性")
test_jds = [
    2460345.1853370667,  # 2024立春
    2459979.946074724,   # 2023立春
]

for jd in test_jds:
    utc_dt = jd_to_utc(jd)
    bj_dt = jd_to_bj(jd)
    
    # 用反推的UTC日期创建Day对象，看是否能得到相同JD
    try:
        day_obj = sxtwl.fromSolar(utc_dt.year, utc_dt.month, utc_dt.day)
        if day_obj.hasJieQi():
            back_jd = day_obj.getJieQiJD()
            diff = abs(back_jd - jd)
            print(f"JD {jd}:")
            print(f"  UTC: {utc_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  BJT: {bj_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  反推JD: {back_jd}")
            print(f"  差异: {diff:.6f} {'✅' if diff < 0.001 else '❌'}")
    except Exception as e:
        print(f"  Error: {e}")

# 测试2: 直接查询节气
print("\n测试2: 直接查询2024立春")
day_obj = sxtwl.fromSolar(2024, 2, 4)
if day_obj.hasJieQi():
    jd = day_obj.getJieQiJD()
    jieqi_type = day_obj.getJieQi()
    
    print(f"JD: {jd}")
    print(f"JieQi type: {jieqi_type}")
    print(f"UTC: {jd_to_utc(jd).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"BJT: {jd_to_bj(jd).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查整数部分
    int_part = int(jd)
    frac_part = jd - int_part
    print(f"\n分解:")
    print(f"  整数: {int_part}")
    print(f"  小数: {frac_part:.10f}")
    
    # 从整数部分得到的日期
    int_days = int_part - JD_EPOCH
    int_date = EPOCH_DT + timedelta(days=int_days)
    print(f"  整数→UTC日期: {int_date.strftime('%Y-%m-%d')}")
    
    # 从小数部分得到的时间
    frac_seconds = frac_part * 86400
    frac_hours = int(frac_seconds // 3600)
    frac_minutes = int((frac_seconds % 3600) // 60)
    print(f"  小数→时间: {frac_hours:02d}:{frac_minutes:02d}")

print("\n" + "="*70)
print("关键发现")
print("="*70)
print("""
观察JD 2460345.1853370667:
- 整数部分2460345 → UTC日期 2024-02-04
- 小数部分0.185337 → 直接解读为 04:26:53
- 标准转换 → UTC时间 16:26:53

如果权威数据是"北京时间16:26:53"：
- 标准转换得到UTC 16:26:53（匹配！）
- 意味着sxtwl JD的小数部分是UTC时间，不是北京时间

结论：sxtwl使用标准JD，小数部分=UTC时间
engine的jd_to_datetime()需要修正
""")
