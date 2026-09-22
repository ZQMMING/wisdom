# -*- coding: utf-8 -*-
"""统计baseline里的化气格案例"""
import sys
import io
import json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'D:\shuntian-ziping-p0\baseline_special_20260922.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 统计各格局数量
pattern_count = {}
huaqi_cases = []

for case in data:
    special = case.get('special', '未知')
    pattern_count[special] = pattern_count.get(special, 0) + 1
    
    # 找出化气格案例
    if '化' in special:
        huaqi_cases.append({
            'li': case['li'],
            'key': case['key'],
            'special': special
        })

print("=== baseline格局分布 ===")
for pat, cnt in sorted(pattern_count.items(), key=lambda x: -x[1]):
    print(f"  {pat}: {cnt}条")

print(f"\n=== 化气格案例（共{len(huaqi_cases)}条） ===")
for c in huaqi_cases[:30]:
    print(f"  li={c['li']}, key={c['key']}, special={c['special']}")

# 找专旺格案例
zw_cases = [c for c in data if '格' in c.get('special', '') and '从' not in c.get('special', '')]
print(f"\n=== 专旺格案例（共{len(zw_cases)}条） ===")
for c in zw_cases[:10]:
    print(f"  li={c['li']}, key={c['key']}, special={c['special']}")
