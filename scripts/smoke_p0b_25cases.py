# -*- coding: utf-8 -*-
"""P0-b 25条化气格案例冒烟测试"""
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

# 从key解析pillars
def parse_key(key):
    """从八字key解析pillars"""
    # key格式：庚申乙酉庚戌庚辰
    gz_list = [key[i:i+2] for i in range(0, len(key), 2)]
    return {
        'year': list(gz_list[0]),
        'month': list(gz_list[1]),
        'day': list(gz_list[2]),
        'hour': list(gz_list[3])
    }

print("=== P0-b 25条化气格案例冒烟测试 ===\n")

results = []
zhuanwang_count = 0
spec_gap_count = 0
other_count = 0

for i, case in enumerate(huaqi_cases, 1):
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
        
        # 判断落点
        if zw:
            zhuanwang_count += 1
            landing = f"专旺格: {zw} ({zw_state})"
            status = "✅ 归位专旺"
        elif patterns:
            other_count += 1
            landing = f"其他格局: {patterns}"
            status = "⚠️ 其他格局"
        else:
            spec_gap_count += 1
            landing = "无格局"
            status = "❌ spec_gap"
        
        print(f"[{i:2d}/25] li={li:3d} {key}")
        print(f"     旧: {old_special} → 新: {landing}")
        print(f"     {status}")
        if not zw:
            print(f"     gate_debug: {gate_debug}")
        
        results.append({
            'li': li,
            'key': key,
            'old_special': old_special,
            'new_zhuanwang': zw,
            'new_state': zw_state,
            'new_patterns': patterns,
            'gate_debug': gate_debug,
            'status': status
        })
    except Exception as e:
        spec_gap_count += 1
        print(f"[{i:2d}/25] li={li:3d} {key}")
        print(f"     ❌ 错误: {e}")
        results.append({
            'li': li,
            'key': key,
            'old_special': old_special,
            'error': str(e),
            'status': "❌ ERROR"
        })
    print()

# 汇总
print("="*50)
print(f"=== 汇总 ===")
print(f"  归位专旺格: {zhuanwang_count}/25 ({zhuanwang_count/25*100:.1f}%)")
print(f"  其他格局: {other_count}/25 ({other_count/25*100:.1f}%)")
print(f"  spec_gap: {spec_gap_count}/25 ({spec_gap_count/25*100:.1f}%)")
print(f"  门槛: ≥20条归位专旺")

# 保存结果
with open(r'D:\shuntian-ziping-p0\results\smoke_p0b_25cases.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n结果已保存到: results/smoke_p0b_25cases.json")
