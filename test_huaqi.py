#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""化气族L4分级测试"""
import sys
sys.path.insert(0, '.')

from engines.huaqi_grade import huaqi_pan


def run(name, day_stem, branches, stems):
    result = huaqi_pan(stems, branches, day_stem, None)
    print(f"{name}: {result}")
    return result


print("=== 化气族五格分级测试 ===")
run("甲己化土(戊辰己未甲辰己巳)", "甲", ["辰", "未", "辰", "巳"], ["戊", "己", "甲", "己"])
run("乙庚化金(乙酉甲申乙酉庚辰)", "乙", ["酉", "申", "酉", "辰"], ["乙", "甲", "乙", "庚"])
run("丙辛化水(丙子辛卯丙申辛卯)", "丙", ["子", "子", "申", "卯"], ["丙", "辛", "丙", "辛"])
run("丁壬化木(丁卯壬寅丁亥壬寅)", "丁", ["卯", "寅", "亥", "寅"], ["丁", "壬", "丁", "壬"])
run("戊癸化火(戊午丁巳戊子癸亥)", "戊", ["午", "巳", "子", "亥"], ["戊", "丁", "戊", "癸"])
