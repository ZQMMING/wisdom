# -*- coding: utf-8 -*-
"""PATCH-003A 第二步：令/旺/强/时/地 五术语簇完整审计
输出：每簇×每书 ORIGINAL 原文（含对象/关系初判依据）"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'D:\shuntian-ziping-p0\registries\source'
ENGINES = ['yhzp', 'pzzq', 'dts', 'qtbj', 'smth', 'sftk']
ENG_NAME = {'yhzp': 'YHZP渊海', 'pzzq': 'PZZQ真诠', 'dts': 'DTS滴天',
            'qtbj': 'QTBJ穷通', 'smth': 'SMTH三命', 'sftk': 'SFTK神峰'}

CLUSTERS = {
    '令': ['得令', '失令', '令星', '用事', '司令', '司權', '司权', '當權', '当权', '人元', '提綱', '提纲'],
    '旺': ['身旺', '太旺', '旺相', '旺極', '旺极', '旺氣', '旺气', '旺勢', '旺势', '主旺', '日主旺', '印旺', '財旺', '财旺', '官旺', '煞旺', '殺旺', '杀旺', '食旺', '梟旺', '枭旺', '劫旺', '旺之極'],
    '强': ['身強', '身强', '太強', '太强', '主強', '主强', '強旺', '强旺', '遇劫為強', '遇劫为强', '黨盛為強', '党盛为强', '強殺', '强杀', '日主強'],
    '时': ['得時', '得时', '失時', '失时', '生時', '生时', '時支', '时支', '時上', '时上', '時干', '时干', '子時', '子时', '進氣', '进气', '退氣', '退气'],
    '地': ['得地', '得垣', '歸垣', '归垣', '坐祿', '坐禄', '得祿', '得禄', '宅舍', '地載', '地载', '得局', '黨盛', '党盛', '地支至切'],
}

books = {}
for eng in ENGINES:
    lines = open(f'{ROOT}/sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
    books[eng] = [json.loads(l) for l in lines if l.strip()]

out = []
out.append('# PATCH-003A 第二步：令/旺/強/時/地 五术语簇审计（六部原文 ORIGINAL 优先）\n')
out.append('> 日期：2026-09-16 ｜ 目标：提取现代术语+异称+对象+关系+章节上下文，供 SEMANTIC_ROLE 判定\n')
out.append('> 铁律：关键词命中≠语义归类；逐条按 object/relation 初判；text_layer=ORIGINAL 优先\n')

for cluster, keys in CLUSTERS.items():
    out.append(f'\n{"="*60}\n## 术语簇「{cluster}」\n关键词：{" / ".join(keys)}\n')
    for eng in ENGINES:
        hits = [s for s in books[eng] if s.get('text_layer') == 'ORIGINAL' and any(k in s.get('source_text', '') for k in keys)]
        if not hits:
            continue
        out.append(f'\n### {ENG_NAME[eng]}（ORIGINAL {len(hits)}条，取代表）\n')
        shown = 0
        for s in hits[:5]:
            out.append(f'- `{s["source_id"]}` [{s.get("chapter")}]')
            out.append(f'  {s.get("source_text", "")[:150]}')
            shown += 1

open(r'D:\shuntian-ziping-p0\docs\PATCH-003A_术语簇审计_令旺强时地_2026-09-16.md', 'w', encoding='utf-8').write('\n'.join(out))
print('术语簇审计文档已生成')
# 打印计数
for cluster, keys in CLUSTERS.items():
    line = f'{cluster}: '
    for eng in ENGINES:
        n = sum(1 for s in books[eng] if s.get('text_layer') == 'ORIGINAL' and any(k in s.get('source_text', '') for k in keys))
        line += f'{ENG_NAME[eng]}={n} '
    print(line)
