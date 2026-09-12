# -*- coding: utf-8 -*-
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
roots = ["D:/顺天系统资料", "D:/shuntian/docs", "C:/Users/ming/Desktop/V2版本手册", "C:/Users/ming/Desktop"]
hits = []
for r in roots:
    if not os.path.isdir(r): continue
    for root, dirs, files in os.walk(r):
        for f in files:
            if f.endswith((".md", ".txt")):
                p = os.path.join(root, f)
                try:
                    t = io.open(p, encoding="utf-8", errors="ignore").read()
                except: continue
                if any(k in t for k in ["食伤制杀", "伤官制官", "食伤生财", "印化官杀", "官杀制比劫", "比劫制财", "职业"]):
                    cnt = sum(t.count(k) for k in ["食伤制杀", "伤官制官", "食伤生财", "印化官杀", "官杀制比劫", "比劫制财", "职业"])
                    hits.append((cnt, p))
hits.sort(reverse=True)
for c, p in hits[:30]:
    print(c, p)
