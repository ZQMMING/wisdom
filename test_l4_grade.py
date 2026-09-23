#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L4分级用例v5"""
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


print("=== F2从财补全 ===")
# CONFIRMED→MID_1: 戊戌戊戌甲丑己巳（官杀泄财减项1）
run("从财MID_1(戊戌戊戌甲丑己巳)", "甲", ["戌", "戌", "丑", "巳"], ["戊", "戊", "甲", "己"])

# MID_2: 加辰中乙木余气根→root_qi>0→REJECT？不对，root_qi>0就不从了
# 改：不当令+官杀泄财=2项减项
run("从财MID_2(戊辰戊戌甲丑己巳)", "甲", ["辰", "戌", "丑", "巳"], ["戊", "戊", "甲", "己"])

print("\n=== F3从儿补全 ===")
# MID_1: 丙寅丁巳甲午庚丑（官杀泄气减项1）
run("从儿MID_1(丙寅丁巳甲午庚丑)", "甲", ["寅", "巳", "午", "丑"], ["丙", "丁", "甲", "庚"])

# MID_2: 不当令+官杀泄气=2项减项
run("从儿MID_2(丙寅丁巳甲丑庚丑)", "甲", ["寅", "巳", "丑", "丑"], ["丙", "丁", "甲", "庚"])

print("\n=== F4从强补全 ===")
# MID_2: 戊寅戊午庚辰己未（不当令+官杀泄气=2项）
run("从强MID_2(戊寅戊午庚辰己未)", "庚", ["寅", "午", "辰", "未"], ["戊", "戊", "庚", "己"])

# CONFIRMED: 印比当令，无杂气
# 庚日主，辰月印星土当令，地支辰戌丑未全土
run("从强CONFIRMED(戊辰戊戌庚戌己未)", "庚", ["辰", "戌", "戌", "未"], ["戊", "戊", "庚", "己"])
