#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L4 MID_2用例v3——新减项逻辑"""
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


print("=== F2从财MID_2（官杀泄财+天干透官杀）===")
# 甲日主，丑月土财当令，辛金官杀透干，丑中辛金官杀泄气
run("从财MID_2(戊丑己丑甲丑辛丑)", "甲", ["丑", "丑", "丑", "丑"], ["戊", "己", "甲", "辛"])

print("\n=== F3从儿MID_2（财星泄气+天干透财）===")
# 甲日主，巳月火食伤当令，戊土财星透干，食伤生财泄气
run("从儿MID_2(丙午丁巳甲戌戊辰)", "甲", ["午", "巳", "戌", "辰"], ["丙", "丁", "甲", "戊"])

print("\n=== F4从强MID_2（官杀泄气+天干透官杀）===")
# 甲日主，子月水印星当令，庚金官杀透干，官杀克身泄气
run("从强MID_2(壬子丙子甲子庚午)", "甲", ["子", "子", "子", "午"], ["壬", "丙", "甲", "庚"])
