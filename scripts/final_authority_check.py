#!/usr/bin/env python3
"""
最终权威验证 - 修正时区处理
"""

from datetime import datetime, timezone, timedelta

# 新华网官方报道（确认是北京时间）
XINHUA_2024_LICHUN_BJ = datetime(2024, 2, 4, 16, 26, 53)  # 北京时间
XINHUA_2024_LICHUN_UTC = XINHUA_2024_LICHUN_BJ.replace(tzinfo=timezone.utc) - timedelta(hours=8)

print("="*70)
print("权威数据源")
print("="*70)
print(f"\n新华网报道2024年立春:")
print(f"  北京时间: {XINHUA_2024_LICHUN_BJ.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  对应UTC:  {XINHUA_2024_LICHUN_UTC.strftime('%Y-%m-%d %H:%M:%S')}")

# sxtwl输出
JD_2024_LICHUN = 2460345.1853370667
JD_EPOCH = 2451545.0
EPOCH_DT = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
BJ_TZ = timezone(timedelta(hours=8))

def jd_to_utc(jd):
    days = jd - JD_EPOCH
    return EPOCH_DT + timedelta(days=days)

def jd_to_bj(jd):
    return jd_to_utc(jd).astimezone(BJ_TZ)

print("\n" + "="*70)
print("sxtwl输出")
print("="*70)
print(f"\nJD值: {JD_2024_LICHUN}")

utc_from_jd = jd_to_utc(JD_2024_LICHUN)
bj_from_jd = jd_to_bj(JD_2024_LICHUN)

print(f"\n标准JD转换:")
print(f"  UTC:      {utc_from_jd.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  北京时间: {bj_from_jd.strftime('%Y-%m-%d %H:%M:%S')}")

print("\n" + "="*70)
print("对比分析")
print("="*70)

print(f"\n情况1: 新华网'北京时间'是真正的北京时间")
print(f"  期望UTC: {XINHUA_2024_LICHUN_UTC.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  实际UTC: {utc_from_jd.strftime('%Y-%m-%d %H:%M:%S')}")
diff = abs((utc_from_jd - XINHUA_2024_LICHUN_UTC).total_seconds())
print(f"  差值: {diff:.0f}秒")
if diff < 60:
    print(f"  ✅ 匹配!")
else:
    print(f"  ❌ 不匹配")

print(f"\n情况2: 新华网'北京时间'实际是UTC时间")
print(f"  期望UTC: {XINHUA_2024_LICHUN_BJ.replace(tzinfo=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  实际UTC: {utc_from_jd.strftime('%Y-%m-%d %H:%M:%S')}")
diff = abs((utc_from_jd - XINHUA_2024_LICHUN_BJ.replace(tzinfo=timezone.utc)).total_seconds())
print(f"  差值: {diff:.0f}秒")
if diff < 60:
    print(f"  ✅ 匹配! 说明新华网误标时区")
else:
    print(f"  ❌ 不匹配")

print("\n" + "="*70)
print("最终结论")
print("="*70)
print("""
根据验证：
1. sxtwl JD = 2460345.185337
2. 标准JD转换 → UTC = 2024-02-04 16:26:53
3. 新华网报道 → "北京时间16:26:53"

匹配情况：
- 如果新华网是UTC时间: ✅ 完全匹配
- 如果新华网是北京时间: ❌ 差8小时

结论：
- sxtwl使用标准儒略日格式
- 新华网可能误标了时区
- 当前engine的jd_to_datetime()错误解读
""")

# 验证更多数据点
print("\n" + "="*70)
print("额外验证")
print("="*70)

test_cases = [
    (2459979.946074724, "2023-02-04 10:42:20", "2023立春"),
]

for jd_val, expected_bj_str, name in test_cases:
    utc = jd_to_utc(jd_val)
    bj = jd_to_bj(jd_val)
    expected_bj = datetime.strptime(expected_bj_str, '%Y-%m-%d %H:%M:%S')
    
    print(f"\n{name}:")
    print(f"  JD: {jd_val}")
    print(f"  UTC: {utc.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  BJT: {bj.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  期望BJT: {expected_bj.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查是否匹配UTC
    diff_utc = abs((utc - expected_bj.replace(tzinfo=timezone.utc)).total_seconds())
    # 检查是否匹配BJT
    diff_bjt = abs((bj - expected_bj.replace(tzinfo=timezone.utc)).total_seconds())
    
    if diff_utc < 60:
        print(f"  ✅ 匹配UTC (新华网误标)")
    elif diff_bjt < 60:
        print(f"  ✅ 匹配北京时间 (新华网正确)")
    else:
        print(f"  ❌ 不匹配任何情况")
        print(f"     差值(UTC): {diff_utc:.0f}秒, 差值(BJT): {diff_bjt:.0f}秒")
