# -*- coding: utf-8 -*-
"""PATCH-003B 启动：从 R1-05 Scope 提取全部 source_id 生成逐章节核验清单"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

scope = json.load(io.open(r'D:\shuntian-ziping-p0\governance\r1_05_verified_scope.json', encoding='utf-8'))

# 收集全部 source_id（按书分组）
by_book = {}
for dkey, dom in scope.items():
    for b, cells in dom.get('books', {}).items():
        for c in cells:
            sid = c.get('source_id')
            if not sid:
                continue
            by_book.setdefault(b, {}).setdefault(sid, []).append(dkey)

total = 0
checklist = {}
for b in ['YHZP', 'PZZQ', 'DTS', 'QTBJ', 'SMTH', 'SFTK']:
    sids = sorted(by_book.get(b, {}).keys())
    total += len(sids)
    checklist[b] = [{
        'source_id': sid,
        'domains': sorted(set(by_book[b][sid])),
        'chapter_verified': None,
        'text_layer_verified': None,
        'attribution_verified': None,
        'evidence_grade_verified': None,
        'usage_type_verified': None,
        'rule_boundary_ok': None,
        'verification_status': 'PENDING',
        'note': '',
    } for sid in sids]

with io.open(r'D:\shuntian-ziping-p0\governance\patch_003b_evidence_checklist.json', 'w', encoding='utf-8') as f:
    json.dump(checklist, f, ensure_ascii=False, indent=2)

print(f'003B 待核验 source 总数：{total}')
for b, items in checklist.items():
    print(f'  {b}: {len(items)} 条')
