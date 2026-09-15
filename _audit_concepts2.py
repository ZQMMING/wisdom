# -*- coding: utf-8 -*-
"""PATCH-002 审计-2：共享 subject 的 predicate 差异 + 消费字段跨书重复 + source 概念分布"""
import json, io, sys
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'D:\shuntian-ziping-p0'
ENGINES = {'yhzp': '渊海子平', 'pzzq': '子平真诠', 'dts': '滴天髓',
           'qtbj': '穷通宝鉴', 'smth': '三命通会', 'sftk': '神峰通考'}

rules = {}
for eng in ENGINES:
    rules[eng] = [json.loads(l) for l in
                  open(f'{ROOT}/registries/rule/rules.{eng}.jsonl', encoding='utf-8').read().splitlines()
                  if l.strip()]

print('=== 1. 共享 subject 的 (subject, predicate) 组合 ===')
SHARED = ['day_master', 'element', 'pattern', 'stem', 'ten_god', 'yangren']
for subj in SHARED:
    print(f'\n[{subj}]')
    for eng in ENGINES:
        combos = Counter((r.get('predicate'), r.get('rule_type')) for r in rules[eng]
                         if r.get('subject') == subj)
        if combos:
            print(f'  {ENGINES[eng]}({eng}): {dict(combos)}')

print()
print('=== 2. 规则消费字段（preconditions.field）跨书重复 ===')
field_by_engine = defaultdict(set)
for eng in ENGINES:
    for r in rules[eng]:
        for c in r.get('preconditions', {}).get('conditions', []):
            f = c.get('field', '')
            if f:
                field_by_engine[eng].add(f)
all_fields = set()
for eng in field_by_engine:
    all_fields |= field_by_engine[eng]
print('共享字段（>=2 引擎消费）:')
for f in sorted(all_fields):
    appears = [eng for eng in ENGINES if f in field_by_engine[eng]]
    if len(appears) >= 2:
        print(f'  {f}: {", ".join(ENGINES[e] for e in appears)}')

print()
print('=== 3. source 层：关键概念词在六部出现分布 ===')
import os
KEYWORDS = ['印輕', '印旺', '印綬太旺', '母慈滅子', '身弱印', '身旺印', '財輕官重',
            '官星清', '濁氣', '一清到底', '旺衰', '根氣', '得令', '化神', '從格']
src_dir = f'{ROOT}/registries/source'
for fn in sorted(os.listdir(src_dir)):
    if not fn.endswith('.jsonl'):
        continue
    eng = fn.replace('sources.', '').replace('.jsonl', '')
    text = open(f'{src_dir}/{fn}', encoding='utf-8').read()
    hits = [kw for kw in KEYWORDS if kw in text]
    if hits:
        print(f'{ENGINES.get(eng, eng)}: {hits}')
