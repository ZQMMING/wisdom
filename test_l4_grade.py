#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L4分级用例验证v2"""
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


print("=== F1从杀REJECT用例 ===")
# 甲日主，满盘金杀，时干透壬水印星→REJECT
# 地支申酉子丑：无木根，root_qi=0
run("从杀REJECT(庚申辛酉壬子辛丑·印透)", "甲", ["申", "酉", "子", "丑"], ["庚", "辛", "壬", "辛"])

print("\n=== F2从财分级用例（戌月，无木根）===")
# CONFIRMED: 戊戌 壬戌 甲辰 己巳 → 甲日主，戌月土财当令，无比印
run("从财CONFIRMED(戊戌壬戌甲辰己巳)", "甲", ["戌", "戌", "辰", "巳"], ["戊", "壬", "甲", "己"])

# MID_1: 官杀泄财（寅木官杀）
run("从财MID_1(戊戌壬戌甲辰丙寅)", "甲", ["戌", "戌", "辰", "寅"], ["戊", "壬", "甲", "丙"])

# MID_2: 不当令+官杀泄财
run("从财MID_2(戊戌壬戌甲辰乙卯)", "甲", ["戌", "戌", "辰", "卯"], ["戊", "壬", "甲", "乙"])

# REJECT: 印透生身
run("从财REJECT(戊戌壬戌甲辰丙寅·印透?)", "甲", ["戌", "戌", "辰", "寅"], ["戊", "壬", "甲", "丙"])
