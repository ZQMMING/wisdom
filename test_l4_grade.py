#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L4分级用例v8"""
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
# 戊戌 庚申 甲子 己酉——甲日主，地支戌申子酉无木
run("从财MID_2(戊戌庚申甲子己酉)", "甲", ["戌", "申", "子", "酉"], ["戊", "庚", "甲", "己"])

print("\n=== F3从儿MID_2（巳月火食伤当令）===")
# 丙午 丁巳 甲戌 戊申——甲日主，地支午巳戌申无木
run("从儿MID_2(丙午丁巳甲戌戊申)", "甲", ["午", "巳", "戌", "申"], ["丙", "丁", "甲", "戊"])

print("\n=== F4从强CONFIRMED（root_qi=0，印比成势）===")
# 壬子 癸酉 甲申 乙丑——甲日主，地支子酉申丑无木
run("从强CONFIRMED(壬子癸酉甲申乙丑)", "甲", ["子", "酉", "申", "丑"], ["壬", "癸", "甲", "乙"])
