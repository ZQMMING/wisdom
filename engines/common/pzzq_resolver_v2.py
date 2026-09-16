# -*- coding: utf-8 -*-
"""PATCH-140 PZZQ Resolver v2
candidate + PatternTypeRegistry + PZZQ Assertion -> pattern_condition_state
只挂条件, 不判成格/破格.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REG = json.load(open(ROOT/'registries/pzzq_pattern_type_registry_v1.json', encoding='utf-8'))
# alias -> canonical
ALIAS2CANON = {}
for canon, aliases in REG['aliases'].items():
    ALIAS2CANON[canon] = canon
    for a in aliases:
        ALIAS2CANON[a] = canon

_BUCKET = {'requires': 'required', 'supports': 'supported', 'activates': 'required',
           'selects': 'supported', 'blocks': 'blocked', 'rejects': 'blocked',
           'changes': 'supported', 'separates': 'supported', 'distinguishes': 'supported',
           'determines': 'supported'}


def resolve(candidate, pzzq_assertions):
    canon = candidate['pattern_type']
    out = {
        'pattern': canon,
        'candidate_status': candidate['status'],
        'resolution_status': 'CONDITION_ATTACHED',
        'conditions': {'required': [], 'blocked': [], 'supported': []},
        'evidence': candidate.get('evidence', []),
        'assertion_links': [],
    }
    for a in pzzq_assertions:
        subj = a['subject']
        # subject归一到canon
        if subj in ALIAS2CANON and ALIAS2CANON[subj] == canon:
            bucket = _BUCKET.get(a['predicate'])
            link = {'id': a['assertion_id'], 'predicate': a['predicate'],
                    'object': a['object'], 'source_evidence': a.get('source_evidence', [])}
            out['assertion_links'].append(link)
            obj = a['object']
            if bucket == 'required' and obj not in out['conditions']['required']:
                out['conditions']['required'].append(obj)
            elif bucket == 'blocked' and obj not in out['conditions']['blocked']:
                out['conditions']['blocked'].append(obj)
            elif bucket == 'supported' and obj not in out['conditions']['supported']:
                out['conditions']['supported'].append(obj)
    return out


if __name__ == '__main__':
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.path.insert(0, '.')
    from engines.common.l0_fact_builder import build
    from engines.common.pzzq_producer_v1 import produce_pattern_candidates
    rows = [json.loads(l) for l in open(ROOT/'registries/assertions/pzzq_assertions.jsonl', encoding='utf-8')]
    gc001 = {'year': ['癸','亥'], 'month': ['壬','戌'], 'day': ['乙','未'], 'hour': ['壬','午']}
    facts = build(gc001)
    cands = produce_pattern_candidates(facts)['pattern_candidates']
    print('GC-001 正财候选 resolve:')
    print(json.dumps(resolve(cands[0], rows), ensure_ascii=False, indent=2))
