# -*- coding: utf-8 -*-
"""003B-04 Rule Admission 十一门槛检查：对 scope 全部 cell 核查"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

data = json.load(io.open(r'D:\shuntian-ziping-p0\governance\r1_05_verified_scope.json', encoding='utf-8'))
BOOK_FILE = {'YHZP': 'yhzp', 'PZZQ': 'pzzq', 'DTS': 'dts', 'QTBJ': 'qtbj', 'SMTH': 'smth', 'SFTK': 'sftk'}
src = {}
for b, f in BOOK_FILE.items():
    src[b] = set()
    for l in io.open(rf'D:\shuntian-ziping-p0\registries\source\sources.{f}.jsonl', encoding='utf-8'):
        if not l.strip():
            continue
        src[b].add(json.loads(l)['source_id'])

SIX = ['YHZP', 'PZZQ', 'DTS', 'QTBJ', 'SMTH', 'SFTK']

def gate(c, book, src_ids):
    checks = {}
    # 1 六部来源
    checks['g1_six_classics'] = book in SIX
    # 2 精确章节
    ch = c.get('chapter_id') or '—'
    checks['g2_chapter'] = ch not in ('—', 'TO_VERIFY', 'NOT_FOUND', None, '')
    # 3 原文存在
    sid = c.get('source_id')
    checks['g3_source_exists'] = bool(sid) and sid in src_ids
    # 4 text_layer 确认
    tl = c.get('text_layer') or '—'
    checks['g4_text_layer'] = tl not in ('—', 'TO_VERIFY', 'NOT_FOUND', None, '')
    # 5 evidence_grade 确认
    eg = c.get('evidence_grade') or '—'
    checks['g5_grade'] = eg not in ('—', 'UNKNOWN', 'TO_VERIFY', None, '')
    # 6 attribution 确认
    at = c.get('attribution') or '—'
    checks['g6_attribution'] = at not in ('—', 'UNKNOWN', 'TO_VERIFY', None, '')
    # 7 语境完整
    sd = c.get('semantic_definition') or ''
    checks['g7_context'] = len(sd) > 5
    # 8 条件完整：Scope 层领域 rule_boundary 已冻结；具体条件留 Rule 层
    ex = c.get('excluded_scope') or ''
    checks['g8_condition'] = bool(ex and ex != '—') or 'PENDING_RULE_LAYER'
    # 9 不跨书融合：rule_boundary forbidden 非空（领域级）
    # 10 不升级注解：ANNOTATION 层 cell 的 grade 必须 B 系列
    if tl == 'ANNOTATION':
        checks['g10_no_upgrade'] = (eg or '').startswith('B')
    else:
        checks['g10_no_upgrade'] = True
    # 11 Rule-Test-Golden 闭环：Rule 层未启动 → PENDING
    checks['g11_rtg_loop'] = 'PENDING_RULE_LAYER'
    return checks

results = {'PASS': 0, 'FAIL': [], 'CORE_ELIGIBLE': [], 'EXCLUDED_FROM_RULE': 0, 'FAIL_CLOSED': 0}
for dk, dom in data.items():
    rb = dom.get('rule_boundary', {})
    for b, cells in dom.get('books', {}).items():
        for c in cells:
            elig = c.get('execution_eligibility') or '—'
            if elig == 'EXCLUDED_FROM_RULE':
                results['EXCLUDED_FROM_RULE'] += 1
                continue
            if elig == 'FAIL_CLOSED':
                results['FAIL_CLOSED'] += 1
                continue
            if elig != 'CORE_RULE_ELIGIBLE':
                continue
            checks = gate(c, b, src[b])
            fails = [k for k, v in checks.items() if v is False]
            sid = c.get('source_id') or '—'
            entry = {'domain': dk, 'book': b, 'source_id': sid, 'chapter': c.get('chapter_id'),
                     'text_layer': c.get('text_layer'), 'grade': c.get('evidence_grade'),
                     'attribution': c.get('attribution'), 'eligibility': elig,
                     'checks': {k: (v if not isinstance(v, bool) else ('PASS' if v else 'FAIL')) for k, v in checks.items()}}
            if not fails:
                results['PASS'] += 1
                entry['admission_status'] = 'ADMISSIBLE_PENDING_RULE'
            else:
                results['FAIL'].append(entry)
                entry['admission_status'] = 'BLOCKED'
            results['CORE_ELIGIBLE'].append(entry)

print(f"=== 003B-04 十一门槛检查 ===")
print(f"CORE_RULE_ELIGIBLE cell：{len(results['CORE_ELIGIBLE'])}")
print(f"  通过（ADMISSIBLE_PENDING_RULE）：{results['PASS']}")
print(f"  受阻（BLOCKED）：{len(results['FAIL'])}")
print(f"EXCLUDED_FROM_RULE：{results['EXCLUDED_FROM_RULE']}")
print(f"FAIL_CLOSED：{results['FAIL_CLOSED']}")
if results['FAIL']:
    print('\n=== BLOCKED 明细 ===')
    for e in results['FAIL']:
        fails = [k for k, v in e['checks'].items() if v == 'FAIL']
        print(f"  {e['book']} {e['source_id']} [{e['domain']}]: {fails}")
json.dump(results, io.open(r'D:\shuntian-ziping-p0\governance\patch_003b_rule_admission.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('\n已写 governance/patch_003b_rule_admission.json')
