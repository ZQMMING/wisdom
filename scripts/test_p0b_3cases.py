# -*- coding: utf-8 -*-
"""P0-b 三条人工断言测试"""
import sys
import io
sys.path.insert(0, r'D:\shuntian-ziping-p0')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from engines.common.special_pattern import build_special_patterns

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
        'expected': '从革格',
        'expected_state': 'CONFIRMED'
    },
    {
        'name': '用例2：必破（同上但透丙丁）',
        'pillars': {
            'year': ['丙', '申'],
            'month': ['乙', '酉'],
            'day': ['庚', '戌'],
            'hour': ['丙', '午']
        },
        'expected': None,  # 不应成专旺
        'expected_state': None
    },
    {
        'name': '用例3：必不成（日主甲木，金局全）',
        'pillars': {
            'year': ['甲', '申'],
            'month': ['甲', '酉'],
            'day': ['甲', '戌'],
            'hour': ['甲', '子']
        },
        'expected': None,  # 不应成从革格
        'expected_state': None
    }
]

print("=== P0-b 三条人工断言测试 ===\n")

for i, tc in enumerate(test_cases, 1):
    print(f"--- 用例{i}: {tc['name']} ---")
    try:
        # 简化的facts和wp（实际需要完整输入，这里只验证语法和基本逻辑）
        result = build_special_patterns(tc['pillars'], {}, {}, None)
        zw = result.get('zhuanwang')
        zw_state = result.get('zhuanwang_state')
        patterns = [p['name'] for p in result.get('patterns', [])]
        
        print(f"  专旺格: {zw or '无'}")
        print(f"  专旺状态: {zw_state or '无'}")
        print(f"  格局列表: {patterns}")
        
        if tc['expected']:
            if zw == tc['expected'] and zw_state == tc['expected_state']:
                print(f"  ✅ 通过")
            else:
                print(f"  ❌ 失败：预期 {tc['expected']}/{tc['expected_state']}，实际 {zw}/{zw_state}")
        else:
            if not zw:
                print(f"  ✅ 通过（未成专旺）")
            else:
                print(f"  ❌ 失败：预期未成专旺，实际成了 {zw}")
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    print()
