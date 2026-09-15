# -*- coding: utf-8 -*-
"""1. 六神篇/总言篇 非歌诗开头正文条目（确认体例）
2. SFTK rules 引用的 source_id 清单（评估降级影响面）"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print('===== SFTK-124 總言篇 / SFTK-125 六神篇 非歌詩开头条目 =====')
for l in open(r'D:\shuntian-ziping-p0\registries\source\sources.sftk.jsonl', encoding='utf-8').read().splitlines():
    if not l.strip():
        continue
    s = json.loads(l)
    if s.get('chapter') in ('總言篇', '六神篇') and not s.get('source_text', '').strip().startswith(('歌', '詩')):
        print(f"  {s['source_id']} | {s.get('text_layer')} | {s.get('evidence_grade')} | {s.get('source_text', '')[:60]}")

print()
print('===== SFTK rules 引用 source_id =====')
srcs = set()
for l in open(r'D:\shuntian-ziping-p0\registries\rule\rules.sftk.jsonl', encoding='utf-8').read().splitlines():
    if not l.strip():
        continue
    r = json.loads(l)
    for sid in r.get('source_ids', []):
        srcs.add(sid)
print(f'SFTK 规则引用 source 数: {len(srcs)}')
for sid in sorted(srcs):
    print('  ', sid)
