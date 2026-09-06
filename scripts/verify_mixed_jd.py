#!/usr/bin/env python3
"""
验证 sxtwl JD 的混合时间基准假设
假设：整数部分 = 标准JD日期（UTC），小数部分 = 北京时间
"""

import sxtwl
from datetime import datetime, timezone, timedelta

print("="*70)
print("sxtwl JD 混合时间基准验证")
print("="*70)

JD_EPOCH = 2451545.0
EPOCH_DT = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
BJ_TZ = timezone(timedelta(hours=8))

def standard_jd_to_utc(jd):
    """标准JD转换"""
    days = jd - JD_EPOCH
    return EPOCH_DT + timedelta(days=days)

def mixed_interpretation(jd):
    """混合解释：整数=UTC日期，小数=北京时间"""
    int_part = int(jd)
    frac_part = jd - int_part
    
    # 从整数部分得到UTC日期
    utc_dt = standard_jd_to_utc(float(int_part))
    
    # 从小数部分得到北京时间时间
    total_sec = frac_part * 86400
    h = int(total_sec // 3600)
    m = int((total_sec % 3600) // 60)
    s = int(total_sec % 60)
    
    # 组合：UTC日期 + 北京时间时间
    bj_time = datetime(
        utc_dt.year, utc_dt.month, utc_dt.day,
        h, m, s
    )
    return bj_time

# 测试案例
test_cases = [
    (2024, 2, 4, "立春", "16:26:53"),
    (2023, 2, 4, "立春", "10:42:20"),
]

print("\n测试 sxtwl 节气时间:")
for year, month, day, name, expected_bj in test_cases:
    print(f"\n{'─'*70}")
    print(f"{year}年 {name}")
    print(f"预期北京时间: {expected_bj}")
    
    day_obj = sxtwl.fromSolar(year, month, day)
    jd = day_obj.getJieQiJD()
    
    print(f"sxtwl JD: {jd}")
    
    # 方法1: 标准转换
    utc_dt = standard_jd_to_utc(jd)
    bj_from_utc = utc_dt.astimezone(BJ_TZ)
    print(f"方法1 (标准JD→UTC→BJT): {bj_from_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 方法2: 混合解释
    mixed_bj = mixed_interpretation(jd)
    print(f"方法2 (混合解释):       {mixed_bj.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 对比
    if mixed_bj.strftime('%H:%M:%S') == expected_bj:
        print(f"✅ 方法2匹配！假设成立：整数=UTC日期，小数=北京时间")
    elif bj_from_utc.strftime('%H:%M:%S') == expected_bj:
        print(f"✅ 方法1匹配！sxtwl使用标准JD")
    else:
        print(f"❌ 都不匹配")

print("\n" + "="*70)
print("结论")
print("="*70)
print("""
如果方法2匹配，说明 sxtwl 使用了一种特殊的 JD 表示：
- 整数部分：标准儒略日日期（UTC）
- 小数部分：北京时间的时间部分

这种设计是为了方便中文用户直接读取北京时间。
""")
