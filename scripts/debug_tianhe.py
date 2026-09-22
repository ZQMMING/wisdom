# -*- coding: utf-8 -*-
"""调试tian_he：为什么乙庚合没被识别"""
import sys
import io
sys.path.insert(0, r'D:\shuntian-ziping-p0')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from engines.common.l0_fact_builder import build
from engines.common.daymaster_tian_he import build_tian_he

# li=66: 庚申乙酉庚戌庚辰
pillars = {
    'year': ['庚', '申'],
    'month': ['乙', '酉'],
    'day': ['庚', '戌'],
    'hour': ['庚', '辰']
}

facts = build(pillars)
th = build_tian_he(pillars, facts)

print("=== tian_he 调试 ===")
print(f"he_pairs: {th.get('he_pairs', [])}")
print(f"month_qi_wuxing: {th.get('month_qi_wuxing')}")
print(f"huashen_on_month_qi: {th.get('huashen_on_month_qi')}")

# 手动检查乙庚合
print(f"\n=== 手动检查 ===")
print(f"年干: {pillars['year'][0]}")
print(f"月干: {pillars['month'][0]}")
print(f"日干: {pillars['day'][0]}")
print(f"时干: {pillars['hour'][0]}")
print(f"乙庚合: 月干乙 + 日干庚 = {frozenset(('乙', '庚'))}")
