# -*- coding: utf-8 -*-
"""PATCH-003B 逐条核验：原文层级 vs scope cell 期望层级 一致性比对"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

checklist = json.load(io.open(r'D:\shuntian-ziping-p0\governance\patch_003b_evidence_checklist.json', encoding='utf-8'))
scope = json.load(io.open(r'D:\shuntian-ziping-p0\governance\r1_05_verified_scope.json', encoding='utf-8'))

BOOK_FILE = {'YHZP': 'yhzp', 'PZZQ': 'pzzq', 'DTS': 'dts', 'QTBJ': 'qtbj', 'SMTH': 'smth', 'SFTK': 'sftk'}
src = {}
for b, f in BOOK_FILE.items():
    src[b] = {}
    for l in io.open(rf'D:\shuntian-ziping-p0\registries\source\sources.{f}.jsonl', encoding='utf-8'):
        if not l.strip():
            continue
        s = json.loads(l)
        src[b][s['source_id']] = s

# 收集 scope 中每个 source 的期望（按书）
expect_by_book = {}
for dk, dom in scope.items():
    for b, cells in dom.get('books', {}).items():
        for c in cells:
            sid = c.get('source_id')
            if not sid:
                continue
            expect_by_book.setdefault(b, {}).setdefault(sid, []).append({
                'domain': dk,
                'layer': c.get('text_layer'),
                'grade': c.get('evidence_grade'),
                'attr': c.get('attribution'),
            })

issues = []
verified = 0
for book, items in checklist.items():
    for it in items:
        sid = it['source_id']
        if it.get('verification_status') == 'RESOLVED_NOT_FOUND':
            continue
        s = src.get(book, {}).get(sid)
        if not s:
            continue
        o_tl, o_eg, o_at = s.get('text_layer'), s.get('evidence_grade'), s.get('attribution')
        exps = expect_by_book.get(book, {}).get(sid, [])
        for e in exps:
            # 期望中有 TO_VERIFY 的跳过（第一批转换遗留）
            if e['layer'] == 'TO_VERIFY':
                continue
            mism = []
            if e['layer'] and e['layer'] != '—' and o_tl and e['layer'] != o_tl:
                mism.append(f"layer scope={e['layer']} 原文={o_tl}")
            if e['grade'] and e['grade'] != '—' and o_eg and e['grade'] != o_eg:
                mism.append(f"grade scope={e['grade']} 原文={o_eg}")
            if e['attr'] and e['attr'] != '—' and o_at and e['attr'] != o_at:
                mism.append(f"attr scope={e['attr']} 原文={o_at}")
            if mism:
                issues.append((book, sid, e['domain'], '；'.join(mism)))
            else:
                verified += 1

print(f'=== 一致：{verified} 条 ===')
print(f'=== 不一致：{len(issues)} 条 ===')
for b, sid, dom, m in issues:
    print(f'  {b} {sid} [{dom}]: {m}')
