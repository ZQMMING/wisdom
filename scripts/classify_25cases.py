# -*- coding: utf-8 -*-
"""25条化气格案例S1/S2/S3分类统计"""
import sys
import io
import json
sys.path.insert(0, r'D:\shuntian-ziping-p0')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from engines.common.unified_overview import build_unified_overview

# 25条化气格案例（从baseline提取）
huaqi_cases = [
    {"li": 22, "key": "庚寅壬午丁卯癸卯", "old_special": "化木气格"},
    {"li": 66, "key": "庚申乙酉庚戌庚辰", "old_special": "化金气格"},
    {"li": 71, "key": "戊申壬戌庚申乙酉", "old_special": "化金气格"},
    {"li": 114, "key": "庚申乙酉庚戌庚辰", "old_special": "化金气格"},
    {"li": 124, "key": "辛丑癸巳戊申丙辰", "old_special": "化火气格"},
    {"li": 218, "key": "戊午壬戌丁卯癸卯", "old_special": "化木气格"},
    {"li": 247, "key": "壬申丙午癸亥戊午", "old_special": "化火气格"},
    {"li": 255, "key": "乙卯乙酉庚寅壬午", "old_special": "化金气格"},
    {"li": 283, "key": "丁丑壬子辛巳丙申", "old_special": "化水气格"},
    {"li": 284, "key": "戊子戊午癸酉戊午", "old_special": "化火气格"},
    {"li": 314, "key": "丙戌辛丑己卯甲子", "old_special": "化土气格"},
    {"li": 326, "key": "丁卯辛亥丙寅丙申", "old_special": "化水气格"},
    {"li": 338, "key": "乙丑甲申甲辰己巳", "old_special": "化土气格"},
    {"li": 339, "key": "戊辰壬戌甲辰己巳", "old_special": "化土气格"},
    {"li": 341, "key": "己卯丁卯壬午癸卯", "old_special": "化木气格"},
    {"li": 342, "key": "丙戌戊戌癸巳壬戌", "old_special": "化火气格"},
    {"li": 348, "key": "己卯甲戌甲子己巳", "old_special": "化土气格"},
    {"li": 350, "key": "甲寅丁丑甲戌己巳", "old_special": "化土气格"},
    {"li": 352, "key": "甲辰丁卯壬辰辛亥", "old_special": "化木气格"},
    {"li": 356, "key": "己未辛未丙戌戊戌", "old_special": "化水气格"},
    {"li": 412, "key": "甲申癸酉庚子乙酉", "old_special": "化金气格"},
    {"li": 431, "key": "庚午乙酉庚午壬午", "old_special": "化金气格"},
    {"li": 453, "key": "己丑丙子辛酉壬辰", "old_special": "化水气格"},
    {"li": 458, "key": "丙戌己亥甲戌庚午", "old_special": "化土气格"},
    {"li": 485, "key": "己丑庚午戊申癸亥", "old_special": "化火气格"},
]

def parse_key(key):
    gz_list = [key[i:i+2] for i in range(0, len(key), 2)]
    return {
        'year': list(gz_list[0]),
        'month': list(gz_list[1]),
        'day': list(gz_list[2]),
        'hour': list(gz_list[3])
    }

print("=== 25条化气格案例 S1/S2/S3分类 ===\n")

# 去重：按key去重
seen_keys = set()
unique_cases = []
duplicates = []

for case in huaqi_cases:
    if case['key'] in seen_keys:
        duplicates.append(case)
    else:
        seen_keys.add(case['key'])
        unique_cases.append(case)

print(f"原始25条 → 去重后{len(unique_cases)}条")
print(f"重复{len(duplicates)}条: {[d['li'] for d in duplicates]}")
print()

# 分类统计
s1_count = 0  # 局不全（dm_ju=0）
s2_count = 0  # 局全但本行不透（tougan_row=False）
s3_count = 0  # 被gate_ok拦下（官杀闸/财星闸命中）
zw_count = 0   # 归位专旺格
other_count = 0  # 其他格局

s3_cases = []
other_cases_list = []

for case in unique_cases:
    li = case['li']
    key = case['key']
    old_special = case['old_special']
    
    try:
        pillars = parse_key(key)
        result = build_unified_overview(pillars)
        special = result.get('special_pattern', {})
        
        zw = special.get('zhuanwang')
        zw_state = special.get('zhuanwang_state')
        patterns = [p['name'] for p in special.get('patterns', [])]
        gate_debug = special.get('_gate_debug', [])
        
        # 解析gate_debug
        has_dm_ju = any('dm_ju' in g for g in gate_debug)
        has_tougan = any('tougan_row' in g for g in gate_debug)
        has_guan_sha = any('官杀闸' in g for g in gate_debug)
        has_cai_xing = any('财星闸' in g for g in gate_debug)
        
        if zw:
            zw_count += 1
            category = "Z:归位专旺"
        elif patterns:
            other_count += 1
            category = "O:其他格局"
            other_cases_list.append({"li": li, "key": key, "old": old_special, "new": patterns})
        else:
            # S1/S2/S3分类
            if has_dm_ju:
                s1_count += 1
                category = "S1:局不全(dm_ju=0)"
            elif has_tougan:
                s2_count += 1
                category = "S2:局全但本行不透"
            elif has_guan_sha or has_cai_xing:
                s3_count += 1
                category = "S3:被gate_ok拦下"
                s3_cases.append({"li": li, "key": key, "old": old_special, "gate_debug": gate_debug})
            else:
                category = "?:其他"
        
        print(f"li={li:3d} {key}")
        print(f"     旧: {old_special} → 新: {zw or patterns or '无'}")
        print(f"     分类: {category}")
        if not zw and not patterns:
            print(f"     gate_debug: {gate_debug}")
        print()
    except Exception as e:
        print(f"li={li:3d} {key} - 错误: {e}\n")

# 汇总
print("="*60)
print(f"=== 分类汇总（去重后{len(unique_cases)}条） ===")
print(f"  Z: 归位专旺格: {zw_count}条")
print(f"  O: 其他格局: {other_count}条")
print(f"  S1: 局不全(dm_ju=0): {s1_count}条")
print(f"  S2: 局全但本行不透: {s2_count}条")
print(f"  S3: 被gate_ok拦下: {s3_count}条")
print()

print(f"=== S3案例详情（需人工复核） ===")
for c in s3_cases:
    print(f"  li={c['li']:3d} {c['key']} ({c['old']})")
    print(f"       {c['gate_debug']}")
print()

print(f"=== 其他格局案例 ===")
for c in other_cases_list:
    print(f"  li={c['li']:3d} {c['key']}")
    print(f"       {c['old']} → {c['new']}")
