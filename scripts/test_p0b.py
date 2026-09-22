# -*- coding: utf-8 -*-
"""P0-b验证脚本：测试化气格合并后的专旺格判定"""
import sys
import io
sys.path.insert(0, r'D:\shuntian-ziping-p0')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 测试li=66：庚申乙酉庚戌庚辰（乙庚合+申酉戌全）
from engines.common.special_pattern import build_special_patterns

# 构造测试输入
pillars = {
    'year': ['庚', '申'],
    'month': ['乙', '酉'],
    'day': ['庚', '戌'],
    'hour': ['庚', '辰']
}

# 简化的facts和wp（实际需要完整输入，这里只验证语法）
try:
    result = build_special_patterns(pillars, {}, {}, None)
    print("li=66 测试结果:")
    print(f"  专旺格: {result.get('zhuanwang', '无')}")
    print(f"  专旺状态: {result.get('zhuanwang_state', '无')}")
    print(f"  化气格: {result.get('hua_qi', '无')}")
    print(f"  格局列表: {[p['name'] for p in result.get('patterns', [])]}")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
