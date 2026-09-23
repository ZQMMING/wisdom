#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""debug正格用例"""
import sys
sys.path.insert(0, '.')

from spec.root_qi import shi, calc_root_qi, STEM_WUXING
from engines.cong_ge_gates import WUXING_OF
from engines.zhuanwang_gates import zhuanwang_f0


def debug(name, day_stem, branches, stems):
    print(f"\n=== {name} ===")
    day_wx = STEM_WUXING[day_stem]
    cong_wx = WUXING_OF[day_wx]
    
    for family, wx in cong_wx.items():
        s = shi(branches, stems, wx, branches[1])
        print(f"  {family}({wx}): {s:.2f}")
    
    root_qi = calc_root_qi(day_stem, branches, stems)
    print(f"  root_qi: {root_qi}")
    
    zw_ok, zw_reason = zhuanwang_f0(stems, branches, day_stem, None)
    print(f"  专旺F0: {zw_ok} | {zw_reason}")


# 七杀成格
debug("七杀成格(食神制杀)", "甲", ["子", "申", "子", "辰"], ["甲", "壬", "甲", "丙"])

# 食神成格
debug("食神成格(食神生财)", "甲", ["子", "巳", "子", "辰"], ["甲", "己", "甲", "戊"])
