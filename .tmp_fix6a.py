# -*- coding: utf-8 -*-
import io
p = "src/tongshu/engines/blind_judgment.py"
src = io.open(p, encoding="utf-8").read()

# ── 修6a：EVIDENCE 补充 ──
old = """    "BLIND-DJ-009": "过河拆桥：先取后用（辛卯戊戌己亥癸酉 数亿大企业）",
"""
new = """    "BLIND-DJ-009": "过河拆桥：先取后用（辛卯戊戌己亥癸酉 数亿大企业）",
    "BLIND-DJ-010": "穿官损官：穿比冲更狠，官根受损、体制内不适应（丁未癸卯庚子丁丑 官场梦碎）",
    "BLIND-DJ-011": "官星被劫财合走：非我所有、做功无效（乙巳甲申辛酉乙未 仓库保管员）",
    "BLIND-DJ-012": "宾主易位/官星投墓：主位配偶星被劫财收走，婚姻难长久（甲寅丙子己亥戊辰）",
"""
assert old in src, "EVIDENCE OLD NOT FOUND"
src = src.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(src)
print("OK EVIDENCE 已补")
