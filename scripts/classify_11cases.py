# -*- coding: utf-8 -*-
"""11条两轴皆空案例分类：从格优先接管 vs 纯baseline错标"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 11条两轴皆空（B2=False + A局全=False）
cases = [
    ("li-071", "戊申壬戌庚申乙酉", "化金气格", "从旺格"),
    ("li-338", "乙丑甲申甲辰己巳", "化土气格", "从杀格"),
    ("li-342", "丙戌戊戌癸巳壬戌", "化火气格", "从杀/从官"),
    ("li-356", "己未辛未丙戌戊戌", "化水气格", "从儿格"),
    ("li-458", "丙戌己亥甲戌庚午", "化土气格", "从杀格"),
    ("li-022", "庚寅壬午丁卯癸卯", "化木气格", "正格？"),
    ("li-218", "戊午壬戌丁卯癸卯", "化木气格", "正格？"),
    ("li-314", "丙戌辛丑己卯甲子", "化土气格", "正格？"),
    ("li-339", "戊辰壬戌甲辰己巳", "化土气格", "正格？"),
    ("li-348", "己卯甲戌甲子己巳", "化土气格", "正格？"),
    ("li-350", "甲寅丁丑甲戌己巳", "化土气格", "正格？"),
]

print("=== 11条两轴皆空案例分类 ===\n")
print(f"{'li':<8} {'四柱':<14} {'旧格局':<10} {'新格局':<10} {'分类':<15}")
print("-" * 70)

congge_count = 0
baseline_error_count = 0

for li, key, old_pat, new_pat in cases:
    if "从" in new_pat:
        category = "从格优先接管"
        congge_count += 1
    else:
        category = "纯baseline错标"
        baseline_error_count += 1
    
    print(f"{li:<8} {key:<14} {old_pat:<10} {new_pat:<10} {category:<15}")

print()
print(f"从格优先接管: {congge_count}条")
print(f"纯baseline错标: {baseline_error_count}条")
