#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L4分级用例v11"""
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


print("=== F2从财CONFIRMED（四丑全土）===")
run("从财CONFIRMED(戊丑己丑甲丑戊丑)", "甲", ["丑", "丑", "丑", "丑"], ["戊", "己", "甲", "戊"])

print("\n=== F2从财MID_2（食伤泄财）===")
run("从财MID_2(丙丑己丑甲丑丁丑)", "甲", ["丑", "丑", "丑", "丑"], ["丙", "己", "甲", "丁"])

print("\n=== F3从儿CONFIRMED ===")
run("从儿CONFIRMED(丙午丁巳甲丑戊丑)", "甲", ["午", "巳", "丑", "丑"], ["丙", "丁", "甲", "戊"])

print("\n=== F3从儿MID_2 ===")
run("从儿MID_2(丙午丁巳甲丑己丑)", "甲", ["午", "巳", "丑", "丑"], ["丙", "丁", "甲", "己"])

print("\n=== F4从强CONFIRMED（四子全水）===")
run("从强CONFIRMED(壬子癸子甲子乙丑)", "甲", ["子", "子", "子", "丑"], ["壬", "癸", "甲", "乙"])

print("\n=== F4从强REJECT（官杀破格）===")
run("从强REJECT(壬子癸子甲子庚午)", "甲", ["子", "子", "子", "午"], ["壬", "癸", "甲", "庚"])
