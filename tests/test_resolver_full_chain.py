# -*- coding: utf-8 -*-
"""PATCH-148 Resolver真实全链回归: resolve->evaluate_conditions->candidate_state"""
import sys, json
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build
from engines.common.pzzq_producer_v1 import produce_pattern_candidates
from engines.common.pzzq_resolver_v2 import resolve, evaluate_conditions

rows = [json.loads(l) for l in open('registries/assertions/pzzq_assertions.jsonl', encoding='utf-8')]

def chain(facts, pattern):
    cands = [c for c in produce_pattern_candidates(facts)['pattern_candidates'] if c['pattern_type'] == pattern]
    if not cands: return None
    return evaluate_conditions(resolve(cands[0], rows), facts)

# A: 乙日戌月时干戊透 -> 财有根SAT + 财透SAT, blocked财太露=UNKNOWN
A = build({'year': ['癸','亥'], 'month': ['壬','戌'], 'day': ['乙','未'], 'hour': ['戊','午']})
# B: GC-001 财有根SAT但财透UNSAT
B = build({'year': ['癸','亥'], 'month': ['壬','戌'], 'day': ['乙','未'], 'hour': ['壬','午']})

for name, f in [('A 财有根SAT+财透SAT', A), ('B 财有根SAT+财透UNSAT', B)]:
    r = chain(f, '正财')
    print(name, '| required:', r['required_bundle']['bundle_status'],
          '| blocked:', r['blocked_bundle']['bundle_status'],
          '| direction:', r['candidate_state']['candidate_direction'])
