# -*- coding: utf-8 -*-
"""P0-b 冒烟测试：3条人工断言 + _gate_debug调试信息"""
import sys
import io
sys.path.insert(0, r'D:\shuntian-ziping-p0')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from engines.common.unified_overview import build_unified_overview

# 测试用例
test_cases = [
    {
        'name': '用例1：必成（li=66 庚申乙酉庚戌庚辰）',
        'pillars': {
            'year': ['庚', '申'],
            'month': ['乙', '酉'],
            'day': ['庚', '戌'],
            'hour': ['庚', '辰']
        },
        'expect_pattern': '从革格',
        'expect_state': 'CONFIRMED'
    },
    {
        'name': '用例2：必破（同上但透丙丁）',
        'pillars': {
            'year': ['丙', '申'],
            'month': ['乙', '酉'],
            'day': ['庚', '戌'],
            'hour': ['丙', '午']
        },
        'expect_pattern': None,  # 不应成专旺
        'expect_state': None
    },
    {
        'name': '用例3：必不成（日主甲木，金局全）',
        'pillars': {
            'year': ['甲', '申'],
            'month': ['甲', '酉'],
            'day': ['甲', '戌'],
            'hour': ['甲', '子']
        },
        'expect_pattern': None,  # 不应成从革格
        'expect_state': None
    }
]

print("=== P0-b 冒烟测试（真实排盘） ===\n")

for i, tc in enumerate(test_cases, 1):
    print(f"--- 用例{i}: {tc['name']} ---")
    try:
        # 走真实排盘管线
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
        else:
            if not zw:
                print(f"  ✅ 未成专旺")
            else:
                print(f"  ❌ 预期未成专旺，实际成了 {zw}")
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    print()
