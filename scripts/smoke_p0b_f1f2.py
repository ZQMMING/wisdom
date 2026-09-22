# -*- coding: utf-8 -*-
"""P0-b F1/F2验证：从格判定zw化对称性"""
import sys
import io
sys.path.insert(0, r'D:\shuntian-ziping-p0')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from engines.common.unified_overview import build_unified_overview

# F1/F2用例：验证从格判定zw化对称性
test_cases = [
    # F1：日主甲木，庚辛官杀透干，但庚乙合化金使官杀被合
    {
        'name': "F1：日主甲木，庚辛官杀透干，但庚乙合化金",
        'pillars': {
            'year': ['庚', '申'],
            'month': ['乙', '酉'],  # 庚乙合化金，官杀被合
            'day': ['甲', '戌'],
            'hour': ['辛', '丑']
        },
        'expect_no_congsha': True,  # 预期不成从杀格（官杀被合化了）
    },
    
    # F2：日主庚金，财星甲乙透干，但乙庚合化金使财星被合
    # 这其实是li=66的反面验证：同一个乙庚合，在专旺侧算"财不透"，在从格侧也必须算"财不透"
    {
        'name': "F2：日主庚金，财星甲乙透干，但乙庚合化金",
        'pillars': {
            'year': ['甲', '申'],
            'month': ['乙', '酉'],  # 乙庚合化金，财星被合
            'day': ['庚', '戌'],
            'hour': ['甲', '子']
        },
        'expect_zhuanwang': True,  # 预期判专旺格（财星被合化了，不破格）
    },
]

print("=== P0-b F1/F2验证（从格判定zw化对称性） ===\n")

for i, tc in enumerate(test_cases, 1):
    print(f"--- {tc['name']} ---")
    try:
        result = build_unified_overview(tc['pillars'])
        special = result.get('special_pattern', {})
        
        zw = special.get('zhuanwang')
        zw_state = special.get('zhuanwang_state')
        patterns = [p['name'] for p in special.get('patterns', [])]
        gate_debug = special.get('_gate_debug', [])
        
        print(f"  专旺格: {zw or '无'}")
        print(f"  专旺状态: {zw_state or '无'}")
        print(f"  格局列表: {patterns}")
        print(f"  _gate_debug: {gate_debug}")
        
        # 检查是否有从杀格
        has_congsha = any('从杀' in p for p in patterns)
        
        if 'expect_no_congsha' in tc:
            if not has_congsha:
                print(f"  ✅ 不成从杀格（官杀被合化了）")
            else:
                print(f"  ❌ 预期不成从杀格，实际成了从杀格")
        
        if 'expect_zhuanwang' in tc:
            if zw:
                print(f"  ✅ 判专旺格（财星被合化了，不破格）")
            else:
                print(f"  ❌ 预期判专旺格，实际没判")
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    print()
