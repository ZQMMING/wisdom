#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""专旺族F0总闸测试"""
import sys
sys.path.insert(0, '.')

from engines.zhuanwang_gates import zhuanwang_f0


def run(name, day_stem, branches, stems):
    ok, reason = zhuanwang_f0(stems, branches, day_stem, None)
    print(f"{name}: {ok} | {reason}")
    return ok


print("=== 专旺族五格测试 ===")
# 曲直格：甲寅 丁卯 甲寅 乙亥
run("曲直格(甲寅丁卯甲寅乙亥)", "甲", ["寅", "卯", "寅", "亥"], ["甲", "丁", "甲", "乙"])

# 炎上格：丙巳 甲午 丙午 甲午
run("炎上格(丙巳甲午丙午甲午)", "丙", ["巳", "午", "午", "午"], ["丙", "甲", "丙", "甲"])

# 稼穑格：戊辰 己未 戊戌 癸丑
run("稼穑格(戊辰己未戊戌癸丑)", "戊", ["辰", "未", "戌", "丑"], ["戊", "己", "戊", "癸"])

# 从革格：庚申 乙酉 庚申 乙酉
run("从革格(庚申乙酉庚申乙酉)", "庚", ["申", "酉", "申", "酉"], ["庚", "乙", "庚", "乙"])

# 润下格：壬子 癸亥 壬子 辛亥
run("润下格(壬子癸亥壬子辛亥)", "壬", ["子", "亥", "子", "亥"], ["壬", "癸", "壬", "辛"])
