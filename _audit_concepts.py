# -*- coding: utf-8 -*-
"""PATCH-002 审计：六部 rules subject/predicate 概念分布 + 同词异义候选"""
import json, io, sys
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'D:\shuntian-ziping-p0\registries\rule'
ENGINES = {'yhzp': '渊海子平', 'pzzq': '子平真诠', 'dts': '滴天髓',
           'qtbj': '穷通宝鉴', 'smth': '三命通会', 'sftk': '神峰通考'}

# 1. 各引擎 subject 分布
subj_by_engine = defaultdict(Counter)
pred_by_engine = defaultdict(Counter)
total = 0
for eng, name in ENGINES.items():
    lines = open(f'{ROOT}/rules.{eng}.jsonl', encoding='utf-8').read().splitlines()
    for l in lines:
        if not l.strip():
            continue
        r = json.loads(l)
        subj_by_engine[eng][r.get('subject', '')] += 1
        pred_by_engine[eng][r.get('predicate', '')] += 1
        total += 1

print('规则总数:', total)
print()
print('=== 跨引擎共享 subject（同词异义候选）===')
# 找出出现在 >=2 引擎的 subject
all_subjects = set()
for eng in subj_by_engine:
    all_subjects |= set(subj_by_engine[eng])
for subj in sorted(all_subjects):
    appears = [(eng, subj_by_engine[eng][subj]) for eng in ENGINES if subj_by_engine[eng][subj] > 0]
    if len(appears) >= 2:
        print(f'\n{subj}:')
        for eng, cnt in appears:
            print(f'  {ENGINES[eng]}({eng}): {cnt}')
