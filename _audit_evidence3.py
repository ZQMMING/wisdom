# -*- coding: utf-8 -*-
"""PENDING-EVIDENCE-03 钉查：YHZP/QTBJ/DTS/PZZQ 印旺条 章节定位 + text_layer"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TARGETS = {
    'yhzp': ['YHZP-138-001', 'YHZP-083-002', 'YHZP-131-001', 'YHZP-084-002', 'YHZP-100-002'],
    'qtbj': ['QTBJ-040-001', 'QTBJ-049-001', 'QTBJ-094-001', 'QTBJ-111-002', 'QTBJ-111-005'],
    'dts': ['DTS-045-001', 'DTS-033-015', 'DTS-033-014'],
    'pzzq': ['PZZQ-007-001', 'PZZQ-007-022', 'PZZQ-007-023'],
}
for eng, sids in TARGETS.items():
    print(f'===== {eng} =====')
    lines = open(f'D:/shuntian-ziping-p0/registries/source/sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
    for l in lines:
        if not l.strip():
            continue
        s = json.loads(l)
        if s.get('source_id') in sids:
            print(f"  {s['source_id']} | 章节: {s.get('chapter')} | layer: {s.get('text_layer')} | grade: {s.get('evidence_grade')}")
            print(f"    text: {s.get('source_text', '')[:90]}")
