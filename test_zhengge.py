#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""正格族F0测试"""
import sys
sys.path.insert(0, '.')

from engines.zhengge_gates import zhengge_f0


def run(name, branches):
    ok, reason = zhengge_f0(branches)
    print(f"{name}: {ok} | {reason}")
    return ok


print("=== 正格族F0测试 ===")
run("月令完好(甲寅)", ["子", "寅", "辰", "午"])
run("月令被冲无合解(寅月申冲)", ["申", "寅", "辰", "午"])
run("月令被冲有合解(寅月申冲+亥合)", ["申", "寅", "亥", "午"])
run("月令子被午冲", ["午", "子", "辰", "午"])
run("月令子被午冲有丑合", ["午", "子", "丑", "午"])
