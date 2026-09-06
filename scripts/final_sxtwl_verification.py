#!/usr/bin/env python3
"""
最终确认：sxtwl JD 时间基准
"""

import sxtwl
from datetime import datetime, timezone, timedelta

print("="*70)
print("sxtwl JD 时间基准最终确认")
print("="*70)

JD_EPOCH = 2451545.0
EPOCH_DT = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
BJ_TZ = timezone(timedelta(hours=8))

def jd_to_utc(jd):
    days = jd - JD_EPOCH
    return EPOCH_DT + timedelta(days=days)

def jd_to_bj(jd):
    return jd_to_utc(jd).astimezone(BJ_TZ)

# 多个节气验证
test_cases = [
    (2024, 2, 4, "立春"),
    (2024, 3, 5, "惊蛰"),
    (2024, 4, 4, "清明"),
    (2024, 5, 5, "立夏"),
    (2023, 2, 4, "立春"),
]

print("\n节气象验证:")
for year, month, day, name in test_cases:
    day_obj = sxtwl.fromSolar(year, month, day)
    if day_obj.hasJieQi():
        jd = day_obj.getJieQiJD()
        utc_dt = jd_to_utc(jd)
        bj_dt = jd_to_bj(jd)
        
        print(f"\n{name} {year}:")
        print(f"  JD:            {jd}")
        print(f"  UTC:           {utc_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  北京时间:      {bj_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 关键观察
        int_part = int(jd)
        frac_part = jd - int_part
        frac_seconds = frac_part * 86400
        direct_h = int(frac_seconds // 3600)
        direct_m = int((frac_seconds % 3600) // 60)
        
        print(f"  整数部分→日期: {utc_dt.strftime('%Y-%m-%d')}")
        print(f"  小数直接解读:  {direct_h:02d}:{direct_m:02d}")
        print(f"  标准UTC时间:   {utc_dt.strftime('%H:%M:%S')}")

print("\n" + "="*70)
print("结论")
print("="*70)
print("""
sxtwl 使用标准儒略日(JD)格式：
- 整数部分：UTC日期
- 小数部分：UTC时间（非北京时间）

这意味着：
1. 当前 engine 的 jd_to_datetime() 错误地假设小数部分=北京时间
2. 所有节气时间实际上偏移了8小时
3. 需要修正转换逻辑

修正方案：
  使用标准JD转换：
    utc_dt = EPOCH_DT + timedelta(days=jd - JD_EPOCH)
    bj_dt = utc_dt.astimezone(BJ_TZ)
""")
