#!/usr/bin/env python3
"""4维交叉验证：从4个来源提取64卦核心断言，生成对照表。
维度1: 项目内置 classical_text.py (卦辞+大象辞)
维度2: chinese-fortune 64hex-full.md (白话总结)
维度3: 倪海厦 corpus (人间道+卜筮关键判语)
维度4: 互联网权威 (已搜索的前16卦，后续补充)
"""
import re
import json
import sys
sys.path.insert(0, r"D:\TODAY\backend\src")

from tongshu.engines.yi.classical_text import _CLASSICAL_TEXTS

# 维度1: 项目内置经典原文
dim1 = {}
for name, data in _CLASSICAL_TEXTS.items():
    dim1[name] = {
        "gua_ci": data.get("gua_ci", ""),
        "da_xiang": data.get("da_xiang_ci", ""),
    }

# 维度2: chinese-fortune 64hex-full.md
doc_path = r"D:\today\chinese-fortune\references\64hex-full.md"
text = open(doc_path, encoding="utf-8").read()
dim2 = {}
# 按 ## 分割
blocks = re.split(r'\n## ', text)
for block in blocks[1:]:
    lines = block.split('\n')
    title = lines[0].strip()
    # 提取卦名: "1. 乾 Qián (The Creative / Heaven)"
    m = re.match(r'\d+\.\s+(\S+)', title)
    if not m:
        continue
    gua_name_cn = m.group(1)
    # 找完整卦名
    full_name = None
    for cn_name in dim1.keys():
        if cn_name.startswith(gua_name_cn) or gua_name_cn in cn_name:
            full_name = cn_name
            break
    if not full_name:
        # 尝试映射
        name_map = {
            "乾": "乾为天", "坤": "坤为地", "屯": "水雷屯", "蒙": "山水蒙",
            "需": "水天需", "讼": "天水讼", "师": "地水师", "比": "水地比",
            "小畜": "风天小畜", "履": "天泽履", "泰": "地天泰", "否": "天地否",
            "同人": "天火同人", "大有": "火天大有", "谦": "地山谦", "豫": "雷地豫",
            "随": "泽雷随", "蛊": "山风蛊", "临": "地泽临", "观": "风地观",
            "噬嗑": "火雷噬嗑", "贲": "山火贲", "剥": "山地剥", "复": "地雷复",
            "无妄": "天雷无妄", "大畜": "山天大畜", "颐": "山雷颐", "大过": "泽风大过",
            "坎": "坎为水", "离": "离为火", "咸": "泽山咸", "恒": "雷风恒",
            "遁": "天山遁", "大壮": "雷天大壮", "晋": "火地晋", "明夷": "地火明夷",
            "家人": "风火家人", "睽": "火泽睽", "蹇": "水山蹇", "解": "雷水解",
            "损": "山泽损", "益": "风雷益", "夬": "泽天夬", "姤": "天风姤",
            "萃": "泽地萃", "升": "地风升", "困": "泽水困", "井": "水风井",
            "革": "泽火革", "鼎": "火风鼎", "震": "震为雷", "艮": "艮为山",
            "渐": "风山渐", "归妹": "雷泽归妹", "丰": "雷火丰", "旅": "火山旅",
            "巽": "巽为风", "兑": "兑为泽", "涣": "风水涣", "节": "水泽节",
            "中孚": "风泽中孚", "小过": "雷山小过", "既济": "水火既济", "未济": "火水未济",
        }
        full_name = name_map.get(gua_name_cn)
    if not full_name:
        continue
    # 提取白话
    baihua = ""
    for line in lines:
        if line.startswith("**白话**"):
            baihua = line.replace("**白话**：", "").strip()
            break
    dim2[full_name] = {"baihua": baihua}

# 维度3: 倪海厦 corpus 提取
corpus_path = r"D:\today\nihai-tianji-corpus\docs\09-六十四卦.md"
corpus_text = open(corpus_path, encoding="utf-8").read()
dim3 = {}
corpus_blocks = re.split(r'\n## ', corpus_text)
for block in corpus_blocks[1:]:
    lines = block.split('\n')
    title = lines[0].strip()
    m = re.match(r'(.+?)（', title)
    gua_name = m.group(1) if m else title.split('（')[0]
    if gua_name not in dim1:
        continue
    # 提取人间道第一段
    renjian = ""
    bushi = ""
    current_section = None
    for line in lines[1:]:
        if line.startswith('### '):
            current_section = line[4:].strip()
        elif line.startswith('- 「') and current_section:
            quote = re.search(r'「(.+?)」', line)
            if quote:
                q = quote.group(1)
                if '人间道' in current_section and not renjian and len(q) > 15:
                    renjian = q[:120]
                elif '卜筮' in current_section and not bushi and len(q) > 15:
                    bushi = q[:120]
    dim3[gua_name] = {"renjian": renjian, "bushi": bushi}

# 生成对照表
print(f"维度1(经典原文): {len(dim1)}卦")
print(f"维度2(白话总结): {len(dim2)}卦")
print(f"维度3(倪海厦): {len(dim3)}卦")
print()

# 输出前16卦的4维对照
all_names = list(dim1.keys())
results = []
for name in all_names:
    entry = {"name": name}
    d1 = dim1.get(name, {})
    entry["dim1_gua_ci"] = d1.get("gua_ci", "")
    entry["dim1_daxiang"] = d1.get("da_xiang", "")
    d2 = dim2.get(name, {})
    entry["dim2_baihua"] = d2.get("baihua", "")
    d3 = dim3.get(name, {})
    entry["dim3_renjian"] = d3.get("renjian", "")
    entry["dim3_bushi"] = d3.get("bushi", "")
    results.append(entry)

# 保存
out_path = r"D:\TODAY\backend\data\research\64gua_4dim_validation.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"已保存 {len(results)}卦到 {out_path}")
print()

# 打印前8卦对照
for r in results[:8]:
    print(f"=== {r['name']} ===")
    print(f"  经典: {r['dim1_gua_ci'][:40]}... | {r['dim1_daxiang'][:30]}")
    print(f"  白话: {r['dim2_baihua'][:60]}")
    if r['dim3_renjian']:
        print(f"  倪海厦人间道: {r['dim3_renjian'][:60]}...")
    if r['dim3_bushi']:
        print(f"  倪海厦卜筮: {r['dim3_bushi'][:60]}...")
    print()
