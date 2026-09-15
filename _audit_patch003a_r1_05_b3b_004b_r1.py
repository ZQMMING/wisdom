# -*- coding: utf-8 -*-
"""PATCH-004B-R1：strength_state 六级固化 + definition_type/semantic_role 治理字段"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. 修订 004B registry
P1 = r'D:\shuntian-ziping-p0\governance\patch_004b_state_model_registry.json'
d1 = json.load(io.open(P1, encoding='utf-8'))
for st in d1['3_enum_required']['states']:
    if st['state_id'] == 'strength_state':
        st['values_human_proposal'] = None
        st['values'] = ["STRONG", "SLIGHTLY_STRONG", "NEUTRAL", "SLIGHTLY_WEAK", "WEAK", "UNDETERMINED"]
        st['definition_type'] = 'RELATIONAL_RESULT'
        st['semantic_role'] = 'RELATIONAL_STATE'
        st['note'] = 'PATCH-004B-R1 Human 裁决：采用 PATCH-001 六级，废弃七值方案；STRONG=规则层确认后的强状态（非旺/得令/有根）；UNDETERMINED=证据不足或冲突；禁 definition_type=POWER_LEVEL'
        break
json.dump(d1, io.open(P1, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('004B registry 修订：strength_state 六级 + RELATIONAL_RESULT/RELATIONAL_STATE')

# 2. enum_registry 补治理字段
P2 = r'D:\shuntian-ziping-p0\governance\enum_registry.json'
d2 = json.load(io.open(P2, encoding='utf-8'))
for e in d2['enums']:
    if e['enum_id'] == 'dts_strength_state':
        e['definition_type'] = 'RELATIONAL_RESULT'
        e['semantic_role'] = 'RELATIONAL_STATE'
        e['state_definition'] = {
            'STRONG': '规则层确认后的强状态',
            'SLIGHTLY_STRONG': '偏强状态',
            'NEUTRAL': '中和/难偏状态',
            'SLIGHTLY_WEAK': '偏弱状态',
            'WEAK': '规则层确认后的弱状态',
            'UNDETERMINED': '证据不足或冲突'
        }
        e['validation_schema'] = {
            'prohibited_definition_type': ['POWER_LEVEL'],
            'prohibited_source': ['旺', '得令', '得根'],
            'prohibited_conversion': ['WANG→STRONG', 'order_state→STRONG', 'root_state→STRONG', 'factor_count→STRONG']
        }
        break
d2['version'] = 'v1.8.1'
d2['changelog'] = d2.get('changelog', [])
d2['changelog'].append('v1.8.1 PATCH-004B-R1（2026-09-16）：dts_strength_state 补 definition_type=RELATIONAL_RESULT / semantic_role=RELATIONAL_STATE / state_definition / validation_schema（禁 POWER_LEVEL）')
json.dump(d2, io.open(P2, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('enum_registry v1.8.1：dts_strength_state 治理字段已写')

# 验证
d2b = json.load(io.open(P2, encoding='utf-8'))
for e in d2b['enums']:
    if e['enum_id'] == 'dts_strength_state':
        print('  值域:', e['values'])
        print('  definition_type:', e.get('definition_type'))
        print('  semantic_role:', e.get('semantic_role'))
        print('  state_definition 项数:', len(e.get('state_definition', {})))
        break
print('  version:', d2b['version'])
