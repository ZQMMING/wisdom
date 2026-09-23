#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L4分级用例v6"""
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


print("=== F2从财MID_2（申月金旺，财失令）===")
# 戊申 庚申 甲子 己巳
run("从财MID_2(戊申庚申甲子己巳)", "甲", ["申", "申", "子", "巳"], ["戊", "庚", "甲", "己"])

print("\n=== F3从儿MID_2（root_qi=0）===")
# 丙子 丁巳 甲申 庚丑
run("从儿MID_2(丙子丁巳甲申庚丑)", "甲", ["子", "巳", "申", "丑"], ["丙", "丁", "甲", "庚"])

print("\n=== F4从强CONFIRMED（纯印比）===")
# 壬寅 癸卯 甲寅 乙亥——甲日主，卯月木当令，全印比
run("从强CONFIRMED(壬寅癸卯甲寅乙亥)", "甲", ["寅", "卯", "寅", "亥"], ["壬", "癸", "甲", "乙"])
