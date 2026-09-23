#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""专旺族L4分级测试"""
import sys
sys.path.insert(0, '.')

from engines.zhuanwang_grade import zhuanwang_pan


def run(name, day_stem, branches, stems):
    result = zhuanwang_pan(stems, branches, day_stem, None)
    print(f"{name}: {result}")
    return result


print("=== 专旺族五格分级测试 ===")
run("曲直格(甲寅丁卯甲寅乙亥)", "甲", ["寅", "卯", "寅", "亥"], ["甲", "丁", "甲", "乙"])
run("炎上格(丙巳甲午丙午甲午)", "丙", ["巳", "午", "午", "午"], ["丙", "甲", "丙", "甲"])
run("稼穑格(戊辰己未戊戌癸丑)", "戊", ["辰", "未", "戌", "丑"], ["戊", "己", "戊", "癸"])
run("从革格(庚申乙酉庚申乙酉)", "庚", ["申", "酉", "申", "酉"], ["庚", "乙", "庚", "乙"])
run("润下格(壬子癸亥壬子辛亥)", "壬", ["子", "亥", "子", "亥"], ["壬", "癸", "壬", "辛"])
