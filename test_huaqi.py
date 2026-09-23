#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""化气族现状测试"""
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


print("=== 化气族命例测试 ===")
# 甲己化土：甲子 己巳 甲戌 己巳
run("甲己化土(甲子己巳甲戌己巳)", "甲", ["子", "巳", "戌", "巳"], ["甲", "己", "甲", "己"])

# 乙庚化金：乙酉 庚辰 乙酉 庚辰
run("乙庚化金(乙酉庚辰乙酉庚辰)", "乙", ["酉", "辰", "酉", "辰"], ["乙", "庚", "乙", "庚"])

# 丙辛化水：丙子 辛卯 丙申 辛卯
run("丙辛化水(丙子辛卯丙申辛卯)", "丙", ["子", "卯", "申", "卯"], ["丙", "辛", "丙", "辛"])

# 丁壬化木：丁卯 壬寅 丁亥 壬寅
run("丁壬化木(丁卯壬寅丁亥壬寅)", "丁", ["卯", "寅", "亥", "寅"], ["丁", "壬", "丁", "壬"])

# 戊癸化火：戊午 丁巳 戊子 丁巳
run("戊癸化火(戊午丁巳戊子丁巳)", "戊", ["午", "巳", "子", "巳"], ["戊", "丁", "戊", "丁"])
