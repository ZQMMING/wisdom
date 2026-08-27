#!/usr/bin/env python3
"""基于4维数据生成64卦核心断言对照表，标注共识度。"""
import json

data = json.load(open(r"D:\TODAY\backend\data\research\64gua_4dim_validation.json", encoding="utf-8"))

# 从白话总结提取核心断言关键词
def extract_core_assertion(baihua, gua_ci, daxiang):
    """从白话+卦辞+大象提取核心断言"""
    core = baihua.strip()
    if not core:
        # 从大象辞提取
        core = daxiang.replace("君子以", "").replace("先王以", "").replace("后以", "").strip()
    return core[:80]

# 计算共识度
def calc_consensus(entry):
    score = 0
    if entry["dim1_gua_ci"]: score += 1
    if entry["dim2_baihua"]: score += 1
    if entry["dim3_renjian"] or entry["dim3_bushi"]: score += 1
    return score

print("| # | 卦名 | 核心断言(白话) | 经典支持 | 倪海厦补充 | 共识度 |")
print("|---|---|---|---|---|---|")

for i, entry in enumerate(data, 1):
    name = entry["name"]
    core = extract_core_assertion(entry["dim2_baihua"], entry["dim1_gua_ci"], entry["dim1_daxiang"])
    classic = entry["dim1_daxiang"][:20] if entry["dim1_daxiang"] else "-"
    nihai = ""
    if entry["dim3_renjian"]:
        nihai = entry["dim3_renjian"][:25] + "..."
    elif entry["dim3_bushi"]:
        nihai = entry["dim3_bushi"][:25] + "..."
    else:
        nihai = "-"
    consensus = calc_consensus(entry)
    stars = "★" * consensus + "☆" * (3 - consensus)
    print(f"| {i} | {name} | {core} | {classic} | {nihai} | {stars} |")

print()
print(f"总计: {len(data)}卦")
high = sum(1 for e in data if calc_consensus(e) == 3)
mid = sum(1 for e in data if calc_consensus(e) == 2)
low = sum(1 for e in data if calc_consensus(e) == 1)
print(f"三维共识(★★★): {high}卦")
print(f"二维共识(★★☆): {mid}卦")
print(f"一维独断(★☆☆): {low}卦")
