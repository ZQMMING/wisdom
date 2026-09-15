# -*- coding: utf-8 -*-
"""PATCH-003A 术语簇提取：勢/根/令/時/地/旺/強 六部原文表达变体扫描"""
import json, io, sys, re
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'D:\shuntian-ziping-p0\registries\source'
ENGINES = ['yhzp', 'pzzq', 'dts', 'qtbj', 'smth', 'sftk']
ENG_NAME = {'yhzp': 'YHZP', 'pzzq': 'PZZQ', 'dts': 'DTS', 'qtbj': 'QTBJ', 'smth': 'SMTH', 'sftk': 'SFTK'}

# 候选异名模式（正则，用于找原文表达）
PATTERNS = {
    '勢': r'[\u4e00-\u9fff]{0,3}勢[\u4e00-\u9fff]{0,3}',
    '根': r'[\u4e00-\u9fff]{0,3}根[\u4e00-\u9fff]{0,3}',
    '令': r'[\u4e00-\u9fff]{0,3}令[\u4e00-\u9fff]{0,3}',
    '時': r'[\u4e00-\u9fff]{0,3}時[\u4e00-\u9fff]{0,3}',
    '地': r'[\u4e00-\u9fff]{0,3}地[\u4e00-\u9fff]{0,3}',
    '旺': r'[\u4e00-\u9fff]{0,3}旺[\u4e00-\u9fff]{0,3}',
    '強': r'[\u4e00-\u9fff]{0,3}強[\u4e00-\u9fff]{0,3}',
    '強': r'[\u4e00-\u9fff]{0,3}强[\u4e00-\u9fff]{0,3}',
}

focus = ['勢', '根']
books = {}
for eng in ENGINES:
    lines = open(f'{ROOT}/sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
    books[eng] = [json.loads(l) for l in lines if l.strip()]

for w in focus:
    pat = PATTERNS[w]
    print(f"\n########## 概念「{w}」— 六部原文表达变体 TOP ##########")
    all_expr = Counter()
    examples = {}
    for eng in ENGINES:
        for s in books[eng]:
            t = s.get('source_text', '')
            if w not in t:
                continue
            for m in re.findall(pat, t):
                all_expr[m] += 1
                if m not in examples:
                    examples[m] = (eng, s['source_id'], s.get('chapter', '?'))
    for expr, n in all_expr.most_common(40):
        if n >= 1:
            e, sid, ch = examples[expr]
            print(f"  {expr} ×{n}  [{e} {sid} {ch}]")
