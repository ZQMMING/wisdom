# -*- coding: utf-8 -*-
"""显示所有40个不匹配案例的原文,检查评估脚本提取是否准确"""
import json

with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', encoding='utf-8') as f:
    mismatches = json.load(f)

print(f'剩余不匹配案例总数: {len(mismatches)}')
print(f'{"="*100}')

for i, m in enumerate(mismatches):
    chart = m.get('chart', '')
    dayun_str = m.get('dayun', '')
    engine_label = m.get('engine_label', '') or m.get('engine', '')
    text = m.get('text', '')
    text_snippet = m.get('text_snippet', '')
    
    # 判断引擎是喜还是忌
    engine_is_xi = ('SUPPORT' in engine_label or '喜' in engine_label)
    engine_str = '喜' if engine_is_xi else '忌'
    
    # 原文是喜还是忌
    text_is_xi = (text == 'XI')
    text_str = '喜' if text_is_xi else '忌'
    
    # 是否匹配（引擎和原文一致）
    match = (engine_is_xi == text_is_xi)
    
    print(f'\n[{i+1}] {chart} 大运={dayun_str}')
    print(f'  引擎={engine_str}({engine_label}) | 原文={text_str} | {"匹配?" if match else "不匹配"}')
    print(f'  原文片段: {text_snippet[:150]}')
