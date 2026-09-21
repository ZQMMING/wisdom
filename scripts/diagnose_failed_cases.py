#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诊断失败测试案例的special_pattern输出"""
import sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build as l0b
from engines.common.wuxing_power import build_wuxing_power
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.special_pattern import build_special_patterns

K = ('year', 'month', 'day', 'hour')

def gp(s):
    return {K[i // 2]: [s[i], s[i + 1]] for i in range(0, 8, 2)}

CASES = [
    ('丙寅庚寅壬午乙巳', '从财', 'CANDIDATE'),
    ('癸亥乙卯己未丁卯', '从杀', 'CANDIDATE'),
    ('庚子庚辰戊申辛酉', '从儿', 'CONFIRMED'),
    ('壬戌甲辰丁酉己酉', '从财', 'CANDIDATE'),
    ('戊辰壬戌甲辰己巳', '化土', 'CONFIRMED'),
]

for bazi, expect_cat, expect_status in CASES:
    print(f"\n=== {bazi} ===")
    print(f"期望: {expect_cat}/{expect_status}")
    try:
        p = gp(bazi)
        f = l0b(p)
        th = build_tian_he(p, f)
        wp = build_wuxing_power(p, f, th)
        sp = build_special_patterns(p, f, wp, th)
        got = sp.get('cong_type') or sp.get('zhuanwang') or sp.get('hua_qi') or '无'
        state = sp.get('cong_state') or (sp['patterns'][0]['state'] if sp.get('patterns') else '')
        print(f"实际: {got}/{state}")
        # 打印详细patterns
        patterns = sp.get('patterns', [])
        if patterns:
            for pat in patterns:
                print(f"  pattern: {pat}")
        else:
            print("  无patterns")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
