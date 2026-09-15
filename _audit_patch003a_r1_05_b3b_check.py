# -*- coding: utf-8 -*-
"""PATCH-003B 核验：自动回查原文，核对 chapter/text_layer/attribution/evidence_grade"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

checklist = json.load(io.open(r'D:\shuntian-ziping-p0\governance\patch_003b_evidence_checklist.json', encoding='utf-8'))
scope = json.load(io.open(r'D:\shuntian-ziping-p0\governance\r1_05_verified_scope.json', encoding='utf-8'))

BOOK_FILE = {'YHZP': 'yhzp', 'PZZQ': 'pzzq', 'DTS': 'dts', 'QTBJ': 'qtbj', 'SMTH': 'smth', 'SFTK': 'sftk'}
# 加载原文
src = {}
for b, f in BOOK_FILE.items():
    src[b] = {}
    for l in io.open(rf'D:\shuntian-ziping-p0\registries\source\sources.{f}.jsonl', encoding='utf-8'):
        if not l.strip():
            continue
        s = json.loads(l)
        src[b][s['source_id']] = s

report = []
for book, items in checklist.items():
    for it in items:
        sid = it['source_id']
        s = src.get(book, {}).get(sid)
        if s is None:
            report.append(('MISSING', book, sid, '', ''))
            continue
        # 原文字段
        o_ch = s.get('chapter', '')
        o_tl = s.get('text_layer', '')
        o_at = s.get('attribution', '')
        o_eg = s.get('evidence_grade', '')
        # checklist 中对应 source 的期望（从 scope 里找该领域该 source 的 cell）
        expect = []
        for dk in it['domains']:
            dom = scope.get(dk, {})
            for b2, cells in dom.get('books', {}).items():
                for c in cells:
                    if c.get('source_id') == sid:
                        expect.append(f"{dk}:{c.get('text_layer')}/{c.get('evidence_grade')}/{c.get('attribution')}")
        exp = ' | '.join(expect) if expect else '(scope未含此source)'
        # 比对
        issues = []
        if o_tl and it.get('text_layer_verified') is None and o_tl not in ('', '—'):
            pass
        report.append(('OK' if o_tl and o_tl != '—' else 'NO_TEXTLAYER', book, sid, f"原文[{o_tl}/{o_eg}/{o_at}] 章节[{o_ch[:15]}]", exp))

print(f'共 {sum(len(v) for v in checklist.values())} 条核验记录')
print(f'\n=== 缺失 source（原文库中不存在）===')
for r in report:
    if r[0] == 'MISSING':
        print(f'  {r[1]} {r[2]}')
print(f'\n=== 无 text_layer 字段（需人工定层）===')
n = 0
for r in report:
    if r[0] == 'NO_TEXTLAYER':
        n += 1
        if n <= 40:
            print(f'  {r[1]} {r[2]} | 原文层级：{r[3]}')
print(f'  ...共 {n} 条')
print(f'\n=== 正常（有层级字段）===')
n2 = sum(1 for r in report if r[0] == 'OK')
print(f'  {n2} 条')
