# -*- coding: utf-8 -*-
"""
PATCH-124 independent validator (organizer side, not the subagent's self-check).
Reads registries/assertions/smth_assertions.jsonl and runs the audit gates:
  G1 field completeness / JSON validity
  G2 assertion_id sequential from ASSERT-SMTH-0001
  G3 namespace closed set {SMTH.luck, SMTH.luck_response, SMTH.time_modifier, SMTH.special_reference}
  G4 assertion_type / runtime_action / polarity / grade enums
  G5 consumer == ["SMTH"]
  G6 source_evidence all exist in smth_evidence.jsonl and belong to the CANDIDATE set
  G7 FORBIDDEN: predicate rewrites/alters or natal-rewrite semantics
  G8 FORBIDDEN: human-affair fortune words in subject/object/human_text
  G9 FORBIDDEN: specific-year 应期 phrases (某年+发财/升官/结婚...)
  G10 classic == 三命通会, audit_status == CANDIDATE
Prints PASS/FAIL per gate + distributions. Exit non-zero on any FAIL.
"""
import json, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'registries', 'assertions', 'smth_assertions.jsonl')
EV = os.path.join(HERE, 'registries', 'evidence', 'smth_evidence.jsonl')
CAND = os.path.join(HERE, 'registries', 'evidence', 'smth_patch124_candidates.json')

ALLOWED_NS = {'SMTH.luck', 'SMTH.luck_response', 'SMTH.time_modifier', 'SMTH.special_reference'}
ALLOWED_TYPE = {'DEFINITION', 'CONDITION', 'RELATION', 'EXCEPTION', 'NEGATION'}
ALLOWED_RA = {'SUPPORT_STATE', 'CHANGE_RELATION', 'BLOCK_RULE', 'CONTEXT_MARKER'}
ALLOWED_POL = {'positive', 'negative', 'neutral'}
ALLOWED_GRADE = {'A', 'B'}
REQUIRED = ['assertion_id','source_evidence','classic','namespace','subject','predicate',
            'object','condition','polarity','assertion_type','grade','consumer',
            'runtime_action','human_text','audit_status']

FORBIDDEN_PRED = re.compile(r'rewrit|alter|overwrit|覆盖|改写|改变本命|改写命局', re.I)
FORTUNE_WORDS = ['发财','發財','升官','結婚','结婚','富貴','富贵','貧賤','贫贱','夭',
                 '娼','淫','濫','克妻','剋妻','无子','無子','財物耗散','财物耗散','破家',
                 '橫死','横死','伶仃','孤貧','大貴人','大貴','拜相','封侯']
YINGQI = re.compile(r'某年|今年|明年|\d{4}\s*年.{0,6}(發|发|升官|結婚|结婚|生|死)')

ev_ids = set()
for l in open(EV, encoding='utf-8'):
    if l.strip():
        ev_ids.add(json.loads(l)['evidence_id'])
cand_ids = {r['evidence_id'] for r in json.load(open(CAND, encoding='utf-8'))}

lines = [l for l in open(A, encoding='utf-8') if l.strip()]
rows = []
fails = []

# G1
for i, l in enumerate(lines):
    try:
        rows.append(json.loads(l))
    except Exception as e:
        fails.append(f'G1 line {i+1} not JSON: {e}')
if rows:
    for i, r in enumerate(rows):
        missing = [f for f in REQUIRED if f not in r]
        if missing:
            fails.append(f"G1 {r.get('assertion_id','?')} missing {missing}")

# G2
for i, r in enumerate(rows):
    expect = f'ASSERT-SMTH-{i+1:04d}'
    if r.get('assertion_id') != expect:
        fails.append(f"G2 row {i+1} id={r.get('assertion_id')} expected {expect}")

# G3/G4/G5/G10
for r in rows:
    if r.get('namespace') not in ALLOWED_NS:
        fails.append(f"G3 {r['assertion_id']} bad namespace {r.get('namespace')}")
    if r.get('assertion_type') not in ALLOWED_TYPE:
        fails.append(f"G4 {r['assertion_id']} bad type {r.get('assertion_type')}")
    if r.get('runtime_action') not in ALLOWED_RA:
        fails.append(f"G4 {r['assertion_id']} bad runtime_action {r.get('runtime_action')}")
    if r.get('polarity') not in ALLOWED_POL:
        fails.append(f"G4 {r['assertion_id']} bad polarity {r.get('polarity')}")
    if r.get('grade') not in ALLOWED_GRADE:
        fails.append(f"G4 {r['assertion_id']} bad grade {r.get('grade')}")
    if r.get('consumer') != ['SMTH']:
        fails.append(f"G5 {r['assertion_id']} consumer={r.get('consumer')}")
    if r.get('classic') != '三命通会':
        fails.append(f"G10 {r['assertion_id']} classic={r.get('classic')}")
    if r.get('audit_status') != 'CANDIDATE':
        fails.append(f"G10 {r['assertion_id']} audit_status={r.get('audit_status')}")

# G6
for r in rows:
    for eid in r.get('source_evidence', []):
        if eid not in ev_ids:
            fails.append(f"G6 {r['assertion_id']} cites unknown evidence {eid}")
        elif eid not in cand_ids:
            fails.append(f"G6 {r['assertion_id']} cites non-candidate evidence {eid}")

# G7
for r in rows:
    if FORBIDDEN_PRED.search(str(r.get('predicate',''))) or \
       FORBIDDEN_PRED.search(str(r.get('object',''))) or \
       FORBIDDEN_PRED.search(str(r.get('subject',''))):
        fails.append(f"G7 {r['assertion_id']} natal-rewrite semantics in SPO: {r.get('predicate')} / {r.get('object')}")

# G8
for r in rows:
    blob = ' '.join(str(r.get(k,'')) for k in ('subject','object','human_text'))
    hit = [w for w in FORTUNE_WORDS if w in blob]
    if hit:
        fails.append(f"G8 {r['assertion_id']} fortune words {hit}")

# G9
for r in rows:
    blob = ' '.join(str(r.get(k,'')) for k in ('subject','object','human_text'))
    if YINGQI.search(blob):
        fails.append(f"G9 {r['assertion_id']} specific-year 应期 phrase")

# distributions
print(f'total assertions: {len(rows)}')
print('type  :', dict(collections.Counter(r["assertion_type"] for r in rows)))
print('grade :', dict(collections.Counter(r["grade"] for r in rows)))
print('ns    :', dict(collections.Counter(r["namespace"] for r in rows)))
print('ra    :', dict(collections.Counter(r["runtime_action"] for r in rows)))
print('pol   :', dict(collections.Counter(r["polarity"] for r in rows)))
used_ev = sorted({e for r in rows for e in r['source_evidence']})
print('candidate rows consumed:', len(used_ev), '/ 34')
print('candidate rows NOT consumed:', sorted(cand_ids - set(used_ev)))
print()
if fails:
    print('=== FAIL ===')
    for f in fails:
        print(' ', f)
    sys.exit(1)
print('ALL GATES PASS')
