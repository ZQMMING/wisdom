# -*- coding: utf-8 -*-
"""PATCH-158 Judgment Producer三路径golden"""
import sys, json
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build
from engines.common.pzzq_producer_v1 import produce_pattern_candidates
from engines.common.pzzq_resolver_v2 import resolve, evaluate_conditions
from engines.common.judgment_producer import produce_judgment
rows = [json.loads(l) for l in open('registries/assertions/pzzq_assertions.jsonl', encoding='utf-8')]
def judg(f, ptype='正官'):
    cs = [x for x in produce_pattern_candidates(f)['pattern_candidates'] if x['pattern_type']==ptype][0]
    r = evaluate_conditions(resolve(cs, rows), f)
    return produce_judgment(cs, r, rows)

sup = build({'year':['甲','子'],'month':['庚','申'],'day':['乙','卯'],'hour':['丁','亥']})   # SUPPORTED
hit = build({'year':['甲','子'],'month':['庚','申'],'day':['乙','卯'],'hour':['戊','亥']})   # NOT_SUPPORTED(见财)
cai = build({'year':['癸','亥'],'month':['壬','戌'],'day':['乙','未'],'hour':['戊','午']})    # 财格PENDING(财太露)
cases = [
    ('SUPPORTED产Judgment', judg(sup)['status'], 'RECORDED'),
    ('SUPPORTED direction', judg(sup)['direction'], 'SUPPORTED'),
    ('SUPPORTED有provenance', len(judg(sup)['assertion_ids']) > 0, True),
    ('NOT_SUPPORTED', judg(hit)['status'], 'RECORDED'),
    ('NOT_SUPPORTED direction', judg(hit)['direction'], 'NOT_SUPPORTED'),
    ('财格PENDING不产确定', judg(cai,'正财')['status'], 'PENDING_REVIEW'),
]
fails=0
for n,g,e in cases:
    ok=g==e; fails+=(not ok)
    print(f"{'PASS' if ok else 'FAIL'} {n}: {g} (期望{e})")
print('=>', 'ALL PASS' if fails==0 else f'{fails} FAIL')
sys.exit(1 if fails else 0)
