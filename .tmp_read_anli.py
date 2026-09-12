# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
p = r"D:\顺天系统资料\盲派命理-案例资料集.md"
src = io.open(p, encoding="utf-8").read()
print("LEN:", len(src))
print("=== 目录/标题 ===")
for l in src.splitlines():
    if l.startswith("#") or l.startswith("##") or l.startswith("###"):
        print(l)
