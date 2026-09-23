#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""正格族L1取格测试"""
import sys
sys.path.insert(0, '.')

from engines.zhengge_quge import l1_quge


def run(name, day_stem, branches, stems):
    ge, reason = l1_quge(stems, branches, day_stem)
    print(f"{name}: {ge} | {reason}")
    return ge


print("=== L1取格测试 ===")
# 正官格：甲日主，酉月辛金透干
run("正官格(甲子癸酉甲子)", "甲", ["子", "酉", "子", "亥"], ["甲", "癸", "甲", "X"])

# 七杀格：甲日主，申月庚金透干
run("七杀格(甲子壬申甲子)", "甲", ["子", "申", "子", "亥"], ["甲", "壬", "甲", "X"])

# 食神格：甲日主，巳月丙火透干
run("食神格(甲子己巳甲子)", "甲", ["子", "巳", "子", "亥"], ["甲", "己", "甲", "丙"])

# 比劫当令：甲日主，寅月甲木当令
run("比劫当令(甲寅丙寅甲子)", "甲", ["寅", "寅", "子", "亥"], ["甲", "丙", "甲", "X"])
