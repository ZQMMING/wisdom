# -*- coding: utf-8 -*-
"""PATCH-019 ADMITTED_RULE Registry：从 60 条 Rule Candidate 生成骨架。
全部 status=PENDING_ENGINE_VALIDATION、golden_pass=false；仅引擎验证+Golden 通过后才可转 ADMITTED。"""
import json, io, glob, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

FILES = []
FILES.append(('PATCH-005A', r'D:\shuntian-ziping-p0\governance\patch_005a_concept_boundary_registry.json', 'candidates', 'rule_candidate_id'))
FILES.append(('PATCH-005C', r'D:\shuntian-ziping-p0\governance\patch_005c_strength_state_rule.json', '1_rule_predicate_layer.candidate_predicates', 'rule_id'))
for n in range(6, 17):
    for p in glob.glob(r'D:\shuntian-ziping-p0\governance\patch_%03d_*_rule_modeling.json' % n):
        FILES.append(('PATCH-%03d' % n, p, 'rule_candidates', 'rule_id'))
FILES.append(('PATCH-012', r'D:\shuntian-ziping-p0\governance\patch_012_ganzhi_liuqin_boundary.json', 'A+B', 'rule_id'))

def get_path(d, path):
    cur = d
    for k in path.split('.'):
        cur = cur[k]
    return cur

rules = []
for cid, path, key, idfield in FILES:
    d = json.load(io.open(path, encoding='utf-8'))
    if key == 'A+B':
        cands = d['section_A_ganzhi']['rule_candidates'] + d['section_B_liu_qin']['rule_candidates']
    else:
        cands = get_path(d, key)
    for c in cands:
        rules.append({
            'rule_id': c.get(idfield) or c.get('rule_id'),
            'source_patch': cid,
            'classical_scope': c.get('classical_scope', ''),
            'input_state': (c.get('input_factor') or c.get('input_states') or ['—']),
            'condition': c.get('condition', ''),
            'output': c.get('output') or c.get('output_type') or c.get('output_state') or '',
            'evidence_trace': {
                'source_id': (c.get('source_ids') or ['—'])[0],
                'text_layer': 'ORIGINAL/A 或按 source 层',
                'classical_scope': c.get('classical_scope', '')
            },
            'golden_pass': False,
            'status': 'PENDING_ENGINE_VALIDATION'
        })

registry = {
    'contract_id': 'PATCH-019',
    'name': 'ADMITTED_RULE Registry（准入规则注册表）',
    'status': 'FROZEN_DRAFT',
    'purpose': '最终形成 Engine 可调用规则层；当前全部 PENDING_ENGINE_VALIDATION（引擎未接线），无一条 ADMITTED。',
    'admission_chain': 'Rule Candidate → Golden Validation → Conflict Resolver → ADMITTED_RULE → Engine Execution',
    'rules': rules,
    'acceptance_criteria': [
        'rule_id/classical_scope/input_state/condition/output/evidence_trace/golden_pass 字段齐备',
        '全部 golden_pass=false',
        '全部 status=PENDING_ENGINE_VALIDATION',
        '无一条 ADMITTED（引擎未验证前禁止）'
    ]
}
json.dump(registry, io.open(r'D:\shuntian-ziping-p0\governance\patch_019_admitted_rule_registry.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('ADMITTED_RULE Registry 生成：', len(rules), '条规则，全部 PENDING_ENGINE_VALIDATION')
from collections import Counter
print('按源 PATCH 分布:', dict(Counter(r['source_patch'] for r in rules)))
print('ADMITTED 数:', sum(1 for r in rules if r['status'] == 'ADMITTED'))
