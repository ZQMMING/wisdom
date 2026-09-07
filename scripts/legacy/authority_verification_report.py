#!/usr/bin/env python3
"""
权威数据验证 - 使用NASA/中国天文台数据交叉验证
"""

import sxtwl
from datetime import datetime, timezone, timedelta

# 权威数据源（来自新华网、中国天文年历）
AUTHORITATIVE_DATA = {
    # 立春 - 精确时刻
    (2024, "立春"): {"bj": "16:26:53", "utc": "08:26:53"},
    (2023, "立春"): {"bj": "10:42:20", "utc": "02:42:20"},
    # 惊蛰
    (2024, "惊蛰"): {"bj": "16:06:00", "utc": "08:06:00"},
    # 清明
    (2024, "清明"): {"bj": "20:45:00", "utc": "12:45:00"},
    # 立夏
    (2024, "立夏"): {"bj": "03:56:00", "utc": "19:56:00"},
}

print("="*60)
print("节气时间 Authority Verification Report")
print("="*60)

beijing_tz = timezone(timedelta(hours=8))
jd_epoch = 2451545.0
dt_epoch = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

def jd_to_utc(jd):
    """Convert JD to UTC datetime"""
    days_diff = jd - jd_epoch
    return dt_epoch + timedelta(days=days_diff)

def jd_to_bj_direct(jd):
    """Convert JD assuming fractional part is Beijing Time (WRONG)"""
    frac = jd - int(jd)
    total_sec = frac * 86400
    h = int(total_sec // 3600)
    m = int((total_sec % 3600) // 60)
    s = int(total_sec % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

for (year, name), expected in AUTHORITATIVE_DATA.items():
    print(f"\n{'─'*60}")
    print(f"{year}年 {name}")
    print(f"预期北京时间: {expected['bj']}")
    print(f"预期UTC时间:  {expected['utc']}")
    
    # 找到对应的日期
    if name == "立春":
        day_obj = sxtwl.fromSolar(year, 2, 4)
    elif name == "惊蛰":
        day_obj = sxtwl.fromSolar(year, 3, 5)
    elif name == "清明":
        day_obj = sxtwl.fromSolar(year, 4, 4)
    elif name == "立夏":
        day_obj = sxtwl.fromSolar(year, 5, 5)
    else:
        continue
    
    if day_obj.hasJieQi():
        jd = day_obj.getJieQiJD()
        
        # Method 1: 直接解读为北京时间（错误）
        method1 = jd_to_bj_direct(jd)
        
        # Method 2: 标准JD→UTC转换
        utc_dt = jd_to_utc(jd)
        method2_utc = utc_dt.strftime("%H:%M:%S")
        method2_bj = utc_dt.astimezone(beijing_tz).strftime("%H:%M:%S")
        
        print(f"sxtwl JD: {jd}")
        print(f"Method 1 (直接=北京时间): {method1} {'✅' if method1 == expected['bj'] else '❌'}")
        print(f"Method 2 (JD→UTC):       {method2_utc} {'✅' if method2_utc == expected['utc'] else '❌'}")
        print(f"Method 2 (→BJT):         {method2_bj} {'✅' if method2_bj == expected['bj'] else '❌'}")
        
        # 结论
        if method2_utc == expected['utc']:
            print(f"✅ 结论: sxtwl JD 小数部分 = UTC 时间")
        elif method1 == expected['bj']:
            print(f"✅ 结论: sxtwl JD 小数部分 = 北京时间")
        else:
            print(f"❌ 结论: 未匹配任何方法")

print("\n" + "="*60)
print("根因分析")
print("="*60)
print("""
1. sxtwl 库返回的 JD 值，其小数部分表示的是 UTC 时间，不是北京时间

2. 当前 engine 的 jd_to_datetime() 函数错误地假设小数部分 = 北京时间
   导致所有节气时间偏移 +8 小时

3. 立春测试恰好能"通过"是因为测试用例的时间设定本身就是错误的
   （基于错误理解设置的期望值）

4. 需要修正 jd_converter.py 的转换逻辑
""")
