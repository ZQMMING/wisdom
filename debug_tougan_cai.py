#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""debug_tou_gan"""
import sys
sys.path.insert(0, '.')

from engines.cong_ge_gates import _tou_gan
from spec.root_qi import STEM_WUXING


def test(name, day_stem, stems, target):
    result = _tou_gan(stems, STEM_WUXING[day_stem], target)
    print(f"{name}: {target}透干? {result} | stems={stems}")


# 侍郎从财：壬日主，乙木透干
test("侍郎从财(壬)", "壬", ["丙", "庚", "壬", "乙"], "比")

# 正财格：甲日主，两个甲木透干
test("正财格(甲)", "甲", ["甲", "戊", "甲", "癸"], "比")
