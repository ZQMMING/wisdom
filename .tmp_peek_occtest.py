# -*- coding: utf-8 -*-
import io, sys, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
for f in glob.glob("tests/test_blind*.py"):
    t = io.open(f, encoding="utf-8").read()
    if "occupation" in t or "OCCUPATION" in t:
        print("###", f)
        for l in t.splitlines():
            if "occupation" in l.lower():
                print("  ", l.strip()[:120])
