#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F1-F4测试：从杀用例"""
import sys
sys.path.insert(0, '.')

from spec.root_qi import shi, calc_root_qi, STEM_WUXING
from engines.cong_ge_gates import cong_ge_pan, F0_pass


def run(name, day_stem, branches, stems):
    # 先过F0
    f0 = F0_pass(day_stem, branches, stems)
    if not f0:
        print(f"{name}: F0不通过→正格/REJECT")
        return ("正格", "REJECT", "F0未过")

    # 算势
    day_wx = STEM_WUXING[day_stem]
    from engines.cong_ge_gates import WUXING_OF
    cong_wx = WUXING_OF[day_wx]

    shi_dict = {}
    for family, wx in cong_wx.items():
        shi_dict[family] = shi(branches, stems, wx, branches[1])  # 月支是第二个

    root_qi_val = calc_root_qi(day_stem, branches, stems)
    result = cong_ge_pan(shi_dict, stems, day_stem, branches[1], root_qi_val)

    print(f"{name}: {result}")
    return result


print("=== 从杀用例测试 ===")
# C1: 癸巳 乙卯 己亥 癸酉 → 从杀·MID（食伤制杀）
r = run("C1(癸巳乙卯己亥癸酉)", "己", ["巳", "卯", "亥", "酉"], ["癸", "乙", "己", "癸"])

# C4: 庚申 辛酉 甲子 辛丑 → 从杀·CONFIRMED（印藏不透）
r = run("C4(庚申辛酉甲子辛丑)", "甲", ["申", "酉", "子", "丑"], ["庚", "辛", "甲", "辛"])

# C7=C4（印藏不透）
# C8: 庚申 辛酉 壬子 辛丑 → 印透→REJECT
r = run("C8(庚申辛酉壬子辛丑·印透)", "甲", ["申", "酉", "子", "丑"], ["庚", "壬", "甲", "辛"])
