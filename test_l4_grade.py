#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L4分级用例验证"""
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
    print(f"{name}: {result}")
    return result


print("=== F1从杀分级用例 ===")
# CONFIRMED: 庚申辛酉甲子辛丑（已有C4）
run("从杀CONFIRMED(庚申辛酉甲子辛丑)", "甲", ["申", "酉", "子", "丑"], ["庚", "辛", "甲", "辛"])

# MID_1: 癸巳乙卯己亥癸酉（已有C1，减项1：食伤泄气）
run("从杀MID_1(癸巳乙卯己亥癸酉)", "己", ["巳", "卯", "亥", "酉"], ["癸", "乙", "己", "癸"])

# MID_2: 不当令+食伤泄气
# 甲日主，金杀不当令（月支寅木），酉金食神泄气
run("从杀MID_2(庚申戊寅甲子癸酉)", "甲", ["申", "寅", "子", "酉"], ["庚", "戊", "甲", "癸"])

# REJECT: 印透化煞
run("从杀REJECT(庚申辛酉壬子辛丑)", "甲", ["申", "酉", "子", "丑"], ["庚", "辛", "壬", "辛"])

print("\n=== F2从财分级用例 ===")
# CONFIRMED: 财星当令，纯粹无杂
# 甲日主，土财当令（辰月），无比印
run("从财CONFIRMED(戊辰己未甲辰己巳)", "甲", ["辰", "未", "辰", "巳"], ["戊", "己", "甲", "己"])

# MID_1: 官杀泄财
# 甲日主，土财当令，寅木官杀泄气
run("从财MID_1(戊辰己未甲辰丙寅)", "甲", ["辰", "未", "辰", "寅"], ["戊", "己", "甲", "丙"])

# MID_2: 不当令+官杀泄财
run("从财MID_2(戊辰己未甲辰乙卯)", "甲", ["辰", "未", "辰", "卯"], ["戊", "己", "甲", "乙"])

# REJECT: 比劫争财
run("从财REJECT(戊辰己未甲辰乙丑)", "甲", ["辰", "未", "辰", "丑"], ["戊", "己", "甲", "乙"])
