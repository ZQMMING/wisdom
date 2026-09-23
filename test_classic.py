#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""古籍从格命例锚点验证"""
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
    print(f"  势: {shi_dict}")
    return result


print("=== F1从杀·李侍郎命（乙酉乙酉乙酉甲申）===")
# 乙木日主，四柱皆金煞
run("李侍郎(乙酉乙酉乙酉甲申)", "乙", ["酉", "酉", "酉", "申"], ["乙", "乙", "乙", "甲"])

print("\n=== F3从儿·一品夫人命（甲寅丁卯癸卯乙卯）===")
# 癸水日主，干透甲乙，支全寅卯
run("一品夫人(甲寅丁卯癸卯乙卯)", "癸", ["寅", "卯", "卯", "卯"], ["甲", "丁", "癸", "乙"])

print("\n=== F3从儿·朱元璋命（戊辰壬戌丁丑丁未）===")
# 丁火日主，四库全土
run("朱元璋(戊辰壬戌丁丑丁未)", "丁", ["辰", "戌", "丑", "未"], ["戊", "壬", "丁", "丁"])

print("\n=== F2从财·侍郎命（丙寅庚寅壬午乙巳）===")
# 壬水日主，木火通明
run("侍郎从财(丙寅庚寅壬午乙巳)", "壬", ["寅", "寅", "午", "巳"], ["丙", "庚", "壬", "乙"])
