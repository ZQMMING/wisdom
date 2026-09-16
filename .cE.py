# -*- coding: utf-8 -*-
import sys, inspect
sys.path.insert(0, r"D:\shuntian")
import os
print([f for f in os.listdir(r"D:\shuntian\src\tongshu\engines") if "blind" in f])
# 找 BlindBaziResult 来源
for root, dirs, files in os.walk(r"D:\shuntian\src\tongshu\engines"):
    for f in files:
        if f.endswith(".py") and "blind" in f:
            p = os.path.join(root, f)
            s = open(p, encoding="utf-8", errors="ignore").read()
            if "BlindBaziResult" in s or "class BlindBazi" in s:
                print(p, "->", [l.strip() for l in s.splitlines() if "BlindBaziResult" in l or "def analyze" in l or "def compute" in l or "class Blind" in l][:5])
