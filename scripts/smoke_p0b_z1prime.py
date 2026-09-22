# -*- coding: utf-8 -*-
"""P0-b Z1'验证：只动月令，不动财官"""
import sys
import io
sys.path.insert(0, r'D:\shuntian-ziping-p0')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from engines.common.unified_overview import build_unified_overview

# Z1'用例：只动月令，不动财官
test_cases = [
    # Z1'-亥月：巳酉丑全 + 庚辛透，月令亥（水当令=食伤，专旺所喜）
    {
        'name': "Z1'-亥月：巳酉丑全+庚辛透，月令亥（食伤泄秀）",
        'pillars': {
            'year': ['庚', '巳'],
            'month': ['壬', '亥'],  # 月令亥，水当令（食伤）
            'day': ['庚', '酉'],
            'hour': ['辛', '丑']
        },
        'expect_pattern': '从革格',  # 应判从革格(CANDIDATE/MID)
    },
    
    # Z1'-丑月：巳酉丑全 + 庚辛透，月令丑（土当令=印，专旺所喜）
    {
        'name': "Z1'-丑月：巳酉丑全+庚辛透，月令丑（印星生身）",
        'pillars': {
            'year': ['庚', '巳'],
            'month': ['己', '丑'],  # 月令丑，土当令（印星）
            'day': ['庚', '酉'],
            'hour': ['辛', '丑']
        },
        'expect_pattern': '从革格',  # 应判从革格(CANDIDATE/MID)
    },
]

print("=== P0-b Z1'验证（只动月令，不动财官） ===\n")

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
        
        if tc['expect_pattern']:
            if zw == tc['expect_pattern']:
                print(f"  ✅ 模式匹配")
            else:
                print(f"  ❌ 模式失败：预期 {tc['expect_pattern']}，实际 {zw}")
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    print()
