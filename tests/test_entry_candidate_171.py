# -*- coding: utf-8 -*-
"""PATCH-171 Entry->Candidate Contract golden"""
import sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build
from engines.common.entry_candidate_contract import build_candidates
f = build({'year':['甲','子'],'month':['丁','午'],'day':['乙','卯'],'hour':['丁','亥']})
c = build_candidates(f)
print([x['entry_type'] for x in c['candidates']])
fails=0
def ck(n,g,e):
    global fails
    ok=g==e; fails+=(not ok); print(f"{'PASS' if ok else 'FAIL'} {n}: {g}")
types=[x['entry_type'] for x in c['candidates']]
ck("食神格候选", '食神格' in types, True)
ck("state=CANDIDATE", c['candidates'][0]['state'], 'CANDIDATE')
# 禁输出格成/吉凶
ck("无格成输出", all('格成' not in x['boundary'] for x in c['candidates']), True)
ck("boundary禁成列表", '格成' in c['boundary']['forbidden_outputs'], True)
ck("保留provenance", 'source_fact_ids' in c['candidates'][0], True)
# 非食神盘
f2 = build({'year':['甲','子'],'month':['乙','卯'],'day':['乙','卯'],'hour':['丁','亥']})
c2 = build_candidates(f2)
ck("卯月=建禄候选", any(x['entry_type']=='建禄' for x in c2['candidates']), True)
print('=>', 'ALL PASS' if fails==0 else f'{fails} FAIL')
sys.exit(1 if fails else 0)
