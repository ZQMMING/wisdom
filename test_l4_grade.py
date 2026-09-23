#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L4分级用例v4"""
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


print("=== F3从儿分级用例（巳月，火食伤当令）===")
# CONFIRMED: 甲日主，巳月火食伤当令，地支巳午戌丑，无木根
# 天干丙丁甲庚——丙丁火食伤透干，庚金偏财
run("从儿CONFIRMED(丙寅丁巳甲午庚丑)", "甲", ["寅", "巳", "午", "丑"], ["丙", "丁", "甲", "庚"])

# REJECT: 印透破格（壬水印星透干）
run("从儿REJECT(丙寅丁巳甲午壬申)", "甲", ["寅", "巳", "午", "申"], ["丙", "丁", "甲", "壬"])

print("\n=== F4从强用例（印比成势）===")
# F4+: 庚日主，印星土成势，root_qi=0
run("从强MID_2(戊寅戊午庚辰己未)", "庚", ["寅", "午", "辰", "未"], ["戊", "戊", "庚", "己"])

# F4-: 财破印
run("从强MID_2(戊寅戊午庚辰乙卯)", "庚", ["寅", "午", "辰", "未"], ["戊", "戊", "庚", "乙"])
