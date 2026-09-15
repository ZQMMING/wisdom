# -*- coding: utf-8 -*-
"""R1-03：六部「用事/司令/人元/支藏」全量扫描（12月×12时 schedule 证据收集）"""
import json, io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'D:\shuntian-ziping-p0\registries\source'
ENGINES = ['yhzp', 'pzzq', 'dts', 'qtbj', 'smth', 'sftk']
ENG_NAME = {'yhzp': 'YHZP渊海', 'pzzq': 'PZZQ真诠', 'dts': 'DTS滴天',
            'qtbj': 'QTBJ穷通', 'smth': 'SMTH三命', 'sftk': 'SFTK神峰'}

KEYS = ['用事', '司令', '司權', '司权', '當權', '当权', '人元', '支藏', '藏干', '藏氣', '藏气',
        '用事之神', '主事', '乘權', '乘权', '司天', '當令', '当令']

# 12 支
ZHI = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']

out = []
for eng in ENGINES:
    lines = open(f'{ROOT}/sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
    books = [json.loads(l) for l in lines if l.strip()]
    hits = [s for s in books if any(k in s.get('source_text', '') for k in KEYS)]
    out.append(f'\n{"="*70}\n## {ENG_NAME[eng]}：用事/司令/人元 相关 {len(hits)} 条')
    for s in hits:
        t = s.get('source_text', '')
        # 找涉及哪些地支
        zhis = [z for z in ZHI if z in t]
        out.append(f'\n- `{s["source_id"]}` [{s.get("chapter")}] {s.get("text_layer")}/{s.get("evidence_grade")} attr={s.get("attribution","?")}')
        out.append(f'  涉及地支: {zhis}')
        out.append(f'  {t[:200]}')

open(r'D:\shuntian-ziping-p0\docs\_r103_scan_tmp.md', 'w', encoding='utf-8').write('\n'.join(out))
print('扫描完成，详见 docs/_r103_scan_tmp.md')
for eng in ENGINES:
    lines = open(f'{ROOT}/sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
    books = [json.loads(l) for l in lines if l.strip()]
    n = sum(1 for s in books if any(k in s.get('source_text', '') for k in KEYS))
    print(f'{ENG_NAME[eng]}: {n} 条')
