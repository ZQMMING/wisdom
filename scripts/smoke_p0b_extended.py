# -*- coding: utf-8 -*-
"""P0-b 扩展冒烟测试：Z1/Z2/Z3三条定向用例"""
import sys
import io
sys.path.insert(0, r'D:\shuntian-ziping-p0')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from engines.common.unified_overview import build_unified_overview

# 扩展测试用例
test_cases = [
    # 原有3条
    {
        'name': '用例1：必成（li=66 庚申乙酉庚戌庚辰）',
        'pillars': {
            'year': ['庚', '申'],
            'month': ['乙', '酉'],
            'day': ['庚', '戌'],
            'hour': ['庚', '辰']
        },
        'expect_pattern': '从革格',
    },
    {
        'name': '用例2：必破（同上但透丙丁）',
        'pillars': {
            'year': ['丙', '申'],
            'month': ['乙', '酉'],
            'day': ['庚', '戌'],
            'hour': ['丙', '午']
        },
        'expect_pattern': None,
    },
    {
        'name': '用例3：必不成（日主甲木，金局全）',
        'pillars': {
            'year': ['甲', '申'],
            'month': ['甲', '酉'],
            'day': ['甲', '戌'],
            'hour': ['甲', '子']
        },
        'expect_pattern': None,
    },
    
    # Z1: 巳酉丑全 + 庚辛透，但月令非申酉（验证_is_ling降级是否真的生效）
    {
        'name': 'Z1：巳酉丑全+庚辛透，月令寅（非当旺）',
        'pillars': {
            'year': ['庚', '巳'],
            'month': ['甲', '寅'],  # 月令寅，非申酉（非金当旺）
            'day': ['庚', '酉'],
            'hour': ['辛', '丑']
        },
        'expect_pattern': '从革格',  # 应判从革格(CANDIDATE/MID)，而不是被拦下
    },
    
    # Z2: 亥卯未全 + 甲乙透（曲直格，跨五行同构性）
    {
        'name': 'Z2：亥卯未全+甲乙透，曲直格',
        'pillars': {
            'year': ['甲', '亥'],
            'month': ['乙', '卯'],  # 月令卯，木当旺
            'day': ['甲', '未'],
            'hour': ['乙', '亥']
        },
        'expect_pattern': '曲直格',
    },
    
    # Z3: 辰戌丑未全 + 戊己透（稼穑格，最容易受木破格干扰）
    {
        'name': 'Z3：辰戌丑未全+戊己透，稼穑格',
        'pillars': {
            'year': ['戊', '辰'],
            'month': ['己', '戌'],  # 月令戌，土当旺
            'day': ['戊', '丑'],
            'hour': ['己', '未']
        },
        'expect_pattern': '稼穑格',
    },
]

print("=== P0-b 扩展冒烟测试（真实排盘） ===\n")

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
