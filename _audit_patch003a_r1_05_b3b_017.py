# -*- coding: utf-8 -*-
"""PATCH-017 Golden Validation Layer：从 60 条 Rule Candidate 机械生成 Golden Case Registry
反例由各条 excluded_transition 反向派生；5 个必测反例（旺≠强/得令≠强/有根≠强/调候≠旺衰/病药≠用神）全局登记。"""
import json, io, glob, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

FILES = [
    ('PATCH-005A', r'D:\shuntian-ziping-p0\governance\patch_005a_concept_boundary_registry.json', 'candidates', 'rule_candidate_id'),
    ('PATCH-005C', r'D:\shuntian-ziping-p0\governance\patch_005c_strength_state_rule.json', '1_rule_predicate_layer.candidate_predicates', 'rule_id'),
]
for n in range(6, 17):
    pat = r'D:\shuntian-ziping-p0\governance\patch_%03d_*_rule_modeling.json' % n
    for p in glob.glob(pat):
        FILES.append(('PATCH-%03d' % n, p, 'rule_candidates', 'rule_id'))
# 012 特殊结构
FILES.append(('PATCH-012', r'D:\shuntian-ziping-p0\governance\patch_012_ganzhi_liuqin_boundary.json', 'A+B', 'rule_id'))

registry = {
    'contract_id': 'PATCH-017',
    'name': 'Golden Validation Layer（金标验证层）',
    'status': 'FROZEN_DRAFT',
    'purpose': '把 Rule Candidate 验证成 ADMITTED_RULE 的验证集；当前引擎未接线，全部 validation_status=PENDING_VALIDATION；反例由 excluded_transition 机械派生，不编造语义。',
    'validation_status_values': ['PENDING_VALIDATION', 'STATIC_PASS', 'GOLDEN_PASS', 'ADMITTED', 'REJECTED'],
    'cases': [],
    'global_counter_examples': [
        {'case_id': 'GC-WQ-001', 'title': '旺≠强', 'inputs': {'wang_state': 'WANG'}, 'verify_forbidden': ['wang→strong', 'wang→STRONG'], 'expected_boundary': '旺层与强弱层隔离'},
        {'case_id': 'GC-DL-001', 'title': '得令≠强', 'inputs': {'order_state': 'GET_ORDER', 'root_state': {'object': 'DAYMASTER', 'value': 'NO_ROOT'}}, 'verify_forbidden': ['GET_ORDER→STRONG'], 'expected_boundary': '得令只到 order 层'},
        {'case_id': 'GC-YG-001', 'title': '有根≠强', 'inputs': {'root_state': {'object': 'DAYMASTER', 'value': 'HAS_ROOT'}}, 'verify_forbidden': ['root→STRONG'], 'expected_boundary': '根对象化，不直接产强弱'},
        {'case_id': 'GC-TH-001', 'title': '调候≠旺衰', 'inputs': {'seasonal_state': '寒暖成立'}, 'verify_forbidden': ['seasonal→STRONG'], 'expected_boundary': '调候独立域'},
        {'case_id': 'GC-BY-001', 'title': '病药≠用神', 'inputs': {'bingyao': '有病药关系'}, 'verify_forbidden': ['病药→直接取用神'], 'expected_boundary': '病药与用神分离登记'}
    ]
}

def get_path(d, path):
    cur = d
    for k in path.split('.'):
        cur = cur[k]
    return cur

for cid, path, key, idfield in FILES:
    d = json.load(io.open(path, encoding='utf-8'))
    if key == 'A+B':
        cands = d['section_A_ganzhi']['rule_candidates'] + d['section_B_liu_qin']['rule_candidates']
    else:
        cands = get_path(d, key)
    for c in cands:
        rid = c.get(idfield) or c.get('rule_id')
        excl = c.get('excluded_transition') or c.get('excluded') or []
        if isinstance(excl, str):
            excl = [excl]
        # 反例：由 forbidden 反向派生
        counter = []
        for e in excl:
            parts = str(e).split('→')
            if len(parts) == 2:
                counter.append({'forbidden_mapping': e.strip(), 'counter_example': '存在%s但不得输出%s的案例' % (parts[0].strip(), parts[1].strip())})
        registry['cases'].append({
            'rule_id': rid,
            'source_patch': cid,
            'source_id': (c.get('source_ids') or ['—'])[0],
            'condition': c.get('condition', c.get('concept_definition', '')),
            'counter_example': counter if counter else [{'forbidden_mapping': '(无显式禁转换)', 'counter_example': '结构层候选，验证输出枚举合法性'}],
            'conflict_case': c.get('conflict_case', 'NONE'),
            'expected_boundary': c.get('note', c.get('concept_definition', '')),
            'validation_status': 'PENDING_VALIDATION'
        })

json.dump(registry, io.open(r'D:\shuntian-ziping-p0\governance\patch_017_golden_validation_layer.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('Golden Case Registry 生成：', len(registry['cases']), '条 cases +', len(registry['global_counter_examples']), '条全局必测反例')
# 统计
from collections import Counter
print('按源 PATCH 分布:', dict(Counter(c['source_patch'] for c in registry['cases'])))
