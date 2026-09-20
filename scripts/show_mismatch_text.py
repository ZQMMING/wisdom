# -*- coding: utf-8 -*-
"""显示剩余43个不匹配案例的原文片段,检查评估脚本提取是否准确"""
import json

with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', encoding='utf-8') as f:
    mismatches = json.load(f)

print(f'剩余不匹配案例总数: {len(mismatches)}')
print(f'{"="*100}')

for i, m in enumerate(mismatches[:20]):
    chart = m.get('chart', '')
    dayun_str = m.get('dayun', '')
    engine_label = m.get('engine_label', '') or m.get('engine', '')
    text = m.get('text', '')
    text_snippet = m.get('text_snippet', '')
    
    print(f'\n[{i+1}] {chart} 大运={dayun_str}')
    print(f'  引擎: {engine_label}')
    print(f'  原文(text): {text[:80]}')
    print(f'  原文片段(snippet): {text_snippet[:120]}')
    print(f'  {"-"*80}')
