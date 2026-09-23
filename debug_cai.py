#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""debug可疑点1：财格被从财误拦"""
import sys
sys.path.insert(0, '.')

from spec.root_qi import shi, calc_root_qi, STEM_WUXING
from engines.cong_ge_gates import WUXING_OF


def debug(name, day_stem, branches, stems):
    print(f"\n=== {name} ===")
    day_wx = STEM_WUXING[day_stem]
    cong_wx = WUXING_OF[day_wx]
    
    for family, wx in cong_wx.items():
        s = shi(branches, stems, wx, branches[1])
        print(f"  {family}({wx}): {s:.2f}")
    
    root_qi = calc_root_qi(day_stem, branches, stems)
    print(f"  root_qi: {root_qi}")


# 正财格：甲日主，辰月戊土财星
debug("正财格(甲)", "甲", ["子", "辰", "子", "戌"], ["甲", "戊", "甲", "癸"])

# 偏财格：甲日主，戌月戊土财星
debug("偏财格(甲)", "甲", ["子", "戌", "子", "辰"], ["甲", "戊", "甲", "癸"])
