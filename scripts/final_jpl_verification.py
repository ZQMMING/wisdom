#!/usr/bin/env python3
"""
最终验证 - 使用NASA JPL Horizons权威数据
来源: Wikipedia引用JPL Horizons On-Line Ephemeris System
"""

from datetime import datetime, timezone, timedelta

# NASA JPL Horizons权威数据 (来自Wikipedia)
# https://en.wikipedia.org/wiki/Lichun
JPL_HORIZONS = {
    # 立春 - UTC时间 (从Wikipedia表格提取)
    (2024, 2, 4): datetime(2024, 2, 4, 8, 27, 0, tzinfo=timezone.utc),  # 08:27 UTC
}

# sxtwl JD值
SXTWL_JD = {
    (2024, 2, 4): 2460345.1853370667,
}

JD_EPOCH = 2451545.0
EPOCH_DT = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
BJ_TZ = timezone(timedelta(hours=8))

def jd_to_utc(jd):
    """标准JD转换"""
    days = jd - JD_EPOCH
    return EPOCH_DT + timedelta(days=days)

def jd_to_bj(jd):
    """转换为北京时间"""
    return jd_to_utc(jd).astimezone(BJ_TZ)

print("="*70)
print("NASA JPL Horizons vs sxtwl JD 对比")
print("="*70)

for key in JPL_HORIZONS.keys():
    jpl_utc = JPL_HORIZONS[key]
    jd = SXTWL_JD[key]
    
    utc_from_jd = jd_to_utc(jd)
    bj_from_jd = jd_to_bj(jd)
    
    print(f"\n{key[0]}年立春:")
    print(f"  NASA JPL Horizons (UTC): {jpl_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  sxtwl JD:                {jd}")
    print(f"  sxtwl JD→UTC:            {utc_from_jd.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  sxtwl JD→BJT:            {bj_from_jd.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查与JPL的差异
    diff_utc = abs((utc_from_jd - jpl_utc).total_seconds())
    
    print(f"\n  差值分析:")
    print(f"    JD→UTC vs JPL: {diff_utc:.0f}秒")
    
    if diff_utc < 60:
        print(f"  ✅ sxtwl JD转换 = JPL Horizons (UTC)")
    else:
        print(f"  ❌ 与JPL Horizons不一致，差值{diff_utc:.0f}秒")

# 检查新华网数据
XINHUA_BJ = datetime(2024, 2, 4, 16, 26, 53)  # 新华网：北京时间16:26:53
XINHUA_UTC = XINHUA_BJ.replace(tzinfo=timezone.utc) - timedelta(hours=8)

print("\n" + "="*70)
print("新华网数据对比")
print("="*70)
print(f"\n新华网报道: 北京时间 {XINHUA_BJ.strftime('%H:%M:%S')}")
print(f"对应UTC:   {XINHUA_UTC.strftime('%H:%M:%S')}")
print(f"sxtwl JD→UTC: {utc_from_jd.strftime('%H:%M:%S')}")

diff_xinhua = abs((utc_from_jd - XINHUA_BJ.replace(tzinfo=timezone.utc)).total_seconds())
print(f"\n  与新华网'北京时间'比较: {diff_xinhua:.0f}秒")

if diff_xinhua < 60:
    print(f"  ✅ sxtwl输出匹配新华网'北京时间'")
    print(f"  ⚠️ 这意味着sxtwl的JD小数部分=北京时间，不是UTC")
else:
    print(f"  ❌ 不匹配")

print("\n" + "="*70)
print("最终结论")
print("="*70)
print("""
关键发现：
1. NASA JPL Horizons权威: 2024立春 = 08:27 UTC
2. sxtwl JD转换(标准):    2024立春 = 16:26 UTC  
3. 新华网报道:              2024立春 = 16:26 '北京时间'
4. 差值: JPL与sxtwl相差约8小时

解释：
- NASA JPL是权威天文数据源，显示UTC时间
- sxtwl输出与新华网报道一致
- 但新华网标注为'北京时间'，实际上可能是UTC时间
- 或者sxtwl库内部有特殊的时间基准处理

需要进一步调查：
1. sxtwl库是否有timezone参数控制输出时区
2. 该库的文档是否说明了时间基准
""")
