#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跨族交叉边界联调测试"""
import sys
sys.path.insert(0, '.')

from spec.root_qi import shi, calc_root_qi, STEM_WUXING
from engines.cong_ge_gates import cong_ge_pan, WUXING_OF, F0_pass


def run(name, day_stem, branches, stems):
    # 先算势
    day_wx = STEM_WUXING[day_stem]
    cong_wx = WUXING_OF[day_wx]
    shi_dict = {}
    for family, wx in cong_wx.items():
        shi_dict[family] = shi(branches, stems, wx, branches[1])
    root_qi_val = calc_root_qi(day_stem, branches, stems)

    print(f"{name}:")
    print(f"  root_qi: {root_qi_val}")
    for k, v in shi_dict.items():
        print(f"  {k}: {v:.2f}")

    # 试从格
    result = cong_ge_pan(shi_dict, stems, day_stem, branches[1], root_qi_val)
    print(f"  从格判定: {result}")
    return result


print("=== 边界1：专旺 vs 从强 ===")
# 专旺：庚日主，申酉戌全→root_qi>0
run("专旺(庚申乙酉庚戌戊辰)", "庚", ["申", "酉", "戌", "辰"], ["庚", "乙", "庚", "戊"])

# 从强：庚日主，印星土成势→root_qi=0
run("从强(戊寅戊午庚辰己未)", "庚", ["寅", "午", "辰", "未"], ["戊", "戊", "庚", "己"])

print("\n=== 边界3：从格 vs 正格 ===")
# 从杀：甲日主，满盘金→root_qi=0
run("从杀(庚申辛酉甲子辛丑)", "甲", ["申", "酉", "子", "丑"], ["庚", "辛", "甲", "辛"])

# 正格：甲日主，未中乙木余气→root_qi>0
run("正格(庚申辛酉甲子辛未)", "甲", ["申", "酉", "子", "未"], ["庚", "辛", "甲", "辛"])
