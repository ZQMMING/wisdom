# -*- coding: utf-8 -*-
"""PATCH-144 财格required bundle四态golden: UNSAT>UNKNOWN>SAT"""
import sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build
from engines.common.condition_router import route_condition
from engines.common.condition_bundle import aggregate_required

def bundle(facts):
    req = ['财有根', '财透']  # 财格required (PATCH-142)
    items = [{'condition': c, 'status': route_condition(c, facts)['status']} for c in req]
    return aggregate_required(items), items

# A: 乙日戌月, 财有根(戌藏戊己)=SAT, 财透(戊辛丁未透)=UNSAT
A = build({'year': ['癸','亥'], 'month': ['壬','戌'], 'day': ['乙','未'], 'hour': ['壬','午']})
# C: 乙日戌月, 时干戊透=财透SAT, 财有根SAT
C = build({'year': ['癸','亥'], 'month': ['壬','戌'], 'day': ['乙','未'], 'hour': ['戊','午']})
# D反例: 丁日, 时干庚透=财透SAT(丁火财=金), 地支寅卯辰子无金=>财有根UNSAT
D = build({'year': ['甲','寅'], 'month': ['丁','卯'], 'day': ['丁','午'], 'hour': ['庚','子']})

# B: required含古文词"配合"(no_router=UNKNOWN) -> bundle UNKNOWN
B = build({'year': ['癸','亥'], 'month': ['壬','戌'], 'day': ['乙','未'], 'hour': ['壬','午']})

for name, f, req, exp in [
    ('A 财SAT财透UNSAT', A, ['财有根','财透'], 'UNSATISFIED'),
    ('C 财SAT财透SAT', C, ['财有根','财透'], 'SATISFIED'),
    ('D 财有根UNSAT', D, ['财有根','财透'], 'UNSATISFIED'),
    ('B 含配合UNKNOWN', B, ['财有根','配合'], 'UNKNOWN'),
]:
    items = [{'condition': c, 'status': route_condition(c, f)['status']} for c in req]
    b = aggregate_required(items)
    print(name, [i['status'] for i in items], '-> bundle', b['bundle_status'], '期望', exp)
