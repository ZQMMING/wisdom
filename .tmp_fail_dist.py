# -*- coding: utf-8 -*-
import subprocess, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
r = subprocess.run([".venv/Scripts/python.exe","-m","pytest","tests/","-q","--no-header","--ignore=tests/test_ziping_15_2_evidence_provenance.py","-p","no:randomly"], capture_output=True, text=True, timeout=600)
out = r.stdout + r.stderr
lines = out.splitlines()
# 提取 FAILED/ERROR 行
fails = [l for l in lines if l.startswith("FAILED") or l.startswith("ERROR")]
from collections import Counter
c = Counter()
for l in fails:
    # 取 tests/xxx.py 部分
    if "tests/" in l:
        part = l.split("tests/")[1].split("::")[0]
        c[part] += 1
print("=== 失败分布 ===")
for k, v in c.most_common():
    print(f"{v:4d}  {k}")
print("=== 盲派相关失败 ===")
blind_fails = [l for l in fails if "blind" in l.lower()]
print("\n".join(blind_fails) if blind_fails else "(无)")
print("TOTAL FAIL/ERR:", len(fails))
