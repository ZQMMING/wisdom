#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L4 MID_2用例——减项2"""
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


print("=== F1从杀MID_2（减项2：不当令+食伤泄气）===")
# 甲日主，申月金杀当令，酉金食神泄气
run("从杀MID_2(庚申戊寅甲子癸酉)", "甲", ["申", "寅", "子", "酉"], ["庚", "戊", "甲", "癸"])

print("\n=== F2从财MID_2（减项2：不当令+官杀泄财）===")
# 甲日主，子月水旺（不当令），丑土财星透干，酉金官杀泄财
run("从财MID_2(戊子壬子甲丑癸酉)", "甲", ["子", "子", "丑", "酉"], ["戊", "壬", "甲", "癸"])

print("\n=== F3从儿MID_2（减项2：不当令+官杀泄气）===")
# 甲日主，子月水旺（不当令），午火食伤透干，申金官杀泄气
run("从儿MID_2(丙子壬子甲午壬申)", "甲", ["子", "子", "午", "申"], ["丙", "壬", "甲", "壬"])

print("\n=== F4从强MID_2（减项2：不当令+官杀泄气）===")
# 庚日主，子月水旺（不当令），戊己印星透干，午火官杀泄气
run("从强MID_2(戊子壬子庚午壬午)", "庚", ["子", "子", "午", "午"], ["戊", "壬", "庚", "壬"])
