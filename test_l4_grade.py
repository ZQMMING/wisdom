#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L4分级用例v3"""
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


print("=== F2从财分级用例（戌月，无木根）===")
# CONFIRMED: 戊戌 戊戌 甲丑 己巳 → 甲日主，戌月土财当令，无比印
run("从财CONFIRMED(戊戌戊戌甲丑己巳)", "甲", ["戌", "戌", "丑", "巳"], ["戊", "戊", "甲", "己"])

# MID_1: 官杀泄财（寅木官杀？不对，甲日主官杀是金）
# 申金官杀泄气
run("从财MID_1(戊戌戊戌甲丑壬申)", "甲", ["戌", "戌", "丑", "申"], ["戊", "戊", "甲", "壬"])

# MID_2: 不当令+官杀泄财
run("从财MID_2(戊戌戊戌甲辰壬申)", "甲", ["戌", "戌", "辰", "申"], ["戊", "戊", "甲", "壬"])

# REJECT: 印透生身
run("从财REJECT(戊戌戊戌甲丑壬申·印透)", "甲", ["戌", "戌", "丑", "申"], ["戊", "戊", "甲", "壬"])
