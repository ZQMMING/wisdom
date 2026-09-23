#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L4 MID_2用例v2——丑月土当令"""
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


print("=== F2从财MID_2（丑月土当令，减项2）===")
# 甲日主，丑月土财当令，天干丙丁火食伤泄财，酉金官杀泄财
run("从财MID_2(丙丁己丑甲丑丁酉)", "甲", ["丑", "丑", "丑", "酉"], ["丙", "丁", "甲", "丁"])

print("\n=== F1从杀MID_2（酉月金当令，减项2）===")
# 甲日主，酉月金杀当令，天干丙丁火食伤制杀，午火食伤泄气
run("从杀MID_2(丙申丁酉甲午庚午)", "甲", ["申", "酉", "午", "午"], ["丙", "丁", "甲", "庚"])
