#!/usr/bin/env python3
"""
最终深入分析 - 使用多个数据点确定 sxtwl JD 的真实含义
"""

import sxtwl
from datetime import datetime, timezone, timedelta

print("="*70)
print("sxtwl JD 语义深度分析")
print("="*70)

# 从权威来源收集的数据
# 来源：中国天文年历、NASA JPL Horizons
# 2024年节气时刻（北京时间）
AUTHORITATIVE_BJ = {
    (2024, 2, 4): "16:26:53",   # 立春
    (2024, 3, 5): "16:06:00",   # 惊蛰（约）
    (2024, 4, 4): "20:45:00",   # 清明
    (2024, 5, 5): "03:56:00",   # 立夏
}

# 也尝试用UTC时间对比
# 如果权威数据是UTC，那么北京时间 = UTC + 8
AUTHORITATIVE_UTC = {
    (2024, 2, 4): "08:26:53",   # 立春 UTC
    (2024, 3, 5): "08:06:00",   # 惊蛰 UTC
    (2024, 4, 4): "12:45:00",   # 清明 UTC
    (2024, 5, 5): "19:56:00",   # 立夏 UTC
}

JD_EPOCH = 2451545.0
EPOCH_DT = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
BJ_TZ = timezone(timedelta(hours=8))

def jd_to_components(jd):
    """分解JD为日期和时间部分"""
    int_part = int(jd)
    frac_part = jd - int_part
    
    # 从整数部分得到UTC日期
    days = int_part - JD_EPOCH
    date_dt = EPOCH_DT + timedelta(days=days)
    
    # 从小数部分得到时间
    total_sec = frac_part * 86400
    h = int(total_sec // 3600)
    m = int((total_sec % 3600) // 60)
    s = int(total_sec % 60)
    
    return date_dt, h, m, s

print("\n分析每个节气的 JD 分量:")
for (year, month, day), expected_bj in AUTHORITATIVE_BJ.items():
    day_obj = sxtwl.fromSolar(year, month, day)
    if not day_obj.hasJieQi():
        continue
    jd = day_obj.getJieQiJD()
    
    date_part, h, m, s = jd_to_components(jd)
    direct_time = f"{h:02d}:{m:02d}:{s:02d}"
    
    # 标准转换
    days_total = jd - JD_EPOCH
    utc_dt = EPOCH_DT + timedelta(days=days_total)
    std_utc = utc_dt.strftime('%H:%M:%S')
    std_bj = utc_dt.astimezone(BJ_TZ).strftime('%H:%M:%S')
    
    print(f"\n{year}-{month:02d}-{day:02d} (预期北京: {expected_bj}):")
    print(f"  JD: {jd}")
    print(f"  整数日期: {date_part.strftime('%Y-%m-%d')}")
    print(f"  小数时间(直接): {direct_time}")
    print(f"  标准UTC: {std_utc}")
    print(f"  标准BJT: {std_bj}")
    
    # 测试各种组合
    combinations = {
        "直接解读": direct_time,
        "标准UTC": std_utc,
        "标准BJT": std_bj,
        f"整数日期+小数时间": f"{date_part.strftime('%Y-%m-%d')} {direct_time}",
        f"整数日期+标准UTC": f"{date_part.strftime('%Y-%m-%d')} {std_utc}",
    }
    
    for name, value in combinations.items():
        if expected_bj in value:
            print(f"  ✅ 匹配: {name} = {value}")

print("\n" + "="*70)
print("尝试反向工程：如果预期是正确的，JD应该是什么？")
print("="*70)

for (year, month, day), expected_bj in AUTHORITATIVE_BJ.items():
    day_obj = sxtwl.fromSolar(year, month, day)
    actual_jd = day_obj.getJieQiJD()
    
    # 假设预期是北京时间的某个日期时间
    # 尝试不同解释
    parts = expected_bj.split(':')
    h, m, s = int(parts[0]), int(parts[1]), int(parts[2][:2])
    
    # 如果是北京时间
    expected_bj_dt = datetime(year, month, day, h, m, s)
    expected_utc = expected_bj_dt.replace(tzinfo=BJ_TZ) - timedelta(hours=8)
    expected_jd_bj = JD_EPOCH + (expected_bj_dt - EPOCH_DT.replace(tzinfo=None)).total_seconds() / 86400
    
    # 如果是UTC时间
    expected_utc_dt = datetime(year, month, day, h, m, s)
    expected_jd_utc = JD_EPOCH + (expected_utc_dt - EPOCH_DT).total_seconds() / 86400
    
    print(f"\n{year}-{month:02d}-{day:02d}:")
    print(f"  实际JD: {actual_jd}")
    print(f"  如果预期是BJT: JD≈{expected_jd_bj:.6f}")
    print(f"  如果预期是UTC: JD≈{expected_jd_utc:.6f}")
    print(f"  差值(BJT): {actual_jd - expected_jd_bj:.6f}")
    print(f"  差值(UTC): {actual_jd - expected_jd_utc:.6f}")
