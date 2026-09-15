# -*- coding: utf-8 -*-
"""003B 核验修正：SMTH-030-002 无法核实 → NOT_FOUND/FAIL_CLOSED（禁止无据引用）"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\shuntian-ziping-p0\governance\r1_05_verified_scope.json'
data = json.load(io.open(P, encoding='utf-8'))

# 1. 修正 ganzhi_zuhe 的 SMTH cell
fixed = 0
for cell in data['ganzhi_zuhe']['books']['SMTH']:
    if cell.get('source_id') == 'SMTH-030-002':
        cell['source_id'] = None
        cell['surface_form'] = '（SMTH 干支组合以日时断语为主，无独立A级总纲）'
        cell['chapter_id'] = '—'
        cell['text_layer'] = '—'
        cell['object_type'] = 'FOUR_PILLARS'
        cell['semantic_role'] = 'COMBO_REF'
        cell['semantic_definition'] = '003B 核验修正：原引 SMTH-030-002「地支至切黨盛為強」原文库不存在，禁止无据引用；SMTH 干支组合仅日时断语（REFERENCE/CONDITIONAL）'
        cell['verified_scope'] = 'NOT_FOUND'
        cell['scope_priority'] = '—'
        cell['excluded_scope'] = '日時斷語為條件變量，不得作干支组合总纲'
        cell['evidence_grade'] = None
        cell['attribution'] = None
        cell['execution_eligibility'] = 'FAIL_CLOSED'
        fixed += 1

json.dump(data, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'r1_05_verified_scope.json：ganzhi_zuhe/SMTH 已修正（{fixed} cell → NOT_FOUND/FAIL_CLOSED）')

# 2. 更新 checklist：移除 SMTH-030-002，记录 NOT_FOUND
CP = r'D:\shuntian-ziping-p0\governance\patch_003b_evidence_checklist.json'
cl = json.load(io.open(CP, encoding='utf-8'))
before = len(cl['SMTH'])
cl['SMTH'] = [it for it in cl['SMTH'] if it['source_id'] != 'SMTH-030-002']
cl['SMTH'].append({
    'source_id': 'SMTH-030-002',
    'domains': ['ganzhi_zuhe'],
    'chapter_verified': 'NOT_FOUND',
    'text_layer_verified': 'NOT_FOUND',
    'attribution_verified': 'NOT_FOUND',
    'evidence_grade_verified': 'NOT_FOUND',
    'usage_type_verified': 'EXCLUDED',
    'rule_boundary_ok': True,
    'verification_status': 'RESOLVED_NOT_FOUND',
    'note': '原文库不存在「地支至切黨盛為強」；003B 核验修正为 NOT_FOUND/FAIL_CLOSED，禁止无据引用',
})
json.dump(cl, io.open(CP, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
total = sum(len(v) for v in cl.values())
print(f'checklist：SMTH {before}→{len(cl["SMTH"])}，总计 {total} 条（含 1 条 RESOLVED_NOT_FOUND）')
