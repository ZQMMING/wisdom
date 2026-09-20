# -*- coding: utf-8 -*-
"""分析大运喜忌不匹配案例的错误类型"""
import json

with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', encoding='utf-8') as f:
    mismatches = json.load(f)

print(f'不匹配案例总数: {len(mismatches)}')

# 错误类型统计
error_types = {}
for m in mismatches:
    engine = m.get('engine_label', '') or m.get('engine', '')
    text = m.get('text', '')
    
    # 判断引擎输出
    if 'SUPPORT_USE_GOD' in str(engine) or '喜' in str(engine):
        engine_xi = True
    elif 'SUPPRESS_USE_GOD' in str(engine) or '忌' in str(engine):
        engine_xi = False
    else:
        engine_xi = None
    
    # 判断原文
    text_xi = None
    if '喜' in text or '发' in text or '吉' in text or '亨' in text or '利' in text:
        text_xi = True
    if '忌' in text or '凶' in text or '败' in text or '夭' in text or '贫' in text or '祸' in text:
        if text_xi:
            text_xi = 'MIXED'
        else:
            text_xi = False
    
    # 错误类型
    if engine_xi == True and text_xi == False:
        etype = 'ENGINE_XI_TEXT_JI'
    elif engine_xi == False and text_xi == True:
        etype = 'ENGINE_JI_TEXT_XI'
    elif engine_xi == True and text_xi == 'MIXED':
        etype = 'ENGINE_XI_TEXT_MIXED'
    elif engine_xi == False and text_xi == 'MIXED':
        etype = 'ENGINE_JI_TEXT_MIXED'
    else:
        etype = f'OTHER_eng={engine_xi}_text={text_xi}'
    
    error_types[etype] = error_types.get(etype, 0) + 1

print(f'\n错误类型分布:')
for et, cnt in sorted(error_types.items(), key=lambda x: -x[1]):
    print(f'  {et}: {cnt}')

# 看看前20个不匹配案例的详情
print(f'\n{"="*100}')
print('前20个不匹配案例详情:')
for i, m in enumerate(mismatches[:20]):
    chart = m.get('chart', '')
    dayun = m.get('dayun', '')
    engine = m.get('engine_label', '') or m.get('engine', '')
    text = m.get('text', '')[:100]
    print(f'\n[{i+1}] {chart} 大运={dayun}')
    print(f'  引擎: {engine}')
    print(f'  原文: {text}')
