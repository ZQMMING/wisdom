#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""debug食伤格比值"""
import sys
sys.path.insert(0, '.')

from spec.root_qi import shi, calc_root_qi, STEM_WUXING
from engines.cong_ge_gates import WUXING_OF


def debug(name, day_stem, branches, stems):
    day_wx = STEM_WUXING[day_stem]
    cong_wx = WUXING_OF[day_wx]
    
    shis = {}
    for family, wx in cong_wx.items():
        shis[family] = shi(branches, stems, wx, branches[1])
    
    sorted_shis = sorted(shis.items(), key=lambda kv: kv[1], reverse=True)
    print(f"{name}:")
    for f, v in sorted_shis:
        print(f"  {f}: {v:.2f}")
    ratio = sorted_shis[0][1] / sorted_shis[1][1] if sorted_shis[1][1] > 0 else 999
    print(f"  主势/第二势比值: {ratio:.2f}")
    print()


# 真从儿——一品夫人
debug("一品夫人从儿", "癸", ["卯", "卯", "卯", "卯"], ["甲", "丁", "癸", "乙"])

# 误判——食神格
debug("食神格(甲)", "甲", ["子", "巳", "子", "午"], ["甲", "己", "甲", "戊"])

# 误判——伤官格
debug("伤官格(甲)", "甲", ["子", "午", "子", "巳"], ["甲", "丁", "甲", "丙"])

# 误判——偏印格
debug("偏印格(甲)", "甲", ["子", "子", "子", "酉"], ["甲", "癸", "甲", "辛"])
