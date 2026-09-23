#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""debug三个可疑点"""
import sys
sys.path.insert(0, '.')

from spec.root_qi import shi, calc_root_qi, STEM_WUXING, BRANCH_CANGGAN, BENQI
from engines.cong_ge_gates import WUXING_OF


def debug(name, day_stem, branches, stems):
    print(f"\n=== {name} ===")
    print(f"  日主: {day_stem}({STEM_WUXING[day_stem]})")
    print(f"  天干: {stems}")
    print(f"  地支: {branches}")
    
    day_wx = STEM_WUXING[day_stem]
    cong_wx = WUXING_OF[day_wx]
    
    print(f"\n  势():")
    shis = {}
    for family, wx in cong_wx.items():
        shis[family] = shi(branches, stems, wx, branches[1])
        print(f"    {family}({wx}): {shis[family]:.2f}")
    
    root_qi = calc_root_qi(day_stem, branches, stems)
    print(f"\n  root_qi: {root_qi}")
    
    # 印比占比
    yin_wx_map = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}
    yin_wx = yin_wx_map[day_wx]
    bi_wx = day_wx
    yin_bi_count = 0
    for s in stems:
        if STEM_WUXING.get(s) in {yin_wx, bi_wx}:
            yin_bi_count += 1
    for b in branches:
        if BENQI.get(b) in {yin_wx, bi_wx}:
            yin_bi_count += 1
    print(f"  印比占比: {yin_bi_count}/8 = {yin_bi_count/8*100:.0f}%")
    
    # 地支藏干
    print(f"\n  地支藏干:")
    for b in branches:
        print(f"    {b}: {BRANCH_CANGGAN[b]}")


# 1. 偏印格——应正格·印，判从强
debug("偏印格(甲)", "甲", ["子", "子", "子", "酉"], ["甲", "癸", "甲", "辛"])

# 2. 食神格——应正格·食伤，判从儿
debug("食神格(甲)", "甲", ["子", "巳", "子", "午"], ["甲", "己", "甲", "戊"])

# 3. 伤官格——应正格·食伤，判从儿
debug("伤官格(甲)", "甲", ["子", "午", "子", "巳"], ["甲", "丁", "甲", "丙"])
