# -*- coding: utf-8 -*-
"""显示特定案例的原文"""
import json

with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', encoding='utf-8') as f:
    mismatches = json.load(f)

targets = ['丁酉甲辰戊戌戊午', '辛丑辛丑戊申壬子']

for m in mismatches:
    chart = m.get('chart', '')
    dayun = m.get('dayun', '')
    text = m.get('text', '')
    text_snippet = m.get('text_snippet', '')
    
    if chart in targets:
        print(f"=== {chart} {dayun} (原文: {text}) ===")
        print(f"原文片段: {text_snippet[:300]}")
        print()
