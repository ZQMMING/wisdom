# -*- coding: utf-8 -*-
"""PATCH-002 审计-3：印輕/印旺/母慈滅子 六部原文上下文提取（同词异义核心证据）"""
import json, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'D:\shuntian-ziping-p0'
ENGINES = {'yhzp': '渊海子平', 'pzzq': '子平真诠', 'dts': '滴天髓',
           'qtbj': '穷通宝鉴', 'smth': '三命通会', 'sftk': '神峰通考'}
KEYWORDS = ['印輕', '印旺', '印綬太旺', '母慈滅子', '身弱印', '身旺印', '印重']

src_dir = f'{ROOT}/registries/source'
for fn in sorted(os.listdir(src_dir)):
    if not fn.endswith('.jsonl'):
        continue
    eng = fn.replace('sources.', '').replace('.jsonl', '')
    name = ENGINES.get(eng, eng)
    lines = open(f'{src_dir}/{fn}', encoding='utf-8').read().splitlines()
    print(f'\n{"="*70}\n{name} ({eng})')
    count = 0
    for l in lines:
        if not l.strip():
            continue
        s = json.loads(l)
        text = s.get('source_text', '')
        if any(kw in text for kw in KEYWORDS):
            # 取含关键词的句子（按。！？切）
            import re
            sents = re.split(r'[。！？]', text)
            for sent in sents:
                if any(kw in sent for kw in KEYWORDS):
                    print(f'  [{s.get("source_id")}] {sent.strip()[:150]}')
                    count += 1
    if count == 0:
        print('  （无命中）')
