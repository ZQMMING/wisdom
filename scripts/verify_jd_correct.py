#!/usr/bin/env python3
"""
正确的 JD 转换验证
使用标准算法：JD 2451545.0 = 2000-01-01 12:00:00 UTC
"""

import sxtwl
from datetime import datetime, timezone, timedelta

# 权威数据（来源：新华网、中国天文年历）
AUTHORITATIVE = {
    (2024, 2, 4): {"name": "立春", "bj": "16:26:53", "note": "北京时间"},
    (2023, 2, 4): {"name": "立春", "bj": "10:42:20", "note": "北京时间"},
}

print("="*70)
print("节气时间权威验证 - 正确算法")
print("="*70)

# 标准 JD  epoch
JD_EPOCH = 2451545.0  # JD for 2000-01-01 12:00:00 UTC
EPOCH_DT = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
BJ_TZ = timezone(timedelta(hours=8))

def jd_to_utc(jd: float) -> datetime:
    """标准 JD → UTC 转换"""
    days = jd - JD_EPOCH
    return EPOCH_DT + timedelta(days=days)

def jd_to_bj(jd: float) -> datetime:
    """JD → 北京时间转换"""
    utc_dt = jd_to_utc(jd)
    return utc_dt.astimezone(BJ_TZ)

for (year, month, day), info in AUTHORITATIVE.items():
    print(f"\n{'─'*70}")
    print(f"{year}年 {info['name']} ({month:02d}-{day:02d})")
    print(f"预期北京时间: {info['bj']}")
    
    day_obj = sxtwl.fromSolar(year, month, day)
    if day_obj.hasJieQi():
        jd = day_obj.getJieQiJD()
        print(f"sxtwl JD: {jd}")
        
        # 正确转换
        utc_dt = jd_to_utc(jd)
        bj_dt = jd_to_bj(jd)
        
        print(f"转换结果:")
        print(f"  UTC:     {utc_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  北京时间: {bj_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 对比
        expected_bj = datetime.strptime(info['bj'], "%H:%M:%S").time()
        actual_bj = bj_dt.time()
        
        if actual_bj == expected_bj:
            print(f"  ✅ 匹配！JD 正确转换为北京时间")
        else:
            print(f"  ❌ 不匹配，差值: {actual_bj - expected_bj}")
            
        # 也检查直接解读（错误方法）
        frac = jd - int(jd)
        total_sec = frac * 86400
        direct_h = int(total_sec // 3600)
        direct_m = int((total_sec % 3600) // 60)
        direct_s = int(total_sec % 60)
        direct_time = f"{direct_h:02d}:{direct_m:02d}:{direct_s:02d}"
        print(f"  直接解读(错误): {direct_time}")
        if direct_time == info['bj']:
            print(f"  ⚠️ 警告：直接解读恰好匹配，但这是巧合！")

print("\n" + "="*70)
print("分析结论")
print("="*70)
print("""
1. sxtwl 返回的 JD 是标准儒略日，需要正确转换
2. 当前 engine 的 jd_to_datetime() 使用错误算法
3. 需要修正转换逻辑

修正方案：
  def jd_to_datetime(jd):
      days = jd - 2451545.0
      utc = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc) + timedelta(days=days)
      return utc  # 返回 UTC-aware datetime
""")
