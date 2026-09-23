#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""专旺族现状测试"""
import sys
sys.path.insert(0, '.')

from spec.root_qi import shi, calc_root_qi, STEM_WUXING
from engines.cong_ge_gates import cong_ge_pan, WUXING_OF


def run(name, day_stem, branches, stems):
    day_wx = STEM_WUXING[day_stem]
    cong_wx = WUXING_OF[day_wx]
    shi_dict = {}
    for family, wx in cong_wx.items():
        shi_dict[family] = shi(branches, stems, wx, branches[1])
    root_qi_val = calc_root_qi(day_stem, branches, stems)
    result = cong_ge_pan(shi_dict, stems, day_stem, branches[1], root_qi_val)
    print(f"{name}: root_qi={root_qi_val} {result}")
    return result


print("=== 专旺族用例测试 ===")
# 甲寅 丁卯 甲寅 乙亥——甲日主，寅月木当令，比劫成势
run("曲直格(甲寅丁卯甲寅乙亥)", "甲", ["寅", "卯", "寅", "亥"], ["甲", "丁", "甲", "乙"])

# 丙巳 甲午 丙午 甲午——丙日主，午月火当令，比劫成势
run("炎上格(丙巳甲午丙午甲午)", "丙", ["巳", "午", "午", "午"], ["丙", "甲", "丙", "甲"])

# 戊辰 己未 戊戌 癸丑——戊日主，未月土当令，比劫成势
run("稼穑格(戊辰己未戊戌癸丑)", "戊", ["辰", "未", "戌", "丑"], ["戊", "己", "戊", "癸"])

# 庚申 乙酉 庚申 乙酉——庚日主，酉月金当令，比劫成势
run("从革格(庚申乙酉庚申乙酉)", "庚", ["申", "酉", "申", "酉"], ["庚", "乙", "庚", "乙"])

# 壬子 癸亥 壬子 辛亥——壬日主，亥月水当令，比劫成势
run("润下格(壬子癸亥壬子辛亥)", "壬", ["子", "亥", "子", "亥"], ["壬", "癸", "壬", "辛"])
