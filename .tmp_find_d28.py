# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import glob
for f in ["tests/test_blind_golden.py", "tests/test_blind_negative.py", "tests/test_blind_integration_bazi.py", "tests/test_blind_yingqi.py"]:
    src = io.open(f, encoding="utf-8").read()
    if "D28" in src or "己巳" in src or "丁未" in src:
        print("###", f)
        for l in src.splitlines():
            if "D28" in l or "己巳" in l or "壬申" in l:
                print(l[:160])
