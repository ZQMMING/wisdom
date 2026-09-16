# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r"D:\shuntian")
from tongshu.engines.blind_interpretation import audit_full_coverage, audit_assertion_provenance, audit_modern_fidelity
print("== audit_full_coverage ==")
r = audit_full_coverage()
print(json.dumps(r, ensure_ascii=False, indent=1)[:3000])
