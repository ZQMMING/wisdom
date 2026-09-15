# -*- coding: utf-8 -*-
"""PATCH-003 第一批审计：身旺/身強/身弱/身衰 六部全量分布
输出：命中条目（source_id/章节/text_layer/grade/原文全文）到矩阵文档"""
import json, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'D:\shuntian-ziping-p0\registries\source'
KEYS = ['身旺', '身強', '身弱', '身衰']
ENGINES = ['yhzp', 'pzzq', 'dts', 'qtbj', 'smth', 'sftk']
ENG_NAME = {'yhzp': '渊海子平', 'pzzq': '子平真诠', 'dts': '滴天髓',
            'qtbj': '穷通宝鉴', 'smth': '三命通会', 'sftk': '神峰通考'}

report = []
report.append('# PATCH-003 Concept Audit Matrix 初稿（第一批：身旺/身強/身弱/身衰）\n')
report.append('> 方法：关键词命中 → 全量提取（含章节/text_layer/grade/原文上下文）→ 逐条定语境\n')
report.append('> 铁律：不得断章取义；「身弱」只是文字相同不一定是 Concept 相同；按书×章节拆\n')

total_hit = {}
for eng in ENGINES:
    lines = open(f'{ROOT}/sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
    hits = []
    for l in lines:
        if not l.strip():
            continue
        s = json.loads(l)
        txt = s.get('source_text', '')
        if any(k in txt for k in KEYS):
            hits.append(s)
    total_hit[eng] = len(hits)
    report.append(f'\n## {ENG_NAME[eng]}（{eng}）：命中 {len(hits)} 条\n')
    for s in hits:
        report.append(f'- `{s["source_id"]}` | {s.get("chapter")} | {s.get("text_layer")} | {s.get("evidence_grade")}')
        report.append(f'  {s.get("source_text", "")[:200]}')
        report.append('')

print('各书命中数:', total_hit)
out = '\n'.join(report)
open(r'D:\shuntian-ziping-p0\docs\PATCH-003_ConceptAuditMatrix_身旺身弱_2026-09-16.md', 'w', encoding='utf-8').write(out)
print('矩阵文档已写入 docs/PATCH-003_ConceptAuditMatrix_身旺身弱_2026-09-16.md')
